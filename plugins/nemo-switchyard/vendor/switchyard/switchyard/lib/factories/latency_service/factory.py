# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Latency Service routing :class:`MiddlewareFactory` and its config.

Production-grade routing for Inference Hub deployments where a central
Latency Service owns heartbeat probing and statistical profiling.
Rather than a monolithic strategy, the routing is implemented as a
custom :class:`LLMBackend` that owns:

- a pool of ``OpenAILLMClient`` instances keyed by model ID
- a thread-safe in-memory health cache
- a background daemon poller that refreshes the cache from the Latency Service
- endpoint-selection + retry logic on the request hot path

Request-format translation (Anthropic / Responses API → OpenAI Chat) is
delegated to :class:`ChatRequestTranslationEngine`, so the backend
transparently accepts any inbound format.

See ``docs/latency_service_routing_design.md`` for the full design rationale.

Importing this module registers ``LatencyServiceFactory`` under the name
``"latency_service"`` in the process-wide registry.
"""

from __future__ import annotations

from typing import Any, ClassVar

from pydantic import BaseModel

from switchyard.lib.config import (
    LatencyServiceBackendConfig,
)
from switchyard.lib.registry import BaseMiddlewareFactory, register
from switchyard.lib.request_pipeline import RequestPipeline
from switchyard.lib.response_pipeline import ResponsePipeline
from switchyard.lib.roles import LLMBackend, ResponseTranslator


class LatencyServiceFactory(BaseMiddlewareFactory[LatencyServiceBackendConfig]):
    """Builds a complete latency-service routing chain.

    Mirrors :class:`PassthroughFactory`'s shape with part-builders.
    The health-aware backend routes across many endpoints by consulting
    a centralized Latency Service; no request/response processors are
    needed (unlike random-routing which can optionally attach stats).
    """

    name: ClassVar[str] = "latency_service"
    config_class: ClassVar[type[BaseModel]] = LatencyServiceBackendConfig

    def validate(self, raw: Any) -> LatencyServiceBackendConfig:
        """Coerce a dict (or pre-built model) into ``LatencyServiceBackendConfig``."""
        if isinstance(raw, LatencyServiceBackendConfig):
            return raw
        if isinstance(raw, BaseModel):
            return LatencyServiceBackendConfig(**raw.model_dump())
        if isinstance(raw, dict):
            return LatencyServiceBackendConfig(**raw)
        raise TypeError(
            f"LatencyServiceFactory.validate() expected dict or "
            f"LatencyServiceBackendConfig, got {type(raw).__name__}"
        )

    def build_request_pipeline(
        self, config: LatencyServiceBackendConfig
    ) -> RequestPipeline:
        """No request processors needed for latency service routing."""
        return RequestPipeline([])

    def build_response_pipeline(
        self, config: LatencyServiceBackendConfig
    ) -> ResponsePipeline:
        """No response processors needed for latency service routing."""
        return ResponsePipeline([])

    def build_backend(self, config: LatencyServiceBackendConfig) -> LLMBackend:
        """Build the latency-service-aware backend."""
        from switchyard.lib.backends import LatencyServiceLLMBackend

        return LatencyServiceLLMBackend(config)

    def build_translator(
        self, config: LatencyServiceBackendConfig
    ) -> ResponseTranslator:
        """Use the default response translator."""
        from switchyard.lib.translators import DefaultResponseTranslator

        return DefaultResponseTranslator()


register(LatencyServiceFactory())
