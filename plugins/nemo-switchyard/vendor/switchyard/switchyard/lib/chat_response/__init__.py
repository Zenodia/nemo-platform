# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Typed response hierarchy for the strategy chain.

Six concrete subclasses cover the wire-format x delivery-mode matrix:
OpenAI Chat Completions, OpenAI Responses API, and Anthropic Messages,
each with non-streaming and streaming variants.
"""

from switchyard.lib.chat_response.anthropic import (
    AnthropicChatResponse,
    AnthropicResponseStream,
    AnthropicStreamingChatResponse,
)
from switchyard.lib.chat_response.base import ChatResponse, ChatResponseType
from switchyard.lib.chat_response.openai_chat import (
    CompletionChatResponse,
    ResponseStream,
    StreamingChatResponse,
)
from switchyard.lib.chat_response.openai_responses import (
    ResponsesApiChatResponse,
    ResponsesApiStream,
    ResponsesApiStreamingChatResponse,
)

AnyResponseStream = ResponseStream | ResponsesApiStream | AnthropicResponseStream

__all__ = [
    "AnyResponseStream",
    "AnthropicChatResponse",
    "AnthropicResponseStream",
    "AnthropicStreamingChatResponse",
    "ChatResponse",
    "ChatResponseType",
    "CompletionChatResponse",
    "ResponsesApiChatResponse",
    "ResponsesApiStream",
    "ResponsesApiStreamingChatResponse",
    "ResponseStream",
    "StreamingChatResponse",
]
