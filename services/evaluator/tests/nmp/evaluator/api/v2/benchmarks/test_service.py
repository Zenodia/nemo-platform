# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

from datetime import datetime
from typing import Generator

import nmp.evaluator.entities as entities
import pytest
from nemo_evaluator_sdk.enums import MetricType, ModelFormat
from nemo_evaluator_sdk.values import Model, Rubric, RubricScore
from nmp.common.entities.client import EntityClient
from nmp.evaluator.api.v2.benchmarks.manager import (
    BenchmarkCreationError,
    BenchmarkDeletionError,
    BenchmarkRetrievalError,
    BenchmarksManager,
)
from nmp.evaluator.api.v2.benchmarks.schemas.benchmarks import (
    Benchmark,
    BenchmarkRequest,
    ExtendedBenchmark,
)
from nmp.evaluator.app.values import FilesetRef, MetricRef
from nmp.testing import create_test_client


@pytest.fixture
def mock_entity_client() -> Generator[EntityClient, None, None]:
    """Real EntityClient backed by in-memory storage for integration-style testing."""
    workspaces = ["default", "workspace1", "workspace2", "production"]
    with create_test_client(client_type=EntityClient, workspaces=workspaces) as client:
        yield client


@pytest.fixture
def benchmarks_manager(mock_entity_client) -> BenchmarksManager:
    """BenchmarksManager instance with mocked EntityClient."""
    return BenchmarksManager(mock_entity_client)


@pytest.fixture
def sample_metric_entity():
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


class TestBenchmarksManagerGetAll:
    """Tests for BenchmarksManager.get_all method."""

    @pytest.mark.asyncio
    async def test_get_all_returns_empty_list(self, benchmarks_manager):
        """Test get_all returns empty list when no benchmarks exist."""
        result = await benchmarks_manager.get_all(workspace="default")
        assert len(result.data) == 0

    @pytest.mark.asyncio
    async def test_get_all_returns_benchmarks(
        self, benchmarks_manager, mock_entity_client, mock_sdk, sample_metric_entity, sample_benchmark_request
    ):
        """Test get_all returns all benchmarks for a workspace."""
        # Arrange - Create metric first, then benchmark
        await mock_entity_client.create(sample_metric_entity)
        await benchmarks_manager.create("default", sample_benchmark_request, mock_sdk)

        # Create a second benchmark
        second_request = BenchmarkRequest(
            name="test-benchmark-2",
            description="Second benchmark",
            metrics=[MetricRef(root="default/test-metric")],
            dataset=FilesetRef(root="default/test-dataset-2"),
        )
        await benchmarks_manager.create("default", second_request, mock_sdk)

        # Act
        result = await benchmarks_manager.get_all(workspace="default")

        # Assert
        assert len(result.data) == 2
        assert all(isinstance(b, Benchmark) for b in result.data)
        names = {b.name for b in result.data}
        assert names == {"test-benchmark", "test-benchmark-2"}

    @pytest.mark.asyncio
    async def test_get_all_with_extended_response(
        self, benchmarks_manager, mock_entity_client, mock_sdk, sample_metric_entity, sample_benchmark_request
    ):
        """Test get_all returns extended benchmarks when requested."""
        # Arrange
        await mock_entity_client.create(sample_metric_entity)
        await benchmarks_manager.create("default", sample_benchmark_request, mock_sdk)

        # Act
        result = await benchmarks_manager.get_all(workspace="default", extended_response=True)

        # Assert
        assert len(result.data) == 1
        assert isinstance(result.data[0], ExtendedBenchmark)
        assert result.data[0].name == "test-benchmark"
        # Extended response should have full metric objects, not just refs
        assert len(result.data[0].metrics) == 1


class TestBenchmarksManagerGetByName:
    """Tests for BenchmarksManager.get_by_name method."""

    @pytest.mark.asyncio
    async def test_get_by_name_returns_benchmark(
        self, benchmarks_manager, mock_entity_client, mock_sdk, sample_metric_entity, sample_benchmark_request
    ):
        """Test get_by_name returns the benchmark when it exists."""
        # Arrange
        await mock_entity_client.create(sample_metric_entity)
        await benchmarks_manager.create("default", sample_benchmark_request, mock_sdk)

        # Act
        result = await benchmarks_manager.get_by_name("default", "test-benchmark")

        # Assert
        assert result is not None
        assert isinstance(result, Benchmark)
        assert result.name == "test-benchmark"
        assert result.workspace == "default"

    @pytest.mark.asyncio
    async def test_get_by_name_raises_error_when_not_found(self, benchmarks_manager):
        """Test get_by_name raises BenchmarkRetrievalError when benchmark not found."""
        with pytest.raises(BenchmarkRetrievalError) as exc_info:
            await benchmarks_manager.get_by_name("default", "nonexistent")

        err = exc_info.value
        assert err.error_code == "BENCHMARK_NOT_FOUND"
        assert "default/nonexistent" in err.detail

    @pytest.mark.asyncio
    async def test_get_by_name_with_extended_response(
        self, benchmarks_manager, mock_entity_client, mock_sdk, sample_metric_entity, sample_benchmark_request
    ):
        """Test get_by_name returns extended benchmark when requested."""
        # Arrange
        await mock_entity_client.create(sample_metric_entity)
        await benchmarks_manager.create("default", sample_benchmark_request, mock_sdk)

        # Act
        result = await benchmarks_manager.get_by_name("default", "test-benchmark", extended_response=True)

        # Assert
        assert result is not None
        assert isinstance(result, ExtendedBenchmark)
        assert result.name == "test-benchmark"


