# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

from unittest.mock import AsyncMock, MagicMock

from fastapi import FastAPI
from fastapi.testclient import TestClient
from nmp.common.api.common import Page, PaginationData
from nmp.common.service.dependencies import get_sdk_client
from nmp.evaluator.api.v2.benchmarks import endpoints as benchmarks_endpoints
from nmp.evaluator.api.v2.metrics import endpoints as metrics_endpoints


def test_metric_and_benchmark_jobs_use_distinct_sources():
    """Regression for NV Bug 5868970

    The platform jobs list API can only filter by `source`. If metric and benchmark jobs
    share the same source, list endpoints can return mixed job specs and then fail schema
    validation when rendering the job spec.

    This test would fail without the fix because both routes previously used the same
    `source` ("evaluator"), and this assertion expects distinct `source` values.

    Fix: use distinct sources for metric vs benchmark job routes.
    """

    mock_sdk = MagicMock()
    mock_sdk.jobs.list = AsyncMock(
        return_value=Page(
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
    )

    app = FastAPI()
    app.dependency_overrides[get_sdk_client] = lambda: mock_sdk
    app.include_router(metrics_endpoints.router, prefix="/apis/evaluation")
    app.include_router(benchmarks_endpoints.router, prefix="/apis/evaluation")

    client = TestClient(app)

    import json

    resp = client.get("/apis/evaluation/v2/workspaces/default/metric-jobs")
    assert resp.status_code == 200
    assert mock_sdk.jobs.list.call_count == 1
    kwargs = mock_sdk.jobs.list.call_args.kwargs
    # Filter is forwarded as a JSON string via extra_query so logical-array
    # values ($and/$or) survive the SDK querystring serializer.
    assert json.loads(kwargs["extra_query"]["filter"]) == {"source": {"$eq": "evaluator-metrics"}}

    mock_sdk.jobs.list.reset_mock()
    resp = client.get("/apis/evaluation/v2/workspaces/default/benchmark-jobs")
    assert resp.status_code == 200
    assert mock_sdk.jobs.list.call_count == 1
    kwargs = mock_sdk.jobs.list.call_args.kwargs
    assert json.loads(kwargs["extra_query"]["filter"]) == {"source": {"$eq": "evaluator-benchmarks"}}
