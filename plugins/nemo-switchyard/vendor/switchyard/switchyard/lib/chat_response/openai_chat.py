# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""OpenAI Chat Completions response types and stream wrapper."""

from __future__ import annotations

import logging
from collections.abc import AsyncIterator, Awaitable, Callable

from openai.types.chat import ChatCompletion, ChatCompletionChunk

from switchyard.lib.chat_response.base import ChatResponse, ChatResponseType

log = logging.getLogger(__name__)


class CompletionChatResponse(ChatResponse):
    """Non-streaming response wrapping the OpenAI SDK's ``ChatCompletion``.

    Direct access to SDK-typed fields — ``response.body.choices``,
    ``response.body.usage``, ``response.body.model`` — with full
    autocomplete and type checking.
    """

    def __init__(self, body: ChatCompletion) -> None:
        self._body = body

    @property
    def response_type(self) -> ChatResponseType:
        return ChatResponseType.COMPLETION

    @property
    def body(self) -> ChatCompletion:
        return self._body


class StreamingChatResponse(ChatResponse):
    """Streaming response wrapping a ``ResponseStream``.

    The ``ResponseStream`` provides composable tap (observe) and map
    (transform) operations that execute lazily as chunks flow through.
    Single-consume — the stream can only be iterated once.
    """

    def __init__(self, stream: ResponseStream) -> None:
        self._stream = stream

    @property
    def response_type(self) -> ChatResponseType:
        return ChatResponseType.STREAM

    @property
    def stream(self) -> ResponseStream:
        return self._stream


class ResponseStream:
    """Composable wrapper around ``AsyncIterator[ChatCompletionChunk]``.

    Processors register taps (observe) and maps (transform) that fire
    lazily as chunks flow through.  Multiple processors can attach their
    taps without buffering the entire stream.

    Taps fire **before** maps on each chunk — logging taps always see
    the untransformed data.  Maps compose left-to-right: the output of
    map N is the input to map N+1.

    A failing tap is quarantined after its first exception and never
    called again, so one bad observer cannot break the stream.

    Single-consume — iterating a second time raises ``RuntimeError``.
    """

    __slots__ = ("_source", "_taps", "_maps", "_on_complete", "_consumed")

    def __init__(self, source: AsyncIterator[ChatCompletionChunk]) -> None:
        self._source = source
        self._taps: list[Callable[[ChatCompletionChunk], Awaitable[None]]] = []
        self._maps: list[
            Callable[[ChatCompletionChunk], Awaitable[ChatCompletionChunk]]
        ] = []
        self._on_complete: list[Callable[[], Awaitable[None]]] = []
        self._consumed = False

    def tap(
        self, callback: Callable[[ChatCompletionChunk], Awaitable[None]]
    ) -> ResponseStream:
        """Register a callback that observes every chunk (logging, metrics).

        Returns ``self`` for fluent chaining.
        """
        self._taps.append(callback)
        return self

    def map(
        self, fn: Callable[[ChatCompletionChunk], Awaitable[ChatCompletionChunk]]
    ) -> ResponseStream:
        """Register a transform applied to every chunk (translation, filtering).

        Returns ``self`` for fluent chaining.
        """
        self._maps.append(fn)
        return self

    def on_complete(self, callback: Callable[[], Awaitable[None]]) -> ResponseStream:
        """Register a callback that runs after the stream drains normally.

        Completion callbacks are not invoked if iteration fails or is cancelled,
        which keeps partial/error turns out of downstream logging sinks.
        """
        self._on_complete.append(callback)
        return self

    async def __aiter__(self) -> AsyncIterator[ChatCompletionChunk]:
        if self._consumed:
            raise RuntimeError("ResponseStream has already been consumed")
        self._consumed = True

        failed_taps: set[int] = set()
        completed = False

        try:
            async for chunk in self._source:
                for i, tap_fn in enumerate(self._taps):
                    if i in failed_taps:
                        continue
                    try:
                        await tap_fn(chunk)
                    except Exception:
                        failed_taps.add(i)
                        log.exception("ResponseStream tap failed, quarantining")

                for map_fn in self._maps:
                    chunk = await map_fn(chunk)

                yield chunk
            completed = True
        finally:
            if completed:
                for callback in self._on_complete:
                    try:
                        await callback()
                    except Exception:
                        log.exception("ResponseStream completion callback failed")
