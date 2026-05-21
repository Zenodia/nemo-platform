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
from nemo_platform.types.evaluation import RowScore

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestRowScores:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_method_download(self, client: NeMoPlatform) -> None:
        row_score_stream = client.evaluation.benchmark_jobs.results.row_scores.download(
            job="job",
            workspace="workspace",
        )
        for item in row_score_stream:
            assert_matches_type(RowScore, item, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_method_download_with_all_params(self, client: NeMoPlatform) -> None:
        row_score_stream = client.evaluation.benchmark_jobs.results.row_scores.download(
            job="job",
            workspace="workspace",
            limit=0,
        )
        for item in row_score_stream:
            assert_matches_type(RowScore, item, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_raw_response_download(self, client: NeMoPlatform) -> None:
        response = client.evaluation.benchmark_jobs.results.row_scores.with_raw_response.download(
            job="job",
            workspace="workspace",
        )

        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        stream = response.parse()
        for item in stream:
            assert_matches_type(RowScore, item, path=["line"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_streaming_response_download(self, client: NeMoPlatform) -> None:
        with client.evaluation.benchmark_jobs.results.row_scores.with_streaming_response.download(
            job="job",
            workspace="workspace",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            stream = response.parse()
            for item in stream:
                assert_matches_type(RowScore, item, path=["item"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_path_params_download(self, client: NeMoPlatform) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `workspace` but received ''"):
            client.evaluation.benchmark_jobs.results.row_scores.with_raw_response.download(
                job="job",
                workspace="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `job` but received ''"):
            client.evaluation.benchmark_jobs.results.row_scores.with_raw_response.download(
                job="",
                workspace="workspace",
            )


class TestAsyncRowScores:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_method_download(self, async_client: AsyncNeMoPlatform) -> None:
        row_score_stream = await async_client.evaluation.benchmark_jobs.results.row_scores.download(
            job="job",
            workspace="workspace",
        )
        async for item in row_score_stream:
            assert_matches_type(RowScore, item, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_method_download_with_all_params(self, async_client: AsyncNeMoPlatform) -> None:
        row_score_stream = await async_client.evaluation.benchmark_jobs.results.row_scores.download(
            job="job",
            workspace="workspace",
            limit=0,
        )
        async for item in row_score_stream:
            assert_matches_type(RowScore, item, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_raw_response_download(self, async_client: AsyncNeMoPlatform) -> None:
        response = await async_client.evaluation.benchmark_jobs.results.row_scores.with_raw_response.download(
            job="job",
            workspace="workspace",
        )

        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        stream = await response.parse()
        async for item in stream:
            assert_matches_type(RowScore, item, path=["line"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_streaming_response_download(self, async_client: AsyncNeMoPlatform) -> None:
        async with async_client.evaluation.benchmark_jobs.results.row_scores.with_streaming_response.download(
            job="job",
            workspace="workspace",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            stream = await response.parse()
            async for item in stream:
                assert_matches_type(RowScore, item, path=["item"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_path_params_download(self, async_client: AsyncNeMoPlatform) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `workspace` but received ''"):
            await async_client.evaluation.benchmark_jobs.results.row_scores.with_raw_response.download(
                job="job",
                workspace="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `job` but received ''"):
            await async_client.evaluation.benchmark_jobs.results.row_scores.with_raw_response.download(
                job="",
                workspace="workspace",
            )
