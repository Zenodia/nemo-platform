# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Token cost estimation for LLM models.

Pricing is per 1 million tokens, stored on :class:`ModelPriceData`
so callers get attribute-level autocompletion and mypy-checked
field names instead of stringly-typed dict lookups.

Usage::

    from switchyard.lib.cost_estimator import estimate_cost, MODEL_PRICING

    stats = requests.get("http://localhost:4000/v1/routing/stats").json()
    breakdown = estimate_cost(stats["models"])
    print(f"Total: ${breakdown['total_cost']:.4f}")

See ``docs.anthropic.com/en/docs/about-claude/pricing`` for the
up-to-date Anthropic multipliers that back the Claude entries below.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ModelPriceData:
    """Per-model pricing, priced in USD per 1 million tokens.

    Attributes:
        input: Base input price (fresh tokens that hit the model).
        output: Output / completion price.
        cached: Cache-read price (prompt cache *hit*).  On Anthropic
            this is 0.1× the base input price; on OpenAI the
            provider applies the discount automatically when
            ``prompt_tokens_details.cached_tokens`` is non-zero.
        cache_write: Cache-write price (prompt cache *creation*).
            On Anthropic the 5-minute TTL is 1.25× base input; the
            1-hour TTL is 2× base input (use a separate entry if
            you need the long-TTL rate).  OpenAI has no cache-write
            premium — set this equal to ``input`` so the math
            falls through to the base price.  Defaults to 0.0 for
            providers that do not bill cache-writes separately.
    """

    input: float
    output: float
    cached: float
    cache_write: float = 0.0


# Anthropic multipliers: 5m cache write = 1.25x base input, 1h cache
# write = 2x base input, cache read = 0.1x base input.  The entries
# below use the 5m TTL prices because that is what our random router
# gets by default (no explicit ``cache_control.type = "ephemeral_1h"``
# on the request path).  Add per-tier overrides in
# :class:`BackendTier` when we start pinning the 1h TTL.
MODEL_PRICING: dict[str, ModelPriceData] = {
    # --- OpenAI / NVIDIA Inference Hub (OpenAI wire format) ---
    # OpenAI caching has no write premium; ``cache_write`` = ``input``.
    "openai/openai/gpt-5.2": ModelPriceData(
        input=1.75, output=14.00, cached=0.175, cache_write=1.75,
    ),
    "openai/openai/openai/gpt-5.2": ModelPriceData(
        input=1.75, output=14.00, cached=0.175, cache_write=1.75,
    ),
    "nvidia/nvidia/nemotron-3-super-v3": ModelPriceData(
        input=0.10, output=0.50, cached=0.01, cache_write=0.10,
    ),
    "openai/nvidia/nvidia/nemotron-3-super-v3": ModelPriceData(
        input=0.10, output=0.50, cached=0.01, cache_write=0.10,
    ),
    # --- Anthropic Claude on AWS Bedrock (via NVIDIA Inference Hub) ---
    # 5-minute cache write = 1.25x input; cache read = 0.1x input.
    "aws/anthropic/bedrock-claude-opus-4-7": ModelPriceData(
        input=5.00, output=25.00, cached=0.50, cache_write=6.25,
    ),
    "aws/anthropic/bedrock-claude-opus-4-6": ModelPriceData(
        input=5.00, output=25.00, cached=0.50, cache_write=6.25,
    ),
    "aws/anthropic/bedrock-claude-opus-4-5": ModelPriceData(
        input=5.00, output=25.00, cached=0.50, cache_write=6.25,
    ),
    # --- Anthropic Claude on Azure (via NVIDIA Inference Hub) ---
    # Same per-token pricing as the Bedrock tier at parity versions;
    # listed separately so routing decisions that pick the Azure-hosted
    # variant don't silently report $0 in cost dashboards.  Used by
    # ``RandomRoutingPresets.opus_kimi`` as the Bedrock-avoidance path
    # for Claude Code (Bedrock's 64-char ``toolSpec.name`` cap breaks
    # on auto-injected MCP tool names).  No Azure 4.7 entry because
    # Inference Hub only ships Opus 4.7 via Bedrock today — add one
    # here if/when that changes and a ``opus_47_kimi``-style Azure
    # preset follows.
    "azure/anthropic/claude-opus-4-6": ModelPriceData(
        input=5.00, output=25.00, cached=0.50, cache_write=6.25,
    ),
    "aws/anthropic/bedrock-claude-sonnet-4-6": ModelPriceData(
        input=3.00, output=15.00, cached=0.30, cache_write=3.75,
    ),
    "aws/anthropic/bedrock-claude-sonnet-4-5": ModelPriceData(
        input=3.00, output=15.00, cached=0.30, cache_write=3.75,
    ),
    "aws/anthropic/bedrock-claude-haiku-4-5": ModelPriceData(
        input=1.00, output=5.00, cached=0.10, cache_write=1.25,
    ),
    # --- Anthropic direct API aliases (no AWS prefix) ---
    "claude-opus-4-7": ModelPriceData(
        input=5.00, output=25.00, cached=0.50, cache_write=6.25,
    ),
    "claude-opus-4-6": ModelPriceData(
        input=5.00, output=25.00, cached=0.50, cache_write=6.25,
    ),
    "claude-opus-4-5": ModelPriceData(
        input=5.00, output=25.00, cached=0.50, cache_write=6.25,
    ),
    "claude-sonnet-4-6": ModelPriceData(
        input=3.00, output=15.00, cached=0.30, cache_write=3.75,
    ),
    "claude-sonnet-4-5": ModelPriceData(
        input=3.00, output=15.00, cached=0.30, cache_write=3.75,
    ),
    "claude-haiku-4-5": ModelPriceData(
        input=1.00, output=5.00, cached=0.10, cache_write=1.25,
    ),
}

