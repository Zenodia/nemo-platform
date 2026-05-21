# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""FastAPI endpoint module exposing stats over HTTP.

Serves both ``/v1/stats`` (native) and ``/v1/routing/stats`` (alias
for backwards compatibility — same response body).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from fastapi import APIRouter

from switchyard.lib.endpoints.base import Endpoint as NemoSwitchyardEndpoint
from switchyard.lib.live_stats_collector import LiveStatsCollector
from switchyard.lib.stats_accumulator import StatsAccumulator

if TYPE_CHECKING:
    from fastapi import FastAPI


StatsSource = StatsAccumulator | LiveStatsCollector


class StatsEndpoint(NemoSwitchyardEndpoint):
    """Exposes stats via ``GET /v1/stats`` (+ ``/v1/routing/stats`` alias).

    Contributed
    automatically by :class:`StatsResponseProcessor.get_endpoint` — no
    manual wiring required.

    The ``/v1/routing/stats`` alias exists so existing consumers of the
    historical endpoint path (``benchmark/run_terminal_bench_harbor.sh``, external
    dashboards) work against passthrough without any config change.
    """

    def __init__(self, stats: StatsSource) -> None:
        self._stats = stats

    def register(self, app: FastAPI) -> None:
        routes = APIRouter()
        stats = self._stats

        async def get_stats() -> dict[str, Any]:
            """Snapshot of per-model request / token / latency / cost stats."""
            if isinstance(stats, LiveStatsCollector):
                return stats.to_dict()
            return await stats.snapshot()

        async def reset_stats() -> dict[str, str]:
            """Zero all stats counters."""
            if isinstance(stats, LiveStatsCollector):
                stats.reset()
            else:
                await stats.reset()
            return {"status": "reset"}

        # native path.
        routes.get("/v1/stats")(get_stats)
        routes.post("/v1/stats/reset")(reset_stats)
        # Compatibility alias.
        routes.get("/v1/routing/stats")(get_stats)
        routes.post("/v1/routing/stats/reset")(reset_stats)

        app.include_router(routes, tags=["Stats"])
