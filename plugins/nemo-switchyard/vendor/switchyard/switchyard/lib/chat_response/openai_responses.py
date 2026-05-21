# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""OpenAI Responses API response types and stream wrapper."""

from __future__ import annotations

import logging
from collections.abc import AsyncIterator, Awaitable, Callable

from openai.types.responses import Response as OpenAIResponse
from openai.types.responses import ResponseStreamEvent

from switchyard.lib.chat_response.base import ChatResponse, ChatResponseType

log = logging.getLogger(__name__)


class ResponsesApiChatResponse(ChatResponse):
    """Non-streaming response wrapping the OpenAI SDK's ``Response``.

    Direct access to SDK-typed fields — ``response.body.output``,
    ``response.body.usage``, ``response.body.model``,
    ``response.body.previous_response_id`` — with full autocomplete
    and type checking.
    """

    def __init__(self, body: OpenAIResponse) -> None:
        self._body = body

    @property
    def response_type(self) -> ChatResponseType:
        return ChatResponseType.RESPONSES_API_COMPLETION

    @property
    def body(self) -> OpenAIResponse:
        return self._body


class ResponsesApiStreamingChatResponse(ChatResponse):
    """Streaming response wrapping a ``ResponsesApiStream``.

    Same composable tap/map pattern as ``ResponseStream``, but typed
    for ``ResponseStreamEvent`` from the OpenAI Responses API.
    """

    def __init__(self, stream: ResponsesApiStream) -> None:
        self._stream = stream

    @property
    def response_type(self) -> ChatResponseType:
        return ChatResponseType.RESPONSES_API_STREAM

    @property
    def stream(self) -> ResponsesApiStream:
        return self._stream


class ResponsesApiStream:
    """Composable wrapper around ``AsyncIterator[ResponseStreamEvent]``.

    Same design as ``ResponseStream`` but typed for the OpenAI Responses
    API's streaming event types (``ResponseTextDeltaEvent``,
    ``ResponseCompletedEvent``, etc.).

    Taps fire **before** maps on each event.  A failing tap is
    quarantined.  Single-consume.
    """

    __slots__ = ("_source", "_taps", "_maps", "_on_complete", "_consumed")

    def __init__(self, source: AsyncIterator[ResponseStreamEvent]) -> None:
        self._source = source
        self._taps: list[Callable[[ResponseStreamEvent], Awaitable[None]]] = []
        self._maps: list[
            Callable[[ResponseStreamEvent], Awaitable[ResponseStreamEvent]]
        ] = []
        self._on_complete: list[Callable[[], Awaitable[None]]] = []
        self._consumed = False

    def tap(
        self, callback: Callable[[ResponseStreamEvent], Awaitable[None]]
    ) -> ResponsesApiStream:
        """Register a callback that observes every event (logging, metrics).

        Returns ``self`` for fluent chaining.
        """
        self._taps.append(callback)
        return self

    def map(
        self, fn: Callable[[ResponseStreamEvent], Awaitable[ResponseStreamEvent]]
    ) -> ResponsesApiStream:
        """Register a transform applied to every event.

        Returns ``self`` for fluent chaining.
        """
        self._maps.append(fn)
        return self

    def on_complete(
        self, callback: Callable[[], Awaitable[None]]
    ) -> ResponsesApiStream:
        """Register a callback that runs after the stream drains normally."""
        self._on_complete.append(callback)
        return self

    async def __aiter__(self) -> AsyncIterator[ResponseStreamEvent]:
        if self._consumed:
            raise RuntimeError("ResponsesApiStream has already been consumed")
        self._consumed = True

        failed_taps: set[int] = set()
        completed = False

        try:
            async for event in self._source:
                for i, tap_fn in enumerate(self._taps):
                    if i in failed_taps:
                        continue
                    try:
                        await tap_fn(event)
                    except Exception:
                        failed_taps.add(i)
                        log.exception("ResponsesApiStream tap failed, quarantining")

                for map_fn in self._maps:
                    event = await map_fn(event)

                yield event
            completed = True
        finally:
            if completed:
                for callback in self._on_complete:
                    try:
                        await callback()
                    except Exception:
                        log.exception("ResponsesApiStream completion callback failed")
