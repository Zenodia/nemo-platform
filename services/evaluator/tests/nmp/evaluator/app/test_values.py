# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Tests for evaluator app value models."""

import pytest
from nemo_evaluator_sdk.enums import ModelFormat
from nemo_evaluator_sdk.values import DatasetRows, InferenceParams, Model, RunConfigOnlineModel, SecretRef
from pydantic import ValidationError

# Many tests in this file intentionally pass invalid arguments to verify
# that Pydantic validation rejects them. We use **{} to bypass type checking
# for intentionally invalid arguments.


class TestSecretRefValidation:
    @pytest.mark.parametrize(
        ("value", "expected"),
        [
            ("workspace/name", "workspace/name"),
            ("secret-name", "secret-name"),
            ("NVIDIA_BUILD_API_KEY", "NVIDIA_BUILD_API_KEY"),
            ("workspace/NVIDIA_BUILD_API_KEY", "workspace/NVIDIA_BUILD_API_KEY"),
            ("Workspace/Secret_Name", "Workspace/Secret_Name"),
        ],
    )
    def test_valid_secret_ref(self, value: str, expected: str):
        secret_ref = SecretRef(value)
        assert secret_ref.root == expected

    @pytest.mark.parametrize(
        "value",
        [
            "invalid/workspace/ref",
            "invalid/characters@?",
            "invalid-characters@?",
            "",
        ],
    )
    def test_invalid_secret_ref(self, value: str):
        with pytest.raises(ValidationError) as e:
            SecretRef(value)
        assert "String should match pattern" in str(e.value.errors())


class TestModelSecretEnv:
    @pytest.mark.parametrize(
        ("value", "expected"),
        [
            ("my-workspace/my-secret", "my_workspace_my_secret"),
            ("my-secret", "my_secret"),
            ("9my-secret", "_9my_secret"),
            ("NVIDIA_BUILD_API_KEY", "NVIDIA_BUILD_API_KEY"),
            ("workspace/NVIDIA_BUILD_API_KEY", "workspace_NVIDIA_BUILD_API_KEY"),
            ("Workspace/Secret_Name", "Workspace_Secret_Name"),
        ],
    )
    def test_api_key_env(self, value: str, expected: str):
        model = Model(
            url="http://localhost:8000",
            name="my-model",
            api_key_secret=SecretRef(value),
        )
        assert model.api_key_env == expected


class TestRunConfigValidation:
    """Tests for RunConfig extra field rejection."""

    def test_valid_params_accepted(self):
        """Valid parameters should be accepted."""
        params = RunConfigOnlineModel(
            limit_samples=10,
            parallelism=4,
            max_retries=2,
            request_timeout=120,
            inference=InferenceParams(max_tokens=1024, temperature=0.5),
        )
        assert params.limit_samples == 10
        assert params.parallelism == 4
        assert params.max_retries == 2
        assert params.request_timeout == 120
        assert params.inference is not None
        assert params.inference.max_tokens == 1024

    def test_extra_fields_rejected(self):
        """Unknown fields at top level should be rejected."""
        with pytest.raises(ValidationError) as exc_info:
            RunConfigOnlineModel.model_validate(
                {
                    "limit_samples": 10,
                    "max_tokens": 4096,  # Wrong level - should be inference.max_tokens
                }
            )
        err = exc_info.value
        assert err.errors()[0]["type"] == "extra_forbidden"
        assert "max_tokens" in str(err.errors()[0]["loc"])

    def test_multiple_extra_fields_rejected(self):
        """Multiple unknown fields should all be reported."""
        with pytest.raises(ValidationError) as exc_info:
            RunConfigOnlineModel.model_validate(
                {
                    "limit_samples": 10,
                    "max_tokens": 4096,
                    "temperature": 0.5,
                    "unknown_field": "value",
                }
            )
        err = exc_info.value
        assert len(err.errors()) == 3  # max_tokens, temperature, unknown_field

    def test_inference_params_allow_extra(self):
        """InferenceParams should allow extra fields for vendor-specific params."""
        params = RunConfigOnlineModel.model_validate(
            {
                "inference": {
                    "max_tokens": 1024,
                    "vendor_specific_param": "some_value",
                }
            }
        )
        # Extra fields are allowed in InferenceParams
        assert params.inference is not None
        assert params.inference.max_tokens == 1024


