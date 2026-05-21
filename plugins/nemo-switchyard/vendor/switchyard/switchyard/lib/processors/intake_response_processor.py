# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Response processor that posts completed turns to the intake sink."""

from __future__ import annotations

import time

from switchyard.lib.chat_response.base import ChatResponse
from switchyard.lib.chat_response.streaming_response_accumulator import (
    attach_final_response_callback,
)
from switchyard.lib.factories.intake_sink.intake_sink_config import (
    IntakeSinkConfig,
)
from switchyard.lib.processors.intake_client import IntakeClient
from switchyard.lib.processors.intake_payload_builder import (
    INTAKE_ENDED_AT_MS_KEY,
    INTAKE_SKIP_KEY,
    UNKNOWN_MODEL,
    IntakePayloadBuilder,
)
from switchyard.lib.proxy_context import CTX_PROXY_ACTUAL_MODEL, ProxyContext
from switchyard.lib.roles import ResponseProcessor


class IntakeResponseProcessor(ResponseProcessor):
    """Queue one intake POST per successful response, without blocking the client."""

    def __init__(self, config: IntakeSinkConfig, client: IntakeClient) -> None:
        self._builder = IntakePayloadBuilder(config)
        self._client = client

    async def process(self, ctx: ProxyContext, response: ChatResponse) -> ChatResponse:
        if ctx.metadata.get(INTAKE_SKIP_KEY) is True:
            return response

        served_model = _served_model(ctx)

        async def on_stream_complete(final_response: ChatResponse) -> None:
            self._enqueue_later(ctx, final_response, stream=True)

        if attach_final_response_callback(
            response,
            served_model=served_model,
            callback=on_stream_complete,
        ):
            return response

        self._enqueue_later(ctx, response, stream=False)
        return response

    async def shutdown(self) -> None:
        await self._client.aclose()

    def _enqueue_later(self, ctx: ProxyContext, response: ChatResponse, *, stream: bool) -> None:
        def build_payload() -> dict[str, object]:
            ctx.metadata[INTAKE_ENDED_AT_MS_KEY] = int(time.time() * 1000)
            return self._builder.build(
                ctx=ctx,
                request_snapshot=self._builder.request_from_snapshot(ctx),
                response=response,
                stream=stream,
            )

        self._client.enqueue_background(build_payload)


def _served_model(ctx: ProxyContext) -> str:
    value = ctx.metadata.get(CTX_PROXY_ACTUAL_MODEL)
    if not isinstance(value, str) or not value:
        return UNKNOWN_MODEL
    return value
