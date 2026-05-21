# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""HTTP endpoint serving a ``Switchyard`` as ``POST /v1/messages`` (Anthropic Messages API).

Paper-thin by design: wrap the raw JSON body in ``AnthropicChatRequest``,
run the chain, serialize the result.  All Anthropic ↔ OpenAI format
conversion lives inside the chain (``ChatRequestTranslationEngine`` and
``ChatResponseTranslationEngine``), so the endpoint itself contains zero
translation logic.

Streaming contract:

- When the request body carries ``"stream": true``, the chain's
  translator surfaces an async iterator of Anthropic event dicts; the
  endpoint frames them into Anthropic-style named-event SSE
  (``event: message_start\\ndata: {...}\\n\\n``, …) via
  :func:`iter_anthropic_sse`.
- Non-streaming requests return the Anthropic ``Message`` body as JSON.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from anthropic.types.message_create_params import MessageCreateParamsBase
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, Response, StreamingResponse

from switchyard.lib.chat_request.anthropic import AnthropicChatRequest
from switchyard.lib.endpoints.base import Endpoint as NemoSwitchyardEndpoint
from switchyard.lib.endpoints.sse_helpers import iter_anthropic_sse
from switchyard.lib.middleware_registry import MiddlewareRegistry
from switchyard.lib.proxy_context import ProxyContext
from switchyard.lib.request_metadata import (
    CTX_REQUEST_METADATA,
    RequestMetadata,
)

if TYPE_CHECKING:
    from fastapi import FastAPI

log = logging.getLogger(__name__)


class AnthropicMessagesEndpoint(NemoSwitchyardEndpoint):
    """Composable endpoint that exposes ``POST /v1/messages``."""

    def register(self, app: FastAPI) -> None:
        """Attach ``POST /v1/messages`` onto *app*."""
        router = APIRouter()

        @router.post("/v1/messages", response_model=None)
        async def anthropic_messages(request: Request) -> Response:
            obj = request.app.state.switchyard
            body: MessageCreateParamsBase = await request.json()
            model = str(body.get("model", "<none>"))
            switchyard: Any
            if isinstance(obj, MiddlewareRegistry):
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
            stream = bool(body.get("stream"))
            log.debug(
                "POST /v1/messages model=%s stream=%s keys=%s",
                model, stream, list(body.keys()),
            )
            ctx = ProxyContext()
            ctx.metadata[CTX_REQUEST_METADATA] = RequestMetadata.from_headers(request.headers)

            try:
                chat_request = AnthropicChatRequest(body)
                result = await switchyard.call(chat_request, ctx=ctx)
            except Exception:
                log.exception("POST /v1/messages chain raised model=%s", model)
                raise

            log.debug(
                "POST /v1/messages chain returned model=%s stream=%s result=%s",
                model, stream, type(result).__name__,
            )

            if stream and hasattr(result, "__aiter__"):
                return StreamingResponse(
                    iter_anthropic_sse(result),
                    media_type="text/event-stream",
                )

            if hasattr(result, "model_dump"):
                return JSONResponse(content=result.model_dump())
            return JSONResponse(content=result)

        app.include_router(router, tags=["Anthropic Compatible"])
