# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import math

import nmp.evaluator.entities as entities
import pytest
from nemo_evaluator_sdk.metrics.bleu import BLEUMetric
from nemo_evaluator_sdk.metrics.exact_match import ExactMatchMetric
from nemo_evaluator_sdk.metrics.f1 import F1Metric
from nemo_evaluator_sdk.metrics.rouge import ROUGEMetric
from nemo_evaluator_sdk.metrics.string_check import StringCheckMetric
from nemo_evaluator_sdk.metrics.tool_calling import ToolCallingMetric
from nemo_evaluator_sdk.values import (
    AggregateRangeScore,
    AggregateRubricScore,
    MetricResult,
    MetricScore,
    RubricScoreStat,
    ScoreStats,
)
from nmp.evaluator.app.metrics.aggregation import aggregate_metrics
from nmp.evaluator.app.metrics.metric import new_metric


def test_aggregate_metrics():
    """Test basic aggregation computes all statistics correctly."""
    metric_results = [
        MetricResult(scores=[MetricScore(name="my-score", value=0)]),
        MetricResult(scores=[MetricScore(name="my-score", value=2)]),
        MetricResult(scores=[MetricScore(name="my-score", value=5)]),
        MetricResult(scores=[MetricScore(name="my-score", value=15)]),
    ]
    # Expected: sum=22, mean=5.5, min=0, max=15, variance=33.25, stddev=5.766...
    results = aggregate_metrics(metric_results)

    assert len(results.scores) == 1
    score = results.scores[0]
    assert isinstance(score, AggregateRangeScore)
    assert score.name == "my-score"
    assert score.mean == 5.5
    assert score.count == 4
    assert score.sum == 22.0
    assert score.min == 0.0
    assert score.max == 15.0
    assert math.isclose(score.variance, 33.25)  # population variance
    assert math.isclose(score.std_dev, 5.766281297335398)
    assert score.nan_count == 0


def test_aggregate_metrics_nan():
    """Test that NaN values are excluded from statistics but counted."""
    metric_results = [
        MetricResult(scores=[MetricScore(name="my-score", value=0)]),
        MetricResult(scores=[MetricScore(name="my-score", value=float("nan"))]),
        MetricResult(scores=[MetricScore(name="my-score", value=2)]),
        MetricResult(scores=[MetricScore(name="my-score", value=5)]),
        MetricResult(scores=[MetricScore(name="my-score", value=float("nan"))]),
        MetricResult(scores=[MetricScore(name="my-score", value=15)]),
    ]
    results = aggregate_metrics(metric_results)

    assert len(results.scores) == 1
    score = results.scores[0]
    assert isinstance(score, AggregateRangeScore)
    assert score.name == "my-score"
    assert score.mean == 5.5
    assert score.count == 4  # NaN values excluded from count
    assert score.nan_count == 2  # But tracked separately
    assert score.sum == 22.0
    assert score.min == 0.0
    assert score.max == 15.0


def test_aggregate_metrics_all_nan_returns_null_aggregates():
    metric_results = [
        MetricResult(scores=[MetricScore(name="my-score", value=float("nan"))]),
        MetricResult(scores=[MetricScore(name="my-score", value=float("nan"))]),
    ]

    results = aggregate_metrics(metric_results)

    assert len(results.scores) == 1
    score = results.scores[0]
    assert isinstance(score, AggregateRangeScore)
    assert score.name == "my-score"
    assert score.count == 0
    assert score.nan_count == 2
    assert score.sum is None
    assert score.mean is None
    assert score.min is None
    assert score.max is None
    assert score.variance is None
    assert score.std_dev is None
    assert score.percentiles is None


def test_aggregate_metrics_rubrics():
    """Test rubric score aggregation with distribution tracking."""
    metric_results = [
        MetricResult(
            scores=[
                MetricScore(
                    name="length",
                    value=2,
                    stats=ScoreStats(
                        rubric_distribution=[
                            RubricScoreStat(label="short", value=0, count=0),
                            RubricScoreStat(label="medium", value=1, count=0),
                            RubricScoreStat(label="long", value=2, count=1),
                        ]
                    ),
                )
            ]
        ),
        MetricResult(
            scores=[
                MetricScore(
                    name="length",
                    value=1,
                    stats=ScoreStats(
                        rubric_distribution=[
                            RubricScoreStat(label="short", value=0, count=0),
                            RubricScoreStat(label="medium", value=1, count=1),
                            RubricScoreStat(label="long", value=2, count=0),
                        ]
                    ),
                )
            ]
        ),
        MetricResult(
            scores=[
                MetricScore(
                    name="length",
                    value=2,
                    stats=ScoreStats(
                        rubric_distribution=[
                            RubricScoreStat(label="short", value=0, count=0),
                            RubricScoreStat(label="medium", value=1, count=0),
                            RubricScoreStat(label="long", value=2, count=1),
                        ]
                    ),
                )
            ]
        ),
        MetricResult(
            scores=[
                MetricScore(
                    name="length",
                    value=0,
                    stats=ScoreStats(
                        rubric_distribution=[
                            RubricScoreStat(label="short", value=0, count=1),
                            RubricScoreStat(label="medium", value=1, count=0),
                            RubricScoreStat(label="long", value=2, count=0),
                        ]
                    ),
                )
            ]
        ),
        MetricResult(
            scores=[
                MetricScore(
                    name="quality",
                    value=10,
                    stats=ScoreStats(
                        rubric_distribution=[
                            RubricScoreStat(label="high", value=10, count=1),
                            RubricScoreStat(label="low", value=0, count=0),
                        ]
                    ),
                )
            ]
        ),
    ]

    results = aggregate_metrics(metric_results)

    # Check "length" score - values [2, 1, 2, 0]
    length_score = next(s for s in results.scores if s.name == "length")
    assert isinstance(length_score, AggregateRubricScore)
    assert length_score.mean == 1.25
    assert length_score.count == 4
    assert length_score.sum == 5.0
    assert length_score.min == 0.0
    assert length_score.max == 2.0
    assert length_score.nan_count == 0
    # Rubric distribution should be aggregated
    rubric_dict = {r.label: r.count for r in length_score.rubric_distribution}
    assert rubric_dict == {"short": 1, "medium": 1, "long": 2}
    # Mode category should be "long" (count=2)
    assert length_score.mode_category == "long"

    # Check "quality" score - single value [10]
    quality_score = next(s for s in results.scores if s.name == "quality")
    assert isinstance(quality_score, AggregateRubricScore)
    assert quality_score.mean == 10.0
    assert quality_score.count == 1
    assert quality_score.sum == 10.0
    assert quality_score.variance == 0.0  # Single value has 0 variance
    assert len(quality_score.rubric_distribution) > 0


