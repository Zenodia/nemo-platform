# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Build intake payloads from request/response primitives."""

from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime, timezone
from functools import cache
from importlib.metadata import PackageNotFoundError, version
from typing import cast

from switchyard.lib.chat_request.base import ChatRequest
from switchyard.lib.chat_response.base import ChatResponse
from switchyard.lib.chat_response.openai_chat import CompletionChatResponse
from switchyard.lib.cost_estimator import MODEL_PRICING, estimate_model_cost
from switchyard.lib.factories.intake_sink.intake_sink_config import (
    IntakeSinkConfig,
)
from switchyard.lib.proxy_context import (
    CTX_PROXY_ACTUAL_MODEL,
    ProxyContext,
)
from switchyard.lib.request_metadata import (
    CTX_REQUEST_METADATA,
    RequestMetadata,
)
from switchyard.lib.translation.request_engine import ChatRequestTranslationEngine
from switchyard.lib.translation.response_engine import ChatResponseTranslationEngine

JsonObject = dict[str, object]

#: Context metadata key for random routing tier selection (mirrored from core.backends.random_routing_llm_backend)
_CTX_RANDOM_ROUTING_TIER = "_random_routing_tier"

INTAKE_STARTED_AT_MS_KEY = "_intake_started_at_ms"
INTAKE_ENDED_AT_MS_KEY = "_intake_ended_at_ms"
INTAKE_SESSION_ID_KEY = "_intake_session_id"
INTAKE_INBOUND_FORMAT_KEY = "_intake_inbound_format"
INTAKE_REQUEST_SNAPSHOT_KEY = "_intake_request_snapshot"
INTAKE_SKIP_KEY = "_intake_skip"
UNKNOWN_MODEL = "unknown"
SYNTHETIC_STREAM_RESPONSE_IDS = frozenset(
    {
        "chatcmpl-intake-stream",
        "chatcmpl-switchyard-stream",
        "msg_switchyard_stream",
        "resp_switchyard_stream",
    }
)


