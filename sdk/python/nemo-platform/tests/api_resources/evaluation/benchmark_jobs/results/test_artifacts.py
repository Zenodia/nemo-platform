# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import httpx
import pytest
from respx import MockRouter

from nemo_platform import NeMoPlatform, AsyncNeMoPlatform
from nemo_platform._response import (
    BinaryAPIResponse,
    AsyncBinaryAPIResponse,
    StreamedBinaryAPIResponse,
    AsyncStreamedBinaryAPIResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestArtifacts:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_method_download(self, client: NeMoPlatform, respx_mock: MockRouter) -> None:
        respx_mock.get("/apis/evaluation/v2/workspaces/workspace/benchmark-jobs/job/results/artifacts/download").mock(
            return_value=httpx.Response(200, json={"foo": "bar"})
        )
        artifact = client.evaluation.benchmark_jobs.results.artifacts.download(
            job="job",
            workspace="workspace",
        )
        assert artifact.is_closed
        assert artifact.json() == {"foo": "bar"}
        assert cast(Any, artifact.is_closed) is True
        assert isinstance(artifact, BinaryAPIResponse)

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_raw_response_download(self, client: NeMoPlatform, respx_mock: MockRouter) -> None:
        respx_mock.get("/apis/evaluation/v2/workspaces/workspace/benchmark-jobs/job/results/artifacts/download").mock(
            return_value=httpx.Response(200, json={"foo": "bar"})
        )

        artifact = client.evaluation.benchmark_jobs.results.artifacts.with_raw_response.download(
            job="job",
            workspace="workspace",
        )

        assert artifact.is_closed is True
        assert artifact.http_request.headers.get("X-Stainless-Lang") == "python"
        assert artifact.json() == {"foo": "bar"}
        assert isinstance(artifact, BinaryAPIResponse)

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_streaming_response_download(self, client: NeMoPlatform, respx_mock: MockRouter) -> None:
        respx_mock.get("/apis/evaluation/v2/workspaces/workspace/benchmark-jobs/job/results/artifacts/download").mock(
            return_value=httpx.Response(200, json={"foo": "bar"})
        )
        with client.evaluation.benchmark_jobs.results.artifacts.with_streaming_response.download(
            job="job",
            workspace="workspace",
        ) as artifact:
            assert not artifact.is_closed
            assert artifact.http_request.headers.get("X-Stainless-Lang") == "python"

            assert artifact.json() == {"foo": "bar"}
            assert cast(Any, artifact.is_closed) is True
            assert isinstance(artifact, StreamedBinaryAPIResponse)

        assert cast(Any, artifact.is_closed) is True

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_path_params_download(self, client: NeMoPlatform) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `workspace` but received ''"):
            client.evaluation.benchmark_jobs.results.artifacts.with_raw_response.download(
                job="job",
                workspace="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `job` but received ''"):
            client.evaluation.benchmark_jobs.results.artifacts.with_raw_response.download(
                job="",
                workspace="workspace",
            )


class TestAsyncArtifacts:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_method_download(self, async_client: AsyncNeMoPlatform, respx_mock: MockRouter) -> None:
        respx_mock.get("/apis/evaluation/v2/workspaces/workspace/benchmark-jobs/job/results/artifacts/download").mock(
            return_value=httpx.Response(200, json={"foo": "bar"})
        )
        artifact = await async_client.evaluation.benchmark_jobs.results.artifacts.download(
            job="job",
            workspace="workspace",
        )
        assert artifact.is_closed
        assert await artifact.json() == {"foo": "bar"}
        assert cast(Any, artifact.is_closed) is True
        assert isinstance(artifact, AsyncBinaryAPIResponse)

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_raw_response_download(self, async_client: AsyncNeMoPlatform, respx_mock: MockRouter) -> None:
        respx_mock.get("/apis/evaluation/v2/workspaces/workspace/benchmark-jobs/job/results/artifacts/download").mock(
            return_value=httpx.Response(200, json={"foo": "bar"})
        )

        artifact = await async_client.evaluation.benchmark_jobs.results.artifacts.with_raw_response.download(
            job="job",
            workspace="workspace",
        )

        assert artifact.is_closed is True
        assert artifact.http_request.headers.get("X-Stainless-Lang") == "python"
        assert await artifact.json() == {"foo": "bar"}
        assert isinstance(artifact, AsyncBinaryAPIResponse)

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_streaming_response_download(self, async_client: AsyncNeMoPlatform, respx_mock: MockRouter) -> None:
        respx_mock.get("/apis/evaluation/v2/workspaces/workspace/benchmark-jobs/job/results/artifacts/download").mock(
            return_value=httpx.Response(200, json={"foo": "bar"})
        )
        async with async_client.evaluation.benchmark_jobs.results.artifacts.with_streaming_response.download(
            job="job",
            workspace="workspace",
        ) as artifact:
            assert not artifact.is_closed
            assert artifact.http_request.headers.get("X-Stainless-Lang") == "python"

            assert await artifact.json() == {"foo": "bar"}
            assert cast(Any, artifact.is_closed) is True
            assert isinstance(artifact, AsyncStreamedBinaryAPIResponse)

        assert cast(Any, artifact.is_closed) is True

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_path_params_download(self, async_client: AsyncNeMoPlatform) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `workspace` but received ''"):
            await async_client.evaluation.benchmark_jobs.results.artifacts.with_raw_response.download(
                job="job",
                workspace="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `job` but received ''"):
            await async_client.evaluation.benchmark_jobs.results.artifacts.with_raw_response.download(
                job="",
                workspace="workspace",
            )
