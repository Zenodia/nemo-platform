# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Request processor that stamps the request start time onto the proxy context.

Paired with :class:`StatsResponseProcessor` to compute per-request latency.
"""

from __future__ import annotations

import time

from switchyard.lib.chat_request.base import ChatRequest
from switchyard.lib.proxy_context import ProxyContext
from switchyard.lib.roles import RequestProcessor

# ProxyContext metadata key written by StatsRequestProcessor and read by
# StatsResponseProcessor to compute end-to-end latency.
STATS_STARTED_AT_KEY = "_stats_started_at"


class StatsRequestProcessor(RequestProcessor):
    """Record request start time in ``ctx.metadata`` for latency measurement.

    The companion :class:`StatsResponseProcessor` reads
    :data:`STATS_STARTED_AT_KEY` back out to compute the end-to-end
    latency for the request and attribute it to the right model.
    """

    async def process(self, ctx: ProxyContext, request: ChatRequest) -> ChatRequest:
        ctx.metadata[STATS_STARTED_AT_KEY] = time.perf_counter()
        return request
