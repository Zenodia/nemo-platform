# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

from datetime import datetime

import nmp.evaluator.entities as entities
import pytest
import pytest_asyncio
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from nemo_evaluator_sdk.enums import MetricType, ModelFormat
from nemo_evaluator_sdk.values import Rubric, RubricScore
from nmp.evaluator.api.v2.benchmarks.endpoints import (
    create_benchmark,
    delete_benchmark,
    get_benchmark,
    get_benchmarks_manager,
    router,
)
from nmp.evaluator.api.v2.benchmarks.manager import BenchmarksManager
from nmp.evaluator.api.v2.benchmarks.schemas.benchmarks import (
    BenchmarkJobResult,
    BenchmarkJobResultsListResponse,
    BenchmarkRequest,
    BenchmarksListResponse,
)
from nmp.evaluator.api.v2.benchmarks.schemas.jobs import BenchmarkJobAdapter
from nmp.evaluator.api.v2.common.inline_models import Model
from nmp.evaluator.app.values import (
    BenchmarkEvaluationResult,
    BenchmarkRef,
    FilesetRef,
    MetricRef,
    ModelRef,
)
from pydantic import ValidationError


@pytest.fixture
def sample_metric_entity() -> entities.Metric:
    """Sample LLMJudgeMetric entity for testing benchmarks."""
    entity = entities.LLMJudgeMetric(
        name="test-metric",
        workspace="default",
        type=MetricType.LLM_JUDGE,
        description="Test metric",
        model=Model(
            url="https://api.openai.com/v1",
            name="gpt-4o",
            format=ModelFormat.OPEN_AI,
        ),
        prompt_template="Rate the response: {output}",
        scores=[
            RubricScore(
                name="quality",
                description="Quality of response",
                rubric=[
                    Rubric(label="good", description="Good response", value=1),
                    Rubric(label="bad", description="Bad response", value=0),
                ],
            )
        ],
    )
    entity._id = "metric-123"
    entity._created_at = datetime(2024, 1, 1, 0, 0, 0)
    entity._updated_at = datetime(2024, 1, 1, 0, 0, 0)
    return entity


@pytest.fixture
def sample_benchmark_request():
    """Sample BenchmarkRequest for testing."""
    return BenchmarkRequest(
        name="test-benchmark",
        description="Test benchmark description",
        metrics=[MetricRef(root="default/test-metric")],
        dataset=FilesetRef(root="default/test-dataset"),
    )


def test_benchmark_job_params_reject_aggregate_fields() -> None:
    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        BenchmarkJobAdapter.validate_python(
            {
                "benchmark": "default/test-benchmark",
                "params": {"aggregate_fields": ["mean"]},
            }
        )


@pytest_asyncio.fixture
async def create_sample_benchmarks(
    benchmarks_manager: BenchmarksManager, mock_entity_client, mock_sdk, sample_metric_entity, sample_benchmark_request
):
    """Create 3 metrics and 2 benchmarks"""
    # Benchmark "default/test-benchmark"
    await mock_entity_client.create(sample_metric_entity)
    await benchmarks_manager.create("default", sample_benchmark_request, mock_sdk)

    # Benchmark "default/test-benchmark2"
    metric1 = entities.StringCheckMetric(
        name="metric-1",
        workspace="default",
        operation="equals",
        left_template="{{expected}}",
        right_template="{{output}}",
    )
    metric2 = entities.BLEUMetric(
        name="metric-2",
        workspace="default",
        references=["{{reference}}"],
    )
    await mock_entity_client.create(metric1)
    await mock_entity_client.create(metric2)
    try:
        await benchmarks_manager.create(
            "default",
            BenchmarkRequest(
                name="test-benchmark2",
                description="Test benchmark2 description",
                metrics=[MetricRef(root="default/metric-1"), MetricRef(root="default/metric-2")],
                dataset=FilesetRef(root="default/test-dataset2"),
                labels={"label1": "value1"},
            ),
            mock_sdk,
        )
    except Exception as e:
        print(e)
        raise


