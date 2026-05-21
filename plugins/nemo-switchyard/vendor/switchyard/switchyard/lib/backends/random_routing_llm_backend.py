# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""``LLMBackend`` that routes across two inner tiers by rolling a weighted dice.

Subclass of :class:`MultiLLMBackend` with random-routing-specific additions:

* Construction from a :class:`RandomRoutingConfig` value (turning each
  :class:`BackendTier` into concrete inner backends via
  :meth:`MultiLLMBackend.build_tiers`).
* Coin-flip pick in :meth:`_pick_tier` (one ``rng.random() <
  strong_probability`` per request).
* Stats tracking via :class:`RoutingStats` with per-tier + per-model counters.
* ``_server_config_dict`` with random-routing-specific knobs
  (``preset``, ``strong_probability``, tier details).
* Streaming usage taps and per-format usage recording.
* ``/v1/routing/stats`` HTTP endpoint via :meth:`get_endpoint`.

Chain integration::

    [RequestProcessor*] → RandomRoutingLLMBackend → [ResponseProcessor*] → ResponseTranslator

Inbound format translation stays in each tier's inner backend — they
each run their own :meth:`ChatRequestTranslationEngine.to_any_of`
normalisation at the top of ``call()``, so this router never touches
request bodies beyond rewriting ``request.body["model"]`` to the picked
tier's model.

