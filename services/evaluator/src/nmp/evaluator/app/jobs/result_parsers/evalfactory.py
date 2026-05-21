# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import csv
import json
import logging
import math
import os
from pathlib import Path

from nemo_evaluator_sdk.values import (
    AggregatedMetricResult,
    AggregateRangeScore,
    AggregateRubricScore,
    Histogram,
    MetricScore,
    Percentiles,
    RowScore,
)
from nmp.evaluator.app.jobs.constants import (
    EVALFACTORY_EVALUATION_RESULTS_AGG_SCORES_FILE_NAME,
    EVALUATION_RESULTS_AGG_SCORES_FILE_NAME,
    EVALUATION_RESULTS_ROW_SCORES_FILE_NAME,
    EvalHarness,
)
from nmp.evaluator.app.jobs.result_parsers.base import PreparedResults, ResultsParser
from nmp.evaluator.app.jobs.results import load_evaluation_result
from nmp.evaluator.app.values import (
    BenchmarkEvaluationResult,
    BenchmarkMetricResult,
)

logger = logging.getLogger(__name__)


class EvalFactoryResultsParser(ResultsParser):
    def __init__(self, job_id: str, eval_harness: EvalHarness):
        self.job_id = job_id
        self.eval_harness = eval_harness

    def prepare_results(self, local_results_dir_path: str) -> PreparedResults:
        evalfactory_results_filepath = resolve_evalfactory_results_file_path(local_results_dir_path)
        if evalfactory_results_filepath is None:
            raise FileNotFoundError(
                f"No EvalFactory results file '{EVALFACTORY_EVALUATION_RESULTS_AGG_SCORES_FILE_NAME}' "
                f"found in {local_results_dir_path}"
            )

        scores = _parse_evalfactory_scores(self.job_id, evalfactory_results_filepath)
        normalized_aggregate = _scores_to_aggregated_result(scores)

        # serialize to benchmark result or metric result by harness type
        if self.eval_harness in ["agentic_eval", "retriever"]:
            aggregate_result: AggregatedMetricResult = normalized_aggregate
        else:
            aggregate_result = BenchmarkEvaluationResult(
                results=[BenchmarkMetricResult(scores=normalized_aggregate.scores)]
            )

        aggregate_scores_path = os.path.join(local_results_dir_path, EVALUATION_RESULTS_AGG_SCORES_FILE_NAME)
        with open(aggregate_scores_path, "w") as f:
            f.write(aggregate_result.model_dump_json(indent=2, exclude_none=True))

        row_scores_path = os.path.join(local_results_dir_path, EVALUATION_RESULTS_ROW_SCORES_FILE_NAME)
        # Always regenerate normalized row scores from source artifacts.
        # Some EvalFactory containers emit an empty row-scores.jsonl placeholder.
        _write_evalfactory_row_scores(local_results_dir_path, row_scores_path, self.eval_harness)

        return PreparedResults(aggregate_scores_path=aggregate_scores_path, row_scores_path=row_scores_path)


def resolve_evalfactory_results_file_path(local_results_dir_path: str) -> str | None:
    candidate_paths = [
        os.path.join(local_results_dir_path, "results.yml"),
        os.path.join(local_results_dir_path, "artifacts", "results.yml"),
        os.path.join(local_results_dir_path, "results", "results.yml"),
    ]
    for path in candidate_paths:
        if os.path.isfile(path):
            return path

    root_dir = Path(local_results_dir_path)
    if root_dir.is_dir():
        for path in sorted(root_dir.rglob("results.yml")):
            if path.is_file():
                return str(path)
    return None


def _parse_evalfactory_scores(job_id: str, results_filepath: str) -> list[MetricScore]:
    evaluation_result = load_evaluation_result(job_id, results_filepath, name="", workspace="")
    scores_by_name: dict[str, MetricScore] = {}

    if evaluation_result.tasks:
        for task in evaluation_result.tasks.values():
            for metric in task.metrics.values():
                for score_name, score in metric.scores.items():
                    scores_by_name[score_name] = MetricScore(name=score_name, value=score.value, stats=score.stats)

    if evaluation_result.groups:
        for group in evaluation_result.groups.values():
            if group.metrics:
                for metric in group.metrics.values():
                    for score_name, score in metric.scores.items():
                        if score_name not in scores_by_name:
                            scores_by_name[score_name] = MetricScore(
                                name=score_name, value=score.value, stats=score.stats
                            )

    scores = list(scores_by_name.values())

    # Some system metrics can legitimately emit NaN values while still producing
    # a valid score payload. Only fail when no scores were emitted at all.
    if not scores:
        raise ValueError(
            f"Job {job_id} completed but no evaluation results detected. Job marked as failed: {evaluation_result}"
        )

    return scores


