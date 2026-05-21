# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Tests for the evaluator plugin service surface."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient
from nemo_evaluator.service import EvaluatorPluginService


def test_service_health_route_mounts_with_valid_prefix() -> None:
    app = FastAPI()
    service = EvaluatorPluginService()
    for spec in service.get_routers():
        app.include_router(spec.router, prefix=spec.prefix)

    response = TestClient(app).get("/v1/healthz")

    assert response.status_code == 200
    assert response.json() == {
        "plugin": "evaluator",
        "status": "ok",
        "mode": "sdk-backed-job-scaffold",
        "jobs": ["evaluator.evaluate"],
    }


def test_service_mounts_evaluator_job_collection_at_sdk_route() -> None:
    app = FastAPI()
    service = EvaluatorPluginService()
    for spec in service.get_routers():
        app.include_router(spec.router, prefix=spec.prefix)

    route_paths = {route.path for route in app.routes if hasattr(route, "path")}

    assert "/v2/workspaces/{workspace}/evaluate/jobs" in route_paths