@pytest_asyncio.fixture
async def create_sample_benchmark_job_results(mock_entity_client):
    await mock_entity_client.create(
        entities.BenchmarkJobResult(
            name="result1",
            workspace="default",
            benchmark=BenchmarkRef(root="default/benchmark"),
            metrics=[MetricRef(root="default/metric1"), MetricRef(root="default/metric3")],
            dataset=FilesetRef(root="default/dataset"),
            results=BenchmarkEvaluationResult.model_validate(
                {
                    "results": [
                        {
                            "scores": [
                                {
                                    "name": "accuracy",
                                    "mean": 0.85,
                                    "count": 100,
                                    "nan_count": 0,
                                    "std_dev": 0.2,
                                    "min": 0.1,
                                    "max": 1.0,
                                }
                            ]
                        }
                    ]
                }
            ).results,
        )
    )
    await mock_entity_client.create(
        entities.BenchmarkJobResult(
            name="result2",
            workspace="default",
            benchmark=BenchmarkRef(root="default/benchmark2"),
            metrics=[MetricRef(root="default/metric2")],
            dataset=FilesetRef(root="default/dataset2"),
            results=BenchmarkEvaluationResult.model_validate(
                {"results": [{"scores": [{"name": "accuracy", "mean": 0.2, "count": 100, "nan_count": 0, "min": 0.0}]}]}
            ).results,
        )
    )
    await mock_entity_client.create(
        entities.BenchmarkJobResult(
            name="result3",
            workspace="default",
            benchmark=BenchmarkRef(root="default/benchmark"),
            metrics=[MetricRef(root="default/metric1"), MetricRef(root="default/metric3")],
            dataset=FilesetRef(root="default/dataset"),
            model=ModelRef(root="default/model"),
            labels={"label": "value"},
            results=BenchmarkEvaluationResult.model_validate(
                {
                    "results": [
                        {
                            "scores": [
                                {"name": "accuracy", "mean": 0.1, "count": 100, "nan_count": 0, "min": 0.1, "max": 0.1}
                            ]
                        }
                    ]
                }
            ).results,
        )
    )


def new_test_client(manager: BenchmarksManager) -> TestClient:
    """Fast API test client with benchmarks manager"""

    def override_get_benchmarks_manager() -> BenchmarksManager:
        return manager

    app = FastAPI()
    app.include_router(router, prefix="/apis/evaluation")
    app.dependency_overrides[get_benchmarks_manager] = override_get_benchmarks_manager
    return TestClient(app)


