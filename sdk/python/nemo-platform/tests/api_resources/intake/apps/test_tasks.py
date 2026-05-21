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
from nemo_platform._utils import parse_datetime
from nemo_platform.pagination import SyncDefaultPagination, AsyncDefaultPagination
from nemo_platform.types.intake.apps import (
    Task,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestTasks:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_method_create(self, client: NeMoPlatform) -> None:
        task = client.intake.apps.tasks.create(
            path_name="name",
            workspace="workspace",
            body_name="name",
        )
        assert_matches_type(Task, task, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_method_create_with_all_params(self, client: NeMoPlatform) -> None:
        task = client.intake.apps.tasks.create(
            path_name="name",
            workspace="workspace",
            body_name="name",
            description="description",
            locked=True,
            project="project",
        )
        assert_matches_type(Task, task, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_raw_response_create(self, client: NeMoPlatform) -> None:
        response = client.intake.apps.tasks.with_raw_response.create(
            path_name="name",
            workspace="workspace",
            body_name="name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        task = response.parse()
        assert_matches_type(Task, task, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_streaming_response_create(self, client: NeMoPlatform) -> None:
        with client.intake.apps.tasks.with_streaming_response.create(
            path_name="name",
            workspace="workspace",
            body_name="name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            task = response.parse()
            assert_matches_type(Task, task, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_path_params_create(self, client: NeMoPlatform) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `workspace` but received ''"):
            client.intake.apps.tasks.with_raw_response.create(
                path_name="name",
                workspace="",
                body_name="name",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `path_name` but received ''"):
            client.intake.apps.tasks.with_raw_response.create(
                path_name="",
                workspace="workspace",
                body_name="name",
            )

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_method_retrieve(self, client: NeMoPlatform) -> None:
        task = client.intake.apps.tasks.retrieve(
            name="name",
            workspace="workspace",
            app="app",
        )
        assert_matches_type(Task, task, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_raw_response_retrieve(self, client: NeMoPlatform) -> None:
        response = client.intake.apps.tasks.with_raw_response.retrieve(
            name="name",
            workspace="workspace",
            app="app",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        task = response.parse()
        assert_matches_type(Task, task, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_streaming_response_retrieve(self, client: NeMoPlatform) -> None:
        with client.intake.apps.tasks.with_streaming_response.retrieve(
            name="name",
            workspace="workspace",
            app="app",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            task = response.parse()
            assert_matches_type(Task, task, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_path_params_retrieve(self, client: NeMoPlatform) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `workspace` but received ''"):
            client.intake.apps.tasks.with_raw_response.retrieve(
                name="name",
                workspace="",
                app="app",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `app` but received ''"):
            client.intake.apps.tasks.with_raw_response.retrieve(
                name="name",
                workspace="workspace",
                app="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `name` but received ''"):
            client.intake.apps.tasks.with_raw_response.retrieve(
                name="",
                workspace="workspace",
                app="app",
            )

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_method_list(self, client: NeMoPlatform) -> None:
        task = client.intake.apps.tasks.list(
            name="name",
            workspace="workspace",
        )
        assert_matches_type(SyncDefaultPagination[Task], task, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_method_list_with_all_params(self, client: NeMoPlatform) -> None:
        task = client.intake.apps.tasks.list(
            name="name",
            workspace="workspace",
            filter={
                "app": "app",
                "created_at": {
                    "gte": parse_datetime("2019-12-27T18:11:19.117Z"),
                    "lte": parse_datetime("2019-12-27T18:11:19.117Z"),
                },
                "description": "description",
                "name": "name",
                "project": "project",
                "updated_at": {
                    "gte": parse_datetime("2019-12-27T18:11:19.117Z"),
                    "lte": parse_datetime("2019-12-27T18:11:19.117Z"),
                },
                "workspace": "workspace",
            },
            page=0,
            page_size=0,
            sort="created_at",
        )
        assert_matches_type(SyncDefaultPagination[Task], task, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_raw_response_list(self, client: NeMoPlatform) -> None:
        response = client.intake.apps.tasks.with_raw_response.list(
            name="name",
            workspace="workspace",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        task = response.parse()
        assert_matches_type(SyncDefaultPagination[Task], task, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_streaming_response_list(self, client: NeMoPlatform) -> None:
        with client.intake.apps.tasks.with_streaming_response.list(
            name="name",
            workspace="workspace",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            task = response.parse()
            assert_matches_type(SyncDefaultPagination[Task], task, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_path_params_list(self, client: NeMoPlatform) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `workspace` but received ''"):
            client.intake.apps.tasks.with_raw_response.list(
                name="name",
                workspace="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `name` but received ''"):
            client.intake.apps.tasks.with_raw_response.list(
                name="",
                workspace="workspace",
            )

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_method_delete(self, client: NeMoPlatform) -> None:
        task = client.intake.apps.tasks.delete(
            name="name",
            workspace="workspace",
            app="app",
        )
        assert task is None

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_raw_response_delete(self, client: NeMoPlatform) -> None:
        response = client.intake.apps.tasks.with_raw_response.delete(
            name="name",
            workspace="workspace",
            app="app",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        task = response.parse()
        assert task is None

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_streaming_response_delete(self, client: NeMoPlatform) -> None:
        with client.intake.apps.tasks.with_streaming_response.delete(
            name="name",
            workspace="workspace",
            app="app",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            task = response.parse()
            assert task is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_path_params_delete(self, client: NeMoPlatform) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `workspace` but received ''"):
            client.intake.apps.tasks.with_raw_response.delete(
                name="name",
                workspace="",
                app="app",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `app` but received ''"):
            client.intake.apps.tasks.with_raw_response.delete(
                name="name",
                workspace="workspace",
                app="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `name` but received ''"):
            client.intake.apps.tasks.with_raw_response.delete(
                name="",
                workspace="workspace",
                app="app",
            )

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_method_patch(self, client: NeMoPlatform) -> None:
        task = client.intake.apps.tasks.patch(
            name="name",
            workspace="workspace",
            app="app",
        )
        assert_matches_type(Task, task, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_method_patch_with_all_params(self, client: NeMoPlatform) -> None:
        task = client.intake.apps.tasks.patch(
            name="name",
            workspace="workspace",
            app="app",
            description="description",
            locked=True,
            project="project",
        )
        assert_matches_type(Task, task, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_raw_response_patch(self, client: NeMoPlatform) -> None:
        response = client.intake.apps.tasks.with_raw_response.patch(
            name="name",
            workspace="workspace",
            app="app",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        task = response.parse()
        assert_matches_type(Task, task, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_streaming_response_patch(self, client: NeMoPlatform) -> None:
        with client.intake.apps.tasks.with_streaming_response.patch(
            name="name",
            workspace="workspace",
            app="app",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            task = response.parse()
            assert_matches_type(Task, task, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_path_params_patch(self, client: NeMoPlatform) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `workspace` but received ''"):
            client.intake.apps.tasks.with_raw_response.patch(
                name="name",
                workspace="",
                app="app",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `app` but received ''"):
            client.intake.apps.tasks.with_raw_response.patch(
                name="name",
                workspace="workspace",
                app="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `name` but received ''"):
            client.intake.apps.tasks.with_raw_response.patch(
                name="",
                workspace="workspace",
                app="app",
            )


class TestAsyncTasks:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_method_create(self, async_client: AsyncNeMoPlatform) -> None:
        task = await async_client.intake.apps.tasks.create(
            path_name="name",
            workspace="workspace",
            body_name="name",
        )
        assert_matches_type(Task, task, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncNeMoPlatform) -> None:
        task = await async_client.intake.apps.tasks.create(
            path_name="name",
            workspace="workspace",
            body_name="name",
            description="description",
            locked=True,
            project="project",
        )
        assert_matches_type(Task, task, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncNeMoPlatform) -> None:
        response = await async_client.intake.apps.tasks.with_raw_response.create(
            path_name="name",
            workspace="workspace",
            body_name="name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        task = await response.parse()
        assert_matches_type(Task, task, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncNeMoPlatform) -> None:
        async with async_client.intake.apps.tasks.with_streaming_response.create(
            path_name="name",
            workspace="workspace",
            body_name="name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            task = await response.parse()
            assert_matches_type(Task, task, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_path_params_create(self, async_client: AsyncNeMoPlatform) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `workspace` but received ''"):
            await async_client.intake.apps.tasks.with_raw_response.create(
                path_name="name",
                workspace="",
                body_name="name",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `path_name` but received ''"):
            await async_client.intake.apps.tasks.with_raw_response.create(
                path_name="",
                workspace="workspace",
                body_name="name",
            )

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncNeMoPlatform) -> None:
        task = await async_client.intake.apps.tasks.retrieve(
            name="name",
            workspace="workspace",
            app="app",
        )
        assert_matches_type(Task, task, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncNeMoPlatform) -> None:
        response = await async_client.intake.apps.tasks.with_raw_response.retrieve(
            name="name",
            workspace="workspace",
            app="app",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        task = await response.parse()
        assert_matches_type(Task, task, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncNeMoPlatform) -> None:
        async with async_client.intake.apps.tasks.with_streaming_response.retrieve(
            name="name",
            workspace="workspace",
            app="app",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            task = await response.parse()
            assert_matches_type(Task, task, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncNeMoPlatform) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `workspace` but received ''"):
            await async_client.intake.apps.tasks.with_raw_response.retrieve(
                name="name",
                workspace="",
                app="app",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `app` but received ''"):
            await async_client.intake.apps.tasks.with_raw_response.retrieve(
                name="name",
                workspace="workspace",
                app="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `name` but received ''"):
            await async_client.intake.apps.tasks.with_raw_response.retrieve(
                name="",
                workspace="workspace",
                app="app",
            )

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_method_list(self, async_client: AsyncNeMoPlatform) -> None:
        task = await async_client.intake.apps.tasks.list(
            name="name",
            workspace="workspace",
        )
        assert_matches_type(AsyncDefaultPagination[Task], task, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncNeMoPlatform) -> None:
        task = await async_client.intake.apps.tasks.list(
            name="name",
            workspace="workspace",
            filter={
                "app": "app",
                "created_at": {
                    "gte": parse_datetime("2019-12-27T18:11:19.117Z"),
                    "lte": parse_datetime("2019-12-27T18:11:19.117Z"),
                },
                "description": "description",
                "name": "name",
                "project": "project",
                "updated_at": {
                    "gte": parse_datetime("2019-12-27T18:11:19.117Z"),
                    "lte": parse_datetime("2019-12-27T18:11:19.117Z"),
                },
                "workspace": "workspace",
            },
            page=0,
            page_size=0,
            sort="created_at",
        )
        assert_matches_type(AsyncDefaultPagination[Task], task, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncNeMoPlatform) -> None:
        response = await async_client.intake.apps.tasks.with_raw_response.list(
            name="name",
            workspace="workspace",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        task = await response.parse()
        assert_matches_type(AsyncDefaultPagination[Task], task, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncNeMoPlatform) -> None:
        async with async_client.intake.apps.tasks.with_streaming_response.list(
            name="name",
            workspace="workspace",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            task = await response.parse()
            assert_matches_type(AsyncDefaultPagination[Task], task, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_path_params_list(self, async_client: AsyncNeMoPlatform) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `workspace` but received ''"):
            await async_client.intake.apps.tasks.with_raw_response.list(
                name="name",
                workspace="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `name` but received ''"):
            await async_client.intake.apps.tasks.with_raw_response.list(
                name="",
                workspace="workspace",
            )

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_method_delete(self, async_client: AsyncNeMoPlatform) -> None:
        task = await async_client.intake.apps.tasks.delete(
            name="name",
            workspace="workspace",
            app="app",
        )
        assert task is None

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncNeMoPlatform) -> None:
        response = await async_client.intake.apps.tasks.with_raw_response.delete(
            name="name",
            workspace="workspace",
            app="app",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        task = await response.parse()
        assert task is None

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncNeMoPlatform) -> None:
        async with async_client.intake.apps.tasks.with_streaming_response.delete(
            name="name",
            workspace="workspace",
            app="app",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            task = await response.parse()
            assert task is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncNeMoPlatform) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `workspace` but received ''"):
            await async_client.intake.apps.tasks.with_raw_response.delete(
                name="name",
                workspace="",
                app="app",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `app` but received ''"):
            await async_client.intake.apps.tasks.with_raw_response.delete(
                name="name",
                workspace="workspace",
                app="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `name` but received ''"):
            await async_client.intake.apps.tasks.with_raw_response.delete(
                name="",
                workspace="workspace",
                app="app",
            )

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_method_patch(self, async_client: AsyncNeMoPlatform) -> None:
        task = await async_client.intake.apps.tasks.patch(
            name="name",
            workspace="workspace",
            app="app",
        )
        assert_matches_type(Task, task, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_method_patch_with_all_params(self, async_client: AsyncNeMoPlatform) -> None:
        task = await async_client.intake.apps.tasks.patch(
            name="name",
            workspace="workspace",
            app="app",
            description="description",
            locked=True,
            project="project",
        )
        assert_matches_type(Task, task, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_raw_response_patch(self, async_client: AsyncNeMoPlatform) -> None:
        response = await async_client.intake.apps.tasks.with_raw_response.patch(
            name="name",
            workspace="workspace",
            app="app",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        task = await response.parse()
        assert_matches_type(Task, task, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_streaming_response_patch(self, async_client: AsyncNeMoPlatform) -> None:
        async with async_client.intake.apps.tasks.with_streaming_response.patch(
            name="name",
            workspace="workspace",
            app="app",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            task = await response.parse()
            assert_matches_type(Task, task, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_path_params_patch(self, async_client: AsyncNeMoPlatform) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `workspace` but received ''"):
            await async_client.intake.apps.tasks.with_raw_response.patch(
                name="name",
                workspace="",
                app="app",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `app` but received ''"):
            await async_client.intake.apps.tasks.with_raw_response.patch(
                name="name",
                workspace="workspace",
                app="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `name` but received ''"):
            await async_client.intake.apps.tasks.with_raw_response.patch(
                name="",
                workspace="workspace",
                app="app",
            )