def test_aggregate_metrics_returns_distribution():
    """Test that aggregate_metrics returns percentiles and histogram for range scores."""
    metric_results = [MetricResult(scores=[MetricScore(name="my-score", value=i)]) for i in range(10)]  # values 0-9

    result = aggregate_metrics(metric_results)

    assert len(result.scores) == 1
    agg_score = result.scores[0]
    assert isinstance(agg_score, AggregateRangeScore)
    assert agg_score.name == "my-score"
    assert agg_score.count == 10
    assert agg_score.mean == 4.5  # (0+1+...+9)/10 = 45/10 = 4.5
    assert agg_score.min == 0.0
    assert agg_score.max == 9.0

    # Check percentiles (approximate for 10 values)
    assert agg_score.percentiles.p50 == 4.5  # median
    assert agg_score.percentiles.p100 == 9.0  # max

    # Check histogram has bins
    assert agg_score.histogram is not None
    assert len(agg_score.histogram.bins) == 10  # default 10 bins


class TestNewMetricBLEU:
    """Tests for new_metric factory function with BLEU."""

    @pytest.mark.asyncio
    async def test_new_metric_creates_bleu_metric(self):
        """Test that new_metric creates BLEUMetric from config."""
        params = entities.BLEUMetric(
            name="test-bleu-metric",
            workspace="default",
            references=["{{item.reference}}"],
        )

        metric = await new_metric(params)

        assert isinstance(metric, BLEUMetric)
        assert metric.references == ["{{item.reference}}"]
        assert metric.type.value == "bleu"


class TestNewMetricExactMatch:
    """Tests for new_metric factory function with ExactMatch."""

    @pytest.mark.asyncio
    async def test_new_metric_creates_exact_match_metric(self):
        """Test that new_metric creates ExactMatchMetric from config."""
        params = entities.ExactMatchMetric(
            name="test-exact-match-metric",
            workspace="default",
            reference="{{item.reference}}",
        )

        metric = await new_metric(params)

        assert isinstance(metric, ExactMatchMetric)
        assert metric.reference == "{{item.reference}}"
        assert metric.type.value == "exact-match"


class TestNewMetricF1:
    """Tests for new_metric factory function with F1."""

    @pytest.mark.asyncio
    async def test_new_metric_creates_f1_metric(self):
        """Test that new_metric creates F1Metric from config."""
        params = entities.F1Metric(
            name="test-f1-metric",
            workspace="default",
            reference="{{item.reference}}",
        )

        metric = await new_metric(params)

        assert isinstance(metric, F1Metric)
        assert metric.reference == "{{item.reference}}"
        assert metric.type.value == "f1"


class TestNewMetricROUGE:
    """Tests for new_metric factory function with ROUGE."""

    @pytest.mark.asyncio
    async def test_new_metric_creates_rouge_metric(self):
        """Test that new_metric creates ROUGEMetric from config."""
        params = entities.ROUGEMetric(
            name="test-rouge-metric",
            workspace="default",
            reference="{{item.reference}}",
        )

        metric = await new_metric(params)

        assert isinstance(metric, ROUGEMetric)
        assert metric.reference == "{{item.reference}}"
        assert metric.type.value == "rouge"


class TestNewMetricStringCheck:
    """Tests for new_metric factory function with StringCheck."""

    @pytest.mark.asyncio
    async def test_new_metric_creates_string_check_metric(self):
        """Test that new_metric creates StringCheckMetric from config."""
        params = entities.StringCheckMetric(
            name="test-string-check-metric",
            workspace="default",
            operation="equals",
            left_template="{{item.expected}}",
            right_template="{{sample.output_text}}",
        )

        metric = await new_metric(params)

        assert isinstance(metric, StringCheckMetric)
        assert metric.operation == "equals"
        assert metric.type.value == "string-check"


class TestNewMetricToolCalling:
    """Tests for new_metric factory function with ToolCalling."""

    @pytest.mark.asyncio
    async def test_new_metric_creates_tool_calling_metric(self):
        """Test that new_metric creates ToolCallingMetric from config."""
        params = entities.ToolCallingMetric(
            name="test-tool-calling-metric",
            workspace="default",
            reference="{{item.expected_tool_calls}}",
        )

        metric = await new_metric(params)

        assert isinstance(metric, ToolCallingMetric)
        assert metric.reference == "{{item.expected_tool_calls}}"
        assert metric.type.value == "tool-calling"
