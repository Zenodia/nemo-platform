# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Minimal LLM client wrapper for backends.

This provides a thin wrapper around the OpenAI SDK to support
OpenAI-compatible backends in the chain.
"""

from __future__ import annotations

from typing import Any

from openai import AsyncOpenAI, OpenAI

from switchyard.telemetry import get_telemetry_headers


class OpenAILLMClient:
    """Client that wraps the official OpenAI Python SDK.

    Works with any OpenAI-compatible API (OpenAI, NVIDIA NIM, Azure,
    vLLM, etc.) by accepting a custom ``base_url``.

    Used by :class:`~switchyard.lib.backends.openai_llm_backend.OpenAILLMBackend`
    and other OpenAI-compatible backends.
    """

    client: OpenAI
    async_client: AsyncOpenAI

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
        timeout: float | None = None,
    ) -> None:
        """Initialize the OpenAI client pair.

        Args:
            api_key: API key for authentication. If not provided, falls back
                to OPENAI_API_KEY environment variable.
            base_url: Custom base URL for OpenAI-compatible APIs (e.g.,
                Azure, vLLM, NVIDIA NIM). Defaults to OpenAI's standard URL.
            timeout: Request timeout in seconds. None means no timeout.
        """
        client_kwargs: dict[str, Any] = {}
        if api_key:
            client_kwargs["api_key"] = api_key
        if base_url:
            client_kwargs["base_url"] = base_url
        if timeout is not None:
            client_kwargs["timeout"] = timeout
        client_kwargs["default_headers"] = get_telemetry_headers()

        self.client = OpenAI(**client_kwargs)
        self.async_client = AsyncOpenAI(**client_kwargs)

    async def acompletion(self, **kwargs: Any) -> Any:
        """Async wrapper for chat completions.

        Delegates to the underlying AsyncOpenAI client's chat.completions.create.
        """
        return await self.async_client.chat.completions.create(**kwargs)
