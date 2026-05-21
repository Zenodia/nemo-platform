# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Typed request hierarchy for the strategy chain.

Each subclass wraps its provider SDK's native ``TypedDict``, giving full
IDE autocomplete and type-checked field access while remaining a plain
``dict`` at runtime (zero serialization cost, direct ``**unpack`` into
SDK ``create()`` calls).
"""

from switchyard.lib.chat_request.anthropic import AnthropicChatRequest
from switchyard.lib.chat_request.base import ChatRequest, ChatRequestType
from switchyard.lib.chat_request.openai_chat import OpenAIChatRequest
from switchyard.lib.chat_request.openai_responses import ResponsesChatRequest

__all__ = [
    "AnthropicChatRequest",
    "ChatRequest",
    "ChatRequestType",
    "OpenAIChatRequest",
    "ResponsesChatRequest",
]
