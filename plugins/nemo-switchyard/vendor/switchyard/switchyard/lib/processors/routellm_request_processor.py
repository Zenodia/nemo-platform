# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""RouteLLM request processor — classifier-driven tier selection.

Picks ``"strong"`` or ``"weak"`` based on a classifier score against a
threshold and stamps the result into ``ctx.metadata[CTX_ROUTELLM_TIER]``
for the downstream :class:`RouteLLMLLMBackend` to dispatch on. Mirrors
:class:`RandomRoutingRequestProcessor`'s shape; the only difference
is the picking logic (classifier score vs. weighted coin).

Classifier weights are loaded once per process via
:class:`ResourceCache` so two processors configured with the same
``router_type`` + ``classifier_model`` share one in-memory copy. The
cache is refcounted: ``startup()`` acquires, ``shutdown()`` releases,
the model unloads when the last referent goes away.

The classifier object is duck-typed — anything exposing
``calculate_strong_win_rate(prompt: str) -> float`` works. In production
this is a ``routellm.controller.Controller``'s router; tests can pass a
fake.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Protocol

from switchyard.lib.backends.routellm_llm_backend import (
    CTX_ROUTELLM_TIER,
)
from switchyard.lib.chat_request.anthropic import AnthropicChatRequest
from switchyard.lib.chat_request.openai_chat import OpenAIChatRequest
from switchyard.lib.chat_request.openai_responses import (
    ResponsesChatRequest,
)
from switchyard.lib.resource_cache import ResourceCache
from switchyard.lib.roles import RequestProcessor

if TYPE_CHECKING:
    from switchyard.lib.chat_request.base import ChatRequest
    from switchyard.lib.factories.routellm.factory import RouteLLMConfig
    from switchyard.lib.proxy_context import ProxyContext

log = logging.getLogger(__name__)

# Process-wide cache so multiple processors with the same classifier
# share one loaded copy. Refcounted; an entry evicts on the last release.
_classifier_cache: ResourceCache = ResourceCache()


class _ClassifierProtocol(Protocol):
    """Duck type for the routellm router objects we score with."""

    def calculate_strong_win_rate(self, prompt: str) -> float: ...


class RouteLLMRequestProcessor(RequestProcessor):
    """Score the request and pick a tier; stamp the choice into ``ctx.metadata``.

    Args:
        config: The full :class:`RouteLLMConfig` — both tiers, threshold,
            router type, classifier model.
        classifier: Pre-built classifier (Python escape hatch for
            tests / non-routellm classifiers). When supplied, the
            processor skips :class:`ResourceCache` entirely and uses
            this object directly. Production callers leave this
            ``None`` and let ``startup()`` load via the cache.
    """

    def __init__(
        self,
        config: RouteLLMConfig,
        *,
        classifier: _ClassifierProtocol | None = None,
    ) -> None:
        self._config = config
        self._cache_key = (
            f"routellm-classifier:{config.router_type}:{config.classifier_model}"
        )
        # When a pre-built classifier is injected, ResourceCache is
        # bypassed (tests + custom classifiers). The instance still
        # owns its reference and skips acquire/release on lifecycle.
        self._injected = classifier is not None
        self._classifier: _ClassifierProtocol | None = classifier

    async def startup(self) -> None:
        if self._injected:
            return
        self._classifier = await _classifier_cache.acquire(
            self._cache_key, self._load_classifier,
        )

    async def shutdown(self) -> None:
        if self._injected:
            return
        await _classifier_cache.release(self._cache_key, self._unload_classifier)
        self._classifier = None

    async def process(self, ctx: ProxyContext, request: ChatRequest) -> ChatRequest:
        if self._classifier is None:
            # Defensive — startup() should have run. Default to strong
            # so traffic still flows; log loud so the misuse is visible.
            log.warning(
                "RouteLLMRequestProcessor.process called before startup — "
                "defaulting to 'strong' tier",
            )
            ctx.metadata[CTX_ROUTELLM_TIER] = "strong"
            return request

        prompt = _extract_user_prompt(request)
        if prompt is None:
            log.info("RouteLLM: no user prompt extracted, defaulting to strong")
            ctx.metadata[CTX_ROUTELLM_TIER] = "strong"
            return request

        score = float(self._classifier.calculate_strong_win_rate(prompt))
        tier = "strong" if score >= self._config.threshold else "weak"
        ctx.metadata[CTX_ROUTELLM_TIER] = tier
        log.info(
            "RouteLLM: score=%.4f threshold=%.4f -> %s",
            score, self._config.threshold, tier,
        )
        return request

    # ------------------------------------------------------------------
    # Classifier load / unload — overridable for non-routellm classifiers.
    # ------------------------------------------------------------------

    async def _load_classifier(self) -> _ClassifierProtocol:
        # Local import keeps the routellm[serve] dependency optional —
        # only paid for when this processor's startup actually runs.
        from routellm.controller import Controller

        kwargs: dict[str, Any] = {
            "routers": [self._config.router_type],
            "strong_model": self._config.strong.model,
            "weak_model": self._config.weak.model,
        }
        # Override the router's default checkpoint when the caller
        # supplied one:
        #   config={router_type: {"checkpoint_path": <model id>}}
        # The ``random`` router has no checkpoint to override.
        if self._config.classifier_model and self._config.router_type != "random":
            kwargs["config"] = {
                self._config.router_type: {
                    "checkpoint_path": self._config.classifier_model,
                },
            }
        controller = Controller(**kwargs)
        return controller.routers[self._config.router_type]  # type: ignore[no-any-return]

    async def _unload_classifier(self, value: _ClassifierProtocol) -> None:  # noqa: ARG002
        # routellm classifiers don't expose a teardown; rely on Python
        # GC + the refcount to evict from the cache. If a future
        # classifier needs explicit unloading, override this method.
        return None


def _extract_user_prompt(request: ChatRequest) -> str | None:
    """Extract the latest user-turn text from a typed ``ChatRequest``.

    Dispatches on the concrete request subclass — no blind body probing.
    Returns ``None`` when no user text is found; the processor falls
    back to the strong tier in that case (defensive default).

    The inner message-list iteration still uses ``.get`` because the
    elements are heterogeneous TypedDicts (user, assistant, tool, ...);
    only user-role messages are guaranteed to carry ``content`` of the
    shapes we care about, so we filter on role first and probe the
    ``content`` value defensively.
    """
    if isinstance(request, (OpenAIChatRequest, AnthropicChatRequest)):
        return _last_user_text_from_messages(request.body.get("messages", []))  # type: ignore[arg-type]
    if isinstance(request, ResponsesChatRequest):
        raw_input = request.body.get("input")
        if isinstance(raw_input, str):
            return raw_input or None
        if isinstance(raw_input, list):
            return _last_user_text_from_messages(raw_input)
        return None
    return None


def _last_user_text_from_messages(messages: list[Any]) -> str | None:
    """Return the concatenated text of the last user-role message, or None."""
    for msg in reversed(messages):
        if not isinstance(msg, dict):
            continue
        if msg.get("role") != "user":
            continue
        content = msg.get("content")
        if isinstance(content, str):
            return content or None
        if isinstance(content, list):
            parts = [
                block["text"]
                for block in content
                if isinstance(block, dict) and isinstance(block.get("text"), str)
            ]
            if parts:
                return "\n".join(parts)
    return None
