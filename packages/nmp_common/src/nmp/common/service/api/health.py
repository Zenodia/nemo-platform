# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Common health check router factory."""

import logging
import threading
import time
from typing import Any

import httpx
from nmp.common.config import PlatformConfig
from nmp.common.observability import MARK_INTERNAL_REQUEST_HEADERS

logger = logging.getLogger(__name__)


async def async_wait_for_service_ready(
    platform_config: PlatformConfig,
    service_name: str,
    timeout: float = 60.0,
    poll_interval: float = 0.5,
    http_client: httpx.AsyncClient | None = None,
) -> bool:
    """Wait for a specific platform service to be ready by polling its /status endpoint.

    Uses platform_config.get_service_url(service_name) so each service can have its own URL
    (e.g. from service_discovery). Returns True when the named service appears in
    the response's services.ready list.

    Args:
        platform_config: Platform config; the status URL is derived via get_service_url(service_name).
        service_name: Name of the service to wait for (e.g. "entities", "auth", "files").
        timeout: Maximum time to wait in seconds.
        poll_interval: Time between polling attempts in seconds.
        http_client: Optional client (e.g. for test injection). If None, a temporary client is used.

    Returns:
        True if the service became ready, False if timeout.
    """
    import asyncio

    status_url = f"{platform_config.get_service_url(service_name).rstrip('/')}/status"
    own_client = http_client is None
    if http_client is None:
        http_client = httpx.AsyncClient(timeout=2.0)

    logger.debug("Waiting for service to be ready", extra={"service": service_name, "url": status_url})

    try:
        start = time.monotonic()
        while (time.monotonic() - start) < timeout:
            try:
                response = await http_client.get(
                    status_url,
                    headers=MARK_INTERNAL_REQUEST_HEADERS,
                )
                if response.status_code == 200:
                    data: dict[str, Any] = response.json()
                    ready = (data.get("services") or {}).get("ready") or []
                    if service_name in ready:
                        logger.info("Service is ready", extra={"service": service_name})
                        return True
            except (httpx.RequestError, ValueError) as e:
                logger.debug("Status check failed, will retry", extra={"service": service_name, "error": str(e)})
            await asyncio.sleep(poll_interval)

        logger.warning(
            "Timeout waiting for service to be ready",
            extra={"service": service_name, "url": status_url, "timeout": timeout},
        )
        return False
    finally:
        if own_client:
            await http_client.aclose()


async def async_wait_for_dependencies(
    platform_config: PlatformConfig,
    dependency_names: list[str],
    timeout_per_service: float = 120.0,
    poll_interval: float = 0.5,
    http_client: httpx.AsyncClient | None = None,
) -> bool:
    """Wait for all named platform services to be ready (same pattern as Service._wait_for_dependencies).

    Uses get_service_url(service_name) for each dependency so service APIs may live at different URLs.
    Waits for each dependency in order; returns False if any timeout.

    Args:
        platform_config: Platform config (from Configuration.get_platform_config()).
        dependency_names: Service names to wait for (e.g. ["entities", "auth", "files"]).
        timeout_per_service: Maximum time to wait per service, in seconds.
        poll_interval: Time between polling attempts in seconds.
        http_client: Optional client (e.g. for test injection).

    Returns:
        True if all dependencies became ready, False if any timed out.
    """
    own_client = http_client is None
    if own_client:
        http_client = httpx.AsyncClient(timeout=2.0)
    try:
        for dep in dependency_names:
            if not await async_wait_for_service_ready(
                platform_config,
                dep,
                timeout=timeout_per_service,
                poll_interval=poll_interval,
                http_client=http_client,
            ):
                return False
        return True
    finally:
        if own_client and http_client is not None:
            await http_client.aclose()


def wait_for_service_ready(
    platform_config: PlatformConfig,
    service_name: str,
    stop_signal: threading.Event,
    timeout: float = 60.0,
    poll_interval: float = 0.5,
) -> bool:
    """Wait for a specific platform service to be ready by polling /status.

    Polls the platform's /status endpoint (which always returns 200 with
    per-service status). Returns True when the named service appears in
    services.ready, so e.g. the jobs controller can start once the jobs
    service is ready without waiting for models or other services.

    Args:
        platform_config: Platform config; the status URL is derived via get_service_url(service_name).
        service_name: Name of the service to wait for (e.g. "models", "jobs", "entities").
        stop_signal: Event to check for early termination.
        timeout: Maximum time to wait in seconds.
        poll_interval: Time between polling attempts in seconds.

    Returns:
        True if the service became ready, False if timeout or stop signal.
    """
    start_time = time.time()
    status_url = f"{platform_config.get_service_url(service_name).rstrip('/')}/status"

    logger.info(
        "Waiting for service to be ready",
        extra={"service": service_name, "url": status_url},
    )

    while not stop_signal.is_set() and (time.time() - start_time) < timeout:
        try:
            response = httpx.get(status_url, timeout=2.0, headers=MARK_INTERNAL_REQUEST_HEADERS)
            if response.status_code == 200:
                data: dict[str, Any] = response.json()
                ready = (data.get("services") or {}).get("ready") or []
                if service_name in ready:
                    logger.debug(
                        "Service is ready",
                        extra={"service": service_name, "url": status_url},
                    )
                    return True
        except (httpx.RequestError, ValueError) as e:
            logger.debug(
                "Status check failed, will retry",
                extra={"service": service_name, "url": status_url, "error": str(e)},
            )
        time.sleep(poll_interval)

    if stop_signal.is_set():
        logger.debug("Stop signal received while waiting for service")
    else:
        logger.warning(
            "Timeout waiting for service to be ready; check that the platform URL is reachable and the service has started",
            extra={"service": service_name, "url": status_url, "timeout": timeout},
        )
    return False
