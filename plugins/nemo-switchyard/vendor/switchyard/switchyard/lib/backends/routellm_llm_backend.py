# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""``LLMBackend`` that dispatches across two tiers based on a routing decision.

Subclass of :class:`MultiLLMBackend` whose ``_pick_tier`` reads the tier
label stamped by :class:`RouteLLMRequestProcessor` upstream in the chain.
The classifier scoring lives in the request processor; this backend only
dispatches.

Chain integration::

    [RouteLLMRequestProcessor] → RouteLLMLLMBackend → [...] → ResponseTranslator

Inbound format translation stays in each tier's inner backend — they
each run their own :meth:`ChatRequestTranslationEngine.to_any_of`
normalisation at the top of ``call()``, so this router never touches
request bodies beyond rewriting ``request.body["model"]`` to the picked
tier's model (handled by :class:`MultiLLMBackend`).

Mirrors :class:`RandomRoutingLLMBackend`'s shape — the only difference
is *who* picks the tier (random coin vs. classifier score) and *where*
the pick happens (inside the backend vs. upstream in a request
processor).
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from switchyard.lib.backends.multi_llm_backend import MultiLLMBackend

if TYPE_CHECKING:
    from switchyard.lib.chat_request.base import ChatRequest
    from switchyard.lib.factories.routellm.factory import RouteLLMConfig
    from switchyard.lib.proxy_context import ProxyContext

log = logging.getLogger(__name__)

# Stamped by RouteLLMRequestProcessor; read by RouteLLMLLMBackend._pick_tier.
CTX_ROUTELLM_TIER = "_routellm_tier"


class RouteLLMLLMBackend(MultiLLMBackend):
    """Two-tier LLM backend driven by an upstream classifier decision.

    The tier label is set by :class:`RouteLLMRequestProcessor` (which
    runs the classifier and writes ``ctx.metadata[CTX_ROUTELLM_TIER]``).
    This backend only reads the label and dispatches to the matching
    inner backend — no scoring logic here.

    Defaults to ``"strong"`` if the upstream processor didn't run for
    some reason (defensive — defensive default when no prompt could
    be extracted).
    """

    def __init__(self, config: RouteLLMConfig) -> None:
        super().__init__(
            tiers=self.build_tiers({
                "strong": config.strong,
                "weak": config.weak,
            }),
        )
        self._config = config
        log.info(
            "RouteLLMLLMBackend: strong=%s[%s], weak=%s[%s], threshold=%.3f, "
            "router=%s, stats=%s",
            config.strong.model, config.strong.backend_format.value,
            config.weak.model, config.weak.backend_format.value,
            config.threshold,
            config.router_type,
            "on" if config.enable_stats else "off",
        )

    def _pick_tier(self, ctx: ProxyContext, request: ChatRequest) -> str:  # noqa: ARG002
        tier = ctx.metadata.get(CTX_ROUTELLM_TIER)
        if tier not in ("strong", "weak"):
            log.warning(
                "RouteLLMLLMBackend: CTX_ROUTELLM_TIER not set or invalid (%r) — "
                "defaulting to 'strong'. Did RouteLLMRequestProcessor run?",
                tier,
            )
            tier = "strong"
        return tier