class TestModelValidation:
    """Tests for Model extra field rejection."""

    def test_valid_model_accepted(self):
        """Valid model configuration should be accepted."""
        model = Model(
            url="http://localhost:8000/v1/chat/completions",
            name="test-model",
            format=ModelFormat.NVIDIA_NIM,
        )
        assert model.url == "http://localhost:8000/v1/chat/completions"
        assert model.name == "test-model"
        assert model.format == ModelFormat.NVIDIA_NIM

    def test_extra_fields_rejected(self):
        """Unknown fields should be rejected."""
        with pytest.raises(ValidationError) as exc_info:
            Model.model_validate(
                {
                    "url": "http://localhost:8000/v1/chat/completions",
                    "name": "test-model",
                    "model_type": "chat",  # Not a valid field
                }
            )
        err = exc_info.value
        assert len(err.errors()) == 1
        assert err.errors()[0]["type"] == "extra_forbidden"

    def test_typo_in_field_name_rejected(self):
        """Typos in field names should be rejected."""
        with pytest.raises(ValidationError) as exc_info:
            Model.model_validate(
                {
                    "url": "http://localhost:8000/v1/chat/completions",
                    "name": "test-model",
                    "endpont": "http://wrong",  # Typo: endpont instead of endpoint
                }
            )
        err = exc_info.value
        assert any(e["type"] == "extra_forbidden" for e in err.errors())

    def test_llama_stack_format_accepted(self):
        """llama_stack should be accepted as a valid model format."""
        model = Model.model_validate(
            {
                "url": "http://localhost:8000/v1/chat/completions",
                "name": "test-model",
                "format": "llama_stack",
            }
        )
        assert model.format == ModelFormat.LLAMA_STACK

    def test_lama_stack_format_rejected(self):
        """lama_stack typo should be rejected."""
        with pytest.raises(ValidationError) as exc_info:
            Model.model_validate(
                {
                    "url": "http://localhost:8000/v1/chat/completions",
                    "name": "test-model",
                    "format": "lama_stack",
                }
            )
        err = exc_info.value
        assert any(e["loc"] == ("format",) for e in err.errors())


class TestDatasetRowsValidation:
    """Tests for DatasetRows extra field rejection."""

    def test_valid_dataset_accepted(self):
        """Valid dataset configuration should be accepted."""
        dataset = DatasetRows(
            rows=[{"input": "test", "output": "result"}],
        )
        assert len(dataset.rows) == 1

    def test_extra_fields_rejected(self):
        """Unknown fields should be rejected."""
        with pytest.raises(ValidationError) as exc_info:
            DatasetRows.model_validate(
                {
                    "rows": [{"input": "test"}],
                    "path": "/some/path",  # Not a valid field
                }
            )
        err = exc_info.value
        assert len(err.errors()) == 1
        assert err.errors()[0]["type"] == "extra_forbidden"

    def test_typo_in_field_name_rejected(self):
        """Typos in field names should be rejected."""
        with pytest.raises(ValidationError) as exc_info:
            DatasetRows.model_validate(
                {
                    "rows": [{"input": "test"}],
                    "rowz": [{"input": "test"}],  # Typo: rowz instead of rows
                }
            )
        err = exc_info.value
        assert any(e["type"] == "extra_forbidden" for e in err.errors())

    def test_rows_required(self):
        """Rows field is required and must have at least one item."""
        with pytest.raises(ValidationError) as exc_info:
            DatasetRows()  # type: ignore[call-arg]
        err = exc_info.value
        assert any(e["loc"] == ("rows",) for e in err.errors())

    def test_empty_rows_rejected(self):
        """Empty rows array should be rejected."""
        with pytest.raises(ValidationError) as exc_info:
            DatasetRows(rows=[])
        err = exc_info.value
        assert any(e["type"] == "too_short" for e in err.errors())
