# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Configuration models for the Latency Service usage case.

``LatencyServiceEndpoint`` describes one LLM backend monitored by the
Latency Service.  ``LatencyServiceBackendConfig`` bundles the full
backend configuration — URL of the Latency Service, the endpoint list,
and polling/retry parameters.

The ``model`` field on each endpoint doubles as the endpoint ID used by
the Latency Service's health API — mirroring the routing-by-model-name
convention the rest of the library already follows.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class LatencyServiceEndpoint(BaseModel):
    """One LLM backend registered with the Latency Service.

    The ``model`` field doubles as the endpoint ID used by the Latency
    Service — it must be unique across the endpoint list and it is the
    value the Latency Service returns health verdicts under.

    Attributes:
        model: Model/endpoint ID.  Unique routing + health-lookup key.
        api_key: API key for the backing LLM API.
        base_url: Base URL for the backing LLM API (include ``/v1``).
        timeout: Request timeout in seconds, forwarded to the underlying
            ``OpenAILLMClient``.  ``None`` uses the client default.
    """

    model_config = ConfigDict(frozen=True)

    model: str
    api_key: str | None = None
    base_url: str | None = None
    timeout: float | None = None


class LatencyServiceBackendConfig(BaseModel):
    """Configuration for :class:`LatencyServiceLLMBackend`.

    Attributes:
        latency_service_url: Base URL of the Latency Service
            (e.g. ``"http://latency-service.inference-hub.svc:8080"``).
        endpoints: LLM backends to route across.  Each must have a
            unique ``model`` — this is the routing + health-lookup key.
        poll_interval_s: How often the background poller refreshes
            health from the Latency Service.  Health is cached between
            polls; the request hot path never blocks on a network call.
        poll_timeout_s: Timeout for the health API call.
        max_retries: On error, retry on a different endpoint up to this
            many times.  Dedup prevents re-selecting an endpoint that
            already failed for the same request.
    """

    latency_service_url: str = ""
    endpoints: list[LatencyServiceEndpoint] = Field(default_factory=list)
    poll_interval_s: float = 10.0
    poll_timeout_s: float = 5.0
    max_retries: int = 2
