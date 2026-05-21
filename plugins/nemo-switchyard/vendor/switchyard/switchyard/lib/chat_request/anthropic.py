# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Anthropic Messages API format request."""

from __future__ import annotations

from anthropic.types.message_create_params import MessageCreateParamsBase

from switchyard.lib.chat_request.base import ChatRequest, ChatRequestType


class AnthropicChatRequest(ChatRequest):
    """Anthropic Messages API format request.

    ``body`` is ``MessageCreateParamsBase`` — the Anthropic SDK's
    ``TypedDict``.  At runtime it's a plain dict, so
    ``**request.body`` unpacks directly into
    ``client.messages.create()``.
    """

    def __init__(self, body: MessageCreateParamsBase) -> None:
        self._body = body

    @property
    def request_type(self) -> ChatRequestType:
        return ChatRequestType.ANTHROPIC

    @property
    def body(self) -> MessageCreateParamsBase:
        return self._body