class TestCreateBenchmarkEndpoint:
    """Tests for create_benchmark endpoint."""

    @pytest.mark.asyncio
    async def test_create_benchmark_successfully(
        self, benchmarks_manager, mock_entity_client, mock_sdk, sample_metric_entity, sample_benchmark_request
    ):
        """Test create_benchmark endpoint successfully creates a benchmark."""
        # Arrange
        await mock_entity_client.create(sample_metric_entity)

        # Act
        result = await create_benchmark(
            workspace="default",
            benchmark=sample_benchmark_request,
            benchmarks_manager=benchmarks_manager,
            sdk=mock_sdk,
        )

        # Assert
        assert result is not None
        assert result.name == "test-benchmark"
        assert result.workspace == "default"

    @pytest.mark.asyncio
    async def test_create_benchmark_rejects_system_workspace(
        self, benchmarks_manager, mock_sdk, sample_benchmark_request
    ):
        """Test create_benchmark rejects requests to system workspace."""
        with pytest.raises(HTTPException) as exc_info:
            await create_benchmark(
                workspace="system",
                benchmark=sample_benchmark_request,
                benchmarks_manager=benchmarks_manager,
                sdk=mock_sdk,
            )

        err = exc_info.value
        assert err.status_code == 403
        assert isinstance(err.detail, str)
        assert "system" in err.detail.lower()
        assert "reserved" in err.detail.lower()

    @pytest.mark.asyncio
    async def test_create_benchmark_returns_404_when_metric_not_found(
        self, benchmarks_manager, mock_sdk, sample_benchmark_request
    ):
        """Test create_benchmark returns 404 when referenced metric not found."""
        with pytest.raises(HTTPException) as exc_info:
            await create_benchmark(
                workspace="default",
                benchmark=sample_benchmark_request,
                benchmarks_manager=benchmarks_manager,
                sdk=mock_sdk,
            )

        err = exc_info.value
        assert err.status_code == 404
        assert isinstance(err.detail, str)
        assert "test-metric" in err.detail

    @pytest.mark.asyncio
    async def test_create_benchmark_returns_409_when_name_already_exists(
        self, benchmarks_manager, mock_entity_client, mock_sdk, sample_metric_entity, sample_benchmark_request
    ):
        """Test create_benchmark returns 409 when benchmark name already exists."""
        # Arrange
        await mock_entity_client.create(sample_metric_entity)
        await create_benchmark(
            workspace="default",
            benchmark=sample_benchmark_request,
            benchmarks_manager=benchmarks_manager,
            sdk=mock_sdk,
        )

        # Act
        with pytest.raises(HTTPException) as exc_info:
            await create_benchmark(
                workspace="default",
                benchmark=sample_benchmark_request,
                benchmarks_manager=benchmarks_manager,
                sdk=mock_sdk,
            )

        # Assert
        err = exc_info.value
        assert err.status_code == 409
        assert isinstance(err.detail, str)
        assert "test-benchmark" in err.detail

    @pytest.mark.asyncio
    async def test_create_benchmark_with_extended_response(
        self, benchmarks_manager, mock_entity_client, mock_sdk, sample_metric_entity, sample_benchmark_request
    ):
        """Test create_benchmark returns extended response when requested."""
        # Arrange
        await mock_entity_client.create(sample_metric_entity)

        # Act
        result = await create_benchmark(
            workspace="default",
            benchmark=sample_benchmark_request,
            benchmarks_manager=benchmarks_manager,
            sdk=mock_sdk,
            extended_response=True,
        )

        # Assert
        assert result is not None
        assert result.name == "test-benchmark"
        # Extended response should have full metric objects
        assert len(result.metrics) == 1

    def test_create_benchmark_rejects_duplicate_metric_refs(self):
        with pytest.raises(ValidationError):
            BenchmarkRequest(
                name="duplicate-metrics",
                description="Benchmark with duplicate metric refs",
                metrics=[MetricRef(root="default/test-metric"), MetricRef(root="default/test-metric")],
                dataset=FilesetRef(root="default/test-dataset"),
            )


class TestGetBenchmarkEndpoint:
    """Tests for get_benchmark endpoint."""

    @pytest.mark.asyncio
    async def test_get_benchmark_successfully(
        self, benchmarks_manager, mock_entity_client, mock_sdk, sample_metric_entity, sample_benchmark_request
    ):
        """Test get_benchmark endpoint returns benchmark when it exists."""
        # Arrange
        await mock_entity_client.create(sample_metric_entity)
        await benchmarks_manager.create("default", sample_benchmark_request, mock_sdk)

        # Act
        result = await get_benchmark(
            workspace="default",
            name="test-benchmark",
            benchmarks_manager=benchmarks_manager,
        )

        # Assert
        assert result is not None
        assert result.name == "test-benchmark"
        assert result.workspace == "default"

    @pytest.mark.asyncio
    async def test_get_benchmark_returns_404_when_not_found(self, benchmarks_manager):
        """Test get_benchmark returns 404 when benchmark not found."""
        with pytest.raises(HTTPException) as exc_info:
            await get_benchmark(
                workspace="default",
                name="nonexistent",
                benchmarks_manager=benchmarks_manager,
            )

        err = exc_info.value
        assert err.status_code == 404
        assert isinstance(err.detail, str)
        assert "nonexistent" in err.detail

    @pytest.mark.asyncio
    async def test_get_benchmark_with_extended_response(
        self, benchmarks_manager, mock_entity_client, mock_sdk, sample_metric_entity, sample_benchmark_request
    ):
        """Test get_benchmark returns extended response when requested."""
        # Arrange
        await mock_entity_client.create(sample_metric_entity)
        await benchmarks_manager.create("default", sample_benchmark_request, mock_sdk)

        # Act
        result = await get_benchmark(
            workspace="default",
            name="test-benchmark",
            benchmarks_manager=benchmarks_manager,
            extended_response=True,
        )

        # Assert
        assert result is not None
        assert result.name == "test-benchmark"


