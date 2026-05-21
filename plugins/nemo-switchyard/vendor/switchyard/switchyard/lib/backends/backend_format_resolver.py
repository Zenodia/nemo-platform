# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Resolve generic backend tier formats into concrete backend wire formats.

The Anthropic Messages probe lives here because ``BackendFormat.AUTO`` is
the only backend-format capability decision Switchyard makes today.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

import httpx

from switchyard.lib.backends.backend_tier import (
    BackendFormat,
    BackendTier,
)

log = logging.getLogger(__name__)
_DEFAULT_TIMEOUT_S = 3.0


@dataclass(frozen=True)
class BackendFormatResolution:
    """Concrete backend format selected for a generic tier."""

    backend_format: BackendFormat
    reason: str


class BackendFormatResolver:
    """Resolve ``BackendFormat.AUTO`` through reusable capability probes."""

    @staticmethod
    def resolve(tier: BackendTier) -> BackendFormatResolution:
        """Return the concrete backend format for ``tier``.

        Explicit formats are already resolved. ``AUTO`` needs a real endpoint
        probe, so missing probe inputs fail fast instead of silently picking
        a backend that may only work by accident.
        """
        if tier.backend_format is not BackendFormat.AUTO:
            return BackendFormatResolution(
                backend_format=tier.backend_format,
                reason="backend format is explicitly configured",
            )

        return BackendFormatResolver._resolve_auto(tier)

    @staticmethod
    def _resolve_auto(tier: BackendTier) -> BackendFormatResolution:
        if not tier.base_url:
            raise ValueError(
                "backend_format='auto' requires base_url so Switchyard can "
                "probe Anthropic Messages support.",
            )
        if not tier.api_key:
            raise ValueError(
                "backend_format='auto' requires api_key so Switchyard can "
                "probe Anthropic Messages support.",
            )

        if not _looks_like_anthropic_model(tier.model):
            return BackendFormatResolution(
                backend_format=BackendFormat.OPENAI,
                reason=(
                    "model does not look Anthropic-native; using OpenAI "
                    "Chat Completions format"
                ),
            )

        if probe_anthropic_messages_support_sync(
            base_url=tier.base_url,
            api_key=tier.api_key,
        ):
            return BackendFormatResolution(
                backend_format=BackendFormat.ANTHROPIC,
                reason="endpoint exposes Anthropic Messages support",
            )

        return BackendFormatResolution(
            backend_format=BackendFormat.OPENAI,
            reason="endpoint did not expose Anthropic Messages support",
        )


def _looks_like_anthropic_model(model: str) -> bool:
    """Return whether a model id should prefer Anthropic Messages probing.

    Mixed providers such as NVIDIA Inference Hub can expose ``/v1/messages``
    at the endpoint level while many routed models on that same endpoint are
    still OpenAI-Chat-native.  Probing the endpoint alone would then classify
    every ``BackendFormat.AUTO`` tier as Anthropic.  Use the tier model id as
    the first discriminator and only probe for Anthropic-looking model names.
    """
    lowered = model.lower()
    if "claude" in lowered:
        return True
    parts = [part for part in lowered.replace(":", "/").split("/") if part]
    return "anthropic" in parts


def _interpret_status(status: int) -> bool:
    """Return True iff the status code indicates the route is wired."""
    if status == 404:
        return False
    if status == 401:
        log.warning(
            "Anthropic /v1/messages probe got HTTP 401 — check --api-key. "
            "Falling back to translation mode.",
        )
        return False
    if 200 <= status < 500:
        return True
    log.warning(
        "Anthropic /v1/messages probe got HTTP %d; falling back to translation mode.",
        status,
    )
    return False


def _probe_headers(api_key: str) -> dict[str, str]:
    return {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }


def strip_v1_suffix(base_url: str) -> str:
    """Return *base_url* with a trailing ``/v1`` path component removed.

    Switchyard's ``--base-url`` convention follows OpenAI's (e.g.
    ``https://inference-api.nvidia.com/v1``), but the Anthropic SDK and
    raw ``/v1/messages`` probing both treat the base URL as the API
    root and append ``/v1/messages`` themselves. Without this trim the
    two conventions collide — ``https://host/v1`` + ``/v1/messages``
    becomes ``https://host/v1/v1/messages``.
    """
    stripped = base_url.rstrip("/")
    if stripped.endswith("/v1"):
        return stripped[:-3]
    return stripped


def probe_anthropic_messages_support_sync(
    *,
    base_url: str,
    api_key: str,
    timeout_s: float = _DEFAULT_TIMEOUT_S,
) -> bool:
    """Synchronous version of :func:`probe_anthropic_messages_support`.

    Preferred at startup (no running event loop required). Uses
    ``httpx.Client`` so no asyncio event loop is created; async clients
    built afterward bind their connection pools to uvicorn's event loop
    on first use rather than to a now-closed startup loop.
    """
    url = f"{strip_v1_suffix(base_url)}/v1/messages"
    try:
        with httpx.Client(timeout=timeout_s) as client:
            resp = client.post(url, headers=_probe_headers(api_key), json={})
    except (httpx.TimeoutException, httpx.NetworkError) as e:
        log.warning(
            "Anthropic /v1/messages probe failed (%s); "
            "falling back to translation mode.",
            type(e).__name__,
        )
        return False
    return _interpret_status(resp.status_code)


async def probe_anthropic_messages_support(
    *,
    base_url: str,
    api_key: str,
    timeout_s: float = _DEFAULT_TIMEOUT_S,
) -> bool:
    """Return True iff ``{base_url}/v1/messages`` is a functional route.

    Sends an empty-body probe POST with real auth. Response interpretation:

    * 404 → route not wired → return False (use translation)
    * 401 → return False (credential validation happens on the real request)
    * 400 / 422 → server validator ran → route exists → return True
    * 200 → server accepted even empty body → route exists → return True
    * 5xx / timeout / network error → return False
    """
    url = f"{strip_v1_suffix(base_url)}/v1/messages"
    try:
        async with httpx.AsyncClient(timeout=timeout_s) as client:
            resp = await client.post(url, headers=_probe_headers(api_key), json={})
    except (httpx.TimeoutException, httpx.NetworkError) as e:
        log.debug(
            "Anthropic /v1/messages probe unavailable (%s); "
            "using OpenAI translation mode.",
            type(e).__name__,
        )
        return False

    status = resp.status_code
    if status == 404:
        log.debug(
            "Anthropic /v1/messages probe got HTTP 404; "
            "using OpenAI translation mode.",
        )
        return False
    if status == 401:
        log.debug(
            "Anthropic /v1/messages probe got HTTP 401; "
            "using OpenAI translation mode.",
        )
        return False
    if 200 <= status < 500:
        return True
    log.debug(
        "Anthropic /v1/messages probe got HTTP %d; "
        "using OpenAI translation mode.",
        status,
    )
    return False
