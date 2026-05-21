# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""ResponseProcessor that records per-model token usage into a LiveStatsCollector.

This is the single stats-recording mechanism for the chain when using
LiveStatsCollector (vs StatsAccumulator). It is format-agnostic (handles
Anthropic Messages, OpenAI Chat Completions, and OpenAI Responses API)
and routing-policy-agnostic (works with any LLMBackend).

Model attribution uses ``ctx.metadata["_proxy_actual_model"]`` which
every backend writes before returning its response. Tier labelling
uses ``ctx.metadata["_random_routing_tier"]`` (written by
RandomRoutingLLMBackend) and defaults to ``""`` for single-backend chains.

The processor exposes ``get_routing_stats()`` / ``reset_routing_stats()``
and ``get_endpoint()`` so the chain's app factory can mount a live stats
endpoint at ``GET /v1/routing/stats`` with no extra wiring.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from anthropic.types import RawMessageStreamEvent

from switchyard.lib.chat_response.anthropic import (
    AnthropicChatResponse,
    AnthropicStreamingChatResponse,
)
from switchyard.lib.chat_response.base import ChatResponse
from switchyard.lib.chat_response.openai_chat import (
    CompletionChatResponse,
    StreamingChatResponse,
)
from switchyard.lib.chat_response.openai_responses import (
    ResponsesApiChatResponse,
    ResponsesApiStreamingChatResponse,
)
from switchyard.lib.live_stats_collector import LiveStatsCollector
from switchyard.lib.proxy_context import ProxyContext
from switchyard.lib.roles import ResponseProcessor

if TYPE_CHECKING:
    from switchyard.lib.endpoints.base import Endpoint


class StatsResponseProcessor(ResponseProcessor):
    """Records token usage after each LLM call into a :class:`LiveStatsCollector`.

    Non-streaming responses: reads usage directly from the response body.

    Streaming responses: attaches a lightweight tap to the stream so
    usage-carrying events update the collector as they flow through —
    no buffering, zero impact on streaming latency.

    Supported response types
    ------------------------
    * :class:`AnthropicChatResponse` — non-streaming Anthropic
    * :class:`AnthropicStreamingChatResponse` — streaming Anthropic SSE
    * :class:`CompletionChatResponse` — non-streaming OpenAI Chat
    * :class:`StreamingChatResponse` — streaming OpenAI Chat
    * :class:`ResponsesApiChatResponse` — non-streaming OpenAI Responses
    * :class:`ResponsesApiStreamingChatResponse` — streaming OpenAI Responses
    """

    def __init__(
        self,
        collector: LiveStatsCollector,
        *,
        expose_endpoint: bool = True,
    ) -> None:
        self._collector = collector
        self._expose_endpoint = expose_endpoint

    async def process(self, ctx: ProxyContext, response: ChatResponse) -> ChatResponse:
        model: str = ctx.metadata.get("_proxy_actual_model", "unknown")
        tier: str = ctx.metadata.get("_random_routing_tier", "")

        if isinstance(response, AnthropicChatResponse):
            _record_anthropic(response, model, tier, self._collector)
        elif isinstance(response, AnthropicStreamingChatResponse):
            _attach_anthropic_tap(response, model, tier, self._collector)
        elif isinstance(response, CompletionChatResponse):
            _record_openai_chat(response, model, tier, self._collector)
        elif isinstance(response, StreamingChatResponse):
            _attach_openai_chat_tap(response, model, tier, self._collector)
        elif isinstance(response, ResponsesApiChatResponse):
            _record_openai_responses(response, model, tier, self._collector)
        elif isinstance(response, ResponsesApiStreamingChatResponse):
            _attach_openai_responses_tap(response, model, tier, self._collector)
        return response

    # ------------------------------------------------------------------
    # HTTP stats endpoint integration
    # ------------------------------------------------------------------

    def get_routing_stats(self) -> dict[str, object]:
        """Return a snapshot of accumulated per-model statistics."""
        return self._collector.to_dict()

    def reset_routing_stats(self) -> None:
        """Reset all accumulated statistics to zero."""
        self._collector.reset()

    def get_endpoint(self) -> Endpoint | None:
        """Contribute ``GET /v1/routing/stats`` to the server."""
        if not self._expose_endpoint:
            return None
        from switchyard.lib.endpoints.stats_endpoint import (
            StatsEndpoint,
        )

        return StatsEndpoint(self._collector)


# ---------------------------------------------------------------------------
# Non-streaming extractors
# ---------------------------------------------------------------------------


def _record_anthropic(
    response: AnthropicChatResponse,
    model: str,
    tier: str,
    collector: LiveStatsCollector,
) -> None:
    u = response.body.usage
    if not u:
        return
    input_tok = getattr(u, "input_tokens", 0) or 0
    cache_create = getattr(u, "cache_creation_input_tokens", 0) or 0
    cache_read = getattr(u, "cache_read_input_tokens", 0) or 0
    completion = getattr(u, "output_tokens", 0) or 0
    collector.record(
        model, tier,
        prompt_tokens=input_tok + cache_create + cache_read,
        completion_tokens=completion,
        cache_read_tokens=cache_read,
        cache_creation_tokens=cache_create,
    )


