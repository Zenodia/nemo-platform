# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Anthropic Messages API response types and stream wrapper."""

from __future__ import annotations

import logging
from collections.abc import AsyncIterator, Awaitable, Callable

from anthropic.types import Message as AnthropicMessage
from anthropic.types import RawMessageStreamEvent

from switchyard.lib.chat_response.base import ChatResponse, ChatResponseType

log = logging.getLogger(__name__)


class AnthropicChatResponse(ChatResponse):
    """Non-streaming response wrapping the Anthropic SDK's ``Message``.

    Direct access to SDK-typed fields — ``response.body.content``,
    ``response.body.usage``, ``response.body.model``, ``response.body.stop_reason``
    — with full autocomplete and type checking.
    """

    def __init__(self, body: AnthropicMessage) -> None:
        self._body = body

    @property
    def response_type(self) -> ChatResponseType:
        return ChatResponseType.ANTHROPIC_COMPLETION

    @property
    def body(self) -> AnthropicMessage:
        return self._body


class AnthropicStreamingChatResponse(ChatResponse):
    """Streaming response wrapping an ``AnthropicResponseStream``.

    Same composable tap/map pattern as ``ResponseStream``, but typed
    for ``RawMessageStreamEvent`` chunks from the Anthropic SDK.
    """

    def __init__(self, stream: AnthropicResponseStream) -> None:
        self._stream = stream

    @property
    def response_type(self) -> ChatResponseType:
        return ChatResponseType.ANTHROPIC_STREAM

    @property
    def stream(self) -> AnthropicResponseStream:
        return self._stream


class AnthropicResponseStream:
    """Composable wrapper around ``AsyncIterator[RawMessageStreamEvent]``.

    Same design as ``ResponseStream`` but typed for Anthropic's streaming
    event types (``RawMessageStartEvent``, ``RawContentBlockDeltaEvent``,
    etc.).

    Taps fire **before** maps on each event.  A failing tap is
    quarantined.  Single-consume.
    """

    __slots__ = ("_source", "_taps", "_maps", "_on_complete", "_consumed")

    def __init__(self, source: AsyncIterator[RawMessageStreamEvent]) -> None:
        self._source = source
        self._taps: list[Callable[[RawMessageStreamEvent], Awaitable[None]]] = []
        self._maps: list[
            Callable[[RawMessageStreamEvent], Awaitable[RawMessageStreamEvent]]
        ] = []
        self._on_complete: list[Callable[[], Awaitable[None]]] = []
        self._consumed = False

    def tap(
        self, callback: Callable[[RawMessageStreamEvent], Awaitable[None]]
    ) -> AnthropicResponseStream:
        """Register a callback that observes every event (logging, metrics).

        Returns ``self`` for fluent chaining.
        """
        self._taps.append(callback)
        return self

    def map(
        self, fn: Callable[[RawMessageStreamEvent], Awaitable[RawMessageStreamEvent]]
    ) -> AnthropicResponseStream:
        """Register a transform applied to every event.

        Returns ``self`` for fluent chaining.
        """
        self._maps.append(fn)
        return self

    def on_complete(
        self, callback: Callable[[], Awaitable[None]]
    ) -> AnthropicResponseStream:
        """Register a callback that runs after the stream drains normally."""
        self._on_complete.append(callback)
        return self

    async def __aiter__(self) -> AsyncIterator[RawMessageStreamEvent]:
        if self._consumed:
            raise RuntimeError("AnthropicResponseStream has already been consumed")
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
                        log.exception("AnthropicResponseStream tap failed, quarantining")

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
                        log.exception("AnthropicResponseStream completion callback failed")
