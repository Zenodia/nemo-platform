# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""backend that calls ``/v1/messages`` directly, no format translation.

Counterpart to :class:`OpenAILLMBackend`, but for backends that speak
the Anthropic Messages API natively (e.g. ``aws/anthropic/*`` and
``azure/anthropic/*`` models on NVIDIA Inference Hub). When the backend
accepts Anthropic-shaped requests and returns Anthropic-shaped
responses, we can skip the Anthropic↔OpenAI-Chat round-trip that
:class:`OpenAILLMBackend` applies.

Declares Anthropic as its only supported request type. Non-Anthropic
inbound (OpenAI Chat) is normalized via
``ChatRequestTranslationEngine.to_any_of`` — which already knows how
to translate OpenAI Chat → Anthropic. Responses API inbound raises
``NotImplementedError`` until someone wires that translation.

Why this backend exists separately from :class:`OpenAILLMBackend`
=================================================================

The NVIDIA Inference Hub exposes both ``/v1/chat/completions`` and
``/v1/messages`` for Anthropic models on Bedrock and Azure, so on
paper either backend class can serve the same upstream model.  The
two backends are kept distinct because they differ on **who owns the
Chat ↔ Anthropic-Messages translation correctness**:

* :class:`OpenAILLMBackend` sends Chat Completions over the wire.
  The hub's LiteLLM does the Chat → Bedrock-Anthropic / Azure-Anthropic
  translation server-side.
* :class:`AnthropicNativeLLMBackend` sends Anthropic Messages over the
  wire.  We do any inbound Chat → Messages translation in process
  via :class:`ChatRequestTranslationEngine`; the hub's LiteLLM is
  effectively a passthrough.

Hub-side LiteLLM (1.83.7 as of 2026-04-25) has reproducible bugs in
its Chat-Completions→Anthropic translation that newer Anthropic
models reject:

* **Opus 4.7 + ``reasoning_effort=high`` over Chat Completions** —
  Hub LiteLLM emits ``thinking={"type": "enabled", "budget_tokens":
  …}`` (the legacy shape).  Opus 4.7 on Bedrock rejects with
  ``"thinking.type.enabled is not supported for this model. Use
  thinking.type.adaptive and output_config.effort to control thinking
  behavior."``.  Routing Opus 4.7 through this backend (we emit
  ``thinking={"type": "adaptive"}`` + ``output_config={"effort":
  …}`` directly) avoids the broken translator.  See the
  ``opus_47_*`` presets in
  :mod:`switchyard.lib.factories.random_routing.random_routing_presets`
  — they all force ``BackendFormat.ANTHROPIC`` for the strong tier.

* **Hub-side thinking-config loss on the
  ``LiteLLM-anthropic-provider → /v1/messages`` path** — When a
  client (specifically, harbor's ``terminus-2`` agent with
  ``--model anthropic/<opus>``) builds a Messages request with
  ``temperature=1.0`` baked in, *something* between harbor's
  LiteLLM, our switchyard, and the hub's LiteLLM drops the thinking
  config before it reaches the upstream model.  The model then sees
  ``temperature=1.0`` with no recognised thinking marker and rejects
  with ``"`temperature` may only be set to 1 when thinking is enabled
  or in adaptive mode."``.  Reproduced 2026-04-25 against three
  deployments — Bedrock 4.7, Bedrock 4.6, *and* Azure 4.6 — all return
  the identical Anthropic-API-level error message, so this is **not**
  a Bedrock-specific quirk; the rule lives at the model API.  We
  verified at the ``ANTHROPIC_LOG=debug`` trace level that *we* send
  the correct shape; the loss happens on a hop we don't control.
  Currently mitigated by keeping ``harbor_model=openai/gpt-5.2`` (or
  any other ``openai/`` prefix) for Opus benchmarks.  See
  ``.agents/skills/run-tb-experiment/SKILL.md`` "Known limitation:
  ``harbor_model=anthropic/<opus-model>`` is broken on the NVIDIA
  hub" for the operator-facing note.

The deliberate split — one backend per wire format — is what gives
operators a per-tier knob (``BackendTier.backend_format``) to
choose where translation correctness lives.  Folding both wire
formats into a single dual-format backend would re-create the hub's
broken Chat-Completions translation path for the Anthropic side, so
:meth:`supported_request_types` is intentionally **single-format**
even though the hub itself accepts both endpoints.
"""

from __future__ import annotations

import inspect
import logging
from typing import Any

from anthropic import AsyncAnthropic, BadRequestError

from switchyard.lib.backends.llm_backend_tuning import (
    LLMBackendTuning,
    ReasoningEffort,
)
from switchyard.lib.chat_request.anthropic import AnthropicChatRequest
from switchyard.lib.chat_request.base import ChatRequest, ChatRequestType
from switchyard.lib.chat_response.anthropic import (
    AnthropicChatResponse,
    AnthropicResponseStream,
    AnthropicStreamingChatResponse,
)
from switchyard.lib.chat_response.base import ChatResponse
from switchyard.lib.proxy_context import ProxyContext
from switchyard.lib.roles import LLMBackend
from switchyard.lib.translation.anthropic_openai import (
    normalize_anthropic_tool_use_ids,
)
from switchyard.lib.translation.request_engine import (
    ChatRequestTranslationEngine,
)

log = logging.getLogger(__name__)

_THINKING_REJECTION_MARKERS = (
    "adaptive thinking",
    "thinking is not supported",
    "thinking.type",
    "output_config",
    "effort",
    "reasoning",
)

_FALLBACK_SDK_KNOWN_KWARGS: frozenset[str] = frozenset({
    # Required by the Anthropic SDK overload; routing these into extra_body
    # makes messages.create fail before request construction.
    "max_tokens",
    "messages",
    "model",
    # Current optional Anthropic Messages fields.
    "cache_control",
    "container",
    "inference_geo",
    "metadata",
    "output_config",
    "service_tier",
    "stop_sequences",
    "stream",
    "system",
    "temperature",
    "thinking",
    "tool_choice",
    "tools",
    "top_k",
    "top_p",
    # Transport / passthrough kwargs accepted by the SDK.
    "extra_body",
    "extra_headers",
    "extra_query",
    "timeout",
})


def _bad_request_mentions_thinking_effort(exc: BadRequestError) -> bool:
    """Return whether a 400 appears to reject thinking/output effort."""

    parts = [str(exc)]
    body = getattr(exc, "body", None)
    if body is not None:
        parts.append(repr(body))
    text = " ".join(parts).lower()
    return any(marker in text for marker in _THINKING_REJECTION_MARKERS)


def _thinking_reconfiguration_message(
    *,
    model: str,
    effort: object,
    upstream_error: BadRequestError,
) -> str:
    return (
        f"Model {model!r} rejected Switchyard's configured Anthropic thinking "
        f"tuning with effort={effort!r}. Reconfigure this LLM to use a model "
        "that supports adaptive thinking/output_config.effort, or disable "
        "Switchyard reasoning tuning for this route. For Claude Code "
        "passthrough: `switchyard configure --target claude "
        "--claude-reasoning-effort none`, or one-off "
        "`switchyard launch claude --reasoning-effort none`. "
        "For random-routing, set the affected tier to "
        "`--strong-reasoning-effort none` or `--weak-reasoning-effort none`. "
        f"Upstream error: {upstream_error}"
    )


class AnthropicNativeLLMBackend(LLMBackend):
    """Backend that POSTs to an Anthropic-compatible ``/v1/messages`` endpoint.

    Normalizes inbound requests to :class:`AnthropicChatRequest` and
    calls ``AsyncAnthropic.messages.create``. Returns
    :class:`AnthropicChatResponse` (non-stream) or
    :class:`AnthropicStreamingChatResponse` (stream).

    Optional :class:`LLMBackendTuning` applies two per-request
    transformations before the upstream call:

    * ``max_output_tokens`` — injected as ``body["max_tokens"]`` only
      when the client's body carries no ``max_tokens``.  Anthropic
      requires ``max_tokens``, so this doubles as a safety net.
    * ``reasoning_effort`` — translated to Anthropic's native
      adaptive thinking + ``output_config.effort`` pattern (the
      recommended shape on Claude Opus 4.6 / 4.7 and Sonnet 4.6):

      * :attr:`ReasoningEffort.DISABLED` sets
        ``body["thinking"] = {"type": "disabled"}``.
      * :attr:`ReasoningEffort.LOW` / ``MEDIUM`` / ``HIGH`` /
        ``XHIGH`` / ``MAX`` set
        ``body["thinking"] = {"type": "adaptive"}`` and
        ``body["output_config"]["effort"] = value``.  A caller-supplied
        ``output_config`` with other keys is preserved.
      * ``None`` (passthrough) leaves ``body["thinking"]`` and
        ``body["output_config"]`` alone.

      Regardless of the tuning, ``body["reasoning_effort"]`` is
      *always* stripped because it is not a valid Anthropic field and
      the SDK's runtime validator rejects it.

    Model compatibility: this backend is built for **Claude Opus 4.6
    / 4.7 and Claude Sonnet 4.6**.  ``XHIGH`` is Opus 4.7 only; older
    models in the 4.x range reject the effort parameter or adaptive
    thinking entirely.  Callers targeting older Claude models should
    set ``reasoning_effort=None`` and write ``body["thinking"]``
    explicitly.
    """

    def __init__(
        self,
        client: AsyncAnthropic,
        tuning: LLMBackendTuning | None = None,
    ) -> None:
        self._client = client
        self._tuning = tuning or LLMBackendTuning()
        # Discover the installed SDK's accepted ``messages.create``
        # kwargs once. ``AsyncMessages.create`` does runtime kwarg
        # validation and raises ``TypeError`` for unknown fields —
        # Claude Code sends newer Anthropic fields like
        # ``context_management`` that may not yet be in the installed
        # SDK's TypedDict. Anything the SDK doesn't name we shuttle
        # through ``extra_body``, which the SDK merges into the wire
        # payload without validation.
        try:
            self._sdk_known_kwargs = frozenset(
                inspect.signature(client.messages.create).parameters.keys(),
            )
        except (ValueError, TypeError):
            log.debug(
                "AnthropicNativeLLMBackend: could not introspect "
                "messages.create signature; using fallback kwarg allowlist",
            )
            self._sdk_known_kwargs = _FALLBACK_SDK_KNOWN_KWARGS

    @property
    def supported_request_types(self) -> list[ChatRequestType]:
        """Anthropic only, on purpose — do not add ``OPENAI_CHAT``.

        Expanding this list to include ``OPENAI_CHAT`` would skip the
        Chat → Messages translation in
        :func:`ChatRequestTranslationEngine.to_any_of`, but
        :meth:`call` below issues
        ``self._client.messages.create(**kwargs)`` against the
        Anthropic SDK which only speaks ``/v1/messages``.  Skipping
        translation while keeping the Messages-API outbound would
        send Chat-shaped kwargs (``messages`` shape mismatch,
        ``reasoning_effort`` instead of ``thinking``, no top-level
        ``system``, etc.) to a Messages endpoint and 400 on every
        request.

        The "Chat in / Chat out" path already exists as a sibling
        backend: :class:`OpenAILLMBackend`.  Pick that backend at the
        ``BackendTier.backend_format`` layer.  See the module
        docstring for why the two-backend split is load-bearing
        (hub-side LiteLLM Chat→Anthropic translator bugs we route
        around by owning the translation ourselves on the
        ``BackendFormat.ANTHROPIC`` path).
        """
        return [ChatRequestType.ANTHROPIC]

    async def call(self, ctx: ProxyContext, request: ChatRequest) -> ChatResponse:
        normalized = ChatRequestTranslationEngine.to_any_of(
            request, self.supported_request_types,
        )
        assert isinstance(normalized, AnthropicChatRequest)  # noqa: S101
        anthropic_request = normalized

        body = dict(anthropic_request.body)
        self._apply_tuning(body)
        self._normalize_tool_use_ids(body)

        model = body.get("model", "<unknown>")
        is_stream = bool(body.get("stream"))
        ctx.metadata["_proxy_actual_model"] = model
        log.debug(
            "AnthropicNativeLLMBackend: model=%s, stream=%s", model, is_stream,
        )

        kwargs = self._split_kwargs(body)

        # Bypass the SDK's 10-minute non-streaming safety check.  When
        # ``max_tokens`` is large (Opus 4.7 with our 128k tuning
        # fallback crosses the SDK's ``expected_time = 3600 * max_tokens
        # / 128_000`` threshold), ``messages.create`` raises
        # ``ValueError("Streaming is required ...")`` for non-streaming
        # callers unless they pass an explicit ``timeout``.  Harbor and
        # other benchmark clients don't stream, so without this the
        # call never leaves the SDK.  Skip when the caller already
        # passed a timeout (don't stomp explicit configuration).
        if not is_stream and "timeout" not in kwargs:
            kwargs["timeout"] = 3600.0

        # ``**kwargs`` dispatch can't prove which create() overload it hits;
        # runtime shape matches and the SDK validates server-side.
        try:
            result = await self._client.messages.create(**kwargs)
        except BadRequestError as exc:
            if self._is_configured_thinking_rejection(exc, body):
                raise ValueError(
                    _thinking_reconfiguration_message(
                        model=str(model),
                        effort=self._tuning.reasoning_effort.value
                        if self._tuning.reasoning_effort is not None else None,
                        upstream_error=exc,
                    ),
                ) from exc
            raise

        if is_stream:
            return AnthropicStreamingChatResponse(AnthropicResponseStream(result))
        return AnthropicChatResponse(result)

    def _is_configured_thinking_rejection(
        self,
        exc: BadRequestError,
        body: dict[str, object],
    ) -> bool:
        if self._tuning.reasoning_effort is None:
            return False
        if "thinking" not in body and "output_config" not in body:
            return False
        return _bad_request_mentions_thinking_effort(exc)

    # ------------------------------------------------------------------
    # Tuning application (private)
    # ------------------------------------------------------------------

    #: Fields stripped from every outgoing request body before it
    #: reaches ``messages.create``.  Two reasons a field lands here:
    #:
    #: * ``reasoning_effort`` — OpenAI-only key; the Anthropic SDK's
    #:   pydantic validator rejects it as an unknown kwarg.
    #: * ``context_management`` — Anthropic-native beta feature used
    #:   by Claude Code 2.1+ for context-window management.  AWS
    #:   Bedrock's Opus deployment rejects it with
    #:   ``"context_management: Extra inputs are not permitted"``
    #:   (Bedrock's API surface lags Anthropic's native; it doesn't
    #:   recognise the field).  We don't know at this layer whether
    #:   the upstream is Bedrock or native, so we strip
    #:   unconditionally — losing the auto-context-trim behaviour on
    #:   native Anthropic but unblocking every Bedrock route.
    _STRIPPED_REQUEST_FIELDS: tuple[str, ...] = (
        "reasoning_effort",
        "context_management",
    )

    def _apply_tuning(self, body: dict[str, object]) -> None:
        """Apply :class:`LLMBackendTuning` to the outgoing body in-place.

        Also strips fields listed in :attr:`_STRIPPED_REQUEST_FIELDS`
        — see the attribute docstring for the per-field rationale.

        Uses ``dict[str, object]`` rather than ``dict[str, Any]`` so
        new code doesn't add to the codebase's ``explicit-any``
        backlog.  The shape we read/write through this method is
        str-keyed and values are a mix of primitives and nested
        dicts — all subtypes of :class:`object`.
        """
        for key in self._STRIPPED_REQUEST_FIELDS:
            removed = body.pop(key, None)
            if removed is not None:
                log.debug(
                    "AnthropicNativeLLMBackend: stripped incompatible "
                    "field %r from body", key,
                )

        # --- max_output_tokens: only inject when client omitted
        # ``max_tokens``. ---
        if self._tuning.max_output_tokens is not None:
            if "max_tokens" not in body:
                body["max_tokens"] = self._tuning.max_output_tokens
                log.debug(
                    "AnthropicNativeLLMBackend: injected max_tokens=%d "
                    "(tuning fallback)",
                    self._tuning.max_output_tokens,
                )

        # --- reasoning_effort → adaptive thinking + output_config.effort ---
        effort = self._tuning.reasoning_effort
        if effort is None:
            return  # passthrough — leave thinking / output_config alone
        if effort is ReasoningEffort.DISABLED:
            body["thinking"] = {"type": "disabled"}
            log.debug(
                "AnthropicNativeLLMBackend: set thinking=disabled "
                "(tuning=DISABLED)",
            )
            return
        # LOW / MEDIUM / HIGH / XHIGH / MAX → adaptive thinking plus
        # ``output_config.effort``.  Preserve any sibling keys the
        # caller may have set under ``output_config`` (the effort
        # parameter coexists with other config fields).
        body["thinking"] = {"type": "adaptive"}
        existing_cfg = body.get("output_config")
        if isinstance(existing_cfg, dict):
            existing_cfg["effort"] = effort.value
        else:
            body["output_config"] = {"effort": effort.value}
        log.debug(
            "AnthropicNativeLLMBackend: set thinking=adaptive + "
            "output_config.effort=%r (tuning)",
            effort.value,
        )

    @staticmethod
    def _normalize_tool_use_ids(body: dict[str, object]) -> None:
        messages = body.get("messages")
        normalized_messages = normalize_anthropic_tool_use_ids(messages)
        if normalized_messages is not messages:
            body["messages"] = normalized_messages

    def _split_kwargs(self, body: dict[str, Any]) -> dict[str, Any]:
        """Route unknown-to-SDK fields through ``extra_body``.

        Keeps every field the SDK recognizes as a direct kwarg (so the
        SDK can validate, URL-construct, etc.). Everything else (newer
        Anthropic fields like ``context_management``, future beta
        fields, anything the installed SDK version is behind on) lands
        in ``extra_body``, which the SDK forwards to the server
        verbatim.
        """
        kwargs: dict[str, Any] = {}
        extras: dict[str, Any] = {}
        for key, value in body.items():
            if key in self._sdk_known_kwargs:
                kwargs[key] = value
            else:
                extras[key] = value
        if extras:
            # Preserve any user-supplied extra_body (unlikely from
            # Claude Code, but don't overwrite if it appears).
            existing = kwargs.get("extra_body")
            if isinstance(existing, dict):
                kwargs["extra_body"] = {**existing, **extras}
            else:
                kwargs["extra_body"] = extras
        return kwargs
