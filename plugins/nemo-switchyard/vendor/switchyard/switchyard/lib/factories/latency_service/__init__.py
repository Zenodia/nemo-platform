# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Latency Service routing — usage case.

Production-grade routing for Inference Hub deployments where a central
Latency Service owns heartbeat probing and statistical profiling.
Rather than a monolithic strategy, this usage case is implemented as
a custom LLMBackend that owns a pool of OpenAI clients, a thread-safe
in-memory health cache, and endpoint-selection + retry logic.

See ``docs/latency_service_routing_design.md`` for the full design rationale.
"""

from switchyard.lib.backends import (
    EndpointHealthStatus,
    HealthPoller,
    LatencyServiceLLMBackend,
)
from switchyard.lib.config import (
    LatencyServiceBackendConfig,
    LatencyServiceEndpoint,
)
from switchyard.lib.factories.latency_service.factory import (
    LatencyServiceFactory,
)

__all__ = [
    "EndpointHealthStatus",
    "HealthPoller",
    "LatencyServiceBackendConfig",
    "LatencyServiceEndpoint",
    "LatencyServiceLLMBackend",
    "LatencyServiceFactory",
]
