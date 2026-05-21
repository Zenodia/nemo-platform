# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""OpenAI Chat Completions format request."""

from __future__ import annotations

from openai.types.chat.completion_create_params import CompletionCreateParamsBase

from switchyard.lib.chat_request.base import ChatRequest, ChatRequestType


class OpenAIChatRequest(ChatRequest):
    """OpenAI Chat Completions format request.

    ``body`` is ``CompletionCreateParamsBase`` — the OpenAI SDK's
    ``TypedDict``.  At runtime it's a plain dict, so
    ``**request.body`` unpacks directly into
    ``client.chat.completions.create()``.
    """

    def __init__(self, body: CompletionCreateParamsBase) -> None:
        self._body = body

    @property
    def request_type(self) -> ChatRequestType:
        return ChatRequestType.OPENAI_CHAT

    @property
    def body(self) -> CompletionCreateParamsBase:
        return self._body
