# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Default end-of-chain response translator.

Delegates to ``ChatResponseTranslationEngine``, dispatching on the
``ChatResponse`` subtype (non-streaming vs streaming) and letting the
engine handle the request-type-based format selection:

- ``OpenAIChatRequest``     → Chat Completions format
- ``AnthropicChatRequest``  → Anthropic Messages format
- ``ResponsesChatRequest``  → OpenAI Responses API format

Returns the unwrapped SDK body (non-streaming) or a composable async
iterator (streaming). Endpoints are responsible for turning the body
into JSON or the iterator into SSE frames.
"""

from __future__ import annotations

from switchyard.lib.chat_request.base import ChatRequest
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
from switchyard.lib.proxy_context import ProxyContext
from switchyard.lib.roles import ResponseTranslator, TranslatedResponse
from switchyard.lib.translation.response_engine import (
    ChatResponseTranslationEngine,
)


class DefaultResponseTranslator(ResponseTranslator):
    """Dispatches to the right ``ChatResponseTranslationEngine`` method by response type.

    This is the standard translator used in most chains — every format
    flows through the same centralized translation engine, so new formats
    or new conversions don't require changes to individual chains.
    """

    async def translate(
        self,
        ctx: ProxyContext,
        request: ChatRequest,
        response: ChatResponse,
    ) -> TranslatedResponse:
        if isinstance(
            response,
            (CompletionChatResponse, AnthropicChatResponse, ResponsesApiChatResponse),
        ):
            return ChatResponseTranslationEngine.translate(request, response)
        if isinstance(
            response,
            (
                StreamingChatResponse,
                AnthropicStreamingChatResponse,
                ResponsesApiStreamingChatResponse,
            ),
        ):
            return ChatResponseTranslationEngine.translate_stream(request, response)
        raise NotImplementedError(
            f"DefaultResponseTranslator has no dispatch for response type "
            f"{type(response).__name__}"
        )
