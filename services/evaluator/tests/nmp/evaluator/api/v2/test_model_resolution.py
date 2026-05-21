# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Tests for model resolution utilities."""

from typing import Any, cast
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from nemo_evaluator_sdk.enums import ModelFormat
from nemo_evaluator_sdk.values import Model as SDKModel
from nemo_platform import NotFoundError
from nmp.evaluator.api.v2.common.inline_models import Model
from nmp.evaluator.api.v2.common.model_resolution import (
    resolve_model,
    resolve_params_model_refs,
    rewrite_models_for_job_container,
)
from nmp.evaluator.app.values.common import ModelRef
from pydantic import ValidationError


class TestResolveModel:
    """Tests for resolve_model function."""

    @pytest.mark.asyncio
    async def test_resolve_model_passthrough(self):
        """Model values are returned unchanged."""
        model = Model(url="http://example.com/v1", name="gpt-4o", format=ModelFormat.OPEN_AI)
        result = await resolve_model(model)
        assert result is model

    @pytest.mark.asyncio
    async def test_resolve_sdk_model_coerces_to_service_model(self):
        """SDK Model values are revalidated as service API Model values."""
        model = SDKModel(url="http://example.com/v1", name="gpt-4o", format=ModelFormat.OPEN_AI)
        result = await resolve_model(model)

        assert isinstance(result, Model)
        assert result.model_dump(mode="json") == model.model_dump(mode="json")

    @pytest.mark.asyncio
    async def test_resolve_model_ref(self):
        """ModelRef is resolved via SDK to an Model with IGW URL."""
        mock_sdk = MagicMock()
        mock_sdk.models.retrieve = AsyncMock(return_value=MagicMock())
        mock_sdk.models.get_model_entity_route_openai_url = MagicMock(
            return_value="http://gateway:8080/v1/my-workspace/my-model"
        )

        ref = ModelRef(root="my-workspace/my-model")
        result = await resolve_model(ref, sdk=mock_sdk)

        assert isinstance(result, Model)
        assert result.url == "http://gateway:8080/v1/my-workspace/my-model"
        assert result.name == "my-model"
        assert result.format == "nim"
        mock_sdk.models.retrieve.assert_called_once_with("my-model", workspace="my-workspace")

    @pytest.mark.asyncio
    async def test_resolve_model_ref_invalid_format(self):
        """ModelRef with invalid format is rejected by Pydantic validation."""
        with pytest.raises(ValidationError, match="string_pattern_mismatch"):
            ModelRef(root="no-slash")

    @pytest.mark.asyncio
    async def test_resolve_model_ref_empty_parts(self):
        """ModelRef with empty workspace or name is rejected by Pydantic validation."""
        with pytest.raises(ValidationError):
            ModelRef(root="/model-name")

        with pytest.raises(ValidationError):
            ModelRef(root="workspace/")

    @pytest.mark.asyncio
    async def test_resolve_model_ref_not_found(self):
        """ModelRef pointing to non-existent entity raises ValueError with helpful message."""
        mock_sdk = MagicMock()
        # NotFoundError requires response, body, and message
        mock_response = httpx.Response(status_code=404, request=httpx.Request("GET", "http://test"))
        mock_sdk.models.retrieve = AsyncMock(
            side_effect=NotFoundError(
                response=mock_response,
                body=None,
                message="Not found",
            )
        )

        ref = ModelRef(root="my-workspace/missing-model")
        with pytest.raises(ValueError, match="not found") as exc_info:
            await resolve_model(ref, sdk=mock_sdk)

        # Verify the error message includes actionable details
        assert "missing-model" in str(exc_info.value)
        assert "my-workspace" in str(exc_info.value)
        assert "inline model definition" in str(exc_info.value)

        # Verify the original NotFoundError is chained
        assert isinstance(exc_info.value.__cause__, NotFoundError)

    @pytest.mark.asyncio
    async def test_resolve_model_unsupported_type(self):
        """Unsupported model type raises TypeError."""
        with pytest.raises(TypeError, match="Unsupported model type"):
            await resolve_model(cast(Any, "raw-string"))


