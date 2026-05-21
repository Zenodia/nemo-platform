# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import json
from collections.abc import AsyncIterator
from datetime import datetime
from typing import Any, cast
from unittest.mock import patch

import data_designer.config as dd
import httpx
import pandas as pd
import pytest
import respx
from data_designer.config.analysis.column_statistics import GeneralColumnStatistics
from data_designer.config.analysis.dataset_profiler import DatasetProfilerResults
from data_designer.config.dataset_metadata import DatasetMetadata
from nemo_data_designer_plugin.functions._types import (
    AnalysisFrame,
    DatasetFrame,
    DatasetMetadataFrame,
    LogFrame,
    ProcessorOutputFrame,
)
from nemo_data_designer_plugin.sdk import http as sdk_http
from nemo_data_designer_plugin.sdk.errors import (
    DataDesignerClientError,
    DataDesignerConfigValidationError,
    DataDesignerPreviewError,
)
from nemo_data_designer_plugin.sdk.job_resources import AsyncDataDesignerJobResource, DataDesignerJobResource
from nemo_data_designer_plugin.sdk.resources import AsyncDataDesignerResource, DataDesignerResource
from nemo_platform import AsyncNeMoPlatform, NeMoPlatform
from nemo_platform.types.inference import ModelProvider as NMPModelProvider
from nemo_platform_plugin.functions.frames import Done, Error, Heartbeat
from pydantic import BaseModel


@pytest.fixture
def platform() -> NeMoPlatform:
    return NeMoPlatform(base_url="http://testserver", workspace="default", access_token="token")


@pytest.fixture
def async_platform() -> AsyncNeMoPlatform:
    return AsyncNeMoPlatform(base_url="http://testserver", workspace="default", access_token="token")


@pytest.fixture
def resource(platform: NeMoPlatform) -> DataDesignerResource:
    return DataDesignerResource(platform)


@pytest.fixture
def async_resource(async_platform: AsyncNeMoPlatform) -> AsyncDataDesignerResource:
    return AsyncDataDesignerResource(async_platform)


@pytest.fixture
def config_builder() -> dd.DataDesignerConfigBuilder:
    builder = dd.DataDesignerConfigBuilder(model_configs=[dd.ModelConfig(alias="text", model="model")])
    builder.add_column(
        column_config=dd.SamplerColumnConfig(
            name="foo",
            sampler_type=dd.SamplerType.CATEGORY,
            params=dd.CategorySamplerParams(values=["a", "b"]),
        )
    )
    return builder


def make_basic_dataset() -> pd.DataFrame:
    return pd.DataFrame(data={"foo": [1, 2, 3]}).convert_dtypes(dtype_backend="pyarrow")


async def _async_iter(frames: list[BaseModel]) -> AsyncIterator[BaseModel]:
    for frame in frames:
        yield frame


def make_successful_preview_frames() -> list[BaseModel]:
    dataset = make_basic_dataset()
    dataset_dict = cast(list[dict[str, Any]], dataset.to_dict(orient="records"))
    dataset_metadata = DatasetMetadata()
    analysis = DatasetProfilerResults(
        num_records=3,
        target_num_records=3,
        column_statistics=[
            GeneralColumnStatistics(
                column_name="foo",
                num_records=3,
                num_null=0,
                num_unique=3,
                pyarrow_dtype="int",
                simple_dtype="int",
                column_type="general",
            )
        ],
    )
    return [
        LogFrame(level="info", message="Some message"),
        Heartbeat(),
        DatasetMetadataFrame(metadata=dataset_metadata),
        DatasetFrame(records=dataset_dict),
        ProcessorOutputFrame(processor_name="processor", records=[{"foo": "bar"}]),
        AnalysisFrame(analysis=analysis),
        Done(),
    ]


@pytest.mark.parametrize("path", ["preview", "/preview", "///preview"])
def test_http_url_normalizes_leading_slashes(platform: NeMoPlatform, path: str) -> None:
    assert sdk_http.url(platform, None, path) == "http://testserver/apis/data-designer/v2/workspaces/default/preview"


def test_http_url_normalizes_empty_path(platform: NeMoPlatform) -> None:
    assert sdk_http.url(platform, None, "") == "http://testserver/apis/data-designer/v2/workspaces/default/"


def test_preview_success(resource: DataDesignerResource, config_builder: dd.DataDesignerConfigBuilder) -> None:
    with patch.object(resource, "_preview", return_value=make_successful_preview_frames()):
        preview_results = resource.preview(config_builder)

    assert isinstance(preview_results.dataset, pd.DataFrame)
    pd.testing.assert_frame_equal(preview_results.dataset, make_basic_dataset())
    assert preview_results.processor_artifacts == {"processor": [{"foo": "bar"}]}


@pytest.mark.parametrize("seed_kind", ["df", "local", "directory", "file_contents"])
def test_preview_rejects_remote_unsupported_seed_sources(
    resource: DataDesignerResource,
    config_builder: dd.DataDesignerConfigBuilder,
    seed_kind: str,
    tmp_path,
) -> None:
    if seed_kind == "df":
        seed_source = dd.DataFrameSeedSource(df=pd.DataFrame(data={"foo": [1, 2, 3]}))
    elif seed_kind == "local":
        seed_file = tmp_path / "seed.parquet"
        make_basic_dataset().to_parquet(seed_file)
        seed_source = dd.LocalFileSeedSource(path=str(seed_file))
    elif seed_kind == "directory":
        seed_source = dd.DirectorySeedSource(path=str(tmp_path))
    else:
        seed_source = dd.FileContentsSeedSource(path=str(tmp_path))

    config_builder.with_seed_dataset(seed_source)

    with (
        patch.object(resource, "_preview", side_effect=AssertionError("preview request should not be sent")),
        pytest.raises(DataDesignerConfigValidationError) as exc_info,
    ):
        resource.preview(config_builder)

    assert "only supports seed data" in str(exc_info.value)


