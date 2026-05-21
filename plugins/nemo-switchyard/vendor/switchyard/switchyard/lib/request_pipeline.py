# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Composite request processor pipeline for chains."""

from __future__ import annotations

import logging
from collections.abc import Iterable, Iterator

from switchyard.lib.chat_request.base import ChatRequest
from switchyard.lib.proxy_context import ProxyContext
from switchyard.lib.roles import RequestProcessor

log = logging.getLogger(__name__)


class RequestPipeline(RequestProcessor):
    """Ordered composite of :class:`RequestProcessor` instances.

    ``RequestPipeline`` is itself a ``RequestProcessor``, so callers can
    compose nested pipelines or pass one anywhere a request processor is
    accepted. Construction and mutation validate the role at runtime so
    configuration mistakes fail before the first request.
    """

    def __init__(
        self,
        processors: Iterable[RequestProcessor] | None = None,
    ) -> None:
        self._processors: list[RequestProcessor] = []
        if processors is None:
            return
        for index, processor in enumerate(processors):
            self._processors.append(self._validate_processor(processor, index=index))

    @property
    def processors(self) -> tuple[RequestProcessor, ...]:
        """Return processors in execution order."""
        return tuple(self._processors)

    def __iter__(self) -> Iterator[RequestProcessor]:
        return iter(self._processors)

    def __len__(self) -> int:
        return len(self._processors)

    def iter_processors(self) -> Iterator[RequestProcessor]:
        """Yield leaf processors in execution order, flattening nested pipelines."""
        for processor in self._processors:
            if isinstance(processor, RequestPipeline):
                yield from processor.iter_processors()
            else:
                yield processor

    def then(self, processor: RequestProcessor) -> RequestPipeline:
        """Append ``processor`` and return this pipeline for fluent construction."""
        self._processors.append(self._validate_processor(processor, index=len(self._processors)))
        return self

    async def process(self, ctx: ProxyContext, request: ChatRequest) -> ChatRequest:
        """Run each request processor in order."""
        for processor in self._processors:
            request = await processor.process(ctx, request)
        return request

    async def startup(self) -> None:
        """Run ``startup()`` on each leaf processor in execution order.

        If a processor's ``startup()`` raises, already-started processors
        are ``shutdown()`` in reverse order before the exception
        propagates — partial pipelines are not left half-initialised.
        """
        started: list[RequestProcessor] = []
        try:
            for processor in self.iter_processors():
                await processor.startup()
                started.append(processor)
        except BaseException:
            for processor in reversed(started):
                try:
                    await processor.shutdown()
                except Exception:
                    pass
            raise

    async def shutdown(self) -> None:
        """Run ``shutdown()`` on each leaf processor in reverse execution order.

        Errors are swallowed and logged so one misbehaving processor doesn't
        prevent the rest from cleaning up.
        """
        for processor in reversed(list(self.iter_processors())):
            try:
                await processor.shutdown()
            except Exception:
                log.exception(
                    "RequestPipeline: shutdown raised for %s",
                    type(processor).__name__,
                )

    @staticmethod
    def _validate_processor(
        processor: object,
        *,
        index: int,
    ) -> RequestProcessor:
        if not isinstance(processor, RequestProcessor):
            raise TypeError(
                "RequestPipeline processor at index "
                f"{index} must be RequestProcessor, got {type(processor).__name__}"
            )
        return processor