class TestResolveParamsModelRefs:
    """Tests for resolve_params_model_refs function."""

    @pytest.mark.asyncio
    async def test_resolve_params_no_model_refs(self):
        """Params without model refs are returned unchanged."""
        params = {"some_key": "some_value", "number": 42}
        result = await resolve_params_model_refs(params)
        assert result == params

    @pytest.mark.asyncio
    async def test_resolve_params_judge_model_ref(self):
        """String model ref in judge param is resolved to Model dict."""
        resolved_model = Model(
            url="http://gateway:8080/v1/ws/judge",
            name="judge",
            format=ModelFormat.NVIDIA_NIM,
        )

        params = {
            "judge": {
                "model": "ws/judge",
                "other_setting": "value",
            },
        }

        with patch(
            "nmp.evaluator.api.v2.common.model_resolution.resolve_model",
            new_callable=AsyncMock,
            return_value=resolved_model,
        ):
            result = await resolve_params_model_refs(params)

        # The model field should be replaced with a Model dict
        assert isinstance(result["judge"]["model"], dict)
        assert result["judge"]["model"]["url"] == "http://gateway:8080/v1/ws/judge"
        assert result["judge"]["model"]["name"] == "judge"
        assert result["judge"]["model"]["format"] == "nim"
        # Other settings preserved
        assert result["judge"]["other_setting"] == "value"

    @pytest.mark.asyncio
    async def test_resolve_params_judge_embeddings_model_ref(self):
        """String model ref in judge_embeddings param is resolved."""
        resolved_model = Model(
            url="http://gateway:8080/v1/ws/embed",
            name="embed",
            format=ModelFormat.NVIDIA_NIM,
        )

        params = {
            "judge_embeddings": {
                "model": "ws/embed",
            },
        }

        with patch(
            "nmp.evaluator.api.v2.common.model_resolution.resolve_model",
            new_callable=AsyncMock,
            return_value=resolved_model,
        ):
            result = await resolve_params_model_refs(params)

        assert isinstance(result["judge_embeddings"]["model"], dict)
        assert result["judge_embeddings"]["model"]["name"] == "embed"

    @pytest.mark.asyncio
    async def test_resolve_params_dict_model_unchanged(self):
        """Dict model values (inline models) are not modified."""
        params = {
            "judge": {
                "model": {"url": "http://example.com/v1", "name": "gpt-4o", "format": "openai"},
            },
        }
        result = await resolve_params_model_refs(params)
        # Dict model should remain unchanged
        assert result["judge"]["model"] == params["judge"]["model"]

    @pytest.mark.asyncio
    async def test_resolve_params_does_not_mutate_original(self):
        """Original params dict is not mutated."""
        params = {
            "judge": {
                "model": {"url": "http://example.com/v1", "name": "gpt-4o", "format": "openai"},
            },
        }
        original_model = dict(params["judge"]["model"])
        await resolve_params_model_refs(params)
        assert params["judge"]["model"] == original_model


class TestRewriteModelsForJobContainer:
    def test_rewrites_loopback_model_urls(self):
        payload = {
            "model": {
                "url": "http://localhost:8080/apis/inference-gateway/v2/workspaces/ws/model/test/-/v1",
                "host_url": "http://127.0.0.1:9000",
                "name": "test-model",
                "format": "nim",
            }
        }

        result = rewrite_models_for_job_container(payload, target_base_url="http://nmp-quickstart:8080")

        assert result["model"]["url"] == (
            "http://nmp-quickstart:8080/apis/inference-gateway/v2/workspaces/ws/model/test/-/v1"
        )
        assert result["model"]["host_url"] == "http://nmp-quickstart:8080"
        assert payload["model"]["url"].startswith("http://localhost")

    def test_rewrites_nested_models_only(self):
        payload = {
            "metric_params": {
                "judge": {
                    "model": {
                        "url": "http://127.0.0.1:8080/apis/inference-gateway/v2/workspaces/ws/model/judge/-/v1",
                        "name": "judge-model",
                        "format": "nim",
                    }
                }
            },
            "other_url": "http://localhost:8080/leave-alone",
        }

        result = rewrite_models_for_job_container(payload, target_base_url="http://container-abc123:8080")

        assert result["metric_params"]["judge"]["model"]["url"] == (
            "http://container-abc123:8080/apis/inference-gateway/v2/workspaces/ws/model/judge/-/v1"
        )
        assert result["other_url"] == "http://localhost:8080/leave-alone"

    def test_leaves_non_loopback_model_urls_unchanged(self):
        payload = {
            "model": {
                "url": "http://gateway:8080/apis/inference-gateway/v2/workspaces/ws/model/test/-/v1",
                "name": "test-model",
                "format": "nim",
            }
        }

        result = rewrite_models_for_job_container(payload, target_base_url="http://container-abc123:8080")

        assert result == payload
