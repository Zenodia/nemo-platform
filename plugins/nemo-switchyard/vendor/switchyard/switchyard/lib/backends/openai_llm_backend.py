# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""OpenAI Chat Completions LLM backend."""

from __future__ import annotations

import inspect
import logging
from typing import Any

from openai import AsyncStream, BadRequestError

from switchyard.lib.backends.llm_backend_tuning import (
    OPENAI_UNSUPPORTED_REASONING_EFFORTS,
    LLMBackendTuning,
    ReasoningEffort,
)
from switchyard.lib.chat_request.base import ChatRequest, ChatRequestType
from switchyard.lib.chat_request.openai_chat import OpenAIChatRequest
from switchyard.lib.chat_response.base import ChatResponse
from switchyard.lib.chat_response.openai_chat import (
    CompletionChatResponse,
    ResponseStream,
    StreamingChatResponse,
)
from switchyard.lib.llm_client import OpenAILLMClient
from switchyard.lib.proxy_context import ProxyContext
from switchyard.lib.roles import LLMBackend
from switchyard.lib.translation.request_engine import ChatRequestTranslationEngine

log = logging.getLogger(__name__)

_REASONING_REJECTION_MARKERS = (
    "unsupported",
    "not supported",
    "unrecognized",
    "unknown",
    "extra",
    "invalid",
    "not permitted",
)


def _bad_request_mentions_reasoning_effort(exc: BadRequestError) -> bool:
    """Return whether a 400 appears to reject the reasoning-effort field."""

    parts = [str(exc)]
    body = getattr(exc, "body", None)
    if body is not None:
        parts.append(repr(body))
    text = " ".join(parts).lower()
    if "reasoning_effort" in text:
        return True
    if "reasoning effort" in text:
        return True
    return "reasoning" in text and any(
        marker in text for marker in _REASONING_REJECTION_MARKERS
    )


def _reasoning_reconfiguration_message(
    *,
    model: str,
    effort: object,
    upstream_error: BadRequestError,
) -> str:
    return (
        f"Model {model!r} rejected Switchyard's configured "
        f"reasoning_effort={effort!r}. Reconfigure this LLM to use a model "
        "that supports that reasoning level, or disable Switchyard reasoning "
        "tuning for this route. For Claude Code passthrough: "
        "`switchyard configure --target claude "
        "--claude-reasoning-effort none`, or one-off "
        "`switchyard launch claude --reasoning-effort none`. "
        "For random-routing, set the affected tier to "
        "`--strong-reasoning-effort none` or `--weak-reasoning-effort none`. "
        f"Upstream error: {upstream_error}"
    )