class TestListBenchmarksEndpoint:
    """Tests for list_benchmarks endpoint."""

    @pytest.mark.asyncio
    async def test_list_benchmarks_returns_empty_page(self, benchmarks_manager):
        """Test list_benchmarks returns empty page when no benchmarks exist."""
        client = new_test_client(benchmarks_manager)
        resp = client.get("/apis/evaluation/v2/workspaces/default/benchmarks")
        assert resp.status_code == 200, resp.json()

        result = BenchmarksListResponse.model_validate(resp.json())
        assert result.pagination is not None

        assert result.data == []
        assert result.pagination.total_results == 0
        assert result.pagination.page == 1

    @pytest.mark.asyncio
    async def test_list_benchmarks_returns_benchmarks(self, benchmarks_manager, create_sample_benchmarks):  # noqa: ARG002
        """Test list_benchmarks returns all benchmarks in workspace."""
        client = new_test_client(benchmarks_manager)
        resp = client.get("/apis/evaluation/v2/workspaces/default/benchmarks")
        assert resp.status_code == 200, resp.json()

        result = BenchmarksListResponse.model_validate(resp.json())
        assert result.pagination is not None

        # Assert
        assert len(result.data) == 2
        assert result.pagination.total_results == 2
        assert result.pagination.page == 1
        names = {b.name for b in result.data}
        assert names == {"test-benchmark", "test-benchmark2"}

        # Verify metric is a reference
        for b in result.data:
            if hasattr(b, "metrics"):
                assert isinstance(b.metrics, list)
                for metric in b.metrics:
                    assert isinstance(metric, MetricRef)

    @pytest.mark.asyncio
    async def test_list_benchmarks_with_extended_response(self, benchmarks_manager, create_sample_benchmarks):  # noqa: ARG002
        """Test list_benchmarks returns extended response when requested."""
        client = new_test_client(benchmarks_manager)
        resp = client.get("/apis/evaluation/v2/workspaces/default/benchmarks?extended_response=true")
        assert resp.status_code == 200, resp.json()

        result = BenchmarksListResponse.model_validate(resp.json())
        assert result.pagination is not None

        # Assert
        assert len(result.data) == 2
        assert result.pagination.total_results == 2
        assert result.pagination.page == 1
        names = {b.name for b in result.data}
        assert names == {"test-benchmark", "test-benchmark2"}

        # Verify metric is not a reference
        for b in result.data:
            if hasattr(b, "metrics"):
                metrics = b.metrics
                assert isinstance(metrics, list)
                for metric in metrics:
                    assert not isinstance(metric, MetricRef)

    @pytest.mark.asyncio
    async def test_list_benchmarks_sort_pagination(self, benchmarks_manager, create_sample_benchmarks):  # noqa: ARG002
        """Test list_benchmarks returns sorted response."""
        client = new_test_client(benchmarks_manager)
        resp = client.get("/apis/evaluation/v2/workspaces/default/benchmarks?page_size=5&sort=name")
        assert resp.status_code == 200, resp.json()

        result = BenchmarksListResponse.model_validate(resp.json())
        assert result.pagination is not None

        # Assert
        assert len(result.data) == 2
        assert result.pagination.total_results == 2
        assert result.pagination.page == 1
        assert result.pagination.page_size == 5
        names = [b.name for b in result.data]
        assert names == ["test-benchmark", "test-benchmark2"]

    @pytest.mark.asyncio
    async def test_list_benchmarks_filter_dataset(self, benchmarks_manager, create_sample_benchmarks):  # noqa: ARG002
        """Test list_benchmarks returns filtered by dataset."""
        client = new_test_client(benchmarks_manager)
        resp = client.get("/apis/evaluation/v2/workspaces/default/benchmarks?filter[dataset]=default/test-dataset2")
        assert resp.status_code == 200, resp.json()

        result = BenchmarksListResponse.model_validate(resp.json())
        assert result.pagination is not None

        assert len(result.data) == 1
        assert result.pagination.total_results == 1
        assert result.filter == {"dataset": {"$eq": "default/test-dataset2"}}
        assert result.data[0].name == "test-benchmark2"

    @pytest.mark.asyncio
    async def test_list_benchmarks_filter_label(self, benchmarks_manager, create_sample_benchmarks):
        """Test list_benchmarks returns filtered by label."""
        client = new_test_client(benchmarks_manager)

        # Filter with brackets
        resp = client.get("/apis/evaluation/v2/workspaces/default/benchmarks?filter[data.labels.label1]=value1")
        assert resp.status_code == 200, resp.json()

        result_bracket = BenchmarksListResponse.model_validate(resp.json())
        assert result_bracket.pagination is not None

        assert len(result_bracket.data) == 1
        assert result_bracket.pagination.total_results == 1
        assert result_bracket.data[0].name == "test-benchmark2"

        # Filter with json
        filter_param = 'filter={"data.labels.label1": {"$eq": "value1"}}'
        resp = client.get(f"/apis/evaluation/v2/workspaces/default/benchmarks?{filter_param}")
        assert resp.status_code == 200, resp.json()

        result_json = BenchmarksListResponse.model_validate(resp.json())
        assert result_bracket.data == result_json.data
        assert result_bracket.pagination == result_json.pagination


