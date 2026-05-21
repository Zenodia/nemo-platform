# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Role ABCs for the strategy chain.

Four roles enforce the chain shape::

    [RequestProcessor*] → LLMBackend → [ResponseProcessor*] → ResponseTranslator

All methods are async-only. If you need sync, use ``asyncio.run()``.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import AsyncIterable, Mapping
from typing import TypeAlias

from anthropic.types import Message as AnthropicMessage
from anthropic.types import RawMessageStreamEvent
from openai.types.chat import ChatCompletion, ChatCompletionChunk
from openai.types.responses import Response as OpenAIResponse
from openai.types.responses import ResponseStreamEvent

from switchyard.lib.chat_request.base import ChatRequest, ChatRequestType
from switchyard.lib.chat_response.base import ChatResponse
from switchyard.lib.proxy_context import ProxyContext

# The final translated response surfaced by ResponseTranslator.translate().
# Union covers all three formats × (non-streaming | streaming) plus the
# dict-returning converters (Anthropic/Responses synthesize plain dicts
# today — their internals are Tier-C work).
TranslatedStream: TypeAlias = (
    AsyncIterable[ChatCompletionChunk]
    | AsyncIterable[RawMessageStreamEvent]
    | AsyncIterable[ResponseStreamEvent]
    | AsyncIterable[Mapping[str, object]]
    | AsyncIterable[str]
)

TranslatedResponse: TypeAlias = (
    ChatCompletion
    | OpenAIResponse
    | AnthropicMessage
    | Mapping[str, object]
    | TranslatedStream
)


class RequestProcessor(ABC):
    """Pre-processes requests before the LLM call.

    Receives and returns ``ChatRequest`` (any subclass).
    Format-agnostic processors work with the abstract base;
    format-specific ones use ``isinstance`` or the translation engine.

    Lifecycle:

    * ``startup()`` — optional async hook. Callers (the IGW shim, the
      FastAPI lifespan) MUST ``await`` it once after construction and
      before the first request. Default no-op.
    * ``shutdown()`` — optional async hook. Callers MUST ``await`` it once
      before discarding the processor. Default no-op.

    Processors that load expensive resources (classifiers, large HTTP
    clients, background pollers) should acquire/release them through
    :class:`~switchyard.lib.resource_cache.ResourceCache`
    in these hooks so multiple processors with the same config share one
    copy.
    """

    @abstractmethod
    async def process(self, ctx: ProxyContext, request: ChatRequest) -> ChatRequest: ...

    async def startup(self) -> None:  # noqa: B027  # default no-op is the contract
        """Optional async startup hook. Default no-op."""

    async def shutdown(self) -> None:  # noqa: B027  # default no-op is the contract
        """Optional async shutdown hook. Default no-op."""


class LLMBackend(ABC):
    """Makes the actual LLM call.  Exactly one per chain.

    Receives ``ChatRequest``, returns ``ChatResponse``.  The backend
    wraps its SDK output into ``CompletionChatResponse`` or
    ``StreamingChatResponse`` (or Anthropic/Responses API variants).
    Uses the translation engine to convert the request to its native
    format if needed.

    Each concrete backend declares the request formats it accepts via
    :attr:`supported_request_types`.  The first line of ``call()``
    should normalize the inbound request to any of those formats via
    :meth:`ChatRequestTranslationEngine.to_any_of` — passthrough when
    already supported, translate to the first listed preference
    otherwise.
    """

    @property
    @abstractmethod
    def supported_request_types(self) -> list[ChatRequestType]:
        """Ordered preference of ``ChatRequest`` formats this backend accepts.

        Passthrough always wins when the inbound request's type is in
        the list.  When it isn't,
        :meth:`ChatRequestTranslationEngine.to_any_of` translates to the
        first element.  Most backends return a single-element list (they
        speak one wire format); multi-format backends return several in
        preference order.
        """

    @abstractmethod
    async def call(self, ctx: ProxyContext, request: ChatRequest) -> ChatResponse: ...


class ResponseProcessor(ABC):
    """Post-processes responses after the LLM call.

    Receives and returns ``ChatResponse``.  Dispatches via
    ``isinstance`` to handle completion vs streaming variants, and
    OpenAI vs Anthropic vs Responses API formats.

    Lifecycle:

    * ``startup()`` — optional async hook. Callers MUST ``await`` it once
      after construction and before the first response. Default no-op.
    * ``shutdown()`` — optional async hook. Callers MUST ``await`` it once
      before discarding the processor. Default no-op.

    See :class:`RequestProcessor` for the resource-sharing pattern via
    :class:`~switchyard.lib.resource_cache.ResourceCache`.
    """

    @abstractmethod
    async def process(self, ctx: ProxyContext, response: ChatResponse) -> ChatResponse: ...

    async def startup(self) -> None:  # noqa: B027  # default no-op is the contract
        """Optional async startup hook. Default no-op."""

    async def shutdown(self) -> None:  # noqa: B027  # default no-op is the contract
        """Optional async shutdown hook. Default no-op."""


class ResponseTranslator(ABC):
    """Translates ``ChatResponse`` to the format the client expects.

    Sits at the end of the chain.  Uses the original ``ChatRequest``
    to determine the target format — if the request was an
    ``AnthropicChatRequest``, translate the response to Anthropic
    format.  If ``OpenAIChatRequest``, pass through.
    """

    @abstractmethod
    async def translate(
        self, ctx: ProxyContext, request: ChatRequest, response: ChatResponse,
    ) -> TranslatedResponse: ...
