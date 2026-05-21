# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Switchyard recipes — production-grade wiring compositions.

Recipes compose core components (RequestProcessor, LLMBackend, ResponseProcessor,
ResponseTranslator) into coherent end-to-end pipelines for common use cases:
- RouteLLM strong/weak routing with intelligent cost-optimization
- Latency-aware health-polling across endpoints
- Random routing for A/B testing
- Passthrough to single backend with format translation
- HTTP payload export (intake sink)
"""

from switchyard.lib.factories.intake_sink import (
    IntakeSinkConfig,
    IntakeSinkFactory,
)
from switchyard.lib.factories.latency_service import (
    EndpointHealthStatus,
    HealthPoller,
    LatencyServiceBackendConfig,
    LatencyServiceEndpoint,
    LatencyServiceLLMBackend,
)
from switchyard.lib.factories.random_routing import (
    BackendFormat,
    BackendTier,
    RandomRoutingConfig,
    RandomRoutingLLMBackend,
    RandomRoutingPresets,
)

__all__ = [
    # Latency Service
    "EndpointHealthStatus",
    "HealthPoller",
    "LatencyServiceBackendConfig",
    "LatencyServiceEndpoint",
    "LatencyServiceLLMBackend",
    # Random Routing
    "BackendFormat",
    "BackendTier",
    "RandomRoutingConfig",
    "RandomRoutingLLMBackend",
    "RandomRoutingPresets",
    # Intake Sink
    "IntakeSinkConfig",
    "IntakeSinkFactory",
]
