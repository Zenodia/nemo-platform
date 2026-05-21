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

import pytest

from tests.utils import assert_matches_type
from nemo_platform import NeMoPlatform, AsyncNeMoPlatform
from nemo_platform.types.jobs import PlatformJobTask, PlatformJobListTaskResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestTasks:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_method_retrieve(self, client: NeMoPlatform) -> None:
        task = client.jobs.tasks.retrieve(
            name="name",
            workspace="workspace",
            job="job",
            step="step",
        )
        assert_matches_type(PlatformJobTask, task, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_raw_response_retrieve(self, client: NeMoPlatform) -> None:
        response = client.jobs.tasks.with_raw_response.retrieve(
            name="name",
            workspace="workspace",
            job="job",
            step="step",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        task = response.parse()
        assert_matches_type(PlatformJobTask, task, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_streaming_response_retrieve(self, client: NeMoPlatform) -> None:
        with client.jobs.tasks.with_streaming_response.retrieve(
            name="name",
            workspace="workspace",
            job="job",
            step="step",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            task = response.parse()
            assert_matches_type(PlatformJobTask, task, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_path_params_retrieve(self, client: NeMoPlatform) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `workspace` but received ''"):
            client.jobs.tasks.with_raw_response.retrieve(
                name="name",
                workspace="",
                job="job",
                step="step",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `job` but received ''"):
            client.jobs.tasks.with_raw_response.retrieve(
                name="name",
                workspace="workspace",
                job="",
                step="step",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `step` but received ''"):
            client.jobs.tasks.with_raw_response.retrieve(
                name="name",
                workspace="workspace",
                job="job",
                step="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `name` but received ''"):
            client.jobs.tasks.with_raw_response.retrieve(
                name="",
                workspace="workspace",
                job="job",
                step="step",
            )

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_method_list(self, client: NeMoPlatform) -> None:
        task = client.jobs.tasks.list(
            name="name",
            workspace="workspace",
            job="job",
        )
        assert_matches_type(PlatformJobListTaskResponse, task, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_raw_response_list(self, client: NeMoPlatform) -> None:
        response = client.jobs.tasks.with_raw_response.list(
            name="name",
            workspace="workspace",
            job="job",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        task = response.parse()
        assert_matches_type(PlatformJobListTaskResponse, task, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_streaming_response_list(self, client: NeMoPlatform) -> None:
        with client.jobs.tasks.with_streaming_response.list(
            name="name",
            workspace="workspace",
            job="job",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            task = response.parse()
            assert_matches_type(PlatformJobListTaskResponse, task, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_path_params_list(self, client: NeMoPlatform) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `workspace` but received ''"):
            client.jobs.tasks.with_raw_response.list(
                name="name",
                workspace="",
                job="job",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `job` but received ''"):
            client.jobs.tasks.with_raw_response.list(
                name="name",
                workspace="workspace",
                job="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `name` but received ''"):
            client.jobs.tasks.with_raw_response.list(
                name="",
                workspace="workspace",
                job="job",
            )

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_method_create_or_update(self, client: NeMoPlatform) -> None:
        task = client.jobs.tasks.create_or_update(
            name="name",
            workspace="workspace",
            job="job",
            step="step",
        )
        assert_matches_type(PlatformJobTask, task, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_method_create_or_update_with_all_params(self, client: NeMoPlatform) -> None:
        task = client.jobs.tasks.create_or_update(
            name="name",
            workspace="workspace",
            job="job",
            step="step",
            error_details={"foo": "bar"},
            error_stack="error_stack",
            status="created",
            status_details={"foo": "bar"},
        )
        assert_matches_type(PlatformJobTask, task, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_raw_response_create_or_update(self, client: NeMoPlatform) -> None:
        response = client.jobs.tasks.with_raw_response.create_or_update(
            name="name",
            workspace="workspace",
            job="job",
            step="step",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        task = response.parse()
        assert_matches_type(PlatformJobTask, task, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_streaming_response_create_or_update(self, client: NeMoPlatform) -> None:
        with client.jobs.tasks.with_streaming_response.create_or_update(
            name="name",
            workspace="workspace",
            job="job",
            step="step",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            task = response.parse()
            assert_matches_type(PlatformJobTask, task, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_path_params_create_or_update(self, client: NeMoPlatform) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `workspace` but received ''"):
            client.jobs.tasks.with_raw_response.create_or_update(
                name="name",
                workspace="",
                job="job",
                step="step",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `job` but received ''"):
            client.jobs.tasks.with_raw_response.create_or_update(
                name="name",
                workspace="workspace",
                job="",
                step="step",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `step` but received ''"):
            client.jobs.tasks.with_raw_response.create_or_update(
                name="name",
                workspace="workspace",
                job="job",
                step="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `name` but received ''"):
            client.jobs.tasks.with_raw_response.create_or_update(
                name="",
                workspace="workspace",
                job="job",
                step="step",
            )


class TestAsyncTasks:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncNeMoPlatform) -> None:
        task = await async_client.jobs.tasks.retrieve(
            name="name",
            workspace="workspace",
            job="job",
            step="step",
        )
        assert_matches_type(PlatformJobTask, task, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncNeMoPlatform) -> None:
        response = await async_client.jobs.tasks.with_raw_response.retrieve(
            name="name",
            workspace="workspace",
            job="job",
            step="step",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        task = await response.parse()
        assert_matches_type(PlatformJobTask, task, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncNeMoPlatform) -> None:
        async with async_client.jobs.tasks.with_streaming_response.retrieve(
            name="name",
            workspace="workspace",
            job="job",
            step="step",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            task = await response.parse()
            assert_matches_type(PlatformJobTask, task, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncNeMoPlatform) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `workspace` but received ''"):
            await async_client.jobs.tasks.with_raw_response.retrieve(
                name="name",
                workspace="",
                job="job",
                step="step",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `job` but received ''"):
            await async_client.jobs.tasks.with_raw_response.retrieve(
                name="name",
                workspace="workspace",
                job="",
                step="step",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `step` but received ''"):
            await async_client.jobs.tasks.with_raw_response.retrieve(
                name="name",
                workspace="workspace",
                job="job",
                step="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `name` but received ''"):
            await async_client.jobs.tasks.with_raw_response.retrieve(
                name="",
                workspace="workspace",
                job="job",
                step="step",
            )

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_method_list(self, async_client: AsyncNeMoPlatform) -> None:
        task = await async_client.jobs.tasks.list(
            name="name",
            workspace="workspace",
            job="job",
        )
        assert_matches_type(PlatformJobListTaskResponse, task, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncNeMoPlatform) -> None:
        response = await async_client.jobs.tasks.with_raw_response.list(
            name="name",
            workspace="workspace",
            job="job",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        task = await response.parse()
        assert_matches_type(PlatformJobListTaskResponse, task, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncNeMoPlatform) -> None:
        async with async_client.jobs.tasks.with_streaming_response.list(
            name="name",
            workspace="workspace",
            job="job",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            task = await response.parse()
            assert_matches_type(PlatformJobListTaskResponse, task, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_path_params_list(self, async_client: AsyncNeMoPlatform) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `workspace` but received ''"):
            await async_client.jobs.tasks.with_raw_response.list(
                name="name",
                workspace="",
                job="job",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `job` but received ''"):
            await async_client.jobs.tasks.with_raw_response.list(
                name="name",
                workspace="workspace",
                job="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `name` but received ''"):
            await async_client.jobs.tasks.with_raw_response.list(
                name="",
                workspace="workspace",
                job="job",
            )

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_method_create_or_update(self, async_client: AsyncNeMoPlatform) -> None:
        task = await async_client.jobs.tasks.create_or_update(
            name="name",
            workspace="workspace",
            job="job",
            step="step",
        )
        assert_matches_type(PlatformJobTask, task, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_method_create_or_update_with_all_params(self, async_client: AsyncNeMoPlatform) -> None:
        task = await async_client.jobs.tasks.create_or_update(
            name="name",
            workspace="workspace",
            job="job",
            step="step",
            error_details={"foo": "bar"},
            error_stack="error_stack",
            status="created",
            status_details={"foo": "bar"},
        )
        assert_matches_type(PlatformJobTask, task, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_raw_response_create_or_update(self, async_client: AsyncNeMoPlatform) -> None:
        response = await async_client.jobs.tasks.with_raw_response.create_or_update(
            name="name",
            workspace="workspace",
            job="job",
            step="step",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        task = await response.parse()
        assert_matches_type(PlatformJobTask, task, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_streaming_response_create_or_update(self, async_client: AsyncNeMoPlatform) -> None:
        async with async_client.jobs.tasks.with_streaming_response.create_or_update(
            name="name",
            workspace="workspace",
            job="job",
            step="step",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            task = await response.parse()
            assert_matches_type(PlatformJobTask, task, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_path_params_create_or_update(self, async_client: AsyncNeMoPlatform) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `workspace` but received ''"):
            await async_client.jobs.tasks.with_raw_response.create_or_update(
                name="name",
                workspace="",
                job="job",
                step="step",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `job` but received ''"):
            await async_client.jobs.tasks.with_raw_response.create_or_update(
                name="name",
                workspace="workspace",
                job="",
                step="step",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `step` but received ''"):
            await async_client.jobs.tasks.with_raw_response.create_or_update(
                name="name",
                workspace="workspace",
                job="job",
                step="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `name` but received ''"):
            await async_client.jobs.tasks.with_raw_response.create_or_update(
                name="",
                workspace="workspace",
                job="job",
                step="step",
            )