def _record_openai_chat(
    response: CompletionChatResponse,
    model: str,
    tier: str,
    collector: LiveStatsCollector,
) -> None:
    u = getattr(response.body, "usage", None)
    if u is None:
        return
    prompt = getattr(u, "prompt_tokens", 0) or 0
    completion = getattr(u, "completion_tokens", 0) or 0
    reasoning = 0
    cached = 0
    if (details := getattr(u, "completion_tokens_details", None)) is not None:
        reasoning = getattr(details, "reasoning_tokens", 0) or 0
    if (prompt_details := getattr(u, "prompt_tokens_details", None)) is not None:
        cached = getattr(prompt_details, "cached_tokens", 0) or 0
    collector.record(
        model, tier,
        prompt_tokens=prompt,
        completion_tokens=completion,
        reasoning_tokens=reasoning,
        cache_read_tokens=cached,
    )


def _record_openai_responses(
    response: ResponsesApiChatResponse,
    model: str,
    tier: str,
    collector: LiveStatsCollector,
) -> None:
    u = getattr(response.body, "usage", None)
    if u is None:
        return
    prompt = getattr(u, "input_tokens", 0) or 0
    completion = getattr(u, "output_tokens", 0) or 0
    reasoning = 0
    cached = 0
    if (out_details := getattr(u, "output_tokens_details", None)) is not None:
        reasoning = getattr(out_details, "reasoning_tokens", 0) or 0
    if (in_details := getattr(u, "input_tokens_details", None)) is not None:
        cached = getattr(in_details, "cached_tokens", 0) or 0
    collector.record(
        model, tier,
        prompt_tokens=prompt,
        completion_tokens=completion,
        reasoning_tokens=reasoning,
        cache_read_tokens=cached,
    )


# ---------------------------------------------------------------------------
# Streaming tap installers
# ---------------------------------------------------------------------------


def _attach_anthropic_tap(
    response: AnthropicStreamingChatResponse,
    model: str,
    tier: str,
    collector: LiveStatsCollector,
) -> None:
    """Register a tap that accumulates Anthropic SSE usage."""
    acc: dict[str, int] = {
        "input_tokens": 0,
        "output_tokens": 0,
        "cache_creation_input_tokens": 0,
        "cache_read_input_tokens": 0,
    }
    committed = False

    def _merge(usage: object) -> None:
        for key in acc:
            value = getattr(usage, key, None)
            if isinstance(value, int):
                acc[key] = value

    async def _tap(event: RawMessageStreamEvent) -> None:
        nonlocal committed
        if committed:
            return
        event_type = getattr(event, "type", None)
        if event_type == "message_start":
            msg = getattr(event, "message", None)
            if msg is not None:
                usage = getattr(msg, "usage", None)
                if usage is not None:
                    _merge(usage)
        elif event_type == "message_delta":
            usage = getattr(event, "usage", None)
            if usage is not None:
                _merge(usage)
        elif event_type == "message_stop":
            input_tok = acc["input_tokens"]
            cache_create = acc["cache_creation_input_tokens"]
            cache_read = acc["cache_read_input_tokens"]
            completion = acc["output_tokens"]
            collector.record(
                model, tier,
                prompt_tokens=input_tok + cache_create + cache_read,
                completion_tokens=completion,
                cache_read_tokens=cache_read,
                cache_creation_tokens=cache_create,
            )
            committed = True

    response.stream.tap(_tap)


def _attach_openai_chat_tap(
    response: StreamingChatResponse,
    model: str,
    tier: str,
    collector: LiveStatsCollector,
) -> None:
    """Register a tap for OpenAI Chat streaming usage."""
    seen = False

    async def _tap(chunk) -> None:  # type: ignore[no-untyped-def]
        nonlocal seen
        if seen:
            return
        u = getattr(chunk, "usage", None)
        if u is None:
            return
        prompt = getattr(u, "prompt_tokens", 0) or 0
        completion = getattr(u, "completion_tokens", 0) or 0
        reasoning = 0
        cached = 0
        if (details := getattr(u, "completion_tokens_details", None)) is not None:
            reasoning = getattr(details, "reasoning_tokens", 0) or 0
        if (prompt_details := getattr(u, "prompt_tokens_details", None)) is not None:
            cached = getattr(prompt_details, "cached_tokens", 0) or 0
        collector.record(
            model, tier,
            prompt_tokens=prompt,
            completion_tokens=completion,
            reasoning_tokens=reasoning,
            cache_read_tokens=cached,
        )
        seen = True

    response.stream.tap(_tap)


def _attach_openai_responses_tap(
    response: ResponsesApiStreamingChatResponse,
    model: str,
    tier: str,
    collector: LiveStatsCollector,
) -> None:
    """Register a tap for OpenAI Responses API streaming usage."""
    seen = False

    async def _tap(event) -> None:  # type: ignore[no-untyped-def]
        nonlocal seen
        if seen:
            return
        inner = getattr(event, "response", None)
        if inner is None:
            return
        u = getattr(inner, "usage", None)
        if u is None:
            return
        prompt = getattr(u, "input_tokens", 0) or 0
        completion = getattr(u, "output_tokens", 0) or 0
        reasoning = 0
        cached = 0
        if (out_details := getattr(u, "output_tokens_details", None)) is not None:
            reasoning = getattr(out_details, "reasoning_tokens", 0) or 0
        if (in_details := getattr(u, "input_tokens_details", None)) is not None:
            cached = getattr(in_details, "cached_tokens", 0) or 0
        collector.record(
            model, tier,
            prompt_tokens=prompt,
            completion_tokens=completion,
            reasoning_tokens=reasoning,
            cache_read_tokens=cached,
        )
        seen = True

    response.stream.tap(_tap)