class TestBenchmarksManagerCreate:
    """Tests for BenchmarksManager.create method."""

    @pytest.mark.asyncio
    async def test_create_benchmark_successfully(
        self, benchmarks_manager, mock_entity_client, mock_sdk, sample_metric_entity, sample_benchmark_request
    ):
        """Test create successfully creates a benchmark."""
        # Arrange
        await mock_entity_client.create(sample_metric_entity)

        # Act
        result = await benchmarks_manager.create("default", sample_benchmark_request, mock_sdk)

        # Assert
        assert result is not None
        assert isinstance(result, Benchmark)
        assert result.name == "test-benchmark"
        assert result.workspace == "default"
        assert result.description == "Test benchmark description"
        assert result.id is not None

    @pytest.mark.asyncio
    async def test_create_benchmark_with_extended_response(
        self, benchmarks_manager, mock_entity_client, mock_sdk, sample_metric_entity, sample_benchmark_request
    ):
        """Test create returns extended benchmark when requested."""
        # Arrange
        await mock_entity_client.create(sample_metric_entity)

        # Act
        result = await benchmarks_manager.create("default", sample_benchmark_request, mock_sdk, extended_response=True)

        # Assert
        assert result is not None
        assert isinstance(result, ExtendedBenchmark)
        assert result.name == "test-benchmark"

    @pytest.mark.asyncio
    async def test_create_benchmark_raises_error_when_metric_not_found(
        self, benchmarks_manager, mock_sdk, sample_benchmark_request
    ):
        """Test create raises BenchmarkCreationError when referenced metric not found."""
        # Act & Assert - metric doesn't exist
        with pytest.raises(BenchmarkCreationError) as exc_info:
            await benchmarks_manager.create("default", sample_benchmark_request, mock_sdk)

        err = exc_info.value
        assert err.error_code == "METRIC_NOT_FOUND"
        assert "default/test-metric" in err.detail

    @pytest.mark.asyncio
    async def test_create_benchmark_with_multiple_metrics(
        self, benchmarks_manager, mock_entity_client, mock_sdk, sample_metric_entity
    ):
        """Test create benchmark with multiple metrics."""
        # Arrange - create two metrics
        await mock_entity_client.create(sample_metric_entity)

        second_metric = entities.LLMJudgeMetric(
            name="test-metric-2",
            workspace="default",
            type=MetricType.LLM_JUDGE,
            description="Second metric",
            model=Model(
                url="https://api.openai.com/v1",
                name="gpt-3.5",
                format=ModelFormat.OPEN_AI,
            ),
            prompt_template="Rate: {output}",
            scores=[
                RubricScore(
                    name="score",
                    description="Score",
                    rubric=[
                        Rubric(label="yes", description="Yes", value=1),
                        Rubric(label="no", description="No", value=0),
                    ],
                )
            ],
        )
        await mock_entity_client.create(second_metric)

        request = BenchmarkRequest(
            name="multi-metric-benchmark",
            description="Benchmark with multiple metrics",
            metrics=[
                MetricRef(root="default/test-metric"),
                MetricRef(root="default/test-metric-2"),
            ],
            dataset=FilesetRef(root="default/test-dataset"),
        )

        # Act
        result = await benchmarks_manager.create("default", request, mock_sdk)

        # Assert
        assert result is not None
        assert result.name == "multi-metric-benchmark"
        assert len(result.metrics) == 2

    @pytest.mark.asyncio
    async def test_create_benchmark_with_cross_workspace_metric(self, benchmarks_manager, mock_entity_client, mock_sdk):
        """Test create benchmark with metric from different workspace."""
        # Arrange - create metric in production workspace
        metric = entities.LLMJudgeMetric(
            name="prod-metric",
            workspace="production",
            type=MetricType.LLM_JUDGE,
            description="Production metric",
            model=Model(
                url="https://api.openai.com/v1",
                name="gpt-4o",
                format=ModelFormat.OPEN_AI,
            ),
            prompt_template="Rate: {output}",
            scores=[
                RubricScore(
                    name="quality",
                    description="Quality",
                    rubric=[
                        Rubric(label="good", description="Good", value=1),
                        Rubric(label="bad", description="Bad", value=0),
                    ],
                )
            ],
        )
        await mock_entity_client.create(metric)

        # Create benchmark in default workspace referencing production metric
        request = BenchmarkRequest(
            name="cross-workspace-benchmark",
            description="Benchmark using production metric",
            metrics=[MetricRef(root="production/prod-metric")],
            dataset=FilesetRef(root="default/test-dataset"),
        )

        # Act
        result = await benchmarks_manager.create("default", request, mock_sdk)

        # Assert
        assert result is not None
        assert result.name == "cross-workspace-benchmark"
        assert result.workspace == "default"


