# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Tests for filter parameter parsing on metric-jobs and benchmark-jobs list endpoints.

These endpoints use job_route_factory which supports filtering by name, project,
status, created_at, and updated_at fields via the unified filter parameter.
"""

from unittest.mock import AsyncMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from nmp.common.api.common import Page, PaginationData
from nmp.common.service.dependencies import get_sdk_client
from nmp.evaluator.api.v2.metrics import endpoints as metrics_endpoints


def _empty_jobs_page():
    return Page(
        data=[],
        pagination=PaginationData(
            page=1,
            page_size=10,
            current_page_size=0,
            total_pages=1,
            total_results=0,
        ),
        sort="-created_at",
        filter={},
    )


def _make_client(mock_sdk, *routers) -> TestClient:
    app = FastAPI()
    app.dependency_overrides[get_sdk_client] = lambda: mock_sdk
    for router in routers:
        app.include_router(router, prefix="/apis/evaluation")
    return TestClient(app)


@pytest.fixture
def mock_sdk(mock_sdk):
    mock_sdk.jobs.list = AsyncMock(return_value=_empty_jobs_page())
    return mock_sdk


def _filter_kwargs(mock_sdk) -> dict:
    """Decode the JSON ``filter`` the factory sent via ``extra_query``.

    The factory bypasses the SDK's typed ``filter`` kwarg because the bundled
    querystring serializer mangles the list-of-dict values that ``$and``-style
    composition produces. It sends a JSON-encoded filter through
    ``extra_query`` instead — round it back to a dict here.
    """
    import json

    call_kwargs = mock_sdk.jobs.list.call_args.kwargs
    extra_query = call_kwargs.get("extra_query") or {}
    raw = extra_query.get("filter")
    return json.loads(raw) if raw else {}


def _clauses(filt: dict) -> list[dict]:
    """Flatten the forwarded filter into a list of single-field clauses.

    The factory composes the user filter with the service source predicate via
    a tree-level ``$and`` (so logical roots like ``$or`` stay scoped). When the
    user passes no filter, ``source`` stands alone — handle both shapes here so
    individual tests can assert on a specific clause without caring about the
    surrounding composition.
    """
    if "$and" in filt:
        return list(filt["$and"])
    return [filt]


def _clause_for(filt: dict, field: str) -> dict:
    for clause in _clauses(filt):
        if field in clause:
            return clause
    raise AssertionError(f"No clause for field {field!r} in {filt!r}")


class TestMetricEvaluationJobsFilter:
    @pytest.fixture(autouse=True)
    def _setup(self, mock_sdk):
        self.client = _make_client(mock_sdk, metrics_endpoints.router)
        self.mock_sdk = mock_sdk

    def test_name_filter(self):
        resp = self.client.get("/apis/evaluation/v2/workspaces/default/metric-jobs?filter[name]=my-job")
        assert resp.status_code == 200
        # Bracket notation wraps bare values in $eq so the filter tree carries the operator.
        assert _clause_for(_filter_kwargs(self.mock_sdk), "name") == {"name": {"$eq": "my-job"}}

    def test_status_filter_single(self):
        resp = self.client.get("/apis/evaluation/v2/workspaces/default/metric-jobs?filter[status]=active")
        assert resp.status_code == 200
        assert _clause_for(_filter_kwargs(self.mock_sdk), "status") == {"status": {"$eq": "active"}}

    def test_created_at_filter(self):
        resp = self.client.get(
            "/apis/evaluation/v2/workspaces/default/metric-jobs?filter[created_at][gte]=2024-01-01T00:00:00Z"
        )
        assert resp.status_code == 200
        # Bracket-notation operator aliases (gte) are normalized to canonical $-prefixed keys.
        assert _clause_for(_filter_kwargs(self.mock_sdk), "created_at") == {
            "created_at": {"$gte": "2024-01-01T00:00:00Z"}
        }

    def test_invalid_filter_field_rejected(self):
        resp = self.client.get("/apis/evaluation/v2/workspaces/default/metric-jobs?filter[nonexistent]=foo")
        # make_filter_dep's allowlist rejects unknown fields with 400 before any
        # SDK call is made — assert the SDK was never invoked.
        assert resp.status_code == 400
        self.mock_sdk.jobs.list.assert_not_called()

    def test_filter_includes_source(self):
        """Filter always includes the service source for factory-generated endpoints."""
        resp = self.client.get("/apis/evaluation/v2/workspaces/default/metric-jobs")
        assert resp.status_code == 200
        assert _clause_for(_filter_kwargs(self.mock_sdk), "source") == {"source": {"$eq": "evaluator-metrics"}}


class TestBenchmarkEvaluationJobsFilter:
    @pytest.fixture(autouse=True)
    def _setup(self, mock_sdk):
        from nmp.evaluator.api.v2.benchmarks import endpoints as benchmarks_endpoints

        self.client = _make_client(mock_sdk, benchmarks_endpoints.router)
        self.mock_sdk = mock_sdk

    def test_name_filter(self):
        resp = self.client.get("/apis/evaluation/v2/workspaces/default/benchmark-jobs?filter[name]=my-benchmark")
        assert resp.status_code == 200
        assert _clause_for(_filter_kwargs(self.mock_sdk), "name") == {"name": {"$eq": "my-benchmark"}}

    def test_filter_includes_source(self):
        """Filter always includes the service source for factory-generated endpoints."""
        resp = self.client.get("/apis/evaluation/v2/workspaces/default/benchmark-jobs")
        assert resp.status_code == 200
        assert _clause_for(_filter_kwargs(self.mock_sdk), "source") == {"source": {"$eq": "evaluator-benchmarks"}}
