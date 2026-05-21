# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""OSS-router :class:`MiddlewareFactory` and config.

Importing this module registers ``OSSRouterFactory`` under the name
``"oss_router"`` in the process-wide registry. Registration is a no-op
on re-import (Python caches modules).
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any, ClassVar

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from switchyard.lib.backends.backend_tier import BackendTier
from switchyard.lib.middleware_bundle import MiddlewareBundle
from switchyard.lib.processors.plugin_routing_request_processor import (
    PluginRoutingRequestProcessor,
)
from switchyard.lib.processors.stats_request_processor import StatsRequestProcessor
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


class OSSRouterTier(BaseModel):
    """One tier the plugin may pick.

    The plugin only sees ``label`` (sent in the handshake's
    ``available_tiers``); the ``BackendTier`` is private to the proxy and
    carries the credentials, base URL, and wire format. Keeping this
    split is what lets the plugin run as untrusted code without leaking
    backend secrets.
    """

    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)

    label: str = Field(min_length=1)
    tier: BackendTier


class OSSRouterConfig(BaseModel):
    """Configuration for :class:`OSSRouterFactory`.

    Attributes:
        plugin_command: argv (list) or shell string used to launch the
            plugin executable. Spawned once at chain startup, kept alive
            for the lifetime of the chain, and shut down with the rest
            of the components.
        tiers: Ordered list of tiers the plugin may pick. The first
            entry is the defensive default (used when the plugin
            doesn't run, e.g. during shutdown races).
        fallback_tier: Optional tier label used when the plugin
            errors, times out, or crashes. ``None`` means fail closed.
            Operators opt into fallbacks explicitly so a misbehaving
            plugin can't silently drift traffic onto an unintended tier.
        request_timeout_s: Per-request plugin timeout. Routing decisions
            should be sub-second; default is intentionally tight.
        handshake_timeout_s: Time budget for the startup handshake.
        env: Optional extra env vars merged on top of the proxy's
            environment when spawning the plugin.
        expose_metadata_keys: ``ctx.metadata`` keys to forward to the
            plugin on every ``route`` call. Empty by default — the
            plugin only sees the request summary unless an operator
            explicitly opts a key in.
        enable_stats: When ``True`` (default), the chain collects the
            same per-request stats the random-routing chain does.
    """

    model_config = ConfigDict(frozen=True)

    plugin_command: list[str] | str
    tiers: tuple[OSSRouterTier, ...]
    fallback_tier: str | None = None
    request_timeout_s: float = 5.0
    handshake_timeout_s: float = 10.0
    env: dict[str, str] | None = None
    expose_metadata_keys: tuple[str, ...] = ()
    enable_stats: bool = True

    @field_validator("plugin_command")
    @classmethod
    def _command_non_empty(cls, value: list[str] | str) -> list[str] | str:
        if isinstance(value, str) and not value.strip():
            raise ValueError("plugin_command must be a non-empty string")
        if isinstance(value, list) and not value:
            raise ValueError("plugin_command must be a non-empty list")
        return value

    @field_validator("tiers")
    @classmethod
    def _tiers_non_empty(cls, value: tuple[OSSRouterTier, ...]) -> tuple[OSSRouterTier, ...]:
        if not value:
            raise ValueError("OSSRouterConfig requires at least one tier")
        labels = [t.label for t in value]
        if len(set(labels)) != len(labels):
            raise ValueError(
                f"OSSRouterConfig tier labels must be unique; got {labels}",
            )
        return value

    @model_validator(mode="after")
    def _fallback_tier_known(self) -> OSSRouterConfig:
        if self.fallback_tier is not None:
            labels = {t.label for t in self.tiers}
            if self.fallback_tier not in labels:
                raise ValueError(
                    f"fallback_tier {self.fallback_tier!r} is not in "
                    f"tiers {sorted(labels)}",
                )
        return self


