# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Thread-safe accumulator for per-model stats.

Tracks:
- Per-model: calls / errors / token counts (prompt / completion / cached /
  cache_creation / reasoning) / backend-only latency (``model_call_latency``) /
  end-to-end latency (``total_latency``) / derived averages and cache hit
  rate.
- Global: total requests / errors / token aggregate / routing overhead
  histogram (chain time minus backend time).
- Cost: computed from token counters using
  :func:`switchyard.lib.cost_estimator.estimate_cost`.

Schema serves ``/v1/routing/stats`` and
``foundation/usage_cases/random_routing/random_routing_stats.py`` so the
existing ``benchmark/run_terminal_bench_harbor.sh`` consumer works
unchanged against passthrough.

Shared by:
- :class:`StatsRequestProcessor` — stamps chain-start time.
- :class:`StatsLLMBackend` — records backend-call latency + errors.
- :class:`StatsResponseProcessor` — records tokens + total latency + overhead.
"""

from __future__ import annotations

import heapq
import threading
from dataclasses import dataclass, field
from typing import Any


@dataclass
class _LatencyHistogram:
    """Running latency stats in ms — count / min / max / avg / p50 / p99 / total."""

    count: int = 0
    total_ms: float = 0.0
    min_ms: float = float("inf")
    max_ms: float = 0.0
    # Bounded reservoir; 10k samples is enough for stable p99 without unbounded growth.
    _samples: list[float] = field(default_factory=list)
    _max_samples: int = 10_000

    def record(self, latency_ms: float) -> None:
        self.count += 1
        self.total_ms += latency_ms
        self.min_ms = min(self.min_ms, latency_ms)
        self.max_ms = max(self.max_ms, latency_ms)
        if len(self._samples) < self._max_samples:
            heapq.heappush(self._samples, latency_ms)
        else:
            heapq.heappushpop(self._samples, latency_ms)

    def to_dict(self) -> dict[str, float | int]:
        if self.count == 0:
            return {
                "count": 0, "total_ms": 0.0,
                "min_ms": 0.0, "max_ms": 0.0, "avg_ms": 0.0,
                "p50_ms": 0.0, "p99_ms": 0.0,
            }
        sorted_samples = sorted(self._samples)
        n = len(sorted_samples)
        p50 = sorted_samples[n // 2]
        p99 = sorted_samples[min(n - 1, int(n * 0.99))]
        return {
            "count": self.count,
            "total_ms": round(self.total_ms, 2),
            "min_ms": round(self.min_ms, 2),
            "max_ms": round(self.max_ms, 2),
            "avg_ms": round(self.total_ms / self.count, 2),
            "p50_ms": round(p50, 2),
            "p99_ms": round(p99, 2),
        }


@dataclass
class _ModelStats:
    calls: int = 0
    errors: int = 0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    cached_tokens: int = 0
    cache_creation_tokens: int = 0
    reasoning_tokens: int = 0
    model_call_latency: _LatencyHistogram = field(default_factory=_LatencyHistogram)
    total_latency: _LatencyHistogram = field(default_factory=_LatencyHistogram)
    tier: str | None = None  # "strong" or "weak" for random routing, None for passthrough


class StatsAccumulator:
    """Thread-safe stats store.

    Writes are serialized via :class:`threading.Lock`. Reads return a fully
    computed snapshot suitable for JSON serialization.
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._by_model: dict[str, _ModelStats] = {}
        self._total_requests = 0
        self._total_errors = 0
        self._routing_overhead = _LatencyHistogram()

    async def record_success(
        self,
        *,
        model: str,
        backend_latency_ms: float | None = None,
        tier: str | None = None,
    ) -> None:
        """Called by :class:`StatsLLMBackend` when the backend returns normally."""
        with self._lock:
            self._total_requests += 1
            s = self._by_model.setdefault(model, _ModelStats())
            s.calls += 1
            if tier is not None:
                s.tier = tier
            if backend_latency_ms is not None:
                s.model_call_latency.record(backend_latency_ms)

    async def record_error(self, *, model: str, tier: str | None = None) -> None:
        """Called by :class:`StatsLLMBackend` when the backend raises."""
        with self._lock:
            self._total_requests += 1
            self._total_errors += 1
            s = self._by_model.setdefault(model, _ModelStats())
            s.errors += 1
            if tier is not None:
                s.tier = tier

    async def record_usage(
        self,
        *,
        model: str,
        prompt_tokens: int = 0,
        completion_tokens: int = 0,
        cached_tokens: int = 0,
        cache_creation_tokens: int = 0,
        reasoning_tokens: int = 0,
        total_latency_ms: float | None = None,
        routing_overhead_ms: float | None = None,
        tier: str | None = None,
    ) -> None:
        """Called by :class:`StatsResponseProcessor` after the response is built."""
        with self._lock:
            s = self._by_model.setdefault(model, _ModelStats())
            s.prompt_tokens += prompt_tokens
            s.completion_tokens += completion_tokens
            s.cached_tokens += cached_tokens
            s.cache_creation_tokens += cache_creation_tokens
            s.reasoning_tokens += reasoning_tokens
            if tier is not None:
                s.tier = tier
            if total_latency_ms is not None:
                s.total_latency.record(total_latency_ms)
            if routing_overhead_ms is not None:
                self._routing_overhead.record(routing_overhead_ms)

    async def snapshot(self) -> dict[str, Any]:
        return self.snapshot_sync()

    def snapshot_sync(self) -> dict[str, Any]:
        """Return a thread-safe snapshot for sync readers such as launcher TUIs."""
        with self._lock:
            return self._snapshot_unlocked()

    async def reset(self) -> None:
        self.reset_sync()

    def reset_sync(self) -> None:
        """Reset all counters from sync contexts."""
        with self._lock:
            self._reset_unlocked()

    def _reset_unlocked(self) -> None:
        self._by_model.clear()
        self._total_requests = 0
        self._total_errors = 0
        self._routing_overhead = _LatencyHistogram()

    def _snapshot_unlocked(self) -> dict[str, Any]:
        totals = {
            "prompt": 0, "completion": 0,
            "cached": 0, "cache_creation": 0, "reasoning": 0,
        }
        for s in self._by_model.values():
            totals["prompt"] += s.prompt_tokens
            totals["completion"] += s.completion_tokens
            totals["cached"] += s.cached_tokens
            totals["cache_creation"] += s.cache_creation_tokens
            totals["reasoning"] += s.reasoning_tokens
        totals["total"] = totals["prompt"] + totals["completion"]

        models: dict[str, dict[str, Any]] = {}
        for model, s in self._by_model.items():
            req_pct = (
                round(s.calls / self._total_requests * 100, 2)
                if self._total_requests else 0.0
            )
            tok_total = s.prompt_tokens + s.completion_tokens
            token_pct = (
                round(tok_total / totals["total"] * 100, 2)
                if totals["total"] else 0.0
            )
            avg_prompt = s.prompt_tokens / s.calls if s.calls else 0.0
            avg_completion = s.completion_tokens / s.calls if s.calls else 0.0
            cache_hit_rate = (
                s.cached_tokens / s.prompt_tokens if s.prompt_tokens else 0.0
            )
            models[model] = {
                "calls": s.calls,
                "errors": s.errors,
                "request_pct": req_pct,
                "prompt_tokens": s.prompt_tokens,
                "completion_tokens": s.completion_tokens,
                "total_tokens": tok_total,
                "token_pct": token_pct,
                "cached_tokens": s.cached_tokens,
                "cache_creation_tokens": s.cache_creation_tokens,
                "reasoning_tokens": s.reasoning_tokens,
                "avg_prompt_tokens": round(avg_prompt, 2),
                "avg_completion_tokens": round(avg_completion, 2),
                "cache_hit_rate": round(cache_hit_rate, 4),
                "model_call_latency": s.model_call_latency.to_dict(),
                "total_latency": s.total_latency.to_dict(),
                "tier": s.tier,
            }

        cost_estimate = _compute_cost(models)

        # Compute per-tier stats from the models dict (for random routing).
        tiers: dict[str, dict[str, Any]] = {}
        for tier_name in ("strong", "weak"):
            tier_models = [
                (name, s) for name, s in self._by_model.items()
                if s.tier == tier_name
            ]
            if tier_models:
                # Pick the first (and typically only) model for this tier.
                # For random routing, each tier has exactly one model.
                tier_model_name = tier_models[0][0]
                tier_stats = tier_models[0][1]
                tok_total = tier_stats.prompt_tokens + tier_stats.completion_tokens
                token_pct = (
                    round(tok_total / totals["total"] * 100, 2)
                    if totals["total"] else 0.0
                )
                tiers[tier_name] = {
                    "model": tier_model_name,
                    "calls": tier_stats.calls,
                    "request_pct": (
                        round(tier_stats.calls / self._total_requests * 100, 2)
                        if self._total_requests else 0.0
                    ),
                    "prompt_tokens": tier_stats.prompt_tokens,
                    "completion_tokens": tier_stats.completion_tokens,
                    "total_tokens": tok_total,
                    "token_pct": token_pct,
                }

        return {
            "total_requests": self._total_requests,
            "total_errors": self._total_errors,
            "total_tokens": totals,
            "models": models,
            "tiers": tiers,
            "routing_overhead": self._routing_overhead.to_dict(),
            "cost_estimate": cost_estimate,
        }


def _compute_cost(models: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """Estimate cost from the ``models`` dict using the shared pricing table.

    Safe: on any error (unknown model, malformed data) returns a zero estimate
    so a transient issue in cost math doesn't 500 the stats endpoint.
    """
    try:
        from switchyard.lib.cost_estimator import estimate_cost

        return estimate_cost(models)
    except Exception:
        return {"models": {}, "total_cost": 0.0}
