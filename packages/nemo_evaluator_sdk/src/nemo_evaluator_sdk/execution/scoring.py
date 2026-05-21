# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Shared row-scoring and result-finalization primitives used during execution."""

from collections.abc import Iterable, Sequence
from logging import Logger, getLogger
from typing import Any

from nemo_evaluator_sdk.execution.values import EvaluationError, EvaluationPhase
from nemo_evaluator_sdk.inference import requests_log_var
from nemo_evaluator_sdk.metrics.aggregation import add_corpus_scores, aggregate_metrics
from nemo_evaluator_sdk.metrics.base import CorpusMetric, Metric
from nemo_evaluator_sdk.metrics.utils import metric_type_name
from nemo_evaluator_sdk.values import EvaluationResult, MetricResult, MetricScore, RowScore

logger = getLogger(__name__)


def nan_metric_result(score_names: str | Iterable[str]) -> MetricResult:
    """Build the NaN score payload used for ignored scoring failures.

    Accepts either a single score name (single-metric pipelines) or an
    iterable of score names (multi-score/benchmark pipelines).
    """
    names: Iterable[str] = (score_names,) if isinstance(score_names, str) else score_names
    return MetricResult(scores=[MetricScore(name=name, value=float("nan")) for name in names])


CompletedRowEvaluation = tuple[int, MetricResult | None, RowScore]


def empty_evaluation_result() -> EvaluationResult:
    """Return the canonical empty evaluation result payload."""
    return EvaluationResult(row_scores=[], aggregate_scores=aggregate_metrics([]))


async def finalize_evaluation_result(
    metric: Metric,
    eval_results: Sequence[CompletedRowEvaluation],
    *,
    skip_errored: bool = False,
) -> EvaluationResult:
    """Build the final evaluation result from eval_results row-level outputs.

    Callers are expected to pass ``eval_results`` in the original row order; the
    upstream pipeline (``run_indexed_tasks`` / ``run_generated_sample_scoring_pipeline``)
    already writes results by index, so no re-sorting is performed here.

    When ``skip_errored`` is true, rows whose ``RowScore.metric_errors`` is
    populated are excluded from aggregation so the NaN placeholder produced
    for ignored failures does not contribute to ``nan_count``, and the same
    rows are excluded from the ``items``/``samples`` passed to
    :meth:`CorpusMetric.compute_corpus_scores` so corpus-level aggregation
    (e.g. BLEU/ROUGE-corpus) isn't skewed by failed rows with empty samples.
    Errored rows still appear in ``row_scores``.
    """
    valid_eval_results = [
        (result, row_score)
        for _, result, row_score in eval_results
        if result is not None and not (skip_errored and row_score.metric_errors)
    ]
    metric_results = [result for result, _ in valid_eval_results]
    # Keep all rows in the reported ``row_scores`` (including errored ones); only
    # aggregation and corpus inputs honor ``skip_errored``.
    row_scores = [row_score for _, _, row_score in eval_results]

    aggregated_result = aggregate_metrics(metric_results)

    if valid_eval_results and isinstance(metric, CorpusMetric):
        corpus_metric_result = await metric.compute_corpus_scores(
            items=[row_score.item for _, row_score in valid_eval_results],
            samples=[row_score.sample for _, row_score in valid_eval_results],
        )
        if corpus_metric_result:
            add_corpus_scores(aggregated_result, corpus_metric_result)

    return EvaluationResult(
        row_scores=row_scores,
        aggregate_scores=aggregated_result,
    )


async def score_row(
    metric: Metric,
    row: dict[str, Any],
    sample: dict[str, Any],
    index: int,
    metric_key: str,
    fail_fast: bool,
    generation_requests: list[dict[str, Any]],
    logger: Logger | None = None,
) -> tuple[int, MetricResult | None, RowScore]:
    """Score an already-prepared sample for one row.

    Args:
        metric: Metric object used for scoring.
        row: Input row from the dataset.
        sample: Prepared sample payload passed to the metric.
        index: Row position in the original dataset.
        metric_key: Key used to place score output in ``RowScore.metrics``.
        fail_fast: Whether metric errors should raise immediately. When
            ``True``, the exception is wrapped in ``EvaluationError`` and
            raised. When ``False``, a metric exception yields a NaN score row.
        generation_requests: Requests collected before metric scoring,
            such as online generation requests.
        logger: Optional logger override for row-scoring logs.
    Returns:
        Tuple of ``(index, metric_result_or_none, row_score_payload)``.

    Raises:
        EvaluationError: If row evaluation fails and ``fail_fast`` is ``True``.
    """

    metric_requests: list[dict[str, Any]] = []
    requests_log_var.set(metric_requests)
    active_logger = logger or globals()["logger"]

    try:
        result = await metric.compute_scores(row, sample)
        active_logger.debug(
            "Computed metric",
            extra={
                "item_index": index,
                "metric_type": metric_type_name(metric),
                "scores": [score.model_dump() for score in result.scores],
            },
        )
        return (
            index,
            result,
            RowScore(
                row_index=index,
                item=row,
                sample=sample,
                metrics={metric_key: result.scores},
                requests=[*generation_requests, *metric_requests],
            ),
        )
    except Exception as e:
        if fail_fast:
            raise EvaluationError(
                index,
                str(e),
                phase=EvaluationPhase.METRIC_SCORING,
                metric_key=metric_key,
            ) from e
        active_logger.warning("Evaluation failed, marking as NaN", extra={"item_index": index, "error": str(e)})
        result = nan_metric_result(metric.score_names())
        return (
            index,
            result,
            RowScore(
                row_index=index,
                item=row,
                sample=sample,
                metrics={metric_key: result.scores},
                requests=[*generation_requests, *metric_requests],
                metric_errors={metric_key: str(e)},
            ),
        )
