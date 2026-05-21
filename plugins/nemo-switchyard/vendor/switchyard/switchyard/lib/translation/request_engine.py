# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""ChatRequest translation engine — on-demand format conversion.

Wraps existing pure functions in ``anthropic_openai`` and
``responses_openai`` to convert between ``ChatRequest`` subclasses.
Every ``to_*`` method checks ``isinstance`` first (passthrough if
already the target type), then delegates to the matching pure function.

Stateless — safe to share across chains and threads.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, cast

from switchyard.lib.chat_request.anthropic import AnthropicChatRequest
from switchyard.lib.chat_request.base import ChatRequest, ChatRequestType
from switchyard.lib.chat_request.openai_chat import OpenAIChatRequest
from switchyard.lib.chat_request.openai_responses import ResponsesChatRequest
from switchyard.lib.translation.anthropic_openai import (
    convert_anthropic_request_to_openai,
    convert_openai_request_to_anthropic,
)
from switchyard.lib.translation.responses_openai import (
    convert_responses_request_to_chat_completions,
)

if TYPE_CHECKING:
    from anthropic.types.message_create_params import MessageCreateParamsBase
    from openai.types.chat.completion_create_params import CompletionCreateParamsBase

log = logging.getLogger(__name__)


class ChatRequestTranslationEngine:
    """Converts between ``ChatRequest`` subclasses on demand.

    The backend always speaks Chat Completions, so ``to_openai_chat``
    is the primary conversion path.  Other directions are implemented
    as needed — passthrough is always a no-op.

    Phase 1 supports:

    - ``OpenAIChatRequest``  → passthrough
    - ``AnthropicChatRequest`` → ``OpenAIChatRequest`` (direct)
    - ``ResponsesChatRequest`` → ``OpenAIChatRequest`` (direct)
    - ``OpenAIChatRequest`` → ``AnthropicChatRequest`` (direct)

    All other combinations raise ``NotImplementedError``.
    """

    # ------------------------------------------------------------------
    # to_openai_chat
    # ------------------------------------------------------------------

    @staticmethod
    def to_openai_chat(request: ChatRequest) -> OpenAIChatRequest:
        """Convert any ``ChatRequest`` to OpenAI Chat Completions format.

        No-op if the request is already an ``OpenAIChatRequest``.
        """
        if isinstance(request, OpenAIChatRequest):
            return request

        if isinstance(request, AnthropicChatRequest):
            openai_body = convert_anthropic_request_to_openai(**request.body)
            return OpenAIChatRequest(cast("CompletionCreateParamsBase", openai_body))

        if isinstance(request, ResponsesChatRequest):
            openai_body = convert_responses_request_to_chat_completions(dict(request.body))
            return OpenAIChatRequest(cast("CompletionCreateParamsBase", openai_body))

        raise NotImplementedError(
            f"Request translation to OpenAI Chat not implemented "
            f"for {type(request).__name__}"
        )

    # ------------------------------------------------------------------
    # to_anthropic
    # ------------------------------------------------------------------

    @staticmethod
    def to_anthropic(request: ChatRequest) -> AnthropicChatRequest:
        """Convert any ``ChatRequest`` to Anthropic Messages format.

        No-op if the request is already an ``AnthropicChatRequest``.
        """
        if isinstance(request, AnthropicChatRequest):
            return request

        if isinstance(request, OpenAIChatRequest):
            anthropic_body = convert_openai_request_to_anthropic(**request.body)
            return AnthropicChatRequest(cast("MessageCreateParamsBase", anthropic_body))

        raise NotImplementedError(
            f"Request translation to Anthropic not implemented "
            f"for {type(request).__name__}. "
            "Add when an Anthropic-native backend is introduced."
        )

    # ------------------------------------------------------------------
    # to_responses
    # ------------------------------------------------------------------

    @staticmethod
    def to_responses(request: ChatRequest) -> ResponsesChatRequest:
        """Convert any ``ChatRequest`` to OpenAI Responses API format.

        No-op if the request is already a ``ResponsesChatRequest``.
        """
        if isinstance(request, ResponsesChatRequest):
            return request

        raise NotImplementedError(
            f"Request translation to Responses API not implemented "
            f"for {type(request).__name__}. "
            "Add when a Responses-native backend is introduced."
        )

    # ------------------------------------------------------------------
    # to_any_of — "normalize to any accepted format"
    # ------------------------------------------------------------------

    @classmethod
    def to_any_of(
        cls,
        request: ChatRequest,
        supported: list[ChatRequestType],
    ) -> ChatRequest:
        """Normalize ``request`` to any of ``supported`` formats.

        Passthrough if ``request.request_type`` is in ``supported``.
        Otherwise translate to ``supported[0]`` (the backend's most
        preferred format) via the matching ``to_*`` method.

        Args:
            request: The inbound request in any supported format.
            supported: Ordered preference of request types the backend
                accepts.  The first element is used as the translation
                target when ``request`` isn't already one of the
                supported types.

        Returns:
            Either ``request`` itself (passthrough) or a translated
            ``ChatRequest`` in ``supported[0]``.

        Raises:
            ValueError: ``supported`` is empty.
            NotImplementedError: no translation path exists from
                ``request``'s type to ``supported[0]``.
        """
        if not supported:
            raise ValueError("supported must be non-empty")
        if request.request_type in supported:
            return request
        target = supported[0]
        if target is ChatRequestType.OPENAI_CHAT:
            return cls.to_openai_chat(request)
        if target is ChatRequestType.ANTHROPIC:
            return cls.to_anthropic(request)
        if target is ChatRequestType.OPENAI_RESPONSES:
            return cls.to_responses(request)
        raise NotImplementedError(f"Unknown target request type: {target}")