def test_empty_dataset_frame_raises_preview_error(
    resource: DataDesignerResource, config_builder: dd.DataDesignerConfigBuilder
) -> None:
    with patch.object(resource, "_preview", return_value=[DatasetFrame(records=[])]):
        with pytest.raises(DataDesignerPreviewError):
            resource.preview(config_builder)


def test_error_frame_raises_preview_error(
    resource: DataDesignerResource, config_builder: dd.DataDesignerConfigBuilder
) -> None:
    with patch.object(resource, "_preview", return_value=[Error(message="boom")]):
        with pytest.raises(DataDesignerPreviewError, match="boom"):
            resource.preview(config_builder)


@respx.mock
def test_preview_posts_jsonl_request(
    resource: DataDesignerResource, config_builder: dd.DataDesignerConfigBuilder
) -> None:
    preview_messages = "\n".join(frame.model_dump_json() for frame in make_successful_preview_frames()) + "\n"
    route = respx.post("http://testserver/apis/data-designer/v2/workspaces/default/preview").mock(
        return_value=httpx.Response(200, text=preview_messages)
    )

    preview_results = resource.preview(config_builder, num_records=3)

    request_json = json.loads(route.calls[0].request.content)
    assert request_json["config"]["columns"][0]["column_type"] == "sampler"
    assert request_json["num_records"] == 3
    assert preview_results.dataset is not None


@respx.mock
def test_preview_ignores_unknown_frame_kind(
    resource: DataDesignerResource, config_builder: dd.DataDesignerConfigBuilder
) -> None:
    preview_messages = '{"kind":"future","payload":1}\n' + "\n".join(
        frame.model_dump_json() for frame in make_successful_preview_frames()
    )
    respx.post("http://testserver/apis/data-designer/v2/workspaces/default/preview").mock(
        return_value=httpx.Response(200, text=preview_messages)
    )

    preview_results = resource.preview(config_builder, num_records=3)

    assert preview_results.dataset is not None


@respx.mock
def test_create_job(resource: DataDesignerResource, config_builder: dd.DataDesignerConfigBuilder) -> None:
    route = respx.post("http://testserver/apis/data-designer/v2/workspaces/default/jobs/create").mock(
        return_value=httpx.Response(200, json={"name": "data-designer-abc123"})
    )

    job_resource = resource.create(config_builder)

    assert isinstance(job_resource, DataDesignerJobResource)
    request_json = json.loads(route.calls[0].request.content)
    assert request_json["spec"]["config"]["columns"][0]["column_type"] == "sampler"


@respx.mock
def test_get_job_resource(resource: DataDesignerResource) -> None:
    respx.get("http://testserver/apis/data-designer/v2/workspaces/default/jobs/create/data-designer-abc123").mock(
        return_value=httpx.Response(200, json={"name": "data-designer-abc123"})
    )

    job_resource = resource.get_job_resource("data-designer-abc123")
    assert isinstance(job_resource, DataDesignerJobResource)


def test_get_default_model_configs(resource: DataDesignerResource) -> None:
    assert resource.get_default_model_configs() == []


def test_get_default_model_providers(platform: NeMoPlatform, resource: DataDesignerResource) -> None:
    mock_providers = [
        NMPModelProvider(
            name="provider1",
            workspace="ws1",
            host_url="http://host1",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        ),
        NMPModelProvider(
            name="provider2",
            workspace="ws2",
            host_url="http://host2",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        ),
    ]
    with patch.object(platform.inference.providers, "list", return_value=mock_providers):
        providers = resource.get_default_model_providers()
    assert len(providers) == 2
    assert all(isinstance(provider, dd.ModelProvider) for provider in providers)


@pytest.mark.asyncio
async def test_preview_success_async(
    async_resource: AsyncDataDesignerResource, config_builder: dd.DataDesignerConfigBuilder
) -> None:
    with patch.object(async_resource, "_preview", return_value=_async_iter(make_successful_preview_frames())):
        preview_results = await async_resource.preview(config_builder)

    assert isinstance(preview_results.dataset, pd.DataFrame)
    pd.testing.assert_frame_equal(preview_results.dataset, make_basic_dataset())


@pytest.mark.asyncio
@respx.mock
async def test_create_job_async(
    async_resource: AsyncDataDesignerResource, config_builder: dd.DataDesignerConfigBuilder
) -> None:
    respx.post("http://testserver/apis/data-designer/v2/workspaces/default/jobs/create").mock(
        return_value=httpx.Response(200, json={"name": "data-designer-abc123"})
    )

    job_resource = await async_resource.create(config_builder)
    assert isinstance(job_resource, AsyncDataDesignerJobResource)


@pytest.mark.asyncio
async def test_http_error_handling_async(
    async_resource: AsyncDataDesignerResource, config_builder: dd.DataDesignerConfigBuilder
) -> None:
    request = httpx.Request("POST", "http://testserver")
    response = httpx.Response(422, request=request, json={"detail": "bad config"})
    with patch.object(
        async_resource, "_preview", side_effect=httpx.HTTPStatusError("bad", request=request, response=response)
    ):
        with pytest.raises(DataDesignerConfigValidationError):
            await async_resource.preview(config_builder)

    response = httpx.Response(500, request=request, text="boom")
    with patch.object(
        async_resource, "_preview", side_effect=httpx.HTTPStatusError("bad", request=request, response=response)
    ):
        with pytest.raises(DataDesignerClientError):
            await async_resource.preview(config_builder)
