# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

from unittest.mock import AsyncMock, MagicMock

import pytest
from nemo_platform import NotFoundError, PermissionDeniedError
from nemo_safe_synthesizer.config.job import SafeSynthesizerJobConfig
from nemo_safe_synthesizer.config.parameters import SafeSynthesizerParameters
from nemo_safe_synthesizer.config.replace_pii import PiiReplacerConfig
from nmp.common.jobs.exceptions import PlatformJobCompilationError
from nmp.safe_synthesizer.api.v2.jobs.endpoints import SafeSynthesizerJobConfig as ServiceJobConfig
from nmp.safe_synthesizer.api.v2.jobs.endpoints import job_config_compiler

DEFAULT_WORKSPACE = "default"
DEFAULT_DATA_SOURCE = "default/test-data#file.csv"


@pytest.fixture
def mock_sdk():
    sdk = MagicMock()
    sdk.files.filesets.retrieve = AsyncMock()
    sdk.inference.providers.retrieve = AsyncMock()
    sdk.models.get_provider_route_openai_url = MagicMock(
        return_value="http://nmp-host/apis/inference-gateway/v2/workspaces/default/provider/my-nim/-/v1"
    )
    return sdk


@pytest.fixture
def mock_entity_client():
    return MagicMock()


def _make_spec(
    data_source: str = DEFAULT_DATA_SOURCE,
    classify_model_provider: str | None = None,
    hf_token_secret: str | None = None,
):
    replace_pii = None
    if classify_model_provider is not None:
        replace_pii = PiiReplacerConfig.get_default_config()
        replace_pii.globals.classify.classify_model_provider = classify_model_provider

    return SafeSynthesizerJobConfig(
        data_source=data_source,
        config=SafeSynthesizerParameters(replace_pii=replace_pii),
        hf_token_secret=hf_token_secret,
    )


async def _compile(spec, mock_sdk, mock_entity_client, workspace=DEFAULT_WORKSPACE):
    return await job_config_compiler(
        workspace=workspace,
        original_spec=spec,
        transformed_spec=spec,
        entity_client=mock_entity_client,
        job_name=None,
        sdk=mock_sdk,
    )


# ---------------------------------------------------------------------------
# Data source fileset validation
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_job_config_compiler_validates_data_source(mock_sdk, mock_entity_client):
    """Fileset retrieve is called with the parsed workspace and fileset name."""
    spec = _make_spec(data_source="my-workspace/my-fileset#data.csv")

    await _compile(spec, mock_sdk, mock_entity_client)

    mock_sdk.files.filesets.retrieve.assert_awaited_once_with(name="my-fileset", workspace="my-workspace")


@pytest.mark.asyncio
async def test_job_config_compiler_data_source_workspace_fallback(mock_sdk, mock_entity_client):
    """Fileset without explicit workspace uses the job workspace as fallback."""
    spec = _make_spec(data_source="my-fileset#data.csv")

    await _compile(spec, mock_sdk, mock_entity_client, workspace="fallback-ws")

    mock_sdk.files.filesets.retrieve.assert_awaited_once_with(name="my-fileset", workspace="fallback-ws")


@pytest.mark.asyncio
async def test_job_config_compiler_data_source_not_found(mock_sdk, mock_entity_client):
    """Missing fileset raises PlatformJobCompilationError (→ 422)."""
    mock_sdk.files.filesets.retrieve.side_effect = NotFoundError(
        message="not found", response=MagicMock(status_code=404), body=None
    )
    spec = _make_spec()

    with pytest.raises(PlatformJobCompilationError, match="Could not find fileset"):
        await _compile(spec, mock_sdk, mock_entity_client)


