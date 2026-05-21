# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Authorization helpers for secrets admin API routes."""

from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException
from nmp.common.auth.client import AuthClient
from nmp.common.auth.models import Principal
from nmp.common.config import AuthConfig
from nmp.core.secrets.api.v2.admin.endpoints import require_rotate_encryption_keys_caller


@pytest.fixture
def auth_config_enabled():
    return AuthConfig(enabled=True, policy_decision_point_base_url="http://localhost:8181")


@pytest.mark.asyncio
async def test_require_rotate_allows_platform_admin_permissions(auth_config_enabled):
    auth_client = MagicMock(spec=AuthClient)
    auth_client.auth_enabled = True
    auth_client.principal = Principal(id="admin@example.com")
    auth_client.has_permissions = AsyncMock(return_value=True)

    await require_rotate_encryption_keys_caller(auth_client)

    auth_client.has_permissions.assert_awaited_once_with("system", ["secrets.rotate"])


@pytest.mark.asyncio
async def test_require_rotate_forbids_without_secrets_rotate(auth_config_enabled):
    auth_client = MagicMock(spec=AuthClient)
    auth_client.auth_enabled = True
    auth_client.principal = Principal(id="user@example.com")
    auth_client.has_permissions = AsyncMock(return_value=False)

    with pytest.raises(HTTPException) as exc_info:
        await require_rotate_encryption_keys_caller(auth_client)

    assert exc_info.value.status_code == 403


@pytest.mark.asyncio
async def test_require_rotate_skips_checks_when_auth_disabled():
    auth_client = MagicMock()
    auth_client.auth_enabled = False
    auth_client.principal = Principal(id="user@example.com")

    await require_rotate_encryption_keys_caller(auth_client)