class TestDeleteBenchmarkEndpoint:
    """Tests for delete_benchmark endpoint."""

    @pytest.mark.asyncio
    async def test_delete_benchmark_successfully(
        self, benchmarks_manager, mock_entity_client, mock_sdk, sample_metric_entity, sample_benchmark_request
    ):
        """Test delete_benchmark endpoint successfully deletes a benchmark."""
        # Arrange
        await mock_entity_client.create(sample_metric_entity)
        await benchmarks_manager.create("default", sample_benchmark_request, mock_sdk)

        # Act
        result = await delete_benchmark(
            workspace="default",
            name="test-benchmark",
            benchmarks_manager=benchmarks_manager,
        )

        # Assert
        assert result.message == "Resource deleted successfully"

        # Verify it's deleted
        with pytest.raises(HTTPException) as exc_info:
            await get_benchmark(
                workspace="default",
                name="test-benchmark",
                benchmarks_manager=benchmarks_manager,
            )
        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_benchmark_rejects_system_workspace(self, benchmarks_manager):
        """Test delete_benchmark rejects requests to system workspace."""
        with pytest.raises(HTTPException) as exc_info:
            await delete_benchmark(
                workspace="system",
                name="some-benchmark",
                benchmarks_manager=benchmarks_manager,
            )

        err = exc_info.value
        assert err.status_code == 403
        assert isinstance(err.detail, str)
        assert "system" in err.detail.lower()
        assert "reserved" in err.detail.lower()

    @pytest.mark.asyncio
    async def test_delete_benchmark_returns_404_when_not_found(self, benchmarks_manager):
        """Test delete_benchmark returns 404 when benchmark not found."""
        with pytest.raises(HTTPException) as exc_info:
            await delete_benchmark(
                workspace="default",
                name="nonexistent",
                benchmarks_manager=benchmarks_manager,
            )

        err = exc_info.value
        assert err.status_code == 404
        assert isinstance(err.detail, str)
        assert "nonexistent" in err.detail


