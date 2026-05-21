# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""ChatResponse translation engine — on-demand format conversion.

Wraps existing pure functions in ``anthropic_openai`` and
``responses_openai`` to convert between ``ChatResponse`` subclasses.
Every ``to_*`` method checks ``isinstance`` first (passthrough if
already the target type), then delegates to the matching pure function.

Stateless — safe to share across chains and threads.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from anthropic.types import Message as AnthropicMessage
from openai.types.chat import ChatCompletion
from openai.types.responses import Response as OpenAIResponse

from switchyard.lib.chat_request.anthropic import AnthropicChatRequest
from switchyard.lib.chat_request.base import ChatRequest
from switchyard.lib.chat_request.openai_chat import OpenAIChatRequest
from switchyard.lib.chat_request.openai_responses import ResponsesChatRequest
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
from switchyard.lib.translation.anthropic_openai import (
    convert_anthropic_response_to_openai,
    convert_openai_response_to_anthropic,
    stream_anthropic_to_openai,
    stream_openai_to_anthropic,
)
from switchyard.lib.translation.responses_openai import (
    convert_chat_response_to_responses,
    convert_responses_response_to_chat_completions,
    stream_chat_to_responses_sse,
    stream_responses_to_chat_completion_chunks,
)

if TYPE_CHECKING:
    # Imported under TYPE_CHECKING to avoid a circular import at module load:
    # ``foundation.infra.__init__`` imports ``default_response_translator``
    # which imports this module, so touching ``foundation.infra.roles`` here
    # at runtime cycles through a half-initialized ``response_engine``.
    # ``from __future__ import annotations`` keeps the forward references
    # in signatures intact.
    from switchyard.lib.roles import (
        TranslatedResponse,
        TranslatedStream,
    )

log = logging.getLogger(__name__)


