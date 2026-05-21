# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Tests for the example plugin SDK resources."""

from __future__ import annotations

from typing import cast
from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest
from nemo_example_plugin.sdk import AsyncExampleResource, ExampleResource
from nemo_platform import AsyncNeMoPlatform, NeMoPlatform

BASE = "http://test:8000"
WS = "default"
CONFIG_PAYLOAD = {
    "id": "default/my-filter",
    "name": "my-filter",
    "workspace": "default",
    "blocked_keywords": ["bad"],
    "block_message": "Blocked.",
}


class _SyncPlatform:
    def __init__(self) -> None:
        self.base_url = BASE
        self._client = MagicMock(spec=httpx.Client)


class _AsyncPlatform:
    def __init__(self) -> None:
        self.base_url = BASE
        self._client = AsyncMock(spec=httpx.AsyncClient)


def _sync_resp(payload) -> httpx.Response:
    return httpx.Response(200, request=httpx.Request("GET", BASE), json=payload)


def _async_resp(payload) -> httpx.Response:
    return httpx.Response(200, request=httpx.Request("GET", BASE), json=payload)


def _mw_url(path: str = "") -> str:
    return f"{BASE}/apis/example/v2/workspaces/{WS}/middleware-configs{path}"


# ---------------------------------------------------------------------------
# hello (existing)
# ---------------------------------------------------------------------------


def test_sync_hello() -> None:
    platform = _SyncPlatform()
    platform._client.get.return_value = httpx.Response(
        200, request=httpx.Request("GET", f"{BASE}/apis/example/hello/alice"), json={"message": "Hello, alice!"}
    )
    assert ExampleResource(cast(NeMoPlatform, platform)).hello("alice") == "Hello, alice!"
    platform._client.get.assert_called_once_with(f"{BASE}/apis/example/hello/alice")


@pytest.mark.asyncio
async def test_async_hello() -> None:
    platform = _AsyncPlatform()
    platform._client.get.return_value = httpx.Response(
        200, request=httpx.Request("GET", f"{BASE}/apis/example/hello/bob"), json={"message": "Hello, bob!"}
    )
    assert await AsyncExampleResource(cast(AsyncNeMoPlatform, platform)).hello("bob") == "Hello, bob!"
    platform._client.get.assert_awaited_once_with(f"{BASE}/apis/example/hello/bob")


# ---------------------------------------------------------------------------
# middleware config CRUD — sync
# ---------------------------------------------------------------------------


def test_sync_create_middleware_config() -> None:
    platform = _SyncPlatform()
    platform._client.post.return_value = _sync_resp(CONFIG_PAYLOAD)

    result = ExampleResource(cast(NeMoPlatform, platform)).create_middleware_config(
        WS, "my-filter", blocked_keywords=["bad"]
    )

    platform._client.post.assert_called_once_with(_mw_url(), json={"name": "my-filter", "blocked_keywords": ["bad"]})
    assert result["name"] == "my-filter"


def test_sync_list_middleware_configs() -> None:
    platform = _SyncPlatform()
    platform._client.get.return_value = _sync_resp([CONFIG_PAYLOAD])

    result = ExampleResource(cast(NeMoPlatform, platform)).list_middleware_configs(WS)

    platform._client.get.assert_called_once_with(_mw_url())
    assert len(result) == 1


def test_sync_get_middleware_config() -> None:
    platform = _SyncPlatform()
    platform._client.get.return_value = _sync_resp(CONFIG_PAYLOAD)

    result = ExampleResource(cast(NeMoPlatform, platform)).get_middleware_config(WS, "my-filter")

    platform._client.get.assert_called_once_with(_mw_url("/my-filter"))
    assert result["name"] == "my-filter"


def test_sync_update_middleware_config() -> None:
    platform = _SyncPlatform()
    updated = {**CONFIG_PAYLOAD, "block_message": "Updated."}
    platform._client.patch.return_value = _sync_resp(updated)

    result = ExampleResource(cast(NeMoPlatform, platform)).update_middleware_config(
        WS, "my-filter", block_message="Updated."
    )

    platform._client.patch.assert_called_once_with(_mw_url("/my-filter"), json={"block_message": "Updated."})
    assert result["block_message"] == "Updated."


def test_sync_delete_middleware_config() -> None:
    platform = _SyncPlatform()
    platform._client.delete.return_value = httpx.Response(204, request=httpx.Request("DELETE", _mw_url("/my-filter")))

    ExampleResource(cast(NeMoPlatform, platform)).delete_middleware_config(WS, "my-filter")

    platform._client.delete.assert_called_once_with(_mw_url("/my-filter"))


# ---------------------------------------------------------------------------
# middleware config CRUD — async
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_async_create_middleware_config() -> None:
    platform = _AsyncPlatform()
    platform._client.post.return_value = _async_resp(CONFIG_PAYLOAD)

    result = await AsyncExampleResource(cast(AsyncNeMoPlatform, platform)).create_middleware_config(
        WS, "my-filter", blocked_keywords=["bad"]
    )

    platform._client.post.assert_awaited_once_with(_mw_url(), json={"name": "my-filter", "blocked_keywords": ["bad"]})
    assert result["name"] == "my-filter"


@pytest.mark.asyncio
async def test_async_list_middleware_configs() -> None:
    platform = _AsyncPlatform()
    platform._client.get.return_value = _async_resp([CONFIG_PAYLOAD])

    result = await AsyncExampleResource(cast(AsyncNeMoPlatform, platform)).list_middleware_configs(WS)

    platform._client.get.assert_awaited_once_with(_mw_url())
    assert len(result) == 1


@pytest.mark.asyncio
async def test_async_get_middleware_config() -> None:
    platform = _AsyncPlatform()
    platform._client.get.return_value = _async_resp(CONFIG_PAYLOAD)

    result = await AsyncExampleResource(cast(AsyncNeMoPlatform, platform)).get_middleware_config(WS, "my-filter")

    platform._client.get.assert_awaited_once_with(_mw_url("/my-filter"))
    assert result["name"] == "my-filter"


@pytest.mark.asyncio
async def test_async_update_middleware_config() -> None:
    platform = _AsyncPlatform()
    updated = {**CONFIG_PAYLOAD, "block_message": "Updated."}
    platform._client.patch.return_value = _async_resp(updated)

    result = await AsyncExampleResource(cast(AsyncNeMoPlatform, platform)).update_middleware_config(
        WS, "my-filter", block_message="Updated."
    )

    platform._client.patch.assert_awaited_once_with(_mw_url("/my-filter"), json={"block_message": "Updated."})
    assert result["block_message"] == "Updated."


@pytest.mark.asyncio
async def test_async_delete_middleware_config() -> None:
    platform = _AsyncPlatform()
    platform._client.delete.return_value = httpx.Response(204, request=httpx.Request("DELETE", _mw_url("/my-filter")))

    await AsyncExampleResource(cast(AsyncNeMoPlatform, platform)).delete_middleware_config(WS, "my-filter")

    platform._client.delete.assert_awaited_once_with(_mw_url("/my-filter"))
