# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Concrete :class:`LLMBackend` implementations + colocated backend config.

Each file defines one ``LLMBackend`` (or a backend-scoped config dataclass —
``LLMBackendTuning``). Re-exports live here for ergonomic imports like
``from switchyard.lib.backends import OpenAILLMBackend``.
"""

from switchyard.lib.backends.anthropic_native_llm_backend import (
    AnthropicNativeLLMBackend,
)
from switchyard.lib.backends.backend_format_resolver import (
    BackendFormatResolution,
    BackendFormatResolver,
)
from switchyard.lib.backends.health_poller import (
    EndpointHealthStatus,
    HealthPoller,
)
from switchyard.lib.backends.latency_service_llm_backend import (
    LatencyServiceLLMBackend,
)
from switchyard.lib.backends.llm_backend_tuning import (
    LLMBackendTuning,
    ReasoningEffort,
)
from switchyard.lib.backends.openai_llm_backend import (
    OpenAILLMBackend,
)
from switchyard.lib.backends.stats_llm_backend import (
    STATS_BACKEND_LATENCY_MS_KEY,
    StatsLLMBackend,
)

__all__ = [
    "STATS_BACKEND_LATENCY_MS_KEY",
    "AnthropicNativeLLMBackend",
    "BackendFormatResolution",
    "BackendFormatResolver",
    "EndpointHealthStatus",
    "HealthPoller",
    "LatencyServiceLLMBackend",
    "LLMBackendTuning",
    "OpenAILLMBackend",
    "ReasoningEffort",
    "StatsLLMBackend",
]
