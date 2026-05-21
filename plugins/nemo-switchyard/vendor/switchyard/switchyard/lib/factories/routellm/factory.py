# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""RouteLLM :class:`MiddlewareFactory` and its config.

Port of the legacy ``NemoSwitchyardRouteLLMStrategy`` (under
``switchyard/strategy/routellm.py``, kept for back-compat).
Routing logic is split across two slots:

* :class:`RouteLLMRequestProcessor` (request side) runs the classifier
  and stamps ``"strong"`` / ``"weak"`` into ``ctx.metadata``.
* :class:`RouteLLMLLMBackend` (backend side) reads the metadata and
  dispatches to the matching inner backend.

Config shape mirrors :class:`RandomRoutingConfig` deliberately — same
``BackendTier`` for each tier, same ``enable_stats`` flag, same
``MiddlewareBundle`` factory pattern. The only routellm-specific knobs
are ``threshold``, ``router_type``, and ``classifier_model``.

Importing this module registers :class:`RouteLLMFactory` under the name
``"routellm"`` in the process-wide registry.
"""

from __future__ import annotations

from typing import Any, ClassVar

from pydantic import BaseModel, ConfigDict, field_validator, model_validator

from switchyard.lib.backends.backend_tier import BackendTier
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


class RouteLLMConfig(BaseModel):
    """Configuration for the RouteLLM factory.

    Attributes:
        strong: Strong tier — typically the higher-quality model. Picked
            when ``classifier_score >= threshold``.
        weak: Weak tier — cheaper / faster fallback. Picked when
            ``classifier_score < threshold``.
        threshold: Decision threshold in ``[0.0, 1.0]``. The legacy strategy
            uses the same polarity (higher score = more likely to need
            the strong model).
        router_type: ``routellm`` package router name (``"mf"``,
            ``"bert"``, ``"causal_llm"``, ...). Default ``"mf"`` — the
            matrix-factorisation router.
        classifier_model: Optional override for the classifier weights
            path / HuggingFace id. ``None`` lets the routellm package
            pick its default for ``router_type``. Combined with
            ``router_type`` to form the ``ResourceCache`` key, so two
            processors with the same pair share weights.
        enable_stats: When ``True`` (default), per-tier + per-model
            usage stats are recorded and exposed via the standard
            stats response processor.
    """

    model_config = ConfigDict(frozen=True)

    strong: BackendTier
    weak: BackendTier
    threshold: float = 0.5
    router_type: str = "mf"
    classifier_model: str | None = None
    enable_stats: bool = True

    @field_validator("strong", "weak")
    @classmethod
    def _tier_model_non_empty(cls, tier: BackendTier) -> BackendTier:
        if not tier.model:
            raise ValueError("tier.model must be a non-empty string")
        return tier

    @field_validator("threshold")
    @classmethod
    def _threshold_range(cls, v: float) -> float:
        if not 0.0 <= v <= 1.0:
            raise ValueError(f"threshold must be in [0.0, 1.0], got {v!r}")
        return v

    @model_validator(mode="before")
    @classmethod
    def _coerce_legacy_string_models(cls, raw: Any) -> Any:
        """Promote legacy ``strong_model`` / ``weak_model`` strings into tiers.

        Legacy ``routellm_config`` payloads carried the model names as bare
        strings (``strong_model: "..."`` / ``weak_model: "..."``).
        Accept that shape and lift each into a :class:`BackendTier` so
        existing configs keep validating. Reject payloads that mix the
        legacy field with the modern slot for the same tier — silent
        precedence here would mask config bugs.
        """
        if not isinstance(raw, dict):
            return raw

        result = dict(raw)
        for slot, legacy_key in (("strong", "strong_model"), ("weak", "weak_model")):
            if legacy_key not in result:
                continue
            if slot in result:
                raise ValueError(
                    f"RouteLLMConfig: cannot specify both {slot!r} and "
                    f"{legacy_key!r} — pick one",
                )
            result[slot] = {"model": result.pop(legacy_key)}
        return result


class RouteLLMFactory(BaseMiddlewareFactory[RouteLLMConfig]):
    """Builds the full RouteLLM chain: classifier processor + multi-tier backend."""

    name: ClassVar[str] = "routellm"
    config_class: ClassVar[type[BaseModel]] = RouteLLMConfig

    def validate(self, raw: Any) -> RouteLLMConfig:
        if isinstance(raw, RouteLLMConfig):
            return raw
        if isinstance(raw, BaseModel):
            return RouteLLMConfig(**raw.model_dump())
        if isinstance(raw, dict):
            return RouteLLMConfig(**raw)
        raise TypeError(
            f"RouteLLMFactory.validate() expected dict or "
            f"RouteLLMConfig, got {type(raw).__name__}",
        )

    def _stats_accumulator(self, config: RouteLLMConfig) -> StatsAccumulator:
        cache: dict[int, StatsAccumulator] = self.__dict__.setdefault(
            "_accumulator_cache", {},
        )
        return cache.setdefault(id(config), StatsAccumulator())

    # ------------------------------------------------------------------
    # Part-builders
    # ------------------------------------------------------------------

    def build_request_pipeline(self, config: RouteLLMConfig) -> RequestPipeline:
        # Local import: the processor's load path pulls in routellm[serve],
        # which is a heavy optional dep. Keep it lazy.
        from switchyard.lib.processors.routellm_request_processor import (
            RouteLLMRequestProcessor,
        )

        processors: list[RequestProcessor] = [RouteLLMRequestProcessor(config)]
        if config.enable_stats:
            processors.append(StatsRequestProcessor())
        return RequestPipeline(processors)

    def build_response_pipeline(self, config: RouteLLMConfig) -> ResponsePipeline:
        processors: list[ResponseProcessor] = []
        if config.enable_stats:
            processors.append(StatsResponseProcessor(self._stats_accumulator(config)))
        return ResponsePipeline(processors)

    def build_backend(self, config: RouteLLMConfig) -> LLMBackend:
        from switchyard.lib.backends.routellm_llm_backend import (
            RouteLLMLLMBackend,
        )

        inner: LLMBackend = RouteLLMLLMBackend(config)
        if config.enable_stats:
            from switchyard.lib.backends.stats_llm_backend import (
                StatsLLMBackend,
            )

            return StatsLLMBackend(inner, self._stats_accumulator(config))
        return inner

    def build_translator(
        self, config: RouteLLMConfig,  # noqa: ARG002
    ) -> ResponseTranslator:
        return DefaultResponseTranslator()


register(RouteLLMFactory())