class IntakePayloadBuilder:
    """Pure builder that produces one intake payload per completed turn."""

    def __init__(self, config: IntakeSinkConfig) -> None:
        self._config = config

    def build(
        self,
        *,
        ctx: ProxyContext,
        request_snapshot: ChatRequest,
        response: ChatResponse,
        stream: bool,
    ) -> JsonObject:
        """Build a single intake payload."""
        openai_request = ChatRequestTranslationEngine.to_openai_chat(request_snapshot)
        openai_response = self._build_openai_response_dict(response)
        started_at_ms = _coerce_int(ctx.metadata.get(INTAKE_STARTED_AT_MS_KEY))
        ended_at_ms = _coerce_int(ctx.metadata.get(INTAKE_ENDED_AT_MS_KEY))
        latency_ms = (
            ended_at_ms - started_at_ms
            if started_at_ms is not None and ended_at_ms is not None
            else None
        )
        served_model = _metadata_str_or_unknown(ctx, CTX_PROXY_ACTUAL_MODEL)

        session_id_raw = ctx.metadata.get(INTAKE_SESSION_ID_KEY)
        session_id = session_id_raw if isinstance(session_id_raw, str) and session_id_raw else None
        payload: JsonObject = {
            "data": {
                "request": self._build_request_entry(
                    ctx=ctx,
                    openai_request=dict(openai_request.body),
                    stream=stream,
                ),
                "response": dict(openai_response),
            },
            "context": {
                "app": self._context_app(ctx),
                "task": self._task_name(ctx),
                "thread_id": session_id,
                "user_id": self._config.user_id,
                "session_id": session_id,
                "created_at": _created_at_iso(started_at_ms, ended_at_ms),
            },
            "usage": self._build_usage(
                served_model=served_model,
                openai_response=openai_response,
                started_at_ms=started_at_ms,
                ended_at_ms=ended_at_ms,
                latency_ms=latency_ms,
            ),
        }
        external_id = _response_external_id(openai_response)
        if external_id is not None:
            payload["external_id"] = external_id
        return payload

    def request_from_snapshot(self, ctx: ProxyContext) -> ChatRequest:
        """Read the copied original request wrapper from context metadata."""
        request = ctx.metadata.get(INTAKE_REQUEST_SNAPSHOT_KEY)
        if not isinstance(request, ChatRequest):
            raise ValueError("Missing intake request snapshot in context")
        return request

    def _build_openai_response_dict(self, response: ChatResponse) -> JsonObject:
        translated = ChatResponseTranslationEngine.to_openai_chat(response)
        if isinstance(translated, CompletionChatResponse):
            return cast(JsonObject, translated.body.model_dump(mode="json", exclude_none=True))
        raise NotImplementedError(
            f"Intake payloads require an OpenAI Chat-shaped response, got "
            f"{type(response).__name__}",
        )

    def _build_routing(self, ctx: ProxyContext) -> dict[str, str]:
        random_tier = ctx.metadata.get(_CTX_RANDOM_ROUTING_TIER)
        if not isinstance(random_tier, str) or not random_tier:
            return {}

        return {
            "router_type": "random",
            "routed_to": random_tier,
        }

    def _build_request_entry(
        self,
        *,
        ctx: ProxyContext,
        openai_request: JsonObject,
        stream: bool,
    ) -> JsonObject:
        request_entry = dict(openai_request)
        switchyard_metadata: JsonObject = {
            "version": _switchyard_version(),
            "inbound_format": ctx.metadata.get(INTAKE_INBOUND_FORMAT_KEY),
            "stream": stream,
        }
        routing = self._build_routing(ctx)
        if routing:
            switchyard_metadata["routing"] = routing
        request_entry["switchyard"] = switchyard_metadata
        return request_entry

    def _build_usage(
        self,
        *,
        served_model: str,
        openai_response: Mapping[str, object],
        started_at_ms: int | None,
        ended_at_ms: int | None,
        latency_ms: int | None,
    ) -> JsonObject:
        """Build the structured top-level ``usage`` block consumed by the intake service."""
        usage = openai_response.get("usage")
        input_tokens: int | None = None
        output_tokens: int | None = None
        cached_tokens: int | None = None
        cache_creation_tokens = 0
        if isinstance(usage, Mapping):
            input_tokens = _coerce_int(usage.get("prompt_tokens"))
            output_tokens = _coerce_int(usage.get("completion_tokens"))
            prompt_details = usage.get("prompt_tokens_details")
            if isinstance(prompt_details, Mapping):
                cached_tokens = _coerce_int(prompt_details.get("cached_tokens"))
                cache_creation_tokens = _coerce_int(prompt_details.get("cache_creation_tokens")) or 0

        cost_input: float | None = None
        cost_output: float | None = None
        cost_total: float | None = None
        has_token_usage = input_tokens is not None or output_tokens is not None
        if served_model in MODEL_PRICING and has_token_usage:
            breakdown = estimate_model_cost(
                model=served_model,
                prompt_tokens=input_tokens or 0,
                completion_tokens=output_tokens or 0,
                cached_tokens=cached_tokens or 0,
                cache_creation_tokens=cache_creation_tokens,
            )
            cost_input = breakdown["input_cost"]
            cost_output = breakdown["output_cost"]
            cost_total = breakdown["total_cost"]

        return {
            "model": served_model if served_model != UNKNOWN_MODEL else None,
            "started_at": _ms_to_iso(started_at_ms),
            "ended_at": _ms_to_iso(ended_at_ms),
            "latency_ms": latency_ms,
            "cost_usd": cost_total,
            "cost_input_usd": cost_input,
            "cost_output_usd": cost_output,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cached_tokens": cached_tokens,
        }

    def _context_app(self, ctx: ProxyContext) -> str:
        app_id = _request_metadata(ctx).intake.app or "switchyard"
        if "/" in app_id:
            return app_id
        return f"{self._config.workspace}/{app_id}"

    def _task_name(self, ctx: ProxyContext) -> str:
        return _request_metadata(ctx).intake.task or "chat"


def _request_metadata(ctx: ProxyContext) -> RequestMetadata:
    """Read :class:`RequestMetadata` off ``ctx.metadata`` or return a blank one."""
    value = ctx.metadata.get(CTX_REQUEST_METADATA)
    return value if isinstance(value, RequestMetadata) else RequestMetadata()


def _metadata_str_or_unknown(ctx: ProxyContext, key: str) -> str:
    value = ctx.metadata.get(key)
    if not isinstance(value, str) or not value:
        return UNKNOWN_MODEL
    return value


def _response_external_id(openai_response: Mapping[str, object]) -> str | None:
    response_id = openai_response.get("id")
    if not isinstance(response_id, str) or not response_id:
        return None
    if response_id in SYNTHETIC_STREAM_RESPONSE_IDS:
        return None
    return response_id


def _coerce_int(value: object) -> int | None:
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    return None


@cache
def _switchyard_version() -> str:
    try:
        return version("switchyard")
    except PackageNotFoundError:
        return "unknown"


def _created_at_iso(started_at_ms: int | None, ended_at_ms: int | None) -> str:
    source_ms = started_at_ms if started_at_ms is not None else ended_at_ms
    if source_ms is None:
        return datetime.now(timezone.utc).isoformat()
    return datetime.fromtimestamp(source_ms / 1000, tz=timezone.utc).isoformat()


def _ms_to_iso(value_ms: int | None) -> str | None:
    if value_ms is None:
        return None
    return datetime.fromtimestamp(value_ms / 1000, tz=timezone.utc).isoformat()
