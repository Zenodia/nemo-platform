# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""``LLMBackend`` that routes across many endpoints by Latency Service verdicts.

This is the usage case for Inference Hub deployments where a central
Latency Service owns heartbeat probing and statistical profiling.  The
backend holds a pool of ``OpenAILLMClient`` instances keyed by model ID,
reads health verdicts from a locally-cached map maintained by a
:class:`HealthPoller` daemon thread, and picks a healthy endpoint on
every request.

Chain integration::

    [RequestProcessor*] → LatencyServiceLLMBackend → [ResponseProcessor*] → ResponseTranslator

Request-format translation (Anthropic / Responses → OpenAI Chat) is
delegated to :class:`ChatRequestTranslationEngine`, mirroring
:class:`OpenAILLMBackend`.  Non-OpenAI inbound formats therefore flow
through transparently.
"""

from __future__ import annotations

import logging
import random
import threading
from typing import TYPE_CHECKING

from openai import AsyncStream

from switchyard.lib.backends.health_poller import (
    EndpointHealthStatus,
    HealthPoller,
)
from switchyard.lib.chat_request.base import ChatRequestType
from switchyard.lib.chat_request.openai_chat import OpenAIChatRequest
from switchyard.lib.chat_response.base import ChatResponse
from switchyard.lib.chat_response.openai_chat import (
    CompletionChatResponse,
    ResponseStream,
    StreamingChatResponse,
)
from switchyard.lib.config.latency_service_backend_config import (
    LatencyServiceBackendConfig,
)
from switchyard.lib.llm_client import OpenAILLMClient
from switchyard.lib.roles import LLMBackend
from switchyard.lib.translation.request_engine import (
    ChatRequestTranslationEngine,
)

if TYPE_CHECKING:
    from switchyard.lib.chat_request.base import ChatRequest
    from switchyard.lib.proxy_context import ProxyContext

log = logging.getLogger(__name__)


class LatencyServiceLLMBackend(LLMBackend):
    """Routes to healthy endpoints based on Latency Service health verdicts.

    On construction, builds a pool of ``OpenAILLMClient`` instances
    (one per configured endpoint, keyed by ``model``) and starts a
    :class:`HealthPoller` daemon thread that refreshes the in-memory
    health cache every ``poll_interval_s`` seconds.

    On each ``call()``:

    1. Convert the request to OpenAI Chat format via
       :class:`ChatRequestTranslationEngine`.
    2. Pick an endpoint from the health cache — ``HEALTHY`` preferred,
       then ``UNKNOWN``, then ``DEGRADED``.  Random within a tier.
    3. Override the body's ``model`` with the selected endpoint ID.
    4. Call ``OpenAILLMClient.acompletion``.  On error, retry with a
       different endpoint (dedup prevents re-selecting the same one
       within a single request).
    5. Wrap the response into a ``CompletionChatResponse`` or
       ``StreamingChatResponse``.
    """

    def __init__(self, config: LatencyServiceBackendConfig) -> None:
        if not config.endpoints:
            raise ValueError("At least one endpoint must be configured")

        self._config = config
        self._clients: dict[str, OpenAILLMClient] = {}
        self._health_cache: dict[str, EndpointHealthStatus] = {}
        self._cache_lock = threading.Lock()

        for ep_cfg in config.endpoints:
            model_id = ep_cfg.model
            if not model_id:
                raise ValueError(
                    "Every endpoint must have a 'model' field — "
                    "this is the key used by the Latency Service"
                )
            if model_id in self._clients:
                raise ValueError(f"Duplicate model ID: {model_id}")

            self._clients[model_id] = OpenAILLMClient(
                api_key=ep_cfg.api_key,
                base_url=ep_cfg.base_url,
                timeout=ep_cfg.timeout,
            )
            self._health_cache[model_id] = EndpointHealthStatus.UNKNOWN
            log.info(
                "LatencyServiceLLMBackend endpoint: model=%s base_url=%s",
                model_id, ep_cfg.base_url,
            )

        self._poller = HealthPoller(
            latency_service_url=config.latency_service_url,
            model_ids=list(self._clients.keys()),
            health_cache=self._health_cache,
            cache_lock=self._cache_lock,
            poll_interval_s=config.poll_interval_s,
            poll_timeout_s=config.poll_timeout_s,
        )
        self._poller.start()

    @property
    def supported_request_types(self) -> list[ChatRequestType]:
        """All inner clients speak OpenAI Chat Completions today."""
        return [ChatRequestType.OPENAI_CHAT]

    # -- Endpoint selection (reads from cache, never blocks on network) -----

    def _select_endpoint(self) -> str:
        """Pick a model ID.  Priority: HEALTHY > UNKNOWN > DEGRADED.  Random within tier."""
        with self._cache_lock:
            by_health: dict[EndpointHealthStatus, list[str]] = {
                h: [] for h in EndpointHealthStatus
            }
            for mid, health in self._health_cache.items():
                by_health[health].append(mid)

        for tier in (
            EndpointHealthStatus.HEALTHY,
            EndpointHealthStatus.UNKNOWN,
            EndpointHealthStatus.DEGRADED,
        ):
            if by_health[tier]:
                return random.choice(by_health[tier])

        return random.choice(list(self._clients.keys()))

    # -- Request processing (hot path — no Latency Service call) ------------

    async def call(self, ctx: ProxyContext, request: ChatRequest) -> ChatResponse:
        normalized = ChatRequestTranslationEngine.to_any_of(
            request, self.supported_request_types,
        )
        assert isinstance(normalized, OpenAIChatRequest)  # noqa: S101
        body = dict(normalized.body)

        last_exc: Exception | None = None
        tried: set[str] = set()

        for attempt in range(1 + self._config.max_retries):
            model_id = self._select_endpoint()
            if model_id in tried and len(tried) < len(self._clients):
                remaining = [m for m in self._clients if m not in tried]
                model_id = random.choice(remaining)
            tried.add(model_id)

            body["model"] = model_id
            log.debug(
                "LatencyServiceLLMBackend: attempt=%d model=%s stream=%s",
                attempt + 1, model_id, body.get("stream"),
            )

            try:
                result = await self._clients[model_id].acompletion(**body)
            except Exception as exc:
                log.warning(
                    "Model %s failed (attempt %d): %s",
                    model_id, attempt + 1, exc,
                )
                last_exc = exc
                continue

            ctx.metadata["_latency_service_model"] = model_id
            ctx.metadata["_proxy_actual_model"] = model_id

            if isinstance(result, AsyncStream):
                return StreamingChatResponse(ResponseStream(result))
            return CompletionChatResponse(result)

        raise last_exc  # type: ignore[misc]

    # -- Lifecycle ----------------------------------------------------------

    def shutdown(self) -> None:
        """Stop the background :class:`HealthPoller` daemon.

        Picked up automatically by ``NemoSwitchyardServer``'s component
        teardown hook (see ``server.py``'s lifespan context manager).
        Safe to call multiple times.
        """
        self._poller.stop()

    def is_ready(self) -> bool:
        """True once the background poller has completed at least one successful poll."""
        return self._poller.has_polled
