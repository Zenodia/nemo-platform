# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Switchyard — the chain executor.

Enforces the chain shape::

    [RequestProcessor*] → LLMBackend → [ResponseProcessor*] → ResponseTranslator

Runs the chain end-to-end for a single request.
"""

from __future__ import annotations

import logging
from collections.abc import Iterable
from typing import ClassVar

from switchyard.lib.chat_request.base import ChatRequest
from switchyard.lib.proxy_context import ProxyContext
from switchyard.lib.request_pipeline import RequestPipeline
from switchyard.lib.response_pipeline import ResponsePipeline
from switchyard.lib.roles import (
    LLMBackend,
    RequestProcessor,
    ResponseProcessor,
    ResponseTranslator,
    TranslatedResponse,
)

log = logging.getLogger(__name__)


class Switchyard:
    """Chain executor.

    Accepts a list of request processors, exactly one backend, an
    optional list of response processors, and exactly one translator.
    Validates the shape at construction time — misconfigured chains
    fail fast, not at request time.
    """

    #: Name of the attribute the server stashes this instance onto via
    #: ``app.state``.  Endpoint handlers read it back as
    #: ``request.app.state.switchyard``.
    state_key: ClassVar[str] = "switchyard"

    def __init__(
        self,
        *,
        request_processors: Iterable[RequestProcessor] | None = None,
        backend: LLMBackend,
        response_processors: Iterable[ResponseProcessor] | None = None,
        translator: ResponseTranslator,
    ) -> None:
        self._request_pipeline = RequestPipeline(request_processors)
        self._backend = backend
        self._response_pipeline = ResponsePipeline(response_processors)
        self._translator = translator

    def iter_components(
        self,
    ) -> list[RequestProcessor | LLMBackend | ResponseProcessor | ResponseTranslator]:
        """Return all chain components in execution order.

        The app factory iterates this list to:

        - call ``component.shutdown()`` during app teardown (if defined)
        - collect ``component.get_endpoint()`` contributions during setup
          (if defined)

        Components are heterogeneous: request processors, the single
        backend, response processors, and the terminal translator.
        """
        return [
            *self._request_pipeline.iter_processors(),
            self._backend,
            *self._response_pipeline.iter_processors(),
            self._translator,
        ]

    async def call(
        self,
        request: ChatRequest,
        *,
        ctx: ProxyContext | None = None,
    ) -> TranslatedResponse:
        """Run the full chain for a single request.

        ``ctx`` is optional so HTTP endpoints can seed request metadata
        without reaching into the request body.
        """
        req_type = type(request).__name__
        backend_name = type(self._backend).__name__
        log.debug("chain start: request=%s backend=%s", req_type, backend_name)
        context = ctx or ProxyContext()

        try:
            request = await self._request_pipeline.process(context, request)

            log.debug("backend call: %s", backend_name)
            response = await self._backend.call(context, request)
            log.debug("backend response: %s", type(response).__name__)

            response = await self._response_pipeline.process(context, response)

            log.debug("translator: %s", type(self._translator).__name__)
            result = await self._translator.translate(context, request, response)
            log.debug("chain complete: result=%s", type(result).__name__)
            return result
        except Exception:
            log.exception("chain error: %s backend=%s", req_type, backend_name)
            raise
