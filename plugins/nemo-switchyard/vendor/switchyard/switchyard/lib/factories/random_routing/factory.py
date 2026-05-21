# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Random-routing :class:`MiddlewareFactory` and its config.

Single unified factory for all random-routing use cases:
- Standalone: uses processor + backend + translator
- IGW: uses only processor (ignores backend/translator)

Two tier instances — ``strong`` and ``weak`` — bundled with the coin
bias define the routing behaviour. Each tier picks its own
:class:`BackendFormat`, so strong and weak can mix OpenAI Chat
Completions and Anthropic-native ``/v1/messages`` freely.

Importing this module registers ``RandomRoutingFactory`` under the
name ``"random_routing"`` in the process-wide registry. Re-imports
are a no-op (Python caches module imports).
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any, ClassVar

from pydantic import BaseModel, ConfigDict, field_validator

from switchyard.lib.backends.backend_tier import (
    BackendTier,
)
from switchyard.lib.middleware_bundle import MiddlewareBundle
from switchyard.lib.processors.random_routing_request_processor import (
    RandomRoutingRequestProcessor,
)
from switchyard.lib.processors.stats_request_processor import (
    StatsRequestProcessor,
)
from switchyard.lib.processors.stats_response_processor_accumulator import (
    StatsResponseProcessor,
)
from switchyard.lib.registry import BaseMiddlewareFactory, register
from switchyard.lib.request_pipeline import RequestPipeline
from switchyard.lib.response_pipeline import ResponsePipeline
from switchyard.lib.roles import (
    LLMBackend,
    RequestProcessor,
    ResponseProcessor,
    ResponseTranslator,
)
from switchyard.lib.stats_accumulator import StatsAccumulator
from switchyard.lib.translators.default_response_translator import (
    DefaultResponseTranslator,
)


class RandomRoutingConfig(BaseModel):
    """Configuration for :class:`RandomRoutingLLMBackend`.

    Bundles both tiers + coin bias + recipe extras (``rng_seed``,
    ``preset``). Passed directly to :class:`RandomRoutingLLMBackend`
    and to :meth:`SwitchyardRecipes.random_routing_recipe`.

    Attributes:
        strong: Strong tier — typically the higher-quality model.
            Picked with probability ``strong_probability``.
        weak: Weak tier — typically the cheap / fast model. Picked
            with probability ``1 - strong_probability``.
        strong_probability: Probability in ``[0.0, 1.0]`` of routing
            to ``strong``. Default ``0.5`` (even coin flip). Higher
            value = more strong-tier traffic.
        enable_stats: When ``True`` (default), per-tier + per-model
            usage stats are recorded and exposed via
            ``GET /v1/routing/stats`` /
            ``POST /v1/routing/stats/reset``. ``False`` skips
            recording (hot path is one ``if``) and suppresses the
            HTTP endpoint.
        rng_seed: Optional integer seed for deterministic routing in
            config-driven hosts. ``None`` uses a fresh RNG. The
            recipe also accepts a pre-built ``random.Random``
            instance which overrides this value (Python-only escape
            hatch — instances aren't serializable through Pydantic).
        preset: Optional name of the :class:`RandomRoutingPresets`
            factory that produced this config. Surfaced back through
            :meth:`get_routing_stats` under ``_server_config.preset``
            so saved ``stats.json`` files self-document which
            shipping pair was used. ``None`` when built from raw
            flags.
    """

    model_config = ConfigDict(frozen=True)

    strong: BackendTier
    weak: BackendTier
    strong_probability: float = 0.5
    enable_stats: bool = True
    rng_seed: int | None = None
    preset: str | None = None

    @field_validator("strong", "weak")
    @classmethod
    def _tier_model_non_empty(cls, tier: BackendTier) -> BackendTier:
        if not tier.model:
            raise ValueError("tier.model must be a non-empty string")
        return tier

    @field_validator("strong_probability")
    @classmethod
    def _strong_prob_range(cls, v: float) -> float:
        if not 0.0 <= v <= 1.0:
            raise ValueError(
                f"strong_probability must be in [0.0, 1.0], got {v!r}"
            )
        return v


