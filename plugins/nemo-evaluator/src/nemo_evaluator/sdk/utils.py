# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Evaluator plugin SDK helpers."""

from __future__ import annotations

from nemo_evaluator_sdk.values.multi_metric_results import BenchmarkEvaluationResult
from nemo_evaluator_sdk.values.results import (
    AggregatedMetricResult,
    AggregateFieldName,
    EvaluationResult,
)


def filter_aggregate_scores(
    aggregate_scores: AggregatedMetricResult,
    aggregate_fields: tuple[AggregateFieldName, ...] | None,
) -> AggregatedMetricResult:
    """Return aggregate scores shaped by the requested fields."""
    if not aggregate_fields:
        return aggregate_scores
    fields = frozenset(aggregate_fields)
    return AggregatedMetricResult(scores=[score.with_fields(fields) for score in aggregate_scores.scores])


def filter_evaluation_result(
    result: EvaluationResult,
    aggregate_fields: tuple[AggregateFieldName, ...] | None,
) -> EvaluationResult:
    """Apply result-only aggregate projection to one evaluation result."""
    if not aggregate_fields:
        return result
    return result.model_copy(
        update={"aggregate_scores": filter_aggregate_scores(result.aggregate_scores, aggregate_fields)}
    )


def filter_benchmark_result(
    result: BenchmarkEvaluationResult,
    aggregate_fields: tuple[AggregateFieldName, ...] | None,
) -> BenchmarkEvaluationResult:
    """Apply result-only aggregate projection to a benchmark result."""
    if not aggregate_fields:
        return result
    per_metric = {
        metric_key: filter_evaluation_result(metric_result, aggregate_fields)
        for metric_key, metric_result in result.per_metric.items()
    }
    return result.model_copy(
        update={
            "aggregate_scores": filter_aggregate_scores(result.aggregate_scores, aggregate_fields),
            "per_metric": per_metric,
        }
    )
