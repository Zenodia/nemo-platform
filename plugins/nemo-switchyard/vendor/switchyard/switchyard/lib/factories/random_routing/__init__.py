# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Random routing — usage case.

Built on the four-role chain.  Rolls a weighted coin per request and
delegates to one of two inner :class:`LLMBackend` tiers — no RouteLLM,
no HuggingFace, no LiteLLM.

The backend fits into the standard chain::

    [RequestProcessor*] → RandomRoutingLLMBackend → [ResponseProcessor*] → ResponseTranslator

Configuration is a single :class:`RandomRoutingConfig` value with two
:class:`BackendTier` entries.  Each tier picks its own wire
format via :class:`BackendFormat` — strong and weak can mix OpenAI
Chat Completions and Anthropic-native ``/v1/messages`` freely, because
each tier's inner :class:`LLMBackend` owns its own format
normalisation via :class:`ChatRequestTranslationEngine`.

Token usage and latency are recorded by :class:`StatsResponseProcessor`
and :class:`StatsLLMBackend` downstream in the chain (when
``enable_stats=True`` in the config).
"""

# Backend + config now organized under recipes/random_routing/
# The actual backend and tier classes live in switchyard.lib.backends
from switchyard.lib.backends.backend_tier import (
    BackendFormat,
    BackendTier,
)
from switchyard.lib.backends.random_routing_llm_backend import (
    CTX_RANDOM_ROUTING_TIER,
    RandomRoutingLLMBackend,
)
from switchyard.lib.factories.random_routing.factory import (
    RandomRoutingConfig,
)
from switchyard.lib.factories.random_routing.random_routing_presets import (
    RandomRoutingPresets,
)

__all__ = [
    "CTX_RANDOM_ROUTING_TIER",
    "BackendFormat",
    "RandomRoutingConfig",
    "RandomRoutingLLMBackend",
    "RandomRoutingPresets",
    "BackendTier",
]
