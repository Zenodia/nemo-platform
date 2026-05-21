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

from tests.utils import assert_matches_type
from nemo_platform import NeMoPlatform, AsyncNeMoPlatform
from nemo_platform._response import (
    BinaryAPIResponse,
    AsyncBinaryAPIResponse,
    StreamedBinaryAPIResponse,
    AsyncStreamedBinaryAPIResponse,
)
from nemo_platform.types.shared import PlatformJobResultResponse, PlatformJobListResultResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestResults:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_method_create(self, client: NeMoPlatform) -> None:
        result = client.jobs.results.create(
            name="name",
            workspace="workspace",
            job="job",
            artifact_storage_type="fileset",
            artifact_url="artifact_url",
        )
        assert_matches_type(PlatformJobResultResponse, result, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_raw_response_create(self, client: NeMoPlatform) -> None:
        response = client.jobs.results.with_raw_response.create(
            name="name",
            workspace="workspace",
            job="job",
            artifact_storage_type="fileset",
            artifact_url="artifact_url",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        result = response.parse()
        assert_matches_type(PlatformJobResultResponse, result, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_streaming_response_create(self, client: NeMoPlatform) -> None:
        with client.jobs.results.with_streaming_response.create(
            name="name",
            workspace="workspace",
            job="job",
            artifact_storage_type="fileset",
            artifact_url="artifact_url",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            result = response.parse()
            assert_matches_type(PlatformJobResultResponse, result, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_path_params_create(self, client: NeMoPlatform) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `workspace` but received ''"):
            client.jobs.results.with_raw_response.create(
                name="name",
                workspace="",
                job="job",
                artifact_storage_type="fileset",
                artifact_url="artifact_url",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `job` but received ''"):
            client.jobs.results.with_raw_response.create(
                name="name",
                workspace="workspace",
                job="",
                artifact_storage_type="fileset",
                artifact_url="artifact_url",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `name` but received ''"):
            client.jobs.results.with_raw_response.create(
                name="",
                workspace="workspace",
                job="job",
                artifact_storage_type="fileset",
                artifact_url="artifact_url",
            )

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_method_retrieve(self, client: NeMoPlatform) -> None:
        result = client.jobs.results.retrieve(
            name="name",
            workspace="workspace",
            job="job",
        )
        assert_matches_type(PlatformJobResultResponse, result, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_raw_response_retrieve(self, client: NeMoPlatform) -> None:
        response = client.jobs.results.with_raw_response.retrieve(
            name="name",
            workspace="workspace",
            job="job",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        result = response.parse()
        assert_matches_type(PlatformJobResultResponse, result, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_streaming_response_retrieve(self, client: NeMoPlatform) -> None:
        with client.jobs.results.with_streaming_response.retrieve(
            name="name",
            workspace="workspace",
            job="job",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            result = response.parse()
            assert_matches_type(PlatformJobResultResponse, result, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_path_params_retrieve(self, client: NeMoPlatform) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `workspace` but received ''"):
            client.jobs.results.with_raw_response.retrieve(
                name="name",
                workspace="",
                job="job",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `job` but received ''"):
            client.jobs.results.with_raw_response.retrieve(
                name="name",
                workspace="workspace",
                job="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `name` but received ''"):
            client.jobs.results.with_raw_response.retrieve(
                name="",
                workspace="workspace",
                job="job",
            )

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_method_list(self, client: NeMoPlatform) -> None:
        result = client.jobs.results.list(
            name="name",
            workspace="workspace",
        )
        assert_matches_type(PlatformJobListResultResponse, result, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_method_list_with_all_params(self, client: NeMoPlatform) -> None:
        result = client.jobs.results.list(
            name="name",
            workspace="workspace",
            sort="created_at",
        )
        assert_matches_type(PlatformJobListResultResponse, result, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_raw_response_list(self, client: NeMoPlatform) -> None:
        response = client.jobs.results.with_raw_response.list(
            name="name",
            workspace="workspace",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        result = response.parse()
        assert_matches_type(PlatformJobListResultResponse, result, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_streaming_response_list(self, client: NeMoPlatform) -> None:
        with client.jobs.results.with_streaming_response.list(
            name="name",
            workspace="workspace",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            result = response.parse()
            assert_matches_type(PlatformJobListResultResponse, result, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_path_params_list(self, client: NeMoPlatform) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `workspace` but received ''"):
            client.jobs.results.with_raw_response.list(
                name="name",
                workspace="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `name` but received ''"):
            client.jobs.results.with_raw_response.list(
                name="",
                workspace="workspace",
            )

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_method_download(self, client: NeMoPlatform, respx_mock: MockRouter) -> None:
        respx_mock.get("/apis/jobs/v2/workspaces/workspace/jobs/job/results/name/download").mock(
            return_value=httpx.Response(200, json={"foo": "bar"})
        )
        result = client.jobs.results.download(
            name="name",
            workspace="workspace",
            job="job",
        )
        assert result.is_closed
        assert result.json() == {"foo": "bar"}
        assert cast(Any, result.is_closed) is True
        assert isinstance(result, BinaryAPIResponse)

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_raw_response_download(self, client: NeMoPlatform, respx_mock: MockRouter) -> None:
        respx_mock.get("/apis/jobs/v2/workspaces/workspace/jobs/job/results/name/download").mock(
            return_value=httpx.Response(200, json={"foo": "bar"})
        )

        result = client.jobs.results.with_raw_response.download(
            name="name",
            workspace="workspace",
            job="job",
        )

        assert result.is_closed is True
        assert result.http_request.headers.get("X-Stainless-Lang") == "python"
        assert result.json() == {"foo": "bar"}
        assert isinstance(result, BinaryAPIResponse)

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_streaming_response_download(self, client: NeMoPlatform, respx_mock: MockRouter) -> None:
        respx_mock.get("/apis/jobs/v2/workspaces/workspace/jobs/job/results/name/download").mock(
            return_value=httpx.Response(200, json={"foo": "bar"})
        )
        with client.jobs.results.with_streaming_response.download(
            name="name",
            workspace="workspace",
            job="job",
        ) as result:
            assert not result.is_closed
            assert result.http_request.headers.get("X-Stainless-Lang") == "python"

            assert result.json() == {"foo": "bar"}
            assert cast(Any, result.is_closed) is True
            assert isinstance(result, StreamedBinaryAPIResponse)

        assert cast(Any, result.is_closed) is True

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_path_params_download(self, client: NeMoPlatform) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `workspace` but received ''"):
            client.jobs.results.with_raw_response.download(
                name="name",
                workspace="",
                job="job",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `job` but received ''"):
            client.jobs.results.with_raw_response.download(
                name="name",
                workspace="workspace",
                job="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `name` but received ''"):
            client.jobs.results.with_raw_response.download(
                name="",
                workspace="workspace",
                job="job",
            )


class TestAsyncResults:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_method_create(self, async_client: AsyncNeMoPlatform) -> None:
        result = await async_client.jobs.results.create(
            name="name",
            workspace="workspace",
            job="job",
            artifact_storage_type="fileset",
            artifact_url="artifact_url",
        )
        assert_matches_type(PlatformJobResultResponse, result, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncNeMoPlatform) -> None:
        response = await async_client.jobs.results.with_raw_response.create(
            name="name",
            workspace="workspace",
            job="job",
            artifact_storage_type="fileset",
            artifact_url="artifact_url",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        result = await response.parse()
        assert_matches_type(PlatformJobResultResponse, result, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncNeMoPlatform) -> None:
        async with async_client.jobs.results.with_streaming_response.create(
            name="name",
            workspace="workspace",
            job="job",
            artifact_storage_type="fileset",
            artifact_url="artifact_url",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            result = await response.parse()
            assert_matches_type(PlatformJobResultResponse, result, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_path_params_create(self, async_client: AsyncNeMoPlatform) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `workspace` but received ''"):
            await async_client.jobs.results.with_raw_response.create(
                name="name",
                workspace="",
                job="job",
                artifact_storage_type="fileset",
                artifact_url="artifact_url",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `job` but received ''"):
            await async_client.jobs.results.with_raw_response.create(
                name="name",
                workspace="workspace",
                job="",
                artifact_storage_type="fileset",
                artifact_url="artifact_url",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `name` but received ''"):
            await async_client.jobs.results.with_raw_response.create(
                name="",
                workspace="workspace",
                job="job",
                artifact_storage_type="fileset",
                artifact_url="artifact_url",
            )

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncNeMoPlatform) -> None:
        result = await async_client.jobs.results.retrieve(
            name="name",
            workspace="workspace",
            job="job",
        )
        assert_matches_type(PlatformJobResultResponse, result, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncNeMoPlatform) -> None:
        response = await async_client.jobs.results.with_raw_response.retrieve(
            name="name",
            workspace="workspace",
            job="job",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        result = await response.parse()
        assert_matches_type(PlatformJobResultResponse, result, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncNeMoPlatform) -> None:
        async with async_client.jobs.results.with_streaming_response.retrieve(
            name="name",
            workspace="workspace",
            job="job",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            result = await response.parse()
            assert_matches_type(PlatformJobResultResponse, result, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncNeMoPlatform) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `workspace` but received ''"):
            await async_client.jobs.results.with_raw_response.retrieve(
                name="name",
                workspace="",
                job="job",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `job` but received ''"):
            await async_client.jobs.results.with_raw_response.retrieve(
                name="name",
                workspace="workspace",
                job="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `name` but received ''"):
            await async_client.jobs.results.with_raw_response.retrieve(
                name="",
                workspace="workspace",
                job="job",
            )

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_method_list(self, async_client: AsyncNeMoPlatform) -> None:
        result = await async_client.jobs.results.list(
            name="name",
            workspace="workspace",
        )
        assert_matches_type(PlatformJobListResultResponse, result, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncNeMoPlatform) -> None:
        result = await async_client.jobs.results.list(
            name="name",
            workspace="workspace",
            sort="created_at",
        )
        assert_matches_type(PlatformJobListResultResponse, result, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncNeMoPlatform) -> None:
        response = await async_client.jobs.results.with_raw_response.list(
            name="name",
            workspace="workspace",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        result = await response.parse()
        assert_matches_type(PlatformJobListResultResponse, result, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncNeMoPlatform) -> None:
        async with async_client.jobs.results.with_streaming_response.list(
            name="name",
            workspace="workspace",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            result = await response.parse()
            assert_matches_type(PlatformJobListResultResponse, result, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_path_params_list(self, async_client: AsyncNeMoPlatform) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `workspace` but received ''"):
            await async_client.jobs.results.with_raw_response.list(
                name="name",
                workspace="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `name` but received ''"):
            await async_client.jobs.results.with_raw_response.list(
                name="",
                workspace="workspace",
            )

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_method_download(self, async_client: AsyncNeMoPlatform, respx_mock: MockRouter) -> None:
        respx_mock.get("/apis/jobs/v2/workspaces/workspace/jobs/job/results/name/download").mock(
            return_value=httpx.Response(200, json={"foo": "bar"})
        )
        result = await async_client.jobs.results.download(
            name="name",
            workspace="workspace",
            job="job",
        )
        assert result.is_closed
        assert await result.json() == {"foo": "bar"}
        assert cast(Any, result.is_closed) is True
        assert isinstance(result, AsyncBinaryAPIResponse)

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_raw_response_download(self, async_client: AsyncNeMoPlatform, respx_mock: MockRouter) -> None:
        respx_mock.get("/apis/jobs/v2/workspaces/workspace/jobs/job/results/name/download").mock(
            return_value=httpx.Response(200, json={"foo": "bar"})
        )

        result = await async_client.jobs.results.with_raw_response.download(
            name="name",
            workspace="workspace",
            job="job",
        )

        assert result.is_closed is True
        assert result.http_request.headers.get("X-Stainless-Lang") == "python"
        assert await result.json() == {"foo": "bar"}
        assert isinstance(result, AsyncBinaryAPIResponse)

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_streaming_response_download(self, async_client: AsyncNeMoPlatform, respx_mock: MockRouter) -> None:
        respx_mock.get("/apis/jobs/v2/workspaces/workspace/jobs/job/results/name/download").mock(
            return_value=httpx.Response(200, json={"foo": "bar"})
        )
        async with async_client.jobs.results.with_streaming_response.download(
            name="name",
            workspace="workspace",
            job="job",
        ) as result:
            assert not result.is_closed
            assert result.http_request.headers.get("X-Stainless-Lang") == "python"

            assert await result.json() == {"foo": "bar"}
            assert cast(Any, result.is_closed) is True
            assert isinstance(result, AsyncStreamedBinaryAPIResponse)

        assert cast(Any, result.is_closed) is True

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_path_params_download(self, async_client: AsyncNeMoPlatform) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `workspace` but received ''"):
            await async_client.jobs.results.with_raw_response.download(
                name="name",
                workspace="",
                job="job",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `job` but received ''"):
            await async_client.jobs.results.with_raw_response.download(
                name="name",
                workspace="workspace",
                job="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `name` but received ''"):
            await async_client.jobs.results.with_raw_response.download(
                name="",
                workspace="workspace",
                job="job",
            )
