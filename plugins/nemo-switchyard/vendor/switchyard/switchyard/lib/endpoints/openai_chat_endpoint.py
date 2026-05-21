# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""HTTP endpoint serving a ``Switchyard`` as ``POST /v1/chat/completions``.

The class is stateless — at request time it reads the switchyard from
``request.app.state.switchyard``.  Wire-up is performed by the
``build_switchyard_app()`` convenience factory.

Streaming contract:

- When the request body carries ``"stream": true``, the chain's
  translator surfaces an async iterator of ``ChatCompletionChunk``; the
  endpoint wraps it in a ``StreamingResponse`` emitting OpenAI-style
  SSE frames (``data: {...}\\n\\n`` + ``data: [DONE]\\n\\n``).
- Upstream failures (auth, rate-limit, connection) surface before the
  ``StreamingResponse`` is constructed — they propagate as exceptions
  to the global handler and map to proper HTTP error responses.  Only
  mid-stream iteration errors land in the SSE error branch of
  :func:`iter_chat_completion_sse`.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, Response, StreamingResponse
from openai.types.chat.completion_create_params import CompletionCreateParamsBase

from switchyard.lib.chat_request.openai_chat import OpenAIChatRequest
from switchyard.lib.endpoints.base import Endpoint as NemoSwitchyardEndpoint
from switchyard.lib.endpoints.sse_helpers import iter_chat_completion_sse
from switchyard.lib.middleware_registry import MiddlewareRegistry
from switchyard.lib.proxy_context import ProxyContext
from switchyard.lib.request_metadata import (
    CTX_REQUEST_METADATA,
    RequestMetadata,
)

if TYPE_CHECKING:
    from fastapi import FastAPI


class OpenAIChatEndpoint(NemoSwitchyardEndpoint):
    """Composable endpoint that exposes ``POST /v1/chat/completions``.

    Reads the raw JSON body, wraps it in ``OpenAIChatRequest`` (no
    validation or field-stripping, so provider-specific fields pass
    through transparently), runs the chain, and either JSON-serializes
    the result (non-streaming) or wraps the async chunk iterator in an
    SSE ``StreamingResponse`` (streaming).

    Streaming support is limited to same-format passthrough today —
    i.e. OpenAI Chat Completions inbound against an OpenAI-native
    backend.  Cross-format streaming (Anthropic / Responses inbound)
    raises ``NotImplementedError`` from ``ChatResponseTranslationEngine``
    until streaming translation lands for those formats.
    """

    def register(self, app: FastAPI) -> None:
        """Attach ``POST /v1/chat/completions`` onto *app*."""
        router = APIRouter()

        @router.post("/v1/chat/completions", response_model=None)
        async def chat_completions(request: Request) -> Response:
            obj = request.app.state.switchyard
            body: CompletionCreateParamsBase = await request.json()
            switchyard: Any
            if isinstance(obj, MiddlewareRegistry):
                model = str(body.get("model", ""))
                try:
                    switchyard = obj.lookup_switchyard(model)
                except KeyError:
                    return JSONResponse(
                        status_code=404,
                        content={"error": {
                            "message": f"No chain registered for model {model!r}",
                            "type": "model_not_found",
                            "code": "model_not_found",
                        }},
                    )
            else:
                switchyard = obj
            chat_request = OpenAIChatRequest(body)
            ctx = ProxyContext()
            ctx.metadata[CTX_REQUEST_METADATA] = RequestMetadata.from_headers(request.headers)
            result = await switchyard.call(chat_request, ctx=ctx)

            if body.get("stream"):
                return StreamingResponse(
                    iter_chat_completion_sse(result),
                    media_type="text/event-stream",
                )

            if hasattr(result, "model_dump"):
                return JSONResponse(content=result.model_dump())
            return JSONResponse(content=result)

        app.include_router(router, tags=["OpenAI Compatible"])
