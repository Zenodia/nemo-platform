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
from nemo_platform.types.secrets import PlatformSecretAdminRotationResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestAdmin:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_method_rotate_encryption_keys(self, client: NeMoPlatform) -> None:
        admin = client.secrets.admin.rotate_encryption_keys()
        assert_matches_type(PlatformSecretAdminRotationResponse, admin, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_raw_response_rotate_encryption_keys(self, client: NeMoPlatform) -> None:
        response = client.secrets.admin.with_raw_response.rotate_encryption_keys()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        admin = response.parse()
        assert_matches_type(PlatformSecretAdminRotationResponse, admin, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    def test_streaming_response_rotate_encryption_keys(self, client: NeMoPlatform) -> None:
        with client.secrets.admin.with_streaming_response.rotate_encryption_keys() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            admin = response.parse()
            assert_matches_type(PlatformSecretAdminRotationResponse, admin, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncAdmin:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_method_rotate_encryption_keys(self, async_client: AsyncNeMoPlatform) -> None:
        admin = await async_client.secrets.admin.rotate_encryption_keys()
        assert_matches_type(PlatformSecretAdminRotationResponse, admin, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_raw_response_rotate_encryption_keys(self, async_client: AsyncNeMoPlatform) -> None:
        response = await async_client.secrets.admin.with_raw_response.rotate_encryption_keys()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        admin = await response.parse()
        assert_matches_type(PlatformSecretAdminRotationResponse, admin, path=["response"])

    @pytest.mark.skip(reason="Mock server tests are disabled")
    @parametrize
    async def test_streaming_response_rotate_encryption_keys(self, async_client: AsyncNeMoPlatform) -> None:
        async with async_client.secrets.admin.with_streaming_response.rotate_encryption_keys() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            admin = await response.parse()
            assert_matches_type(PlatformSecretAdminRotationResponse, admin, path=["response"])

        assert cast(Any, response.is_closed) is True