class ChatResponseTranslationEngine:
    """Converts between ``ChatResponse`` subclasses on demand.

    The backend typically produces Chat Completions format, so
    ``to_anthropic`` and ``to_responses`` are the primary conversion
    paths.  Other directions are implemented as needed — passthrough
    is always a no-op.

    Supported conversions:

    - Non-streaming (``to_*`` / ``translate``):
        - ``CompletionChatResponse``  → ``AnthropicChatResponse``
        - ``CompletionChatResponse``  → ``ResponsesApiChatResponse``
        - ``AnthropicChatResponse``   → ``CompletionChatResponse``
        - ``ResponsesApiChatResponse`` → ``CompletionChatResponse``
    - Streaming (``translate_stream``):
        - ``StreamingChatResponse``   → OpenAI chunks (passthrough)
        - ``AnthropicStreamingChatResponse`` → OpenAI chunks
        - ``ResponsesApiStreamingChatResponse`` → OpenAI chunks
        - ``StreamingChatResponse``   → Anthropic event dicts
        - ``ResponsesApiStreamingChatResponse`` → Anthropic event dicts
        - ``StreamingChatResponse``   → Responses SSE frames
        - ``AnthropicStreamingChatResponse`` → Responses SSE frames

    All other combinations raise ``NotImplementedError``.
    """

    # ------------------------------------------------------------------
    # to_openai_chat
    # ------------------------------------------------------------------

    @staticmethod
    def to_openai_chat(
        response: ChatResponse,
    ) -> CompletionChatResponse | StreamingChatResponse:
        """Convert any ``ChatResponse`` to OpenAI Chat Completions format.

        No-op if the response is already OpenAI Chat format.
        """
        if isinstance(response, (CompletionChatResponse, StreamingChatResponse)):
            return response

        if isinstance(response, AnthropicChatResponse):
            anthropic_body = response.body
            openai_dict = convert_anthropic_response_to_openai(
                anthropic_body.model_dump(), model=anthropic_body.model,
            )
            return CompletionChatResponse(ChatCompletion.model_validate(openai_dict))

        if isinstance(response, ResponsesApiChatResponse):
            responses_body: OpenAIResponse = response.body
            openai_dict = convert_responses_response_to_chat_completions(
                responses_body,
                fallback_model=getattr(responses_body, "model", "unknown"),
            )
            return CompletionChatResponse(ChatCompletion.model_validate(openai_dict))

        raise NotImplementedError(
            f"Response translation to OpenAI Chat not implemented "
            f"for {type(response).__name__}"
        )

    # ------------------------------------------------------------------
    # to_anthropic
    # ------------------------------------------------------------------

    @staticmethod
    def to_anthropic(
        response: ChatResponse,
    ) -> AnthropicChatResponse | AnthropicStreamingChatResponse:
        """Convert any ``ChatResponse`` to Anthropic Messages format.

        No-op if the response is already Anthropic format.
        """
        if isinstance(response, (AnthropicChatResponse, AnthropicStreamingChatResponse)):
            return response

        if isinstance(response, CompletionChatResponse):
            anthropic_dict = convert_openai_response_to_anthropic(
                response.body, model=response.body.model,
            )
            return AnthropicChatResponse(AnthropicMessage.model_validate(anthropic_dict))

        raise NotImplementedError(
            f"Response translation to Anthropic not implemented "
            f"for {type(response).__name__}"
        )

    # ------------------------------------------------------------------
    # to_responses
    # ------------------------------------------------------------------

    @staticmethod
    def to_responses(
        response: ChatResponse,
        *,
        original_body: dict[str, Any],
    ) -> ResponsesApiChatResponse | ResponsesApiStreamingChatResponse:
        """Convert any ``ChatResponse`` to OpenAI Responses API format.

        No-op if the response is already Responses API format.
        ``original_body`` is the original Responses API request body,
        used to populate the model name in the output.
        """
        if isinstance(response, (ResponsesApiChatResponse, ResponsesApiStreamingChatResponse)):
            return response

        if isinstance(response, CompletionChatResponse):
            responses_dict = convert_chat_response_to_responses(
                response.body, original_body=original_body,
            )
            return ResponsesApiChatResponse(
                OpenAIResponse.model_construct(**responses_dict),
            )

        raise NotImplementedError(
            f"Response translation to Responses API not implemented "
            f"for {type(response).__name__}"
        )

    # ------------------------------------------------------------------
    # translate / translate_stream (dispatch by request type)
    # ------------------------------------------------------------------

    @staticmethod
    def translate(request: ChatRequest, response: ChatResponse) -> TranslatedResponse:
        """Translate a non-streaming response to the client's expected format.

        Dispatches on the ``ChatRequest`` subclass to pick the target
        format and returns the unwrapped body (``ChatCompletion`` for
        OpenAI passthrough, plain dicts for Anthropic / Responses) that
        endpoints hand directly to ``JSONResponse``.
        """
        if isinstance(request, OpenAIChatRequest):
            if isinstance(response, CompletionChatResponse):
                return response.body
            if isinstance(response, AnthropicChatResponse):
                body = response.body
                return convert_anthropic_response_to_openai(
                    body.model_dump(), model=body.model,
                )
        elif isinstance(request, AnthropicChatRequest):
            if isinstance(response, AnthropicChatResponse):
                return response.body
            if isinstance(response, CompletionChatResponse):
                # Prefer the request's model name; when the request has
                # no ``model`` key the convert function falls back to
                # the response body's ``model`` field, and then to
                # ``"unknown"``.
                return convert_openai_response_to_anthropic(
                    response.body, model=request.body.get("model"),
                )
        elif isinstance(request, ResponsesChatRequest):
            if isinstance(response, ResponsesApiChatResponse):
                return response.body
            if isinstance(response, CompletionChatResponse):
                return convert_chat_response_to_responses(
                    response.body, original_body=dict(request.body),
                )
        else:
            raise NotImplementedError(
                f"Non-streaming translation not implemented for "
                f"request type {type(request).__name__}"
            )

        raise NotImplementedError(
            f"Non-streaming translation from {type(response).__name__} "
            f"to {type(request).__name__} not implemented"
        )

    @staticmethod
    def translate_stream(
        request: ChatRequest,
        response: ChatResponse,
    ) -> TranslatedStream:
        """Translate a streaming response to the client's expected format.

        Returns an async iterator shaped for the target format:

        * ``OpenAIChatRequest`` — passthrough ``ChatCompletionChunk``
          objects (the endpoint frames them with ``iter_chat_completion_sse``).
        * ``AnthropicChatRequest`` — plain event dicts
          (``{"type": "message_start", ...}``, ``content_block_delta``,
          …) that the endpoint frames into Anthropic SSE with
          ``iter_anthropic_sse``.
        * ``ResponsesChatRequest`` — fully-framed Responses API SSE
          strings (already ``"event: ...\\ndata: ...\\n\\n"``) that the
          endpoint forwards through ``iter_preframed_sse``.
        """
        if isinstance(request, OpenAIChatRequest):
            if isinstance(response, StreamingChatResponse):
                return response.stream
            if isinstance(response, AnthropicStreamingChatResponse):
                model = request.body.get("model", "unknown")
                return stream_anthropic_to_openai(response.stream, model=str(model))
            if isinstance(response, ResponsesApiStreamingChatResponse):
                model = request.body.get("model", "unknown")
                return stream_responses_to_chat_completion_chunks(
                    response.stream,
                    model=str(model),
                )
        elif isinstance(request, AnthropicChatRequest):
            if isinstance(response, AnthropicStreamingChatResponse):
                return response.stream
            if isinstance(response, StreamingChatResponse):
                model = request.body.get("model", "unknown")
                return stream_openai_to_anthropic(response.stream, model=model)
            if isinstance(response, ResponsesApiStreamingChatResponse):
                model = str(request.body.get("model", "unknown"))
                chat_stream = stream_responses_to_chat_completion_chunks(
                    response.stream,
                    model=model,
                )
                return stream_openai_to_anthropic(chat_stream, model=model)
        elif isinstance(request, ResponsesChatRequest):
            if isinstance(response, ResponsesApiStreamingChatResponse):
                return response.stream
            if isinstance(response, StreamingChatResponse):
                return stream_chat_to_responses_sse(
                    response.stream, original_body=dict(request.body),
                )
            if isinstance(response, AnthropicStreamingChatResponse):
                model = str(request.body.get("model", "unknown"))
                chat_stream = stream_anthropic_to_openai(
                    response.stream,
                    model=model,
                )
                return stream_chat_to_responses_sse(
                    chat_stream,
                    original_body=dict(request.body),
                )
        else:
            raise NotImplementedError(
                f"Streaming translation not implemented for "
                f"request type {type(request).__name__}"
            )

        raise NotImplementedError(
            f"Streaming translation from {type(response).__name__} "
            f"to {type(request).__name__} not implemented"
        )