def _scores_to_aggregated_result(scores: list[MetricScore]) -> AggregatedMetricResult:
    aggregate_scores: list[AggregateRangeScore | AggregateRubricScore] = []
    for score in scores:
        stats = score.stats
        is_nan = math.isnan(score.value)
        count = stats.count if stats and stats.count is not None else (0 if is_nan else 1)
        nan_count = stats.nan_count if stats and stats.nan_count is not None else (1 if is_nan else 0)
        mean = stats.mean if stats and stats.mean is not None else (None if is_nan else score.value)
        sum_value = stats.sum if stats and stats.sum is not None else (None if mean is None else (mean * count))
        min_value = stats.min if stats and stats.min is not None else mean
        max_value = stats.max if stats and stats.max is not None else mean
        variance = stats.variance if stats and stats.variance is not None else (None if is_nan else 0.0)
        std_dev = stats.stddev if stats and stats.stddev is not None else (None if is_nan else 0.0)

        # Some harnesses emit placeholder zeros for aggregate stats even when no
        # valid values contributed to the score. Treat these stats as undefined.
        if count == 0 and nan_count > 0:
            mean = None
            sum_value = None
            min_value = None
            max_value = None
            variance = None
            std_dev = None

        if stats and stats.rubric_distribution:
            mode_category = max(stats.rubric_distribution, key=lambda item: item.count).label
            aggregate_scores.append(
                AggregateRubricScore(
                    name=score.name,
                    count=count,
                    nan_count=nan_count,
                    sum=sum_value,
                    mean=mean,
                    min=min_value,
                    max=max_value,
                    variance=variance,
                    std_dev=std_dev,
                    rubric_distribution=stats.rubric_distribution,
                    mode_category=mode_category,
                )
            )
            continue

        percentiles = (
            None
            if mean is None
            else Percentiles(
                p10=mean,
                p20=mean,
                p30=mean,
                p40=mean,
                p50=mean,
                p60=mean,
                p70=mean,
                p80=mean,
                p90=mean,
                p100=mean,
            )
        )
        aggregate_scores.append(
            AggregateRangeScore(
                name=score.name,
                count=count,
                nan_count=nan_count,
                sum=sum_value,
                mean=mean,
                min=min_value,
                max=max_value,
                variance=variance,
                std_dev=std_dev,
                percentiles=percentiles,
                histogram=Histogram(bins=[]),
            )
        )

    return AggregatedMetricResult(scores=aggregate_scores)


def _write_evalfactory_row_scores(local_results_dir_path: str, row_scores_path: str, eval_harness: EvalHarness) -> None:
    """Write normalized row-scores.jsonl from EvalFactory row artifacts when available."""
    row_source = _select_evalfactory_row_source(local_results_dir_path, eval_harness)
    if row_source is None:
        # Some EvalFactory jobs do not provide row-level scores; normalize to an empty JSONL artifact.
        logger.debug(
            "No EvalFactory row source found; writing empty row-scores", extra={"results_dir": local_results_dir_path}
        )
        with open(row_scores_path, "w"):
            pass
        return

    source_kind, source_path, source_subkind = row_source
    logger.debug(
        "Selected EvalFactory row source",
        extra={
            "results_dir": local_results_dir_path,
            "source_kind": source_kind,
            "source_path": source_path,
            "source_subkind": source_subkind,
        },
    )
    if source_kind == "retriever":
        rows = _parse_evalfactory_retriever_rows(source_path)
    elif source_kind == "benchmark":
        rows = _parse_evalfactory_benchmark_rows(source_path, source_subkind)
    else:
        rows = _parse_evalfactory_cached_outputs_rows(source_path)

    with open(row_scores_path, "w") as f:
        for row in rows:
            normalized = RowScore.model_validate(row)
            f.write(normalized.model_dump_json() + "\n")


def _select_evalfactory_row_source(
    local_results_dir_path: str,
    eval_harness: EvalHarness,
) -> tuple[str, str, str | None] | None:
    if eval_harness == "retriever":
        retriever_artifact_path = _resolve_evalfactory_retriever_rows_path(local_results_dir_path)
        return ("retriever", retriever_artifact_path, None) if retriever_artifact_path is not None else None
    if eval_harness == "bfcl":
        bfcl_path = _resolve_evalfactory_bfcl_rows_path(local_results_dir_path)
        return ("benchmark", bfcl_path, "bfcl-ndjson") if bfcl_path is not None else None
    if eval_harness == "safety_harness":
        csv_path = _resolve_evalfactory_aegis_rows_path(local_results_dir_path)
        return ("benchmark", csv_path, "aegis-csv") if csv_path is not None else None
    if eval_harness == "bigcode_eval_harness":
        predictions_path = _resolve_evalfactory_predictions_rows_path(local_results_dir_path)
        return ("benchmark", predictions_path, "predictions-json") if predictions_path is not None else None
    if eval_harness in {"agentic_eval", "simple_evals", "lm_eval_harness"}:
        cached_outputs_path = _resolve_evalfactory_cached_outputs_rows_path(local_results_dir_path)
        return ("cached-outputs", cached_outputs_path, None) if cached_outputs_path is not None else None
    logger.debug("Unknown eval_harness type; no row source resolver available", extra={"eval_harness": eval_harness})
    return None


