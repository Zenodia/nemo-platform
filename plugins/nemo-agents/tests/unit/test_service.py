# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Tests for the agents plugin service wiring."""

from __future__ import annotations

from fastapi.routing import APIRoute
from nemo_agents_plugin.jobs.evaluate_agent import EvaluateAgentJob
from nemo_agents_plugin.service import AgentsService
from nemo_platform_plugin.scheduler import submit_path_for


def test_evaluate_job_route_matches_generated_submit_path() -> None:
    service = AgentsService()
    evaluate_router_spec = next(
        spec for spec in service.get_routers() if spec.description == "Submit and track agent evaluation jobs"
    )

    mounted_paths = {
        f"/apis/agents{evaluate_router_spec.prefix}{route.path}"
        for route in evaluate_router_spec.router.routes
        if isinstance(route, APIRoute) and "POST" in route.methods
    }

    assert submit_path_for(EvaluateAgentJob, workspace="{workspace}") in mounted_paths