@pytest.mark.asyncio
async def test_job_config_compiler_data_source_permission_denied(mock_sdk, mock_entity_client):
    """Inaccessible fileset raises PermissionError (→ 403 via api_factory)."""
    mock_sdk.files.filesets.retrieve.side_effect = PermissionDeniedError(
        message="denied", response=MagicMock(status_code=403), body=None
    )
    spec = _make_spec()

    with pytest.raises(PermissionError, match="Access denied to fileset"):
        await _compile(spec, mock_sdk, mock_entity_client)


@pytest.mark.asyncio
async def test_job_config_compiler_data_source_invalid_format(mock_sdk, mock_entity_client):
    """Unparseable data_source raises PlatformJobCompilationError."""
    spec = _make_spec(data_source="")

    with pytest.raises(PlatformJobCompilationError, match="Invalid data_source format"):
        await _compile(spec, mock_sdk, mock_entity_client)


# ---------------------------------------------------------------------------
# Classify model provider
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_job_config_compiler_with_classify_provider(mock_sdk, mock_entity_client):
    """Provider is retrieved and URL set as CLASSIFY_LLM_ENDPOINT_PATH."""
    spec = _make_spec(classify_model_provider="default/my-nim")

    result = await _compile(spec, mock_sdk, mock_entity_client)

    mock_sdk.inference.providers.retrieve.assert_awaited_once_with("my-nim", workspace="default")
    mock_sdk.models.get_provider_route_openai_url.assert_called_once()

    step = next(iter(result["steps"]))
    env = {e["name"]: e.get("value") for e in step.get("environment", [])}
    assert env["CLASSIFY_LLM_ENDPOINT_PATH"] == "/apis/inference-gateway/v2/workspaces/default/provider/my-nim/-/v1"


@pytest.mark.asyncio
async def test_job_config_compiler_without_classify_provider(mock_sdk, mock_entity_client):
    """No SDK calls when classify_model_provider is absent."""
    spec = _make_spec()

    result = await _compile(spec, mock_sdk, mock_entity_client)

    mock_sdk.inference.providers.retrieve.assert_not_awaited()
    step = next(iter(result["steps"]))
    env_names = {e["name"] for e in step.get("environment", [])}
    assert "NIM_ENDPOINT_URL" not in env_names


@pytest.mark.asyncio
async def test_job_config_compiler_classify_provider_wrong_format(mock_sdk, mock_entity_client):
    """ValueError raised for provider reference missing the workspace prefix."""
    spec = _make_spec(classify_model_provider="no-slash-here")

    with pytest.raises(PlatformJobCompilationError, match="Expected 'workspace/provider_name'"):
        await _compile(spec, mock_sdk, mock_entity_client)


# ---------------------------------------------------------------------------
# HuggingFace token secret
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_job_config_compiler_hf_token(mock_sdk, mock_entity_client):
    """HF_TOKEN secret env var is set when hf_token_secret is provided."""
    spec = _make_spec(hf_token_secret="my-hf-secret")

    result = await _compile(spec, mock_sdk, mock_entity_client)

    step = next(iter(result["steps"]))
    env = step.get("environment", [])
    hf_entry = next((e for e in env if e["name"] == "HF_TOKEN"), None)
    assert hf_entry is not None
    assert hf_entry.get("from_secret", {})["name"] == "my-hf-secret"


# ---------------------------------------------------------------------------
# Service job config model validators (enable flags)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "config_input, expected_synthesis, expected_replace_pii_none",
    [
        ({"enable_synthesis": False, "enable_replace_pii": True}, False, False),
        ({}, True, False),
        ({"enable_synthesis": True, "enable_replace_pii": False}, True, True),
    ],
    ids=["synthesis_disabled", "defaults", "pii_disabled"],
)
def test_service_job_config_enable_flags(config_input, expected_synthesis, expected_replace_pii_none):
    """Enable flags are correctly lifted/applied by model validators."""
    spec = ServiceJobConfig.model_validate({"data_source": "fileset://default/data", "config": config_input})
    assert spec.enable_synthesis is expected_synthesis
    if expected_replace_pii_none:
        assert spec.config.replace_pii is None