def _resolve_evalfactory_retriever_rows_path(local_results_dir_path: str) -> str | None:
    candidate_paths = [
        os.path.join(local_results_dir_path, "results", "retriever_cached_outputs.json"),
        os.path.join(local_results_dir_path, "artifacts", "retriever_cached_outputs.json"),
        os.path.join(local_results_dir_path, "retriever_cached_outputs.json"),
    ]
    for candidate_path in candidate_paths:
        if os.path.isfile(candidate_path):
            return candidate_path

    root_dir = Path(local_results_dir_path)
    if root_dir.is_dir():
        for path in sorted(root_dir.rglob("retriever_cached_outputs.json")):
            if path.is_file():
                return str(path)
    return None


def _parse_evalfactory_retriever_rows(retriever_artifact_path: str) -> list[dict]:
    with open(retriever_artifact_path) as f:
        artifact = json.load(f)

    if not isinstance(artifact, dict):
        raise ValueError(
            f"Expected EvalFactory retriever row artifact to be a JSON object at {retriever_artifact_path}, "
            f"got {type(artifact).__name__}"
        )

    rows: list[dict] = []
    for query_id, cached_output in artifact.items():
        if not isinstance(cached_output, dict):
            raise ValueError(
                "Invalid EvalFactory retriever row artifact entry type at "
                f"{retriever_artifact_path} for query '{query_id}': expected object, "
                f"got {type(cached_output).__name__}"
            )

        rows.append(
            {
                "item": {"query_id": query_id},
                "sample": {},
                "metrics": {},
                "requests": [],
                "retriever": cached_output,
            }
        )

    return rows


def _resolve_evalfactory_aegis_rows_path(local_results_dir_path: str) -> str | None:
    candidate_paths = [
        os.path.join(local_results_dir_path, "results", "output.csv"),
        os.path.join(local_results_dir_path, "artifacts", "output.csv"),
        os.path.join(local_results_dir_path, "output.csv"),
    ]
    for candidate_path in candidate_paths:
        if os.path.isfile(candidate_path):
            return candidate_path

    root_dir = Path(local_results_dir_path)
    if root_dir.is_dir():
        for path in sorted(root_dir.rglob("output.csv")):
            if path.is_file():
                return str(path)
    return None


def _resolve_evalfactory_predictions_rows_path(local_results_dir_path: str) -> str | None:
    candidate_paths = [
        os.path.join(local_results_dir_path, "results", "predictions.json"),
        os.path.join(local_results_dir_path, "artifacts", "predictions.json"),
        os.path.join(local_results_dir_path, "predictions.json"),
    ]
    for candidate_path in candidate_paths:
        if os.path.isfile(candidate_path):
            return candidate_path

    root_dir = Path(local_results_dir_path)
    if root_dir.is_dir():
        for path in sorted(root_dir.rglob("predictions.json")):
            if path.is_file():
                return str(path)
    return None


def _resolve_evalfactory_bfcl_rows_path(local_results_dir_path: str) -> str | None:
    results_dir = Path(local_results_dir_path) / "results"
    artifacts_dir = Path(local_results_dir_path) / "artifacts"
    if results_dir.is_dir():
        for path in sorted(results_dir.glob("result/**/*.json")):
            if path.is_file():
                return str(path)
    if artifacts_dir.is_dir():
        for path in sorted(artifacts_dir.glob("result/**/*.json")):
            if path.is_file():
                return str(path)

    root_dir = Path(local_results_dir_path)
    if root_dir.is_dir():
        for path in sorted(root_dir.rglob("result/**/*.json")):
            if path.is_file():
                return str(path)
    return None


def _parse_evalfactory_benchmark_rows(rows_path: str, rows_kind: str | None) -> list[dict]:
    if rows_kind == "aegis-csv":
        return _parse_evalfactory_csv_rows(rows_path)
    if rows_kind == "predictions-json":
        return _parse_evalfactory_predictions_rows(rows_path)
    if rows_kind == "bfcl-ndjson":
        return _parse_evalfactory_bfcl_rows(rows_path)
    raise ValueError(f"Unknown EvalFactory benchmark rows kind '{rows_kind}' for {rows_path}")