class OSSRouterFactory(BaseMiddlewareFactory[OSSRouterConfig]):
    """Factory for plugin-driven routing chains.

    Bundle shape::

        | Slot              | OSSRouterFactory                        |
        | request_pipeline  | [Stats?, PluginRoutingRequestProcessor] |
        | backend           | OSSRouterLLMBackend (+ stats wrapper)   |
        | response_pipeline | [Stats?]                                |
        | translator        | DefaultResponseTranslator               |
    """

    name: ClassVar[str] = "oss_router"
    config_class: ClassVar[type[BaseModel]] = OSSRouterConfig

    def __init__(
        self,
        *,
        stats_accumulator: StatsAccumulator | None = None,
        pre_routing_request_processors: Sequence[RequestProcessor] = (),
    ) -> None:
        self._shared_stats_accumulator = stats_accumulator
        self._pre_routing_request_processors = tuple(pre_routing_request_processors)

    def validate(self, raw: Any) -> OSSRouterConfig:
        if isinstance(raw, OSSRouterConfig):
            return raw
        if isinstance(raw, BaseModel):
            return OSSRouterConfig(**raw.model_dump())
        if isinstance(raw, dict):
            return OSSRouterConfig(**raw)
        raise TypeError(
            f"OSSRouterFactory.validate() expected dict or OSSRouterConfig, "
            f"got {type(raw).__name__}",
        )

    def _stats_accumulator(self, config: OSSRouterConfig) -> StatsAccumulator:
        if self._shared_stats_accumulator is not None:
            return self._shared_stats_accumulator
        cache: dict[int, StatsAccumulator] = self.__dict__.setdefault(
            "_accumulator_cache", {},
        )
        return cache.setdefault(id(config), StatsAccumulator())

    # ------------------------------------------------------------------
    # Part-builders
    # ------------------------------------------------------------------

    def build_request_pipeline(self, config: OSSRouterConfig) -> RequestPipeline:
        processors: list[RequestProcessor] = []
        if config.enable_stats:
            processors.append(StatsRequestProcessor())
        processors.extend(self._pre_routing_request_processors)
        processors.append(PluginRoutingRequestProcessor(
            plugin_command=config.plugin_command,
            tier_models={t.label: t.tier.model for t in config.tiers},
            fallback_tier=config.fallback_tier,
            request_timeout_s=config.request_timeout_s,
            handshake_timeout_s=config.handshake_timeout_s,
            env=config.env,
            expose_metadata_keys=config.expose_metadata_keys,
        ))
        return RequestPipeline(processors)

    def build_response_pipeline(self, config: OSSRouterConfig) -> ResponsePipeline:
        processors: list[ResponseProcessor] = []
        if config.enable_stats:
            processors.append(StatsResponseProcessor(self._stats_accumulator(config)))
        return ResponsePipeline(processors)

    def build_backend(self, config: OSSRouterConfig) -> LLMBackend:
        # Local import: pulls in the multi-tier backend (and transitively
        # the OpenAI / Anthropic SDKs). Deferred so callers that only need
        # the request pipeline (e.g. an IGW host) don't pay the cost.
        from switchyard.lib.backends.oss_router_llm_backend import (
            OSSRouterLLMBackend,
        )

        tiers = {t.label: t.tier for t in config.tiers}
        inner: LLMBackend = OSSRouterLLMBackend(tiers=tiers)
        if config.enable_stats:
            from switchyard.lib.backends.stats_llm_backend import StatsLLMBackend

            return StatsLLMBackend(inner, self._stats_accumulator(config))
        return inner

    def build_translator(
        self,
        config: OSSRouterConfig,  # noqa: ARG002
    ) -> ResponseTranslator:
        return DefaultResponseTranslator()


def _bundle_from_config(config: OSSRouterConfig) -> MiddlewareBundle:
    """Convenience for :meth:`SwitchyardRecipes.oss_router_recipe`."""
    return MiddlewareBundle.from_factory(OSSRouterFactory(), config)


register(OSSRouterFactory())
