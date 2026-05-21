# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Platform health and status routes."""

from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException
from nmp.common.controller import ControllerManager
from nmp.common.service import Service
from nmp.platform_runner.schemas import (
    ClusterInfo,
    ControllerStatusBreakdown,
    HealthLiveResponse,
    HealthNotReadyDetail,
    HealthReadyResponse,
    NotReadyServiceInfo,
    PlatformStatusResponse,
    ServiceStatusBreakdown,
)
from nmp.platform_runner.version import get_platform_version, get_revision
from opentelemetry.semconv.attributes import service_attributes

logger = logging.getLogger(__name__)

NMP_PLATFORM_VERSION_ATTR = "nmp.platform.version"
NMP_PLATFORM_REVISION_ATTR = "nmp.platform.revision"


def get_platform_resource_attributes() -> dict[str, str]:
    """Return OTEL resource attributes for the platform."""
    return {
        service_attributes.SERVICE_NAME: "nemo-platform",
        NMP_PLATFORM_VERSION_ATTR: get_platform_version(),
        NMP_PLATFORM_REVISION_ATTR: get_revision(),
    }


async def _get_service_status_breakdown(services: list[Service]) -> tuple[list[str], list[dict[str, str]]]:
    ready: list[str] = []
    not_ready: list[dict[str, str]] = []
    for service in services:
        if await service.is_ready():
            ready.append(service.name)
        else:
            not_ready.append({"name": service.name})
    return ready, not_ready


def create_platform_health_router(services: list[Service]) -> APIRouter:
    """Create the shared platform health router."""
    router = APIRouter(tags=["Health"])

    @router.get("/cluster-info", operation_id="platform_cluster_info", response_model=ClusterInfo)
    async def cluster_info() -> ClusterInfo:
        return ClusterInfo(platform_version=get_platform_version(), revision=get_revision())

    @router.get("/status", operation_id="platform_status", response_model=PlatformStatusResponse)
    async def status() -> PlatformStatusResponse:
        ready, not_ready = await _get_service_status_breakdown(services)
        ready_count = len(ready)
        not_ready_count = len(not_ready)
        total = len(services)

        if ready_count == total:
            status_value = "healthy"
        elif not_ready_count == total or ready_count == 0:
            status_value = "unhealthy"
        else:
            status_value = "degraded"

        manager = ControllerManager.get_instance()
        all_healthy, controllers = manager.validate_all_healthy(detailed=True)

        return PlatformStatusResponse(
            status=status_value,
            services=ServiceStatusBreakdown(
                ready=ready,
                not_ready=[
                    NotReadyServiceInfo(name=item["name"], message=item.get("message", "")) for item in not_ready
                ],
            ),
            controllers=ControllerStatusBreakdown(healthy=all_healthy, status=controllers),
        )

    @router.get("/health/live", operation_id="platform_health_live", response_model=HealthLiveResponse)
    async def health_live() -> HealthLiveResponse:
        return HealthLiveResponse()

    @router.get("/health/ready", operation_id="platform_health_ready", response_model=HealthReadyResponse)
    async def health_ready() -> HealthReadyResponse:
        services_ready = all([await service.is_ready() for service in services])
        manager = ControllerManager.get_instance()
        all_controllers_healthy, _ = manager.validate_all_healthy(detailed=False)
        if not services_ready or not all_controllers_healthy:
            raise HTTPException(status_code=503, detail=HealthNotReadyDetail().model_dump())
        return HealthReadyResponse()

    return router
