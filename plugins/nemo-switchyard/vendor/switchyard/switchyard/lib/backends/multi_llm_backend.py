# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Multi-tier ``LLMBackend`` base class — dispatch one tier per request.

Accepts an arbitrary number of tiers — each tier is a (backend, model)
pair. Subclasses supply only the *picking strategy* via :meth:`_pick_tier`;
everything else — request-model mutation, ctx stamping, streaming usage
taps — is inherited.

Inbound format translation stays in the inner backends — each tier's
backend (e.g. :class:`OpenAILLMBackend`, :class:`AnthropicNativeLLMBackend`)
runs its own :meth:`ChatRequestTranslationEngine.to_any_of` at the top
of its ``call()``, so the multi-backend itself is format-agnostic and
just delegates ``(ctx, request)`` once a tier is chosen.

Stats and HTTP endpoint wiring are left to subclasses to implement as
they see fit (e.g., random routing with RoutingStats, or a future
RouteLLM backend with different observability).
"""

from __future__ import annotations

import logging
from abc import abstractmethod
from collections.abc import Mapping
from typing import TYPE_CHECKING

from switchyard.lib.backends.backend_tier import (
    BackendFormat,
    BackendTier,
)
from switchyard.lib.chat_request.base import ChatRequestType
from switchyard.lib.roles import LLMBackend

if TYPE_CHECKING:
    from switchyard.lib.chat_request.base import ChatRequest
    from switchyard.lib.chat_response.base import ChatResponse
    from switchyard.lib.proxy_context import ProxyContext

log = logging.getLogger(__name__)


class MultiLLMBackend(LLMBackend):
    """N-tier LLM backend base — dispatch to one tier per request.

    Subclasses provide:

    * Inner backends + model names per tier via :meth:`build_tiers`, or
      by passing pre-built backend/model pairs directly to ``__init__``.
    * :meth:`_pick_tier` — return a tier label (arbitrary string).

    Optional overrides:
    * :meth:`get_endpoint` — contribute HTTP endpoints for stats / control.
    """

    def __init__(
        self,
        *,
        tiers: dict[str, tuple[LLMBackend, str]],
    ) -> None:
        """Initialize with a dict of tier_label -> (backend, model).

        Args:
            tiers: Dict mapping tier label (e.g. "strong", "weak") to a
                tuple of (backend, model_name).
        """
        self._backends: dict[str, LLMBackend] = {}
        self._models: dict[str, str] = {}
        for label, (backend, model) in tiers.items():
            self._backends[label] = backend
            self._models[label] = model

    # ------------------------------------------------------------------
    # Generic BackendTier construction helpers
    # ------------------------------------------------------------------

    @classmethod
    def build_tiers(
        cls,
        tiers: Mapping[str, BackendTier],
    ) -> dict[str, tuple[LLMBackend, str]]:
        """Build ``__init__`` tier tuples from generic ``BackendTier`` config.

        This keeps wire-format dispatch reusable for any multi-backend
        router. Random routing uses it today; a RouteLLM backend can
        use the same helper later without copying OpenAI / Anthropic /
        auto-format construction logic.
        """
        built: dict[str, tuple[LLMBackend, str]] = {}
        for label, tier in tiers.items():
            backend = cls.build_backend(tier)
            log.info(
                "%s: configured tier=%s model=%s backend=%s requested_format=%s",
                cls.__name__,
                label,
                tier.model,
                type(backend).__name__,
                tier.backend_format.value,
            )
            built[label] = (backend, tier.model)
        return built

    @classmethod
    def build_backend(cls, tier: BackendTier) -> LLMBackend:
        """Build one concrete inner backend from generic ``BackendTier`` config."""
        return cls._build_backend(tier)

    @classmethod
    def _build_backend(cls, tier: BackendTier) -> LLMBackend:
        """Build the concrete inner ``LLMBackend`` for a tier.

        Dispatches on :attr:`BackendTier.backend_format`:

        * :attr:`BackendFormat.AUTO` → resolved once at construction
          time using the shared backend-format resolver, then built as
          either :class:`AnthropicNativeLLMBackend` or
          :class:`OpenAILLMBackend`.
        * :attr:`BackendFormat.OPENAI` → :class:`OpenAILLMBackend`
          wrapping a fresh :class:`OpenAILLMClient`. Hits
          ``POST /v1/chat/completions``.
        * :attr:`BackendFormat.ANTHROPIC` →
          :class:`AnthropicNativeLLMBackend` wrapping a fresh
          :class:`AsyncAnthropic` client. ``base_url`` has its
          trailing ``/v1`` stripped via :func:`strip_v1_suffix`
          because the Anthropic SDK appends ``/v1/messages`` itself.

        Local imports keep module load cost low and avoid pulling in
        provider SDKs when callers only use the tier dataclass.
        """
        if tier.backend_format is BackendFormat.AUTO:
            return cls._build_auto_backend(tier)

        if tier.backend_format is BackendFormat.OPENAI:
            return cls._build_openai_backend(tier)

        if tier.backend_format is BackendFormat.ANTHROPIC:
            return cls._build_anthropic_backend(tier)

        raise ValueError(
            f"Unsupported backend_format: {tier.backend_format!r}"
        )

    @classmethod
    def _build_auto_backend(cls, tier: BackendTier) -> LLMBackend:
        from switchyard.lib.backends.backend_format_resolver import (
            BackendFormatResolver,
        )

        resolution = BackendFormatResolver.resolve(tier)
        if resolution.backend_format is BackendFormat.OPENAI:
            log.info(
                "%s: auto backend for model=%s selected OpenAILLMBackend: %s.",
                cls.__name__,
                tier.model,
                resolution.reason,
            )
            return cls._build_openai_backend(tier)

        if resolution.backend_format is BackendFormat.ANTHROPIC:
            log.info(
                "%s: auto backend for model=%s selected "
                "AnthropicNativeLLMBackend: %s.",
                cls.__name__,
                tier.model,
                resolution.reason,
            )
            return cls._build_anthropic_backend(tier)

        raise ValueError(
            f"Unsupported resolved backend_format: {resolution.backend_format!r}",
        )

    @staticmethod
    def _build_openai_backend(tier: BackendTier) -> LLMBackend:
        from switchyard.lib.backends.openai_llm_backend import (
            OpenAILLMBackend,
        )
        from switchyard.lib.llm_client import OpenAILLMClient

        return OpenAILLMBackend(
            OpenAILLMClient(
                api_key=tier.api_key,
                base_url=tier.base_url,
                timeout=tier.timeout,
            ),
            tuning=tier.tuning,
        )

    @staticmethod
    def _build_anthropic_backend(tier: BackendTier) -> LLMBackend:
        from anthropic import AsyncAnthropic

        from switchyard.lib.backends.anthropic_native_llm_backend import (
            AnthropicNativeLLMBackend,
        )
        from switchyard.lib.backends.backend_format_resolver import (
            strip_v1_suffix,
        )
        from switchyard.telemetry import get_telemetry_headers

        # ``AsyncAnthropic`` rejects ``base_url=None`` / ``timeout=None``
        # on some older SDK versions, so pass only args the caller set.
        base_url = (
            strip_v1_suffix(tier.base_url)
            if tier.base_url is not None
            else None
        )
        telemetry = get_telemetry_headers()
        if base_url is None and tier.timeout is None:
            client = AsyncAnthropic(api_key=tier.api_key, default_headers=telemetry)
        elif base_url is not None and tier.timeout is None:
            client = AsyncAnthropic(
                api_key=tier.api_key,
                base_url=base_url,
                default_headers=telemetry,
            )
        elif base_url is None and tier.timeout is not None:
            client = AsyncAnthropic(
                api_key=tier.api_key,
                timeout=tier.timeout,
                default_headers=telemetry,
            )
        else:
            client = AsyncAnthropic(
                api_key=tier.api_key,
                base_url=base_url,
                timeout=tier.timeout,
                default_headers=telemetry,
            )
        return AnthropicNativeLLMBackend(client, tuning=tier.tuning)

    # ------------------------------------------------------------------
    # LLMBackend protocol
    # ------------------------------------------------------------------

    @property
    def supported_request_types(self) -> list[ChatRequestType]:
        """Accept any inbound format — inner backends normalise."""
        return list(ChatRequestType)

    async def call(
        self, ctx: ProxyContext, request: ChatRequest,
    ) -> ChatResponse:
        tier_label = self._pick_tier(ctx, request)
        if tier_label not in self._backends:
            raise ValueError(
                f"_pick_tier returned {tier_label!r}; expected one of "
                f"{sorted(self._backends)}",
            )
        backend = self._backends[tier_label]
        model = self._models[tier_label]

        # Every ``ChatRequest`` subclass exposes ``body`` via its
        # provider ``TypedDict``; the abstract base doesn't declare it,
        # hence the ignore.
        request.body["model"] = model  # type: ignore[attr-defined]

        ctx.metadata["_routing_tier"] = tier_label
        ctx.metadata["_proxy_actual_model"] = model

        log.debug(
            "MultiLLMBackend(%s): picked tier=%s model=%s",
            type(self).__name__, tier_label, model,
        )

        response = await backend.call(ctx, request)
        self._on_response(ctx, response, tier_label, model)

        return response

    # ------------------------------------------------------------------
    # Subclass extension points
    # ------------------------------------------------------------------

    @abstractmethod
    def _pick_tier(self, ctx: ProxyContext, request: ChatRequest) -> str:
        """Return a tier label for this request (e.g. 'strong', 'weak')."""

    def _on_response(
        self, ctx: ProxyContext, response: ChatResponse, tier: str, model: str,
    ) -> None:
        """Hook for subclass-specific response handling (stats, logging, etc).

        Called after the backend returns but before returning to the caller.
        Default does nothing; override to add stats recording, taps, etc.
        """