See ``docs/random_routing_v2_design.md`` for the full design.
"""

from __future__ import annotations

import logging
from importlib.metadata import PackageNotFoundError, version
from typing import TYPE_CHECKING, Any

from switchyard.lib.backends.backend_tier import BackendTier
from switchyard.lib.backends.multi_llm_backend import MultiLLMBackend
from switchyard.lib.chat_response.anthropic import (
    AnthropicChatResponse,
    AnthropicStreamingChatResponse,
)
from switchyard.lib.chat_response.openai_chat import (
    CompletionChatResponse,
    StreamingChatResponse,
)
from switchyard.lib.chat_response.openai_responses import (
    ResponsesApiChatResponse,
    ResponsesApiStreamingChatResponse,
)
from switchyard.lib.factories.random_routing.factory import (
    RandomRoutingConfig,
)
from switchyard.lib.roles import LLMBackend

if TYPE_CHECKING:
    from anthropic.types import RawMessageStreamEvent
    from openai.types.chat import ChatCompletionChunk
    from openai.types.responses import ResponseStreamEvent

    from switchyard.lib.chat_request.base import ChatRequest
    from switchyard.lib.chat_response.base import ChatResponse
    from switchyard.lib.endpoints.base import Endpoint as NemoSwitchyardEndpoint
    from switchyard.lib.proxy_context import ProxyContext

log = logging.getLogger(__name__)

CTX_RANDOM_ROUTING_TIER = "_random_routing_tier"


class RandomRoutingLLMBackend(MultiLLMBackend):
    """LLM router across two inner ``LLMBackend`` tiers.

    Built from a :class:`RandomRoutingConfig`. On construction the
    router turns each :class:`BackendTier` into the appropriate
    concrete inner backend via :meth:`MultiLLMBackend.build_tiers` — one
    fresh client instance per tier, so strong and weak can have
    independent ``api_key`` / ``base_url`` / wire format.

    Tier selection is driven by :class:`RandomRoutingRequestProcessor`,
    which makes the coin-flip decision and stamps the result in
    ``ctx.metadata[CTX_RANDOM_ROUTING_TIER]``. This backend reads that
    decision and dispatches to the appropriate tier.

    Per-request flow (inherited from :class:`MultiLLMBackend`):

    1. :meth:`_pick_tier` reads the tier choice from context (set by
       the upstream request processor).
    2. Base class rewrites ``request.body["model"]`` to the picked
       tier's model, stamps ``ctx.metadata`` with the picked model,
       records the routing decision, and delegates to the inner backend.
    3. Base class taps the response for usage stats (handles all six
       streaming + non-streaming :class:`ChatResponse` variants).

    Args:
        config: The full routing configuration (both tiers + coin
            bias + ``enable_stats``). All validation —
            ``strong_probability`` range, non-empty ``model`` —
            happens on the config's ``__post_init__`` so
            misconfigurations fail at config construction rather than
            at backend construction.
        preset: Optional name of the :class:`RandomRoutingPresets`
            factory that produced ``config``. Surfaced back through
            :meth:`get_routing_stats` under ``_server_config.preset``
            so post-run review of a saved ``stats.json`` can tell at a
            glance which shipping model pair (if any) was used.
            ``None`` when the router was built from raw flags.
    """

    def __init__(
        self,
        config: RandomRoutingConfig,
    ) -> None:
        super().__init__(
            tiers=self.build_tiers({
                "strong": config.strong,
                "weak": config.weak,
            }),
        )

        self._config = config
        self._preset = config.preset
        self._enable_stats = config.enable_stats

        log.info(
            "RandomRoutingLLMBackend: strong=%s[%s], weak=%s[%s], "
            "p_strong=%.3f, stats=%s",
            config.strong.model, config.strong.backend_format.value,
            config.weak.model, config.weak.backend_format.value,
            config.strong_probability,
            "on" if config.enable_stats else "off",
        )

    # ------------------------------------------------------------------
    # Back-compat attribute shims — pre-MultiLLMBackend tests reach into
    # ``._strong_backend`` / ``._weak_backend`` to patch inner clients.
    # ------------------------------------------------------------------

    @property
    def _strong_backend(self) -> LLMBackend:
        return self._backends["strong"]

    @_strong_backend.setter
    def _strong_backend(self, value: LLMBackend) -> None:
        self._backends["strong"] = value

    @property
    def _weak_backend(self) -> LLMBackend:
        return self._backends["weak"]

    @_weak_backend.setter
    def _weak_backend(self, value: LLMBackend) -> None:
        self._backends["weak"] = value

    # ------------------------------------------------------------------
    # Subclass extension points
    # ------------------------------------------------------------------

    def _pick_tier(self, ctx: ProxyContext, request: ChatRequest) -> str:  # noqa: ARG002
        """Read tier choice from context (set by RandomRoutingRequestProcessor).

        Defaults to ``"strong"`` if the upstream processor didn't run for
        some reason (defensive — defensive default).
        """
        # The tier label is set by RandomRoutingRequestProcessor (upstream in the chain).
        # This backend only reads the label and dispatches to the matching inner backend.
        tier = ctx.metadata.get(CTX_RANDOM_ROUTING_TIER, "strong")
        return tier if isinstance(tier, str) else "strong"

    def _on_response(
        self, ctx: ProxyContext, response: ChatResponse, tier: str, model: str,
    ) -> None:
        """Response hook (stats handled by StatsLLMBackend + StatsResponseProcessor)."""
        pass

    def _server_config_dict(self) -> dict[str, Any]:
        """Augment base config with random-routing-specific fields.

        The ``_server_config`` block on stats.json is the single most
        useful postmortem artifact — answers "what was each tier
        running under" without re-deriving from CLI flags or git
        history. ``api_key`` is deliberately omitted (writes are
        sometimes committed to repos); ``has_api_key`` is the
        lossless-enough proxy.
        """
        try:
            switchyard_version: str | None = version("switchyard")
        except PackageNotFoundError:
            switchyard_version = None

        def _tier(tier: BackendTier) -> dict[str, Any]:
            tuning = tier.tuning
            effort = (
                tuning.reasoning_effort.value
                if tuning.reasoning_effort is not None
                else None
            )
            return {
                "model": tier.model,
                "backend_format": tier.backend_format.value,
                "reasoning_effort": effort,
                "max_output_tokens": tuning.max_output_tokens,
                "base_url": tier.base_url,
                "has_api_key": tier.api_key is not None,
            }

        return {
            "preset": self._preset,
            "strong_probability": self._config.strong_probability,
            "enable_stats": self._config.enable_stats,
            "switchyard_version": switchyard_version,
            "strong": _tier(self._config.strong),
            "weak": _tier(self._config.weak),
        }

    # ------------------------------------------------------------------
    # Public stats API
    # ------------------------------------------------------------------

    def get_routing_stats(self) -> dict[str, object]:
        """Return server config metadata.

        Note: per-tier stats are now accumulated by StatsLLMBackend + StatsAccumulator
        and exposed via the generic /v1/stats endpoint with tier-aware grouping.
        """
        return {"_server_config": self._server_config_dict()}

    def reset_routing_stats(self) -> None:
        """No-op: per-tier stats are reset via StatsAccumulator.reset()."""
        pass

    def get_endpoint(self) -> NemoSwitchyardEndpoint | None:
        """Contribute the ``/v1/routing/stats`` HTTP endpoint.

        Returns ``None`` when ``enable_stats`` is ``False`` so a
        health-probe-only server surface stays clean.
        """
        if not self._enable_stats:
            return None
        # stats exposed via StatsResponseProcessor
        return None

    # ------------------------------------------------------------------
    # Usage recording — dispatches on ChatResponse subclass
    # ------------------------------------------------------------------

    def _attach_usage_recording(
        self, response: ChatResponse, model: str, tier: str,
    ) -> None:
        """Record usage for *response*, or install a tap on the stream.

        Non-streaming: extract usage from the SDK body immediately
        and commit to the stats under the lock.

        Streaming: install a ``tap()`` that buffers per-chunk state
        and commits once a usage-bearing chunk arrives. The tap is
        idempotent — for Anthropic, ``RawMessageDeltaEvent.usage``
        reports cumulative output tokens over the life of the stream,
        so we keep the **last** observation and record it once at
        stream end. For OpenAI, ``stream_options.include_usage=True``
        causes the SDK to emit exactly one usage-bearing chunk at the
        end, so we record the first (and only) non-None reading.
        """
        if isinstance(response, CompletionChatResponse):
            self._record_openai_chat_usage(response, model, tier)
            return
        if isinstance(response, ResponsesApiChatResponse):
            self._record_openai_responses_usage(response, model, tier)
            return
        if isinstance(response, AnthropicChatResponse):
            self._record_anthropic_usage(response, model, tier)
            return
        if isinstance(response, StreamingChatResponse):
            self._install_openai_chat_stream_tap(response, model, tier)
            return
        if isinstance(response, ResponsesApiStreamingChatResponse):
            self._install_openai_responses_stream_tap(response, model, tier)
            return
        if isinstance(response, AnthropicStreamingChatResponse):
            self._install_anthropic_stream_tap(response, model, tier)
            return

        log.debug(
            "%s: skipping usage recording for unknown response type %s",
            type(self).__name__, type(response).__name__,
        )

    # -- Non-streaming extractors --------------------------------------

    def _record_openai_chat_usage(
        self, response: CompletionChatResponse, model: str, tier: str,
    ) -> None:
        usage = getattr(response.body, "usage", None)
        if usage is None:
            return
        prompt = getattr(usage, "prompt_tokens", 0) or 0
        completion = getattr(usage, "completion_tokens", 0) or 0
        cached = 0
        prompt_details = getattr(usage, "prompt_tokens_details", None)
        if prompt_details is not None:
            cached = getattr(prompt_details, "cached_tokens", 0) or 0
        self._commit_usage(
            model, tier,
            prompt_tokens=prompt,
            completion_tokens=completion,
            cached_tokens=cached,
        )

    def _record_openai_responses_usage(
        self, response: ResponsesApiChatResponse, model: str, tier: str,
    ) -> None:
        usage = getattr(response.body, "usage", None)
        if usage is None:
            return
        prompt = getattr(usage, "input_tokens", 0) or 0
        completion = getattr(usage, "output_tokens", 0) or 0
        cached = 0
        in_details = getattr(usage, "input_tokens_details", None)
        if in_details is not None:
            cached = getattr(in_details, "cached_tokens", 0) or 0
        self._commit_usage(
            model, tier,
            prompt_tokens=prompt,
            completion_tokens=completion,
            cached_tokens=cached,
        )

    def _record_anthropic_usage(
        self, response: AnthropicChatResponse, model: str, tier: str,
    ) -> None:
        """Anthropic's three input counters are siblings (not parent/child).

        ``input_tokens`` = fresh; ``cache_creation_input_tokens`` =
        cache writes (1.25× base price); ``cache_read_input_tokens`` =
        cache reads (0.1× base price). To align with OpenAI-shaped
        ``prompt_tokens`` semantics (total billed input) we sum all
        three.
        """
        usage = getattr(response.body, "usage", None)
        if usage is None:
            return
        input_tok = getattr(usage, "input_tokens", 0) or 0
        cache_create = getattr(usage, "cache_creation_input_tokens", 0) or 0
        cache_read = getattr(usage, "cache_read_input_tokens", 0) or 0
        completion = getattr(usage, "output_tokens", 0) or 0
        self._commit_usage(
            model, tier,
            prompt_tokens=input_tok + cache_create + cache_read,
            completion_tokens=completion,
            cached_tokens=cache_read,
            cache_creation_tokens=cache_create,
        )

    # -- Streaming tap installers --------------------------------------

    def _install_openai_chat_stream_tap(
        self, response: StreamingChatResponse, model: str, tier: str,
    ) -> None:
        committed = {"done": False}

        async def tap(chunk: ChatCompletionChunk) -> None:
            if committed["done"]:
                return
            usage = getattr(chunk, "usage", None)
            if usage is None:
                return
            prompt = getattr(usage, "prompt_tokens", 0) or 0
            completion = getattr(usage, "completion_tokens", 0) or 0
            cached = 0
            prompt_details = getattr(usage, "prompt_tokens_details", None)
            if prompt_details is not None:
                cached = getattr(prompt_details, "cached_tokens", 0) or 0
            self._commit_usage(
                model, tier,
                prompt_tokens=prompt,
                completion_tokens=completion,
                cached_tokens=cached,
            )
            committed["done"] = True

        response.stream.tap(tap)

    def _install_openai_responses_stream_tap(
        self, response: ResponsesApiStreamingChatResponse,
        model: str, tier: str,
    ) -> None:
        committed = {"done": False}

        async def tap(event: ResponseStreamEvent) -> None:
            if committed["done"]:
                return
            inner = getattr(event, "response", None)
            if inner is None:
                return
            usage = getattr(inner, "usage", None)
            if usage is None:
                return
            prompt = getattr(usage, "input_tokens", 0) or 0
            completion = getattr(usage, "output_tokens", 0) or 0
            cached = 0
            in_details = getattr(usage, "input_tokens_details", None)
            if in_details is not None:
                cached = getattr(in_details, "cached_tokens", 0) or 0
            self._commit_usage(
                model, tier,
                prompt_tokens=prompt,
                completion_tokens=completion,
                cached_tokens=cached,
            )
            committed["done"] = True

        response.stream.tap(tap)

    def _install_anthropic_stream_tap(
        self, response: AnthropicStreamingChatResponse,
        model: str, tier: str,
    ) -> None:
        """Tap that accumulates Anthropic streaming usage.

        ``message_start`` carries initial input + cache counters;
        ``message_delta`` carries cumulative output and may update
        cache counters; ``message_stop`` is the contract "no further
        chunks". We commit on ``message_stop`` using the latest
        observation of each field.
        """
        acc: dict[str, int] = {
            "input_tokens": 0,
            "output_tokens": 0,
            "cache_creation_input_tokens": 0,
            "cache_read_input_tokens": 0,
        }
        committed = {"done": False}

        def _merge(usage: object) -> None:
            for key in acc:
                value = getattr(usage, key, None)
                if isinstance(value, int):
                    acc[key] = value

        async def tap(event: RawMessageStreamEvent) -> None:
            if committed["done"]:
                return
            event_type = getattr(event, "type", None)
            if event_type == "message_start":
                msg = getattr(event, "message", None)
                if msg is not None:
                    usage = getattr(msg, "usage", None)
                    if usage is not None:
                        _merge(usage)
                return
            if event_type == "message_delta":
                usage = getattr(event, "usage", None)
                if usage is not None:
                    _merge(usage)
                return
            if event_type == "message_stop":
                input_tok = acc["input_tokens"]
                cache_create = acc["cache_creation_input_tokens"]
                cache_read = acc["cache_read_input_tokens"]
                completion = acc["output_tokens"]
                self._commit_usage(
                    model, tier,
                    prompt_tokens=input_tok + cache_create + cache_read,
                    completion_tokens=completion,
                    cached_tokens=cache_read,
                    cache_creation_tokens=cache_create,
                )
                committed["done"] = True

        response.stream.tap(tap)

    # -- Lock-protected commit -----------------------------------------

    def _commit_usage(
        self,
        model: str,
        tier: str,
        *,
        prompt_tokens: int,
        completion_tokens: int,
        cached_tokens: int = 0,
        cache_creation_tokens: int = 0,
    ) -> None:
        """No-op: usage is recorded by StatsResponseProcessor + StatsAccumulator."""
        pass
