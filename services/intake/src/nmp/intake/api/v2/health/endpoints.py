# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Health check endpoints."""

from fastapi import APIRouter, Depends, status
from nmp.common.entities.client import EntityClient
from nmp.common.service.dependencies import get_entity_client
from nmp.intake.entities import App

router = APIRouter()

API_TAG = "Health Checks"


@router.get(
    "/health/live",
    tags=[API_TAG],
    status_code=status.HTTP_200_OK,
    summary="Perform a simple liveness check to verify the server is running.",
)
@router.get(
    "/v1/health/live",
    tags=[API_TAG],
    status_code=status.HTTP_200_OK,
    summary="Perform a simple liveness check to verify the server is running.",
)
async def health_live() -> dict:
    """
    Health check endpoint to verify the status of the application.
    """
    return {"status": "healthy"}


@router.get(
    "/health/ready",
    tags=[API_TAG],
    status_code=status.HTTP_200_OK,
    summary="Perform a readiness check to verify the server is able/ready to serve requests.",
)
@router.get(
    "/v1/health/ready",
    tags=[API_TAG],
    status_code=status.HTTP_200_OK,
    summary="Perform a readiness check to verify the server is able/ready to serve requests.",
)
async def health_ready(
    entities_client: EntityClient = Depends(get_entity_client),
) -> dict:
    """
    Health check endpoint to verify the status of the application's dependencies.
    Checks entity store connectivity.
    """
    try:
        # Try a simple query to verify entity store connectivity
        await entities_client.list(App, page=1, page_size=1)
        return {"status": "ready", "entity_store": "connected"}
    except Exception:
        return {"status": "not_ready", "entity_store": "disconnected"}


@router.get(
    "/health",
    tags=[API_TAG],
    status_code=status.HTTP_200_OK,
    summary="Unified health endpoint to check if server is alive and ready to serve requests.",
)
async def health_overall() -> dict:
    """Unified health endpoint."""
    return {"status": "ready"}
