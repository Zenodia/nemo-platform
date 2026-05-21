# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""``LLMBackend`` that dispatches by reading the tier label set by the OSS
routing plugin's request processor.

The decision happens upstream in :class:`PluginRoutingRequestProcessor`,
which calls the external plugin and stamps
``ctx.metadata[CTX_OSS_ROUTER_TIER]``. This backend just reads that
label and dispatches — same shape as :class:`RandomRoutingLLMBackend`,
but with the picking logic moved out of process.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from switchyard.lib.backends.multi_llm_backend import MultiLLMBackend

if TYPE_CHECKING:
    from collections.abc import Mapping

    from switchyard.lib.backends.backend_tier import BackendTier
    from switchyard.lib.chat_request.base import ChatRequest
    from switchyard.lib.proxy_context import ProxyContext

log = logging.getLogger(__name__)

#: Metadata key set by :class:`PluginRoutingRequestProcessor` and read here
#: at dispatch time. Public so plugin-aware response processors and stats
#: collectors can use the same key.
CTX_OSS_ROUTER_TIER = "_oss_router_tier"


class OSSRouterLLMBackend(MultiLLMBackend):
    """Multi-tier LLM backend steered by an external routing plugin.

    Tier labels are arbitrary strings agreed between the chain config and
    the plugin (via the handshake's ``available_tiers``). The processor
    sets ``ctx.metadata[CTX_OSS_ROUTER_TIER]`` to the chosen label;
    :meth:`_pick_tier` reads it.

    The first tier in *tiers* is used as the defensive default when
    metadata is missing (e.g. a request that bypassed the processor).
    """

    def __init__(self, *, tiers: Mapping[str, BackendTier]) -> None:
        if not tiers:
            raise ValueError("OSSRouterLLMBackend requires at least one tier")
        super().__init__(tiers=self.build_tiers(dict(tiers)))
        # First-inserted tier label — used as the defensive default in
        # _pick_tier when the processor didn't run for some reason.
        self._default_tier = next(iter(tiers))
        log.info(
            "OSSRouterLLMBackend: tiers=%s default=%s",
            tuple(tiers),
            self._default_tier,
        )

    def _pick_tier(self, ctx: ProxyContext, request: ChatRequest) -> str:  # noqa: ARG002
        tier = ctx.metadata.get(CTX_OSS_ROUTER_TIER, self._default_tier)
        if not isinstance(tier, str) or tier not in self._backends:
            log.warning(
                "OSSRouterLLMBackend: ctx tier %r is not registered; "
                "falling back to default %r",
                tier,
                self._default_tier,
            )
            return self._default_tier
        return tier