class TestBenchmarksManagerDelete:
    """Tests for BenchmarksManager.delete method."""

    @pytest.mark.asyncio
    async def test_delete_successful(
        self, benchmarks_manager, mock_entity_client, mock_sdk, sample_metric_entity, sample_benchmark_request
    ):
        """Test delete successfully deletes a benchmark."""
        # Arrange
        await mock_entity_client.create(sample_metric_entity)
        await benchmarks_manager.create("default", sample_benchmark_request, mock_sdk)

        # Act
        result = await benchmarks_manager.delete("default", "test-benchmark")

        # Assert
        assert result.message == "Resource deleted successfully"

        # Verify it's actually deleted
        with pytest.raises(BenchmarkRetrievalError):
            await benchmarks_manager.get_by_name("default", "test-benchmark")

    @pytest.mark.asyncio
    async def test_delete_raises_error_when_not_found(self, benchmarks_manager):
        """Test delete raises BenchmarkDeletionError when benchmark not found."""
        with pytest.raises(BenchmarkDeletionError) as exc_info:
            await benchmarks_manager.delete("default", "nonexistent")

        err = exc_info.value
        assert err.error_code == "BENCHMARK_NOT_FOUND"
        assert "default/nonexistent" in err.detail


class TestBenchmarksManagerExists:
    """Tests for BenchmarksManager.exists method."""

    @pytest.mark.asyncio
    async def test_exists_returns_true_when_benchmark_exists(
        self, benchmarks_manager, mock_entity_client, mock_sdk, sample_metric_entity, sample_benchmark_request
    ):
        """Test exists returns True when benchmark exists."""
        # Arrange
        await mock_entity_client.create(sample_metric_entity)
        await benchmarks_manager.create("default", sample_benchmark_request, mock_sdk)

        # Act
        result = await benchmarks_manager.exists("default", "test-benchmark")

        # Assert
        assert result is True

    @pytest.mark.asyncio
    async def test_exists_returns_false_when_benchmark_not_found(self, benchmarks_manager):
        """Test exists returns False when benchmark not found."""
        result = await benchmarks_manager.exists("default", "nonexistent")
        assert result is False


class TestBenchmarksManagerEdgeCases:
    """Tests for edge cases and error conditions."""

    @pytest.mark.asyncio
    async def test_get_all_filters_by_workspace(
        self, benchmarks_manager, mock_entity_client, mock_sdk, sample_metric_entity, sample_benchmark_request
    ):
        """Test get_all filters by workspace correctly."""
        # Arrange - create metric and benchmark in default workspace
        await mock_entity_client.create(sample_metric_entity)
        await benchmarks_manager.create("default", sample_benchmark_request, mock_sdk)

        # Create metric and benchmark in production workspace
        prod_metric = entities.LLMJudgeMetric(
            name="prod-metric",
            workspace="production",
            type=MetricType.LLM_JUDGE,
            description="Production metric",
            model=Model(
                url="https://api.openai.com/v1",
                name="gpt-4o",
                format=ModelFormat.OPEN_AI,
            ),
            prompt_template="Rate: {output}",
            scores=[
                RubricScore(
                    name="quality",
                    description="Quality",
                    rubric=[
                        Rubric(label="good", description="Good", value=1),
                        Rubric(label="bad", description="Bad", value=0),
                    ],
                )
            ],
        )
        await mock_entity_client.create(prod_metric)

        prod_request = BenchmarkRequest(
            name="prod-benchmark",
            description="Production benchmark",
            metrics=[MetricRef(root="production/prod-metric")],
            dataset=FilesetRef(root="production/test-dataset"),
        )
        await benchmarks_manager.create("production", prod_request, mock_sdk)

        # Act
        default_results = await benchmarks_manager.get_all(workspace="default")
        prod_results = await benchmarks_manager.get_all(workspace="production")

        # Assert
        assert len(default_results.data) == 1
        assert default_results.data[0].name == "test-benchmark"
        assert len(prod_results.data) == 1
        assert prod_results.data[0].name == "prod-benchmark"