class RandomRoutingFactory(BaseMiddlewareFactory[RandomRoutingConfig]):
    """Unified random-routing factory for all use cases.

    Builds complete bundle with processor + backend + translator.
    Standalone deployments use all three; IGW hosts can use only
    the processor and ignore backend/translator.

    Bundle shape:
    | Slot              | RandomRoutingFactory |
    |-------------------| -------------------- |
    | request_pipeline  | [RandomRoutingIGW]   |
    | backend           | RandomRoutingLLMBackend (+ stats wrapper) |
    | response_pipeline | [StatsResponseProcessor] |
    | translator        | DefaultResponseTranslator |
    """

    name: ClassVar[str] = "random_routing"
    config_class: ClassVar[type[BaseModel]] = RandomRoutingConfig

    def __init__(
        self,
        *,
        stats_accumulator: StatsAccumulator | None = None,
        pre_routing_request_processors: Sequence[RequestProcessor] = (),
    ) -> None:
        self._shared_stats_accumulator = stats_accumulator
        self._pre_routing_request_processors = tuple(pre_routing_request_processors)

    def validate(self, raw: Any) -> RandomRoutingConfig:
        """Coerce a dict (or pre-built model) into ``RandomRoutingConfig``."""
        if isinstance(raw, RandomRoutingConfig):
            return raw
        if isinstance(raw, BaseModel):
            return RandomRoutingConfig(**raw.model_dump())
        if isinstance(raw, dict):
            return RandomRoutingConfig(**raw)
        raise TypeError(
            f"RandomRoutingFactory.validate() expected dict or "
            f"RandomRoutingConfig, got {type(raw).__name__}"
        )

    def _stats_accumulator(self, config: RandomRoutingConfig) -> StatsAccumulator:
        """Return the shared accumulator for a build pass.

        The response processor and ``StatsLLMBackend`` must share one
        accumulator so token counts, latency, and backend-call counters
        land in one bucket. Keyed by ``id(config)`` so separate build
        passes (different config objects) get independent accumulators.
        """
        if self._shared_stats_accumulator is not None:
            return self._shared_stats_accumulator
        cache: dict[int, StatsAccumulator] = self.__dict__.setdefault(
            "_accumulator_cache", {},
        )
        return cache.setdefault(id(config), StatsAccumulator())

    # ------------------------------------------------------------------
    # Part-builders
    # ------------------------------------------------------------------

    def build_request_pipeline(self, config: RandomRoutingConfig) -> RequestPipeline:
        processors: list[RequestProcessor] = []
        if config.enable_stats:
            processors.append(StatsRequestProcessor())
        processors.extend(self._pre_routing_request_processors)
        processors.append(RandomRoutingRequestProcessor(config))
        return RequestPipeline(processors)

    def build_response_pipeline(self, config: RandomRoutingConfig) -> ResponsePipeline:
        processors: list[ResponseProcessor] = []
        if config.enable_stats:
            processors.append(StatsResponseProcessor(self._stats_accumulator(config)))
        return ResponsePipeline(processors)

    def build_backend(self, config: RandomRoutingConfig) -> LLMBackend:
        # Local import: pulls in the multi-tier backend + (transitively)
        # the OpenAI / Anthropic SDKs. Deferred until ``build_backend``
        # is actually called so IGW hosts don't pay the cost.
        from switchyard.lib.backends.random_routing_llm_backend import (
            RandomRoutingLLMBackend,
        )

        inner: LLMBackend = RandomRoutingLLMBackend(config)
        if config.enable_stats:
            from switchyard.lib.backends.stats_llm_backend import (
                StatsLLMBackend,
            )

            return StatsLLMBackend(inner, self._stats_accumulator(config))
        return inner

    def build_translator(
        self, config: RandomRoutingConfig,  # noqa: ARG002
    ) -> ResponseTranslator:
        return DefaultResponseTranslator()


def _bundle_from_config(config: RandomRoutingConfig) -> MiddlewareBundle:
    """Build a bundle from the unified config (used by the recipe).

    Convenience for :meth:`SwitchyardRecipes.random_routing_recipe`
    so the recipe stays a one-liner.
    """
    return MiddlewareBundle.from_factory(RandomRoutingFactory(), config)


register(RandomRoutingFactory())