class OpenAILLMBackend(LLMBackend):
    """Backend that calls an OpenAI-compatible Chat Completions API.

    Wraps the existing ``OpenAILLMClient`` and returns strongly typed
    ``ChatResponse`` subclasses.  Automatically translates non-OpenAI
    requests to Chat Completions format via ``ChatRequestTranslationEngine``.

    Optional :class:`LLMBackendTuning` applies two per-request
    transformations before the upstream call:

    * ``max_output_tokens`` — injected as ``body["max_tokens"]`` only
      when the client's body carries neither ``max_tokens`` nor
      ``max_completion_tokens``.  Never overrides a client-supplied
      cap.
    * ``reasoning_effort`` — written to ``body["reasoning_effort"]``
      for :attr:`ReasoningEffort.LOW` / :attr:`ReasoningEffort.MEDIUM`
      / :attr:`ReasoningEffort.HIGH`; stripped for
      :attr:`ReasoningEffort.DISABLED`; left alone when the tuning
      field is ``None`` (passthrough).  :attr:`ReasoningEffort.XHIGH`
      and :attr:`ReasoningEffort.MAX` are Anthropic-only — passing
      them on the tuning raises :class:`ValueError` at construction
      time so the misconfiguration surfaces before any traffic flows.

    Open-source models served behind this backend: servers that honor
    ``reasoning_effort`` pick it up natively; servers that ignore it
    drop it silently. Servers that reject it surface a configuration
    error telling the operator to choose a compatible model or set
    ``tuning.reasoning_effort=None``. Servers that need a non-standard
    reasoning field (e.g. Qwen3's
    ``extra_body.chat_template_kwargs.enable_thinking``) should also
    use ``tuning.reasoning_effort=None`` and have the caller set the
    custom field directly on the request body.
    """

    def __init__(
        self,
        client: OpenAILLMClient,
        tuning: LLMBackendTuning | None = None,
    ) -> None:
        effective_tuning = tuning or LLMBackendTuning()
        effort = effective_tuning.reasoning_effort
        if effort is not None and effort in OPENAI_UNSUPPORTED_REASONING_EFFORTS:
            # Fail fast — XHIGH / MAX are Anthropic-only.  Raising
            # here means callers see the misconfiguration at
            # construction (recipe wiring / test setup) instead of at
            # first request.
            raise ValueError(
                f"OpenAILLMBackend does not support "
                f"reasoning_effort={effort.value!r}.  XHIGH and MAX are "
                "Anthropic-only levels — use ReasoningEffort.HIGH as the "
                "ceiling, move this tier to BackendFormat.ANTHROPIC, or "
                "set reasoning_effort=None and write the custom field "
                "directly on the request body."
            )
        self._client = client
        self._tuning = effective_tuning
        # Discover the installed SDK's accepted ``chat.completions.create``
        # kwargs once.  ``AsyncCompletions.create`` validates kwargs at
        # call time and raises ``TypeError`` for unknown fields —
        # upstream clients like Harbor's terminus-2 agent inject non-SDK
        # metadata (e.g. ``session_id`` via ``--ak``) into the request
        # body, which would crash the call.  Anything the SDK doesn't
        # name we shuttle through ``extra_body`` (the SDK forwards it to
        # the server verbatim without validation).  Mirrors
        # ``AnthropicNativeLLMBackend._split_kwargs``.
        #
        # ``None`` disables filtering: if the underlying callable accepts
        # ``**kwargs`` (mocked client in tests, or a future SDK that
        # drops kwarg validation) there is nothing to filter against, so
        # we pass the body through unchanged.  Real ``AsyncOpenAI``
        # clients enumerate their named kwargs and do *not* accept
        # ``**kwargs``, so the introspection below yields a concrete
        # whitelist.
        self._sdk_known_kwargs: frozenset[str] | None = (
            self._introspect_sdk_kwargs(client)
        )

    @staticmethod
    def _introspect_sdk_kwargs(
        client: OpenAILLMClient,
    ) -> frozenset[str] | None:
        """Return SDK-accepted kwargs, or ``None`` if introspection is unreliable.

        Unreliable means: the callable accepts ``**kwargs`` (mock
        clients in tests report exactly this shape) — no filtering is
        possible, so callers should pass the body through untouched.
        """
        try:
            sig = inspect.signature(
                client.async_client.chat.completions.create,
            )
        except (AttributeError, TypeError, ValueError):
            # ``AttributeError`` covers tests that pass a stub object
            # without the real client's attribute chain; ``TypeError`` /
            # ``ValueError`` cover callables that ``inspect`` cannot
            # signature (builtins, C-accelerated mocks, etc.).
            return None
        has_var_keyword = any(
            p.kind is inspect.Parameter.VAR_KEYWORD
            for p in sig.parameters.values()
        )
        if has_var_keyword:
            return None
        return frozenset(sig.parameters.keys())

    @property
    def supported_request_types(self) -> list[ChatRequestType]:
        return [ChatRequestType.OPENAI_CHAT]

    async def call(self, ctx: ProxyContext, request: ChatRequest) -> ChatResponse:
        normalized = ChatRequestTranslationEngine.to_any_of(
            request, self.supported_request_types,
        )
        assert isinstance(normalized, OpenAIChatRequest)  # noqa: S101
        openai_request = normalized

        # Copy before mutation so we never modify the caller's request.
        # Mirrors what ``AnthropicNativeLLMBackend.call`` already does.
        # ``body`` values are heterogeneous (str / int / list / dict /
        # …) so ``object`` is the best narrow type the codebase's
        # ``disallow_any_explicit`` rule allows.
        body: dict[str, object] = dict(openai_request.body)
        self._apply_tuning(body)
        self._ensure_stream_usage(body)

        model = body.get("model", "<unknown>")
        ctx.metadata["_proxy_actual_model"] = model
        log.debug(
            "OpenAILLMBackend: model=%s, stream=%s",
            model, body.get("stream"),
        )

        kwargs = self._split_kwargs(body)
        try:
            result = await self._client.acompletion(**kwargs)
        except BadRequestError as exc:
            if self._is_configured_reasoning_rejection(exc, body):
                raise ValueError(
                    _reasoning_reconfiguration_message(
                        model=str(model),
                        effort=body.get("reasoning_effort"),
                        upstream_error=exc,
                    ),
                ) from exc
            raise

        if isinstance(result, AsyncStream):
            return StreamingChatResponse(ResponseStream(result))
        return CompletionChatResponse(result)

    def _is_configured_reasoning_rejection(
        self,
        exc: BadRequestError,
        body: dict[str, object],
    ) -> bool:
        if self._tuning.reasoning_effort is None:
            return False
        if "reasoning_effort" not in body:
            return False
        return _bad_request_mentions_reasoning_effort(exc)

    def _split_kwargs(self, body: dict[str, Any]) -> dict[str, Any]:
        """Route unknown-to-SDK fields through ``extra_body``.

        Keeps every field the SDK recognizes as a direct kwarg (so the
        SDK can validate, URL-construct, etc.). Everything else
        (Harbor's ``session_id`` agent-kwarg, LiteLLM's proxy metadata,
        anything the installed SDK version is behind on) lands in
        ``extra_body``, which the SDK forwards to the server verbatim.
        Mirrors ``AnthropicNativeLLMBackend._split_kwargs``.

        When :attr:`_sdk_known_kwargs` is ``None`` (unintrospectable
        callable — mocks in tests, ``**kwargs``-accepting wrappers)
        the body is returned as-is: there is nothing to validate
        against, and filtering into ``extra_body`` would silently lose
        real parameters the caller intended to pass through.
        """
        if self._sdk_known_kwargs is None:
            return dict(body)
        kwargs: dict[str, Any] = {}
        extras: dict[str, Any] = {}
        for key, value in body.items():
            if key in self._sdk_known_kwargs:
                kwargs[key] = value
            else:
                extras[key] = value
        if extras:
            # Preserve any user-supplied extra_body instead of stomping.
            existing = kwargs.get("extra_body")
            if isinstance(existing, dict):
                kwargs["extra_body"] = {**existing, **extras}
            else:
                kwargs["extra_body"] = extras
        return kwargs

    # ------------------------------------------------------------------
    # Tuning application (private)
    # ------------------------------------------------------------------

    def _apply_tuning(self, body: dict[str, object]) -> None:
        """Apply :class:`LLMBackendTuning` to the outgoing body in-place.

        Kept as a private method (not a free function) so the backend
        can log the transformations against its logger and so
        subclasses could override if they wanted format-specific
        behaviour beyond what the tuning dataclass captures.
        """
        # --- max_output_tokens: only inject when client omitted both
        # ``max_tokens`` and ``max_completion_tokens`` ---
        if self._tuning.max_output_tokens is not None:
            if "max_tokens" not in body and "max_completion_tokens" not in body:
                body["max_tokens"] = self._tuning.max_output_tokens
                log.debug(
                    "OpenAILLMBackend: injected max_tokens=%d (tuning fallback)",
                    self._tuning.max_output_tokens,
                )

        # --- reasoning_effort: translate enum to wire field ---
        effort = self._tuning.reasoning_effort
        if effort is None:
            return  # passthrough — leave body["reasoning_effort"] alone
        if effort is ReasoningEffort.DISABLED:
            removed = body.pop("reasoning_effort", None)
            if removed is not None:
                log.debug(
                    "OpenAILLMBackend: stripped reasoning_effort=%r "
                    "(tuning=DISABLED)", removed,
                )
            return
        # LOW / MEDIUM / HIGH
        body["reasoning_effort"] = effort.value
        log.debug(
            "OpenAILLMBackend: set reasoning_effort=%r (tuning)",
            effort.value,
        )

    # ------------------------------------------------------------------
    # Streaming usage opt-in (private)
    # ------------------------------------------------------------------

    def _ensure_stream_usage(self, body: dict[str, object]) -> None:
        """Opt the outgoing streaming request into usage reporting.

        OpenAI Chat Completions streaming emits ``usage`` on the final
        chunk only when the caller sets
        ``stream_options.include_usage=True``.  Without this,
        downstream Responses API translation
        (:func:`stream_chat_to_responses_sse`) never receives a
        usage-bearing chunk and reports ``{input,output,total}_tokens=0``
        — surfaces in OpenAI Codex CLI as ``tokens used: 0``.

        We opt in by default but respect an explicit caller opt-out
        (``include_usage=False`` on the client-supplied
        ``stream_options``).  Non-streaming requests are left alone —
        usage always comes back on the response body there.

        The ``{"include_usage": True, **existing}`` merge order lets
        the caller's value win on key collision; if they didn't set
        ``include_usage`` at all, our ``True`` default applies.
        """
        if not body.get("stream"):
            return
        existing = body.get("stream_options")
        if isinstance(existing, dict):
            # Mutate in place — ``existing`` is the same reference
            # ``body["stream_options"]`` points at.  ``setdefault``
            # leaves a caller-supplied ``include_usage`` untouched.
            existing.setdefault("include_usage", True)
        else:
            body["stream_options"] = {"include_usage": True}