def _parse_evalfactory_csv_rows(rows_path: str) -> list[dict]:
    rows: list[dict] = []
    with open(rows_path, newline="") as f:
        reader = csv.DictReader(f)
        for index, row in enumerate(reader):
            rows.append(
                {
                    "item": {"row_index": index},
                    "sample": {},
                    "metrics": {},
                    "requests": [],
                    "benchmark": row,
                }
            )
    return rows


def _parse_evalfactory_predictions_rows(rows_path: str) -> list[dict]:
    with open(rows_path) as f:
        payload = json.load(f)

    if not isinstance(payload, list):
        raise ValueError(
            f"Invalid EvalFactory predictions artifact at {rows_path}: expected list, got {type(payload).__name__}"
        )

    rows: list[dict] = []
    for index, prediction in enumerate(payload):
        rows.append(
            {
                "item": {"row_index": index},
                "sample": {},
                "metrics": {},
                "requests": [],
                "prediction": prediction,
            }
        )
    return rows


def _parse_evalfactory_bfcl_rows(rows_path: str) -> list[dict]:
    rows: list[dict] = []
    with open(rows_path) as f:
        for line_num, line in enumerate(f, start=1):
            stripped_line = line.strip()
            if not stripped_line:
                continue
            row = json.loads(stripped_line)
            if not isinstance(row, dict):
                raise ValueError(
                    f"Invalid EvalFactory BFCL row at {rows_path}:{line_num}: expected object, got {type(row).__name__}"
                )
            rows.append(
                {
                    "item": row,
                    "sample": {},
                    "metrics": {},
                    "requests": [],
                }
            )
    return rows


def _resolve_evalfactory_cached_outputs_rows_path(local_results_dir_path: str) -> str | None:
    known_cached_output_filenames = {
        "answer_acc.jsonl",
        "dataset_with_retrieved_context.jsonl",
        "dataset_with_retrieved_context_and_generated_answer.jsonl",
        "trajectory_eval_input.jsonl",
    }
    candidate_dirs = [
        Path(local_results_dir_path) / "results",
        Path(local_results_dir_path) / "artifacts",
        Path(local_results_dir_path),
    ]

    for candidate_dir in candidate_dirs:
        if not candidate_dir.is_dir():
            continue
        for path in sorted(candidate_dir.rglob("*.jsonl")):
            if not path.is_file():
                continue
            if path.name == EVALUATION_RESULTS_ROW_SCORES_FILE_NAME:
                continue
            if (
                path.name in known_cached_output_filenames
                or path.name.startswith("samples_")
                or "cached_output" in path.name
            ):
                return str(path)
    return None


def _parse_evalfactory_cached_outputs_rows(cached_outputs_path: str) -> list[dict]:
    rows: list[dict] = []
    with open(cached_outputs_path) as f:
        for line_num, line in enumerate(f, start=1):
            stripped_line = line.strip()
            if not stripped_line:
                continue
            row = json.loads(stripped_line)
            if not isinstance(row, dict):
                raise ValueError(
                    f"Invalid EvalFactory cached-outputs row at {cached_outputs_path}:{line_num}: "
                    f"expected object, got {type(row).__name__}"
                )
            rows.append(_normalize_cached_outputs_row(row))
    return rows


def _normalize_cached_outputs_row(row: dict) -> dict:
    if "item" in row and "sample" in row:
        normalized_row = dict(row)
        normalized_row["metrics"] = _normalize_row_metrics(normalized_row.get("metrics"))
        normalized_row.setdefault("requests", [])
        return normalized_row

    return {
        "item": row,
        "sample": {},
        "metrics": {},
        "requests": [],
    }


def _normalize_row_metrics(raw_metrics: object) -> dict[str, list[MetricScore]]:
    if raw_metrics is None:
        return {}
    if not isinstance(raw_metrics, dict):
        raise ValueError(f"Invalid row metrics payload: expected object, got {type(raw_metrics).__name__}")
    normalized: dict[str, list[MetricScore]] = {}
    for metric_name, metric_scores in raw_metrics.items():
        if not isinstance(metric_name, str):
            raise ValueError("Invalid row metrics payload: metric key must be a string")
        if not isinstance(metric_scores, list):
            raise ValueError(
                f"Invalid row metrics payload for '{metric_name}': expected list, got {type(metric_scores).__name__}"
            )
        normalized[metric_name] = [MetricScore.model_validate(score) for score in metric_scores]
    return normalized