class TestGetBenchmarkJobResultsEndpoint:
    @pytest.mark.asyncio
    async def test_get_404(self, benchmarks_manager, create_sample_benchmark_job_results):
        client = new_test_client(benchmarks_manager)
        resp = client.get("/apis/evaluation/v2/workspaces/default/benchmark-job-results/dne")
        assert resp.status_code == 404, resp.json()

    @pytest.mark.asyncio
    async def test_get(self, benchmarks_manager, create_sample_benchmark_job_results):
        client = new_test_client(benchmarks_manager)
        resp = client.get("/apis/evaluation/v2/workspaces/default/benchmark-job-results/result1")
        assert resp.status_code == 200, resp.text

        # Verify entity attrs
        raw_result = resp.json()
        assert "created_at" in raw_result, "missing entity private attributes"

        # doesn't serialize entity attrs, SDK types to though
        result = BenchmarkJobResult.model_validate(raw_result)
        assert result.name == "result1"
        assert result.workspace == "default"
        assert result.benchmark is not None
        assert result.metrics is not None
        assert result.dataset is not None
        assert len(result.results) == 1
        assert len(result.results[0].scores) == 1
        assert result.results[0].scores[0].name == "accuracy"
        assert result.results[0].scores[0].mean == 0.85

    @pytest.mark.asyncio
    async def test_get_aggregate_fields_invalid(self, benchmarks_manager, create_sample_benchmark_job_results):
        client = new_test_client(benchmarks_manager)
        resp = client.get("/apis/evaluation/v2/workspaces/default/benchmark-job-results/result1?aggregate_fields=dne")
        assert resp.status_code == 422, resp.text

    @pytest.mark.asyncio
    async def test_get_aggregate_fields(self, benchmarks_manager, create_sample_benchmark_job_results):
        client = new_test_client(benchmarks_manager)
        resp = client.get("/apis/evaluation/v2/workspaces/default/benchmark-job-results/result1")
        assert resp.status_code == 200, resp.text
        assert "count" in resp.text, "always expect count"
        assert "std_dev" in resp.text, "expected for default"
        assert "min" in resp.text, "expected for default"
        assert "max" in resp.text, "expected for default"

        resp = client.get(
            "/apis/evaluation/v2/workspaces/default/benchmark-job-results/result1?aggregate_fields=std_dev"
        )
        assert resp.status_code == 200, resp.text
        assert "count" in resp.text, "always expect count"
        assert "std_dev" in resp.text, "included in filter"
        assert "min" not in resp.text, "excluded from filter"
        assert "max" not in resp.text, "excluded from filter"

        resp = client.get(
            "/apis/evaluation/v2/workspaces/default/benchmark-job-results/result1?aggregate_fields=std_dev,min"
        )
        assert resp.status_code == 200, resp.text

        assert "count" in resp.text, "always expect count"
        assert "std_dev" in resp.text, "included in filter"
        assert "min" in resp.text, "included in filter"
        assert "max" not in resp.text, "excluded from filter"


class TestDeleteBenchmarkJobResultsEndpoint:
    @pytest.mark.asyncio
    async def test_delete_404(self, benchmarks_manager, create_sample_benchmark_job_results):
        client = new_test_client(benchmarks_manager)
        resp = client.delete("/apis/evaluation/v2/workspaces/default/benchmark-job-results/dne")
        assert resp.status_code == 404, resp.json()

    @pytest.mark.asyncio
    async def test_delete(self, benchmarks_manager, create_sample_benchmark_job_results):
        client = new_test_client(benchmarks_manager)

        resp = client.get("/apis/evaluation/v2/workspaces/default/benchmark-job-results/result1")
        assert resp.status_code == 200

        resp = client.delete("/apis/evaluation/v2/workspaces/default/benchmark-job-results/result1")
        assert resp.status_code == 200, resp.json()

        resp = client.get("/apis/evaluation/v2/workspaces/default/benchmark-job-results/result1")
        assert resp.status_code == 404, "expected entity to be deleted"