_UNKNOWN_MODEL_PRICE = ModelPriceData(input=0.0, output=0.0, cached=0.0)


def estimate_model_cost(
    model: str,
    prompt_tokens: int,
    completion_tokens: int,
    cached_tokens: int = 0,
    cache_creation_tokens: int = 0,
    pricing: dict[str, ModelPriceData] | None = None,
) -> dict[str, float]:
    """Estimate cost for a single model's token usage.

    Splits input tokens into three priced buckets:

    * **Base input** = ``prompt_tokens - cached_tokens -
      cache_creation_tokens`` at the ``input`` rate.
    * **Cached** = ``cached_tokens`` at the ``cached`` rate (0.1×
      base on Anthropic, typically 10 % of base on OpenAI).
    * **Cache creation** = ``cache_creation_tokens`` at the
      ``cache_write`` rate (1.25× base on Anthropic 5m TTL; equal to
      ``input`` on OpenAI where there is no write premium).

    Args:
        model: Model name (looked up in *pricing*, defaults to
            :data:`MODEL_PRICING`).
        prompt_tokens: **Total** input tokens billed.  Must include
            the cached and cache-creation subsets — stats
            normalise Anthropic's three sibling counters into this
            semantic.
        completion_tokens: Output tokens.
        cached_tokens: Subset of ``prompt_tokens`` served from
            prompt cache (cache *read* / hit).
        cache_creation_tokens: Subset of ``prompt_tokens`` written
            to prompt cache (cache *write*).  0 for OpenAI
            responses.  Anthropic-only.
        pricing: Optional per-model price table override.  Defaults
            to :data:`MODEL_PRICING`.

    Returns:
        Dict with the three input-bucket sub-costs plus totals:
        ``base_input_cost``, ``cached_input_cost``,
        ``cache_write_cost``, ``input_cost`` (sum of the three),
        ``output_cost``, ``total_cost``.  Unknown models get zero
        prices and therefore zero costs across the board.
    """
    prices = (pricing or MODEL_PRICING).get(model, _UNKNOWN_MODEL_PRICE)

    base_input = max(prompt_tokens - cached_tokens - cache_creation_tokens, 0)
    base_cost = (base_input / 1e6) * prices.input
    cached_cost = (cached_tokens / 1e6) * prices.cached
    cache_write_cost = (cache_creation_tokens / 1e6) * prices.cache_write
    input_cost = base_cost + cached_cost + cache_write_cost
    output_cost = (completion_tokens / 1e6) * prices.output
    return {
        "base_input_cost": round(base_cost, 6),
        "cached_input_cost": round(cached_cost, 6),
        "cache_write_cost": round(cache_write_cost, 6),
        "input_cost": round(input_cost, 6),
        "output_cost": round(output_cost, 6),
        "total_cost": round(input_cost + output_cost, 6),
    }


def estimate_cost(
    models_stats: dict[str, dict[str, object]],
    pricing: dict[str, ModelPriceData] | None = None,
) -> dict[str, object]:
    """Estimate cost from a routing-stats ``models`` dict.

    Args:
        models_stats: The ``"models"`` dict from
            ``GET /v1/routing/stats``.  Each key is a model ID; each
            value has ``prompt_tokens`` + ``completion_tokens`` and
            (optionally) ``cached_tokens`` + ``cache_creation_tokens``.
            Missing optional fields default to 0 — so older stats
            dumps still compute, they just don't get the new
            cache-write accuracy benefit.  Value type is
            ``dict[str, object]`` because the routing-stats JSON
            mixes ints / floats / strings (``tier`` label) under
            the same mapping; callers should read token counters
            with :func:`int` coercion.
        pricing: Custom pricing table.  Defaults to
            :data:`MODEL_PRICING`.

    Returns:
        A dict with ``{"models": {<name>: <breakdown>}, "total_cost":
        float}`` where each ``<breakdown>`` is the return value of
        :func:`estimate_model_cost`.
    """
    models_out: dict[str, dict[str, float]] = {}
    total_cost = 0.0
    for model, data in models_stats.items():
        breakdown = estimate_model_cost(
            model=model,
            prompt_tokens=_as_int(data.get("prompt_tokens", 0)),
            completion_tokens=_as_int(data.get("completion_tokens", 0)),
            cached_tokens=_as_int(data.get("cached_tokens", 0)),
            cache_creation_tokens=_as_int(data.get("cache_creation_tokens", 0)),
            pricing=pricing,
        )
        models_out[model] = breakdown
        total_cost += breakdown["total_cost"]
    return {
        "models": models_out,
        "total_cost": round(total_cost, 6),
    }


