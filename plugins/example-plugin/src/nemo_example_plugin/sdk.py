# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""SDK resources for the example plugin."""

from __future__ import annotations

from typing import Any

from nemo_platform import AsyncNeMoPlatform, NeMoPlatform
from nemo_platform_plugin.sdk import NemoPluginSDKResources


class ExampleResource:
    """Sync SDK namespace mounted as ``client.example``."""

    def __init__(self, platform: NeMoPlatform) -> None:
        self._platform = platform
        self._http_client = platform._client

    # ------------------------------------------------------------------
    # Hello
    # ------------------------------------------------------------------

    def hello(self, name: str) -> str:
        response = self._http_client.get(self._example_url(f"/hello/{name}"))
        response.raise_for_status()
        payload: dict[str, Any] = response.json()
        return str(payload["message"])

    # ------------------------------------------------------------------
    # Middleware configs CRUD
    # ------------------------------------------------------------------

    def create_middleware_config(
        self,
        workspace: str,
        name: str,
        blocked_keywords: list[str] | None = None,
        block_message: str | None = None,
    ) -> dict[str, Any]:
        """Create an :class:`~nemo_example_plugin.middleware_config.ExampleMiddlewareConfig`."""
        body: dict[str, Any] = {"name": name}
        if blocked_keywords is not None:
            body["blocked_keywords"] = blocked_keywords
        if block_message is not None:
            body["block_message"] = block_message
        response = self._http_client.post(self._workspace_url(workspace, "/middleware-configs"), json=body)
        response.raise_for_status()
        return response.json()

    def list_middleware_configs(self, workspace: str) -> list[dict[str, Any]]:
        """List all middleware configs in *workspace*."""
        response = self._http_client.get(self._workspace_url(workspace, "/middleware-configs"))
        response.raise_for_status()
        return response.json()

    def get_middleware_config(self, workspace: str, name: str) -> dict[str, Any]:
        """Get a single middleware config by *name*."""
        response = self._http_client.get(self._workspace_url(workspace, f"/middleware-configs/{name}"))
        response.raise_for_status()
        return response.json()

    def update_middleware_config(
        self,
        workspace: str,
        name: str,
        blocked_keywords: list[str] | None = None,
        block_message: str | None = None,
    ) -> dict[str, Any]:
        """Partially update a middleware config."""
        body: dict[str, Any] = {}
        if blocked_keywords is not None:
            body["blocked_keywords"] = blocked_keywords
        if block_message is not None:
            body["block_message"] = block_message
        response = self._http_client.patch(self._workspace_url(workspace, f"/middleware-configs/{name}"), json=body)
        response.raise_for_status()
        return response.json()

    def delete_middleware_config(self, workspace: str, name: str) -> None:
        """Delete a middleware config."""
        response = self._http_client.delete(self._workspace_url(workspace, f"/middleware-configs/{name}"))
        response.raise_for_status()

    # ------------------------------------------------------------------
    # URL helpers
    # ------------------------------------------------------------------

    def _example_url(self, path: str) -> str:
        return str(self._platform.base_url).rstrip("/") + "/apis/example" + path

    def _workspace_url(self, workspace: str, path: str) -> str:
        return self._example_url(f"/v2/workspaces/{workspace}{path}")


class AsyncExampleResource:
    """Async SDK namespace mounted as ``client.example``."""

    def __init__(self, platform: AsyncNeMoPlatform) -> None:
        self._platform = platform
        self._http_client = platform._client

    # ------------------------------------------------------------------
    # Hello
    # ------------------------------------------------------------------

    async def hello(self, name: str) -> str:
        response = await self._http_client.get(self._example_url(f"/hello/{name}"))
        response.raise_for_status()
        payload: dict[str, Any] = response.json()
        return str(payload["message"])

    # ------------------------------------------------------------------
    # Middleware configs CRUD
    # ------------------------------------------------------------------

    async def create_middleware_config(
        self,
        workspace: str,
        name: str,
        blocked_keywords: list[str] | None = None,
        block_message: str | None = None,
    ) -> dict[str, Any]:
        """Create an :class:`~nemo_example_plugin.middleware_config.ExampleMiddlewareConfig`."""
        body: dict[str, Any] = {"name": name}
        if blocked_keywords is not None:
            body["blocked_keywords"] = blocked_keywords
        if block_message is not None:
            body["block_message"] = block_message
        response = await self._http_client.post(self._workspace_url(workspace, "/middleware-configs"), json=body)
        response.raise_for_status()
        return response.json()

    async def list_middleware_configs(self, workspace: str) -> list[dict[str, Any]]:
        """List all middleware configs in *workspace*."""
        response = await self._http_client.get(self._workspace_url(workspace, "/middleware-configs"))
        response.raise_for_status()
        return response.json()

    async def get_middleware_config(self, workspace: str, name: str) -> dict[str, Any]:
        """Get a single middleware config by *name*."""
        response = await self._http_client.get(self._workspace_url(workspace, f"/middleware-configs/{name}"))
        response.raise_for_status()
        return response.json()

    async def update_middleware_config(
        self,
        workspace: str,
        name: str,
        blocked_keywords: list[str] | None = None,
        block_message: str | None = None,
    ) -> dict[str, Any]:
        """Partially update a middleware config."""
        body: dict[str, Any] = {}
        if blocked_keywords is not None:
            body["blocked_keywords"] = blocked_keywords
        if block_message is not None:
            body["block_message"] = block_message
        response = await self._http_client.patch(
            self._workspace_url(workspace, f"/middleware-configs/{name}"), json=body
        )
        response.raise_for_status()
        return response.json()

    async def delete_middleware_config(self, workspace: str, name: str) -> None:
        """Delete a middleware config."""
        response = await self._http_client.delete(self._workspace_url(workspace, f"/middleware-configs/{name}"))
        response.raise_for_status()

    # ------------------------------------------------------------------
    # URL helpers
    # ------------------------------------------------------------------

    def _example_url(self, path: str) -> str:
        return str(self._platform.base_url).rstrip("/") + "/apis/example" + path

    def _workspace_url(self, workspace: str, path: str) -> str:
        return self._example_url(f"/v2/workspaces/{workspace}{path}")


example_sdk_resources = NemoPluginSDKResources(
    sync_resource=ExampleResource,
    async_resource=AsyncExampleResource,
)
