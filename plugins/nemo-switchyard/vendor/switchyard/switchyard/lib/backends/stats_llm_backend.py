# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Backend wrapper that records backend-call latency + errors into stats.

idiomatic composition — wraps any :class:`LLMBackend` and attributes
the wrapped backend's call duration to the routed model in the shared
:class:`StatsAccumulator`. Lets :class:`StatsResponseProcessor` compute
``routing_overhead = total_latency - backend_latency`` without reaching
into the base backend.
"""

from __future__ import annotations

import time

from switchyard.lib.chat_request.anthropic import AnthropicChatRequest
from switchyard.lib.chat_request.base import ChatRequest, ChatRequestType
from switchyard.lib.chat_request.openai_chat import OpenAIChatRequest
from switchyard.lib.chat_request.openai_responses import ResponsesChatRequest
from switchyard.lib.chat_response.base import ChatResponse
from switchyard.lib.proxy_context import CTX_PROXY_ACTUAL_MODEL, ProxyContext
from switchyard.lib.roles import LLMBackend
from switchyard.lib.stats_accumulator import StatsAccumulator

# ctx.metadata key: backend latency in ms (for ResponseProcessor to read).
STATS_BACKEND_LATENCY_MS_KEY = "_stats_backend_latency_ms"


class StatsLLMBackend(LLMBackend):
    """Wrap another backend; record success/error + backend latency per model.

    The wrapper is transparent to the chain — it delegates
    :attr:`supported_request_types` and :meth:`call` to the inner backend.
    """

    def __init__(self, inner: LLMBackend, accumulator: StatsAccumulator) -> None:
        self._inner = inner
        self._accumulator = accumulator

    @property
    def supported_request_types(self) -> list[ChatRequestType]:
        return self._inner.supported_request_types

    async def call(self, ctx: ProxyContext, request: ChatRequest) -> ChatResponse:
        model = _request_model(request)
        start = time.perf_counter()
        try:
            response = await self._inner.call(ctx, request)
        except Exception:
            # On error, use the actual model that was routed (if available),
            # not the client-provided model. MultiLLMBackend rewrites the model
            # in the request body before calling the inner backend, so we prefer
            # CTX_PROXY_ACTUAL_MODEL if set (which means routing happened).
            actual_model = ctx.metadata.get(CTX_PROXY_ACTUAL_MODEL) or model
            tier = ctx.metadata.get("_random_routing_tier")
            await self._accumulator.record_error(model=actual_model, tier=tier)
            raise

        backend_latency_ms = (time.perf_counter() - start) * 1000
        ctx.metadata[STATS_BACKEND_LATENCY_MS_KEY] = backend_latency_ms

        # Pull the actual model name the inner backend resolved (overrides
        # may have happened — the base backend writes the resolved model name
        # to ctx.metadata[CTX_PROXY_ACTUAL_MODEL]).
        actual_model = ctx.metadata.get(CTX_PROXY_ACTUAL_MODEL) or model
        tier = ctx.metadata.get("_random_routing_tier")
        await self._accumulator.record_success(
            model=actual_model, backend_latency_ms=backend_latency_ms, tier=tier,
        )
        return response

    def get_endpoint(self) -> object | None:
        """Forward to inner backend's endpoint if it has one.

        Preserves tier-aware routing stats endpoints (e.g., RoutingStatsEndpoint
        from RandomRoutingLLMBackend) when StatsLLMBackend wraps a backend that
        contributes an endpoint.
        """
        inner_ep = getattr(self._inner, "get_endpoint", None)
        if inner_ep is not None:
            return inner_ep()  # type: ignore[no-any-return]
        return None


def _request_model(request: ChatRequest) -> str:
    """Return the request's model label for stats/error attribution."""
    if isinstance(request, (AnthropicChatRequest, OpenAIChatRequest, ResponsesChatRequest)):
        return str(request.body.get("model", "<unknown>"))
    return "<unknown>"