class TestListBenchmarkJobResultsEndpoint:
    @pytest.mark.asyncio
    async def test_list(self, benchmarks_manager, create_sample_benchmark_job_results):
        client = new_test_client(benchmarks_manager)
        resp = client.get("/apis/evaluation/v2/workspaces/default/benchmark-job-results")
        assert resp.status_code == 200, resp.json()

        results = BenchmarkJobResultsListResponse.model_validate(resp.json())
        assert len(results.data) == 3
        assert results.pagination is not None
        assert results.pagination.total_results == 3

        # Verify contains all aggregate fields by default
        assert "std_dev" in resp.text
        assert "min" in resp.text
        assert "max" in resp.text

    @pytest.mark.asyncio
    async def test_list_filter_empty(self, benchmarks_manager, create_sample_benchmark_job_results):
        client = new_test_client(benchmarks_manager)
        resp = client.get("/apis/evaluation/v2/workspaces/default/benchmark-job-results?filter[model]=ws/dne")
        assert resp.status_code == 200, resp.json()

        results = BenchmarkJobResultsListResponse.model_validate(resp.json())
        assert len(results.data) == 0
        assert results.pagination is not None
        assert results.pagination.total_results == 0

    @pytest.mark.asyncio
    async def test_list_filter_benchmark(self, benchmarks_manager, create_sample_benchmark_job_results):
        filter = "filter[benchmark]=default/benchmark"
        client = new_test_client(benchmarks_manager)
        resp = client.get(f"/apis/evaluation/v2/workspaces/default/benchmark-job-results?{filter}")
        assert resp.status_code == 200, resp.json()

        results = BenchmarkJobResultsListResponse.model_validate(resp.json())
        assert results.pagination is not None
        assert len(results.data) == 2
        assert results.pagination.total_results == 2
        for result in results.data:
            assert result.name in ["result1", "result3"]
            assert result.benchmark.root == "default/benchmark"

        # Filter and Sort
        resp = client.get(f"/apis/evaluation/v2/workspaces/default/benchmark-job-results?{filter}&sort=name")
        assert resp.status_code == 200, resp.json()
        results = BenchmarkJobResultsListResponse.model_validate(resp.json())
        assert results.data[0].name == "result1"
        assert results.data[1].name == "result3"

    @pytest.mark.asyncio
    async def test_list_filter_dataset(self, benchmarks_manager, create_sample_benchmark_job_results):
        filter = "filter[dataset]=default/dataset2"
        client = new_test_client(benchmarks_manager)
        resp = client.get(f"/apis/evaluation/v2/workspaces/default/benchmark-job-results?{filter}")
        assert resp.status_code == 200, resp.json()

        results = BenchmarkJobResultsListResponse.model_validate(resp.json())
        assert results.pagination is not None
        assert len(results.data) == 1
        assert results.pagination.total_results == 1
        assert results.data[0].name == "result2"
        assert results.data[0].benchmark.root == "default/benchmark2"
        assert results.data[0].dataset is not None
        assert results.data[0].dataset.root == "default/dataset2"

    @pytest.mark.asyncio
    async def test_list_filter_model(self, benchmarks_manager, create_sample_benchmark_job_results):
        filter = "filter[model]=default/model"
        client = new_test_client(benchmarks_manager)
        resp = client.get(f"/apis/evaluation/v2/workspaces/default/benchmark-job-results?{filter}")
        assert resp.status_code == 200, resp.json()

        results = BenchmarkJobResultsListResponse.model_validate(resp.json())
        assert results.pagination is not None
        assert len(results.data) == 1
        assert results.pagination.total_results == 1
        assert results.data[0].name == "result3"
        assert results.data[0].model is not None
        assert results.data[0].model.root == "default/model"

    @pytest.mark.asyncio
    async def test_list_filter_multiple(self, benchmarks_manager, create_sample_benchmark_job_results):
        filter = "filter[benchmark]=default/benchmark&filter[model]=default/model"
        client = new_test_client(benchmarks_manager)
        resp = client.get(f"/apis/evaluation/v2/workspaces/default/benchmark-job-results?{filter}")
        assert resp.status_code == 200, resp.json()

        results = BenchmarkJobResultsListResponse.model_validate(resp.json())
        assert results.pagination is not None
        assert len(results.data) == 1
        assert results.pagination.total_results == 1
        assert results.data[0].name == "result3"
        assert results.data[0].benchmark.root == "default/benchmark"
        assert results.data[0].model is not None
        assert results.data[0].model.root == "default/model"

    @pytest.mark.asyncio
    async def test_list_filter_metric(self, benchmarks_manager, create_sample_benchmark_job_results):
        filter_param = "filter[metrics][$like]=default/metric2"
        client = new_test_client(benchmarks_manager)
        resp = client.get(f"/apis/evaluation/v2/workspaces/default/benchmark-job-results?{filter_param}")
        assert resp.status_code == 200, resp.json()

        results = BenchmarkJobResultsListResponse.model_validate(resp.json())
        assert results.pagination is not None
        assert len(results.data) == 1
        assert results.pagination.total_results == 1
        assert results.data[0].name == "result2"
        assert results.data[0].benchmark.root == "default/benchmark2"
        assert results.data[0].metrics is not None
        assert MetricRef("default/metric2") in results.data[0].metrics

    @pytest.mark.asyncio
    async def test_list_filter_label(self, benchmarks_manager, create_sample_benchmark_job_results):
        client = new_test_client(benchmarks_manager)

        # Filter with brackets
        filter_param = "filter[data.labels.label]=value"
        resp = client.get(f"/apis/evaluation/v2/workspaces/default/benchmark-job-results?{filter_param}")
        assert resp.status_code == 200, resp.json()

        results_bracket = BenchmarkJobResultsListResponse.model_validate(resp.json())
        assert results_bracket.pagination is not None
        assert len(results_bracket.data) == 1
        assert results_bracket.pagination.total_results == 1
        assert results_bracket.data[0].name == "result3"
        assert "label" in results_bracket.data[0].labels
        assert results_bracket.data[0].labels["label"] == "value"

        # Filter with json
        filter_param = 'filter={"data.labels.label": {"$eq": "value"}}'
        resp = client.get(f"/apis/evaluation/v2/workspaces/default/benchmark-job-results?{filter_param}")
        assert resp.status_code == 200, resp.json()

        result_json = BenchmarkJobResultsListResponse.model_validate(resp.json())
        assert results_bracket.data == result_json.data
        assert results_bracket.pagination == result_json.pagination

    @pytest.mark.asyncio
    async def test_list_aggregate_fields_invalid(self, benchmarks_manager, create_sample_benchmark_job_results):
        client = new_test_client(benchmarks_manager)
        resp = client.get("/apis/evaluation/v2/workspaces/default/benchmark-job-results?aggregate_fields=dne")
        assert resp.status_code == 422, resp.text

    @pytest.mark.asyncio
    async def test_list_aggregate_fields(self, benchmarks_manager, create_sample_benchmark_job_results):
        client = new_test_client(benchmarks_manager)
        resp = client.get("/apis/evaluation/v2/workspaces/default/benchmark-job-results?aggregate_fields=std_dev")
        assert resp.status_code == 200, resp.text
        assert "count" in resp.text, "always expect count"
        assert "std_dev" in resp.text, "included in filter"
        assert "min" not in resp.text, "excluded from filter"
        assert "max" not in resp.text, "excluded from filter"

        resp = client.get("/apis/evaluation/v2/workspaces/default/benchmark-job-results?aggregate_fields=std_dev,min")
        assert resp.status_code == 200, resp.text

        assert "count" in resp.text, "always expect count"
        assert "std_dev" in resp.text, "included in filter"
        assert "min" in resp.text, "included in filter"
        assert "max" not in resp.text, "excluded from filter"
