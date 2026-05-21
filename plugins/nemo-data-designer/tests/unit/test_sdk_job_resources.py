# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import io
import json
import tarfile
from pathlib import Path
from unittest.mock import AsyncMock, patch

import httpx
import pytest
import respx
from nemo_data_designer_plugin.sdk.errors import DataDesignerJobError
from nemo_data_designer_plugin.sdk.job_resources import AsyncDataDesignerJobResource, DataDesignerJobResource
from nemo_data_designer_plugin.sdk.job_results import DataDesignerJobResults
from nemo_platform import AsyncNeMoPlatform, NeMoPlatform


@pytest.fixture
def platform() -> NeMoPlatform:
    return NeMoPlatform(base_url="http://testserver", workspace="test-workspace", access_token="token")


@pytest.fixture
def async_platform() -> AsyncNeMoPlatform:
    return AsyncNeMoPlatform(base_url="http://testserver", workspace="test-workspace", access_token="token")


@pytest.fixture
def job_resource(platform: NeMoPlatform) -> DataDesignerJobResource:
    return DataDesignerJobResource(job_name="test-job", platform=platform, workspace="test-workspace")


@pytest.fixture
def async_job_resource(async_platform: AsyncNeMoPlatform) -> AsyncDataDesignerJobResource:
    return AsyncDataDesignerJobResource(job_name="test-job", platform=async_platform, workspace="test-workspace")


@respx.mock
def test_get_job(job_resource: DataDesignerJobResource) -> None:
    respx.get("http://testserver/apis/data-designer/v2/workspaces/test-workspace/jobs/create/test-job").mock(
        return_value=httpx.Response(200, json={"name": "test-job"})
    )
    assert job_resource.get_job()["name"] == "test-job"


@respx.mock
def test_get_job_status(job_resource: DataDesignerJobResource) -> None:
    respx.get("http://testserver/apis/data-designer/v2/workspaces/test-workspace/jobs/create/test-job/status").mock(
        return_value=httpx.Response(200, json={"status": "active"})
    )
    assert job_resource.get_job_status() == "active"


def test_check_if_complete_raises_when_not_complete(job_resource: DataDesignerJobResource) -> None:
    with patch.object(job_resource, "get_job_status", return_value="active"):
        with pytest.raises(DataDesignerJobError):
            job_resource.check_if_complete(raise_if_not_complete=True)


def test_wait_until_done_success(job_resource: DataDesignerJobResource, caplog: pytest.LogCaptureFixture) -> None:
    with (
        patch("nemo_data_designer_plugin.sdk.job_resources._pause"),
        patch.object(job_resource, "get_job_status", side_effect=["active", "completed"]),
        patch.object(job_resource, "get_logs", return_value=[]),
        caplog.at_level("INFO"),
    ):
        job_resource.wait_until_done()

    assert any("completed successfully" in record.message for record in caplog.records)


@respx.mock
def test_get_logs_multiple_pages(job_resource: DataDesignerJobResource) -> None:
    route = respx.get("http://testserver/apis/data-designer/v2/workspaces/test-workspace/jobs/create/test-job/logs")
    route.mock(
        side_effect=[
            httpx.Response(
                200,
                json={
                    "data": [
                        {
                            "message": json.dumps(
                                {"name": "data_designer.something", "levelname": "INFO", "message": "Page 1"}
                            )
                        }
                    ],
                    "next_page": "cursor1",
                },
            ),
            httpx.Response(
                200,
                json={
                    "data": [
                        {
                            "message": json.dumps(
                                {"name": "data_designer.something", "levelname": "INFO", "message": "Page 2"}
                            )
                        }
                    ],
                    "next_page": None,
                },
            ),
        ]
    )

    logs = job_resource.get_logs()
    assert [log["message"] for log in logs] == ["Page 1", "Page 2"]


def _make_tar_bytes() -> bytes:
    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode="w") as tar:
        data = b"dummy"
        info = tarfile.TarInfo(name="artifacts/dataset/parquet-files/00000.parquet")
        info.size = len(data)
        tar.addfile(info, io.BytesIO(data))
    return buffer.getvalue()


@respx.mock
def test_download_artifacts_success(job_resource: DataDesignerJobResource, tmp_path: Path) -> None:
    with patch.object(job_resource, "_check_if_result_available"):
        respx.get(
            "http://testserver/apis/data-designer/v2/workspaces/test-workspace/jobs/create/test-job/results/artifacts/download"
        ).mock(return_value=httpx.Response(200, content=_make_tar_bytes()))
        respx.get(
            "http://testserver/apis/data-designer/v2/workspaces/test-workspace/jobs/create/test-job/results/analysis/download"
        ).mock(
            return_value=httpx.Response(200, json={"num_records": 0, "target_num_records": 0, "column_statistics": []})
        )
        result = job_resource.download_artifacts(tmp_path)

    assert isinstance(result, DataDesignerJobResults)


@pytest.mark.asyncio
@respx.mock
async def test_get_job_async(async_job_resource: AsyncDataDesignerJobResource) -> None:
    respx.get("http://testserver/apis/data-designer/v2/workspaces/test-workspace/jobs/create/test-job").mock(
        return_value=httpx.Response(200, json={"name": "test-job"})
    )
    result = await async_job_resource.get_job()
    assert result["name"] == "test-job"


@pytest.mark.asyncio
async def test_wait_until_done_success_async(
    async_job_resource: AsyncDataDesignerJobResource, caplog: pytest.LogCaptureFixture
) -> None:
    with (
        patch("nemo_data_designer_plugin.sdk.job_resources._async_pause"),
        patch.object(async_job_resource, "get_job_status", new=AsyncMock(side_effect=["active", "completed"])),
        patch.object(async_job_resource, "get_logs", new=AsyncMock(return_value=[])),
        caplog.at_level("INFO"),
    ):
        await async_job_resource.wait_until_done()

    assert any("completed successfully" in record.message for record in caplog.records)