def _as_int(value: object) -> int:
    """Best-effort coercion to ``int`` for values read out of a
    ``dict[str, object]`` stats mapping.

    Values that arrive as integers stay as integers; ``float`` gets
    truncated with :func:`int`; anything else returns 0 so malformed
    input silently degrades to "no-op" rather than raising.  The
    project's ``disallow_any_explicit`` mypy setting means we can't
    type the dict as ``dict[str, Any]`` and call ``data.get(...) + 0``
    directly.
    """
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    return 0


def _as_float(value: object) -> float:
    """Best-effort coercion to ``float`` (mirror of :func:`_as_int`)."""
    if isinstance(value, (int, float)):
        return float(value)
    return 0.0


def format_cost_report(
    stats: dict[str, object],
    pricing: dict[str, ModelPriceData] | None = None,
) -> str:
    """Format a human-readable cost report from routing stats.

    Args:
        stats: The full response from ``GET /v1/routing/stats``.
        pricing: Custom pricing table.  Defaults to
            :data:`MODEL_PRICING`.

    Returns:
        Multi-line string suitable for printing.
    """
    models_raw = stats.get("models", {})
    models_stats: dict[str, dict[str, object]] = (
        models_raw if isinstance(models_raw, dict) else {}
    )
    cost = estimate_cost(models_stats, pricing)
    cost_models_raw = cost.get("models", {})
    cost_models: dict[str, dict[str, float]] = (
        cost_models_raw if isinstance(cost_models_raw, dict) else {}
    )

    totals_raw = stats.get("total_tokens", {})
    totals: dict[str, object] = (
        totals_raw if isinstance(totals_raw, dict) else {}
    )

    lines: list[str] = []
    # One routing decision == one agent turn at the router layer, so we
    # surface it as "Turns" to match benchmark vocabulary (TerminalBench,
    # SWE-bench, PinchBench all talk turns).  ``stats["total_requests"]``
    # stays the authoritative JSON field — only the human label changes.
    lines.append(f"Turns:  {_as_int(stats.get('total_requests', 0))}")
    lines.append(
        f"Tokens: {_as_int(totals.get('total', 0)):,} "
        f"(prompt: {_as_int(totals.get('prompt', 0)):,}, "
        f"completion: {_as_int(totals.get('completion', 0)):,})"
    )
    lines.append("")
    for model, data in models_stats.items():
        model_cost = cost_models.get(model, {})
        cached = _as_int(data.get("cached_tokens", 0))
        cache_create = _as_int(data.get("cache_creation_tokens", 0))
        base_in = _as_int(data.get("prompt_tokens", 0)) - cached - cache_create
        tok_total = _as_int(data.get("total_tokens", 0))
        tok_pct = _as_float(data.get("token_pct", 0))
        comp_tok = _as_int(data.get("completion_tokens", 0))
        in_cost = model_cost.get("input_cost", 0.0)
        out_cost = model_cost.get("output_cost", 0.0)
        m_total = model_cost.get("total_cost", 0.0)
        lines.append(f"  {model}:")
        # Per-model turn count == per-model ``calls`` in the stats JSON.
        lines.append(f"    Turns:       {_as_int(data.get('calls', 0))}")
        lines.append(f"    Tokens:      {tok_total:,}  ({tok_pct:.1f}%)")
        # Break down the input token counts only when cache activity
        # happened — keeps the report terse on plain traffic.
        if cached or cache_create:
            lines.append(
                f"    Input cost:  ${in_cost:,.4f}  "
                f"({base_in:,} base + {cache_create:,} cache-write "
                f"+ {cached:,} cache-read)"
            )
        else:
            lines.append(
                f"    Input cost:  ${in_cost:,.4f}  "
                f"({base_in:,} tokens)"
            )
        lines.append(f"    Output cost: ${out_cost:,.4f}  "
                      f"({comp_tok:,} tokens)")
        lines.append(f"    Model total: ${m_total:,.4f}")
        lines.append("")
    lines.append(f"  TOTAL COST: ${_as_float(cost['total_cost']):,.4f}")
    return "\n".join(lines)
