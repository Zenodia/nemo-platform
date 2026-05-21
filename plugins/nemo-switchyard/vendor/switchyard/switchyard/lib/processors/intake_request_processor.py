# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Request processor that snapshots inbound metadata for the intake sink."""

from __future__ import annotations

import time
from copy import deepcopy

from switchyard.lib.chat_request.anthropic import AnthropicChatRequest
from switchyard.lib.chat_request.base import ChatRequest
from switchyard.lib.chat_request.openai_chat import OpenAIChatRequest
from switchyard.lib.chat_request.openai_responses import ResponsesChatRequest
from switchyard.lib.processors.intake_payload_builder import (
    INTAKE_INBOUND_FORMAT_KEY,
    INTAKE_REQUEST_SNAPSHOT_KEY,
    INTAKE_SESSION_ID_KEY,
    INTAKE_SKIP_KEY,
    INTAKE_STARTED_AT_MS_KEY,
)
from switchyard.lib.proxy_context import ProxyContext
from switchyard.lib.request_metadata import (
    CTX_REQUEST_METADATA,
    RequestMetadata,
)
from switchyard.lib.roles import RequestProcessor


class IntakeRequestProcessor(RequestProcessor):
    """Capture request metadata needed by the intake sink."""

    async def process(self, ctx: ProxyContext, request: ChatRequest) -> ChatRequest:
        request_metadata = _request_metadata(ctx)
        ctx.metadata[INTAKE_STARTED_AT_MS_KEY] = int(time.time() * 1000)
        ctx.metadata[INTAKE_INBOUND_FORMAT_KEY] = request.request_type.value
        ctx.metadata[INTAKE_SESSION_ID_KEY] = request_metadata.session_id
        client_opt_in = (
            request_metadata.intake.enabled
            if request_metadata.intake.enabled is not None
            else _extract_store_toggle(request)
        )
        skip = client_opt_in is not True
        ctx.metadata[INTAKE_SKIP_KEY] = skip
        if not skip:
            ctx.metadata[INTAKE_REQUEST_SNAPSHOT_KEY] = _copy_request(request)
        return request


def _copy_request(request: ChatRequest) -> ChatRequest:
    if isinstance(request, OpenAIChatRequest):
        return OpenAIChatRequest(deepcopy(request.body))
    if isinstance(request, AnthropicChatRequest):
        return AnthropicChatRequest(deepcopy(request.body))
    if isinstance(request, ResponsesChatRequest):
        return ResponsesChatRequest(deepcopy(request.body))
    raise NotImplementedError(f"Unsupported request type: {type(request).__name__}")


def _extract_store_toggle(request: ChatRequest) -> bool | None:
    if not isinstance(request, (OpenAIChatRequest, AnthropicChatRequest, ResponsesChatRequest)):
        return None
    raw = request.body.get("store")
    if isinstance(raw, bool):
        return raw
    return None


def _request_metadata(ctx: ProxyContext) -> RequestMetadata:
    value = ctx.metadata.get(CTX_REQUEST_METADATA)
    return value if isinstance(value, RequestMetadata) else RequestMetadata()
