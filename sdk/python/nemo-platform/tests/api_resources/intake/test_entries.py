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
from nemo_platform.types.intake import (
    Entry,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestEntries:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_method_create(self, client: NeMoPlatform) -> None:
        entry = client.intake.entries.create(
            workspace="workspace",
            context={
                "app": "app",
                "task": "task",
            },
            data={
                "request": {
                    "messages": [{"role": "user"}],
                    "model": "model",
                },
                "response": {},
            },
        )
        assert_matches_type(Entry, entry, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_method_create_with_all_params(self, client: NeMoPlatform) -> None:
        entry = client.intake.entries.create(
            workspace="workspace",
            context={
                "app": "app",
                "task": "task",
                "created_at": parse_datetime("2019-12-27T18:11:19.117Z"),
                "session_id": "session_id",
                "thread_id": "thread_id",
                "trace_id": "trace_id",
                "user_id": "user_id",
            },
            data={
                "request": {
                    "messages": [{"role": "user"}],
                    "model": "model",
                },
                "response": {
                    "choices": [{"foo": "bar"}],
                    "error": {"foo": "bar"},
                },
            },
            custom_fields={"foo": "bar"},
            events=[
                {
                    "id": "id",
                    "categories": {"foo": 0},
                    "chosen_index": 0,
                    "created_at": parse_datetime("2019-12-27T18:11:19.117Z"),
                    "created_by": {"foo": "string"},
                    "event_type": "user_feedback",
                    "opinion": "x",
                    "rating": 0,
                    "rewrite": "x",
                    "thumb": "up",
                }
            ],
            external_id="external_id",
            project="project",
            usage={
                "cached_tokens": 0,
                "cost_input_usd": 0,
                "cost_output_usd": 0,
                "cost_usd": 0,
                "ended_at": parse_datetime("2019-12-27T18:11:19.117Z"),
                "input_tokens": 0,
                "latency_ms": 0,
                "model": "model",
                "output_tokens": 0,
                "started_at": parse_datetime("2019-12-27T18:11:19.117Z"),
            },
            user_rating={
                "categories": {"foo": 0},
                "chosen_index": 0,
                "opinion": "x",
                "rating": 0,
                "rewrite": "x",
                "thumb": "up",
            },
        )
        assert_matches_type(Entry, entry, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_raw_response_create(self, client: NeMoPlatform) -> None:
        response = client.intake.entries.with_raw_response.create(
            workspace="workspace",
            context={
                "app": "app",
                "task": "task",
            },
            data={
                "request": {
                    "messages": [{"role": "user"}],
                    "model": "model",
                },
                "response": {},
            },
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        entry = response.parse()
        assert_matches_type(Entry, entry, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_streaming_response_create(self, client: NeMoPlatform) -> None:
        with client.intake.entries.with_streaming_response.create(
            workspace="workspace",
            context={
                "app": "app",
                "task": "task",
            },
            data={
                "request": {
                    "messages": [{"role": "user"}],
                    "model": "model",
                },
                "response": {},
            },
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            entry = response.parse()
            assert_matches_type(Entry, entry, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_path_params_create(self, client: NeMoPlatform) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `workspace` but received ''"):
            client.intake.entries.with_raw_response.create(
                workspace="",
                context={
                    "app": "app",
                    "task": "task",
                },
                data={
                    "request": {
                        "messages": [{"role": "user"}],
                        "model": "model",
                    },
                    "response": {},
                },
            )

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_method_retrieve(self, client: NeMoPlatform) -> None:
        entry = client.intake.entries.retrieve(
            name="name",
            workspace="workspace",
        )
        assert_matches_type(Entry, entry, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_raw_response_retrieve(self, client: NeMoPlatform) -> None:
        response = client.intake.entries.with_raw_response.retrieve(
            name="name",
            workspace="workspace",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        entry = response.parse()
        assert_matches_type(Entry, entry, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_streaming_response_retrieve(self, client: NeMoPlatform) -> None:
        with client.intake.entries.with_streaming_response.retrieve(
            name="name",
            workspace="workspace",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            entry = response.parse()
            assert_matches_type(Entry, entry, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_path_params_retrieve(self, client: NeMoPlatform) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `workspace` but received ''"):
            client.intake.entries.with_raw_response.retrieve(
                name="name",
                workspace="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `name` but received ''"):
            client.intake.entries.with_raw_response.retrieve(
                name="",
                workspace="workspace",
            )

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_method_list(self, client: NeMoPlatform) -> None:
        entry = client.intake.entries.list(
            workspace="workspace",
        )
        assert_matches_type(SyncDefaultPagination[Entry], entry, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_method_list_with_all_params(self, client: NeMoPlatform) -> None:
        entry = client.intake.entries.list(
            workspace="workspace",
            filter={
                "id": "string",
                "context": {
                    "app": "app",
                    "session_id": "session_id",
                    "task": "task",
                    "thread_id": "thread_id",
                    "user_id": "user_id",
                },
                "created_at": {
                    "gte": parse_datetime("2019-12-27T18:11:19.117Z"),
                    "lte": parse_datetime("2019-12-27T18:11:19.117Z"),
                },
                "external_id": "string",
                "has_events": True,
                "has_opinion": True,
                "has_rating": True,
                "has_rewrite": True,
                "has_thumb": True,
                "longest_per_thread": True,
                "model": "model",
                "project": "project",
                "updated_at": {
                    "gte": parse_datetime("2019-12-27T18:11:19.117Z"),
                    "lte": parse_datetime("2019-12-27T18:11:19.117Z"),
                },
                "user_rating": {"thumb": "up"},
                "workspace": "workspace",
            },
            page=0,
            page_size=0,
            sort="created_at",
        )
        assert_matches_type(SyncDefaultPagination[Entry], entry, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_raw_response_list(self, client: NeMoPlatform) -> None:
        response = client.intake.entries.with_raw_response.list(
            workspace="workspace",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        entry = response.parse()
        assert_matches_type(SyncDefaultPagination[Entry], entry, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_streaming_response_list(self, client: NeMoPlatform) -> None:
        with client.intake.entries.with_streaming_response.list(
            workspace="workspace",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            entry = response.parse()
            assert_matches_type(SyncDefaultPagination[Entry], entry, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_path_params_list(self, client: NeMoPlatform) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `workspace` but received ''"):
            client.intake.entries.with_raw_response.list(
                workspace="",
            )

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_method_delete(self, client: NeMoPlatform) -> None:
        entry = client.intake.entries.delete(
            name="name",
            workspace="workspace",
        )
        assert entry is None

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_raw_response_delete(self, client: NeMoPlatform) -> None:
        response = client.intake.entries.with_raw_response.delete(
            name="name",
            workspace="workspace",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        entry = response.parse()
        assert entry is None

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_streaming_response_delete(self, client: NeMoPlatform) -> None:
        with client.intake.entries.with_streaming_response.delete(
            name="name",
            workspace="workspace",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            entry = response.parse()
            assert entry is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_path_params_delete(self, client: NeMoPlatform) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `workspace` but received ''"):
            client.intake.entries.with_raw_response.delete(
                name="name",
                workspace="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `name` but received ''"):
            client.intake.entries.with_raw_response.delete(
                name="",
                workspace="workspace",
            )

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_method_patch(self, client: NeMoPlatform) -> None:
        entry = client.intake.entries.patch(
            name="name",
            workspace="workspace",
        )
        assert_matches_type(Entry, entry, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_method_patch_with_all_params(self, client: NeMoPlatform) -> None:
        entry = client.intake.entries.patch(
            name="name",
            workspace="workspace",
            context={
                "app": "app",
                "task": "task",
                "created_at": parse_datetime("2019-12-27T18:11:19.117Z"),
                "session_id": "session_id",
                "thread_id": "thread_id",
                "trace_id": "trace_id",
                "user_id": "user_id",
            },
            custom_fields={"foo": "bar"},
            data={
                "request": {
                    "messages": [{"role": "user"}],
                    "model": "model",
                },
                "response": {
                    "choices": [{"foo": "bar"}],
                    "error": {"foo": "bar"},
                },
            },
            events=[
                {
                    "id": "id",
                    "categories": {"foo": 0},
                    "chosen_index": 0,
                    "created_at": parse_datetime("2019-12-27T18:11:19.117Z"),
                    "created_by": {"foo": "string"},
                    "event_type": "user_feedback",
                    "opinion": "x",
                    "rating": 0,
                    "rewrite": "x",
                    "thumb": "up",
                }
            ],
            usage={
                "cached_tokens": 0,
                "cost_input_usd": 0,
                "cost_output_usd": 0,
                "cost_usd": 0,
                "ended_at": parse_datetime("2019-12-27T18:11:19.117Z"),
                "input_tokens": 0,
                "latency_ms": 0,
                "model": "model",
                "output_tokens": 0,
                "started_at": parse_datetime("2019-12-27T18:11:19.117Z"),
            },
            user_rating={
                "categories": {"foo": 0},
                "chosen_index": 0,
                "opinion": "x",
                "rating": 0,
                "rewrite": "x",
                "thumb": "up",
            },
        )
        assert_matches_type(Entry, entry, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_raw_response_patch(self, client: NeMoPlatform) -> None:
        response = client.intake.entries.with_raw_response.patch(
            name="name",
            workspace="workspace",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        entry = response.parse()
        assert_matches_type(Entry, entry, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_streaming_response_patch(self, client: NeMoPlatform) -> None:
        with client.intake.entries.with_streaming_response.patch(
            name="name",
            workspace="workspace",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            entry = response.parse()
            assert_matches_type(Entry, entry, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_path_params_patch(self, client: NeMoPlatform) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `workspace` but received ''"):
            client.intake.entries.with_raw_response.patch(
                name="name",
                workspace="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `name` but received ''"):
            client.intake.entries.with_raw_response.patch(
                name="",
                workspace="workspace",
            )


class TestAsyncEntries:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_method_create(self, async_client: AsyncNeMoPlatform) -> None:
        entry = await async_client.intake.entries.create(
            workspace="workspace",
            context={
                "app": "app",
                "task": "task",
            },
            data={
                "request": {
                    "messages": [{"role": "user"}],
                    "model": "model",
                },
                "response": {},
            },
        )
        assert_matches_type(Entry, entry, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncNeMoPlatform) -> None:
        entry = await async_client.intake.entries.create(
            workspace="workspace",
            context={
                "app": "app",
                "task": "task",
                "created_at": parse_datetime("2019-12-27T18:11:19.117Z"),
                "session_id": "session_id",
                "thread_id": "thread_id",
                "trace_id": "trace_id",
                "user_id": "user_id",
            },
            data={
                "request": {
                    "messages": [{"role": "user"}],
                    "model": "model",
                },
                "response": {
                    "choices": [{"foo": "bar"}],
                    "error": {"foo": "bar"},
                },
            },
            custom_fields={"foo": "bar"},
            events=[
                {
                    "id": "id",
                    "categories": {"foo": 0},
                    "chosen_index": 0,
                    "created_at": parse_datetime("2019-12-27T18:11:19.117Z"),
                    "created_by": {"foo": "string"},
                    "event_type": "user_feedback",
                    "opinion": "x",
                    "rating": 0,
                    "rewrite": "x",
                    "thumb": "up",
                }
            ],
            external_id="external_id",
            project="project",
            usage={
                "cached_tokens": 0,
                "cost_input_usd": 0,
                "cost_output_usd": 0,
                "cost_usd": 0,
                "ended_at": parse_datetime("2019-12-27T18:11:19.117Z"),
                "input_tokens": 0,
                "latency_ms": 0,
                "model": "model",
                "output_tokens": 0,
                "started_at": parse_datetime("2019-12-27T18:11:19.117Z"),
            },
            user_rating={
                "categories": {"foo": 0},
                "chosen_index": 0,
                "opinion": "x",
                "rating": 0,
                "rewrite": "x",
                "thumb": "up",
            },
        )
        assert_matches_type(Entry, entry, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncNeMoPlatform) -> None:
        response = await async_client.intake.entries.with_raw_response.create(
            workspace="workspace",
            context={
                "app": "app",
                "task": "task",
            },
            data={
                "request": {
                    "messages": [{"role": "user"}],
                    "model": "model",
                },
                "response": {},
            },
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        entry = await response.parse()
        assert_matches_type(Entry, entry, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncNeMoPlatform) -> None:
        async with async_client.intake.entries.with_streaming_response.create(
            workspace="workspace",
            context={
                "app": "app",
                "task": "task",
            },
            data={
                "request": {
                    "messages": [{"role": "user"}],
                    "model": "model",
                },
                "response": {},
            },
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            entry = await response.parse()
            assert_matches_type(Entry, entry, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_path_params_create(self, async_client: AsyncNeMoPlatform) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `workspace` but received ''"):
            await async_client.intake.entries.with_raw_response.create(
                workspace="",
                context={
                    "app": "app",
                    "task": "task",
                },
                data={
                    "request": {
                        "messages": [{"role": "user"}],
                        "model": "model",
                    },
                    "response": {},
                },
            )

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncNeMoPlatform) -> None:
        entry = await async_client.intake.entries.retrieve(
            name="name",
            workspace="workspace",
        )
        assert_matches_type(Entry, entry, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncNeMoPlatform) -> None:
        response = await async_client.intake.entries.with_raw_response.retrieve(
            name="name",
            workspace="workspace",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        entry = await response.parse()
        assert_matches_type(Entry, entry, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncNeMoPlatform) -> None:
        async with async_client.intake.entries.with_streaming_response.retrieve(
            name="name",
            workspace="workspace",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            entry = await response.parse()
            assert_matches_type(Entry, entry, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncNeMoPlatform) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `workspace` but received ''"):
            await async_client.intake.entries.with_raw_response.retrieve(
                name="name",
                workspace="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `name` but received ''"):
            await async_client.intake.entries.with_raw_response.retrieve(
                name="",
                workspace="workspace",
            )

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_method_list(self, async_client: AsyncNeMoPlatform) -> None:
        entry = await async_client.intake.entries.list(
            workspace="workspace",
        )
        assert_matches_type(AsyncDefaultPagination[Entry], entry, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncNeMoPlatform) -> None:
        entry = await async_client.intake.entries.list(
            workspace="workspace",
            filter={
                "id": "string",
                "context": {
                    "app": "app",
                    "session_id": "session_id",
                    "task": "task",
                    "thread_id": "thread_id",
                    "user_id": "user_id",
                },
                "created_at": {
                    "gte": parse_datetime("2019-12-27T18:11:19.117Z"),
                    "lte": parse_datetime("2019-12-27T18:11:19.117Z"),
                },
                "external_id": "string",
                "has_events": True,
                "has_opinion": True,
                "has_rating": True,
                "has_rewrite": True,
                "has_thumb": True,
                "longest_per_thread": True,
                "model": "model",
                "project": "project",
                "updated_at": {
                    "gte": parse_datetime("2019-12-27T18:11:19.117Z"),
                    "lte": parse_datetime("2019-12-27T18:11:19.117Z"),
                },
                "user_rating": {"thumb": "up"},
                "workspace": "workspace",
            },
            page=0,
            page_size=0,
            sort="created_at",
        )
        assert_matches_type(AsyncDefaultPagination[Entry], entry, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncNeMoPlatform) -> None:
        response = await async_client.intake.entries.with_raw_response.list(
            workspace="workspace",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        entry = await response.parse()
        assert_matches_type(AsyncDefaultPagination[Entry], entry, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncNeMoPlatform) -> None:
        async with async_client.intake.entries.with_streaming_response.list(
            workspace="workspace",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            entry = await response.parse()
            assert_matches_type(AsyncDefaultPagination[Entry], entry, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_path_params_list(self, async_client: AsyncNeMoPlatform) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `workspace` but received ''"):
            await async_client.intake.entries.with_raw_response.list(
                workspace="",
            )

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_method_delete(self, async_client: AsyncNeMoPlatform) -> None:
        entry = await async_client.intake.entries.delete(
            name="name",
            workspace="workspace",
        )
        assert entry is None

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncNeMoPlatform) -> None:
        response = await async_client.intake.entries.with_raw_response.delete(
            name="name",
            workspace="workspace",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        entry = await response.parse()
        assert entry is None

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncNeMoPlatform) -> None:
        async with async_client.intake.entries.with_streaming_response.delete(
            name="name",
            workspace="workspace",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            entry = await response.parse()
            assert entry is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncNeMoPlatform) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `workspace` but received ''"):
            await async_client.intake.entries.with_raw_response.delete(
                name="name",
                workspace="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `name` but received ''"):
            await async_client.intake.entries.with_raw_response.delete(
                name="",
                workspace="workspace",
            )

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_method_patch(self, async_client: AsyncNeMoPlatform) -> None:
        entry = await async_client.intake.entries.patch(
            name="name",
            workspace="workspace",
        )
        assert_matches_type(Entry, entry, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_method_patch_with_all_params(self, async_client: AsyncNeMoPlatform) -> None:
        entry = await async_client.intake.entries.patch(
            name="name",
            workspace="workspace",
            context={
                "app": "app",
                "task": "task",
                "created_at": parse_datetime("2019-12-27T18:11:19.117Z"),
                "session_id": "session_id",
                "thread_id": "thread_id",
                "trace_id": "trace_id",
                "user_id": "user_id",
            },
            custom_fields={"foo": "bar"},
            data={
                "request": {
                    "messages": [{"role": "user"}],
                    "model": "model",
                },
                "response": {
                    "choices": [{"foo": "bar"}],
                    "error": {"foo": "bar"},
                },
            },
            events=[
                {
                    "id": "id",
                    "categories": {"foo": 0},
                    "chosen_index": 0,
                    "created_at": parse_datetime("2019-12-27T18:11:19.117Z"),
                    "created_by": {"foo": "string"},
                    "event_type": "user_feedback",
                    "opinion": "x",
                    "rating": 0,
                    "rewrite": "x",
                    "thumb": "up",
                }
            ],
            usage={
                "cached_tokens": 0,
                "cost_input_usd": 0,
                "cost_output_usd": 0,
                "cost_usd": 0,
                "ended_at": parse_datetime("2019-12-27T18:11:19.117Z"),
                "input_tokens": 0,
                "latency_ms": 0,
                "model": "model",
                "output_tokens": 0,
                "started_at": parse_datetime("2019-12-27T18:11:19.117Z"),
            },
            user_rating={
                "categories": {"foo": 0},
                "chosen_index": 0,
                "opinion": "x",
                "rating": 0,
                "rewrite": "x",
                "thumb": "up",
            },
        )
        assert_matches_type(Entry, entry, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_raw_response_patch(self, async_client: AsyncNeMoPlatform) -> None:
        response = await async_client.intake.entries.with_raw_response.patch(
            name="name",
            workspace="workspace",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        entry = await response.parse()
        assert_matches_type(Entry, entry, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_streaming_response_patch(self, async_client: AsyncNeMoPlatform) -> None:
        async with async_client.intake.entries.with_streaming_response.patch(
            name="name",
            workspace="workspace",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            entry = await response.parse()
            assert_matches_type(Entry, entry, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_path_params_patch(self, async_client: AsyncNeMoPlatform) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `workspace` but received ''"):
            await async_client.intake.entries.with_raw_response.patch(
                name="name",
                workspace="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `name` but received ''"):
            await async_client.intake.entries.with_raw_response.patch(
                name="",
                workspace="workspace",
            )
