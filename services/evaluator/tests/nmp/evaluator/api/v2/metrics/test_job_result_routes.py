# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Tests for metrics job result routes configuration."""

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from nmp.common.api.utils import tweak_spec
from nmp.evaluator.api.v2.metrics.endpoints import _jobs_router


class TestMetricJobResultRoutes:
    """Tests verifying metric job result routes are correctly configured."""

    def test_metric_jobs_router_has_typed_result_routes(self):
        """Test that metric jobs router includes typed routes for aggregate-scores and row-scores."""
        app = FastAPI()
        app.include_router(_jobs_router, prefix="/v2/workspaces/{workspace}/evaluation/metrics")

        # Extract all routes from the router
        route_paths = {route.path for route in app.routes if hasattr(route, "path")}

        # Verify typed result download routes exist
        assert (
            "/v2/workspaces/{workspace}/evaluation/metrics/jobs/{job}/results/aggregate-scores/download" in route_paths
        )
        assert "/v2/workspaces/{workspace}/evaluation/metrics/jobs/{job}/results/row-scores/download" in route_paths

        # Verify the fallback wildcard route also exists
        assert "/v2/workspaces/{workspace}/evaluation/metrics/jobs/{job}/results/{name}/download" in route_paths

    def test_metric_aggregate_scores_route_returns_json(self):
        """Test that aggregate-scores download route is configured for JSON response."""
        app = FastAPI()
        app.include_router(_jobs_router, prefix="/metrics")

        openapi_schema = get_openapi(
            title="Test API",
            version="1.0.0",
            routes=app.routes,
        )

        # Find the aggregate-scores download route
        agg_scores_path = "/metrics/jobs/{job}/results/aggregate-scores/download"
        assert agg_scores_path in openapi_schema["paths"], f"Path {agg_scores_path} not found in OpenAPI schema"

        route_schema = openapi_schema["paths"][agg_scores_path]
        # JSON routes default to application/json content type
        assert "get" in route_schema

    def test_metric_row_scores_route_returns_jsonl(self):
        """Test that row-scores download route is configured for JSONL streaming response."""
        app = FastAPI()
        app.include_router(_jobs_router, prefix="/metrics")

        openapi_schema = get_openapi(
            title="Test API",
            version="1.0.0",
            routes=app.routes,
        )

        # Find the row-scores download route
        row_scores_path = "/metrics/jobs/{job}/results/row-scores/download"
        assert row_scores_path in openapi_schema["paths"], f"Path {row_scores_path} not found in OpenAPI schema"

        route_schema = openapi_schema["paths"][row_scores_path]
        assert "get" in route_schema

        # JSONL routes should have application/jsonl content type
        responses = route_schema["get"]["responses"]
        assert "200" in responses
        content = responses["200"].get("content", {})
        assert "application/jsonl" in content, f"Expected application/jsonl in content, got {content}"

    def test_metric_row_scores_route_has_limit_parameter(self):
        """Test that row-scores download route accepts a limit query parameter."""
        app = FastAPI()
        app.include_router(_jobs_router, prefix="/metrics")

        openapi_schema = get_openapi(
            title="Test API",
            version="1.0.0",
            routes=app.routes,
        )

        row_scores_path = "/metrics/jobs/{job}/results/row-scores/download"
        route_schema = openapi_schema["paths"][row_scores_path]
        parameters = route_schema["get"].get("parameters", [])

        # Find the limit parameter
        limit_params = [p for p in parameters if p.get("name") == "limit"]
        assert len(limit_params) == 1, "Expected 'limit' query parameter for JSONL streaming"
        assert limit_params[0]["in"] == "query"

    def test_metric_row_score_schema_excludes_error(self):
        """The derived error summary is hidden from the wire schema."""
        app = FastAPI()
        app.include_router(_jobs_router, prefix="/metrics")

        openapi_schema = tweak_spec(
            get_openapi(
                title="Test API",
                version="1.0.0",
                routes=app.routes,
            )
        )

        row_score_schema = openapi_schema["components"]["schemas"]["RowScore"]
        assert "error" not in row_score_schema.get("properties", {})
        assert "error" not in row_score_schema.get("required", [])
