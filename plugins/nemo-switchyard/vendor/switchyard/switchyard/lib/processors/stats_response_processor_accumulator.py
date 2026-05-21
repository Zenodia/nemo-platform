# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Response processor that records per-model token usage + total latency.

Paired with :class:`StatsRequestProcessor` (chain-start stamp) and
:class:`StatsLLMBackend` (backend-call latency + success / error). All
three share a single :class:`StatsAccumulator`.

This processor is the one that exposes the shared accumulator over HTTP
via :meth:`get_endpoint`.
"""

from __future__ import annotations

import logging
import time
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from switchyard.lib.endpoints.stats_endpoint import StatsEndpoint

from switchyard.lib.backends.stats_llm_backend import STATS_BACKEND_LATENCY_MS_KEY
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
from switchyard.lib.processors.stats_request_processor import STATS_STARTED_AT_KEY
from switchyard.lib.proxy_context import CTX_PROXY_ACTUAL_MODEL, ProxyContext
from switchyard.lib.roles import ResponseProcessor
from switchyard.lib.stats_accumulator import StatsAccumulator

log = logging.getLogger(__name__)


class StatsResponseProcessor(ResponseProcessor):
    """Record token usage + end-to-end latency + routing overhead.

    Works with both :class:`CompletionChatResponse` (records immediately)
    and :class:`StreamingChatResponse` (attaches a lazy tap that fires on
    the final chunk with usage).

    Latency math::

        total_latency_ms   = now - _stats_started_at (stamped by StatsRequestProcessor)
        backend_latency_ms = (stamped by StatsLLMBackend)
        routing_overhead_ms = total_latency_ms - backend_latency_ms

    Backend-call success / error counters are owned by
    :class:`StatsLLMBackend`; this processor only adds token + timing data.
    """

    def __init__(self, accumulator: StatsAccumulator) -> None:
        self._accumulator = accumulator

    def get_endpoint(self) -> StatsEndpoint:
        """Contribute the ``/v1/stats`` endpoint to the server.

        ``NemoSwitchyardServer`` auto-registers this via ``iter_components``.
        """
        from switchyard.lib.endpoints.stats_endpoint import StatsEndpoint

        return StatsEndpoint(self._accumulator)

    async def process(self, ctx: ProxyContext, response: ChatResponse) -> ChatResponse:
        started_at = ctx.metadata.get(STATS_STARTED_AT_KEY)
        backend_latency_ms = ctx.metadata.get(STATS_BACKEND_LATENCY_MS_KEY)
        model = ctx.metadata.get(CTX_PROXY_ACTUAL_MODEL, "<unknown>")
        tier = ctx.metadata.get("_random_routing_tier")

        if isinstance(
            response,
            (CompletionChatResponse, AnthropicChatResponse, ResponsesApiChatResponse),
        ):
            await _record(
                self._accumulator,
                model=model,
                usage=getattr(response.body, "usage", None),
                started_at=started_at,
                backend_latency_ms=backend_latency_ms,
                tier=tier,
            )
            return response

        if isinstance(
            response,
            (
                StreamingChatResponse,
                AnthropicStreamingChatResponse,
                ResponsesApiStreamingChatResponse,
            ),
        ):
            # Streaming: usage only arrives on the final chunk (requires the
            # client to set stream_options.include_usage=True). Record via a
            # tap so we don't buffer the stream ourselves.
            acc = self._accumulator

            async def _tap(chunk: Any) -> None:
                # OpenAI Chat: usage on the final chunk when
                # ``stream_options.include_usage=True``.  Anthropic:
                # ``RawMessageDeltaEvent.usage``.  Responses API: usage
                # is nested under ``ResponseCompletedEvent.response.usage``.
                usage = getattr(chunk, "usage", None)
                if usage is None:
                    inner = getattr(chunk, "response", None)
                    if inner is not None:
                        usage = getattr(inner, "usage", None)
                if usage is None:
                    return
                await _record(
                    acc, model=model, usage=usage,
                    started_at=started_at,
                    backend_latency_ms=backend_latency_ms,
                    tier=tier,
                )

            response.stream.tap(_tap)
            return response

        # Unrecognized response type — no-op on token side (backend still
        # recorded call success / latency via StatsLLMBackend).
        return response


async def _record(
    acc: StatsAccumulator,
    *,
    model: str,
    usage: Any,
    started_at: float | None,
    backend_latency_ms: float | None,
    tier: str | None = None,
) -> None:
    """Pull token fields off an OpenAI- or Anthropic-shaped ``usage`` and record."""
    # OpenAI Chat / Responses use ``prompt_tokens`` / ``completion_tokens``
    # (or ``input_tokens`` / ``output_tokens`` on the Responses surface)
    # with cached counts nested under ``prompt_tokens_details`` /
    # ``input_tokens_details``.  ``prompt_tokens`` already includes
    # cache hits — no summing required.
    #
    # Anthropic uses flat sibling fields ``input_tokens`` (cache *miss*
    # base) plus ``cache_read_input_tokens`` and
    # ``cache_creation_input_tokens``.  The full prompt budget billed
    # for the call is the sum of the three siblings; recording only
    # ``input_tokens`` undercounts (the bug this wiring fixes —
    # see ``test_all_three_cache_buckets_sum_into_prompt_tokens``).
    prompt = 0
    completion = 0
    cached = 0
    cache_creation = 0
    reasoning = 0
    if usage is not None:
        completion = (
            getattr(usage, "completion_tokens", None)
            or getattr(usage, "output_tokens", 0)
            or 0
        )
        prompt_openai = getattr(usage, "prompt_tokens", None)
        if prompt_openai is not None:
            # OpenAI Chat shape — already inclusive of cache hits.
            prompt = prompt_openai or 0
            ptd = getattr(usage, "prompt_tokens_details", None)
            if ptd is not None:
                cached = getattr(ptd, "cached_tokens", 0) or 0
                cache_creation = getattr(ptd, "cache_creation_tokens", 0) or 0
        else:
            base = getattr(usage, "input_tokens", 0) or 0
            # Responses API: cached lives under ``input_tokens_details``.
            itd = getattr(usage, "input_tokens_details", None)
            if itd is not None:
                cached = getattr(itd, "cached_tokens", 0) or 0
            # Anthropic: sibling fields summed into ``prompt`` so the
            # bucket reflects the full billable prompt.
            cache_read = getattr(usage, "cache_read_input_tokens", 0) or 0
            cache_creation_anth = (
                getattr(usage, "cache_creation_input_tokens", 0) or 0
            )
            cached = cached or cache_read
            cache_creation = cache_creation or cache_creation_anth
            prompt = base + cache_read + cache_creation_anth
        ctd = getattr(usage, "completion_tokens_details", None)
        if ctd is not None:
            reasoning = getattr(ctd, "reasoning_tokens", 0) or 0
        else:
            otd = getattr(usage, "output_tokens_details", None)
            if otd is not None:
                reasoning = getattr(otd, "reasoning_tokens", 0) or 0

    total_latency_ms = (
        (time.perf_counter() - started_at) * 1000 if started_at is not None else None
    )
    overhead_ms = None
    if total_latency_ms is not None and backend_latency_ms is not None:
        # Clamp to zero — overhead can round slightly negative due to perf_counter()
        # resolution when the backend dominates the total.
        overhead_ms = max(0.0, total_latency_ms - backend_latency_ms)

    await acc.record_usage(
        model=model,
        prompt_tokens=prompt,
        completion_tokens=completion,
        cached_tokens=cached,
        cache_creation_tokens=cache_creation,
        reasoning_tokens=reasoning,
        total_latency_ms=total_latency_ms,
        routing_overhead_ms=overhead_ms,
        tier=tier,
    )
