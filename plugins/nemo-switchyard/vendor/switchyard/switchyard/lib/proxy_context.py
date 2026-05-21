# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""ProxyContext for sharing metadata between chain components."""

from dataclasses import dataclass, field
from typing import Any

# ---------------------------------------------------------------------------
# Metadata key constants
# ---------------------------------------------------------------------------
# Use these instead of bare strings to avoid silent typos and to make
# cross-component key contracts discoverable at import time.

#: Stores a deep-copy of the incoming request dict.
#: Written by RequestBufferProcessor.
CTX_ORIGINAL_REQUEST = "original_request"

#: Model that was actually used for the LLM call, after any routing/override.
#: Written by routing backends and processors.
CTX_PROXY_ACTUAL_MODEL = "_proxy_actual_model"

#: Routing metadata dict produced by RouteLLMRequestProcessor.
CTX_ROUTING = "_routing"

#: Original inbound format stored by translation layers.
CTX_ORIGINAL_FORMAT = "_original_format"

#: Original model name stored by translation layers.
CTX_ORIGINAL_MODEL = "_original_model"

#: Target wire format chosen by a router (e.g. random routing, RouteLLM).
#: Written by router RequestProcessor implementations; read by
#: FormatTranslateRequestProcessor.
CTX_TARGET_FORMAT = "_target_format"


@dataclass
class ProxyContext:
    """
    Shared metadata context passed through the chain.

    This is a generic metadata container that chain components
    (processors, backends, translators) can use to share data across
    a single request-response cycle.

    Prefer the module-level ``CTX_*`` constants over bare string keys
    to avoid silent typos and make cross-component contracts discoverable.

    Example:
        from switchyard.lib.proxy_context import CTX_ORIGINAL_REQUEST, ProxyContext
        ctx = ProxyContext()
        ctx.metadata[CTX_ORIGINAL_REQUEST] = incoming_request.copy()
        ctx.metadata["custom_data"] = {"key": "value"}
    """

    metadata: dict[str, Any] = field(default_factory=dict)
