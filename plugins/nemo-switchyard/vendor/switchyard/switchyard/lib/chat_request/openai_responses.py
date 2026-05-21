# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""OpenAI Responses API format request."""

from __future__ import annotations

from openai.types.responses.response_create_params import ResponseCreateParamsBase

from switchyard.lib.chat_request.base import ChatRequest, ChatRequestType


class ResponsesChatRequest(ChatRequest):
    """OpenAI Responses API format request.

    ``body`` is ``ResponseCreateParamsBase`` — the OpenAI SDK's
    ``TypedDict`` for the Responses API.  All Responses-specific fields
    (``previous_response_id``, ``conversation``, ``truncation``,
    ``reasoning``, etc.) are first-class typed fields on the body.
    """

    def __init__(self, body: ResponseCreateParamsBase) -> None:
        self._body = body

    @property
    def request_type(self) -> ChatRequestType:
        return ChatRequestType.OPENAI_RESPONSES

    @property
    def body(self) -> ResponseCreateParamsBase:
        return self._body
