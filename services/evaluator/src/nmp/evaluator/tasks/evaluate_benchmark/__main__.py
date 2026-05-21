# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
# property and proprietary rights in and to this material, related
# documentation and any modifications thereto. Any use, reproduction,
# disclosure or distribution of this material and related documentation
# without an express license agreement from NVIDIA CORPORATION or
# its affiliates is strictly prohibited.

import asyncio
import json
import logging
import os
from collections.abc import Sequence
from pathlib import Path
from typing import Any, cast

from nemo_evaluator_sdk.agent_inference import AgentInferenceFn, make_agent_inference_request
from nemo_evaluator_sdk.execution.benchmark_execution import evaluate_benchmark as sdk_evaluate_benchmark
from nemo_evaluator_sdk.execution.values import EvaluationError
from nemo_evaluator_sdk.inference import InferenceFn, make_inference_request
from nemo_evaluator_sdk.resilience.errors import first_failure_cause
from nemo_evaluator_sdk.values import (
    Agent,
    Model,
    RowScore,
    RunConfig,
    RunConfigOnline,
    RunConfigOnlineModel,
)
from nemo_platform import AsyncNeMoPlatform
from nmp.common.jobs.constants import (
    DEFAULT_JOB_STORAGE_PATH,
    DEFAULT_NEMO_JOB_STEP_CONFIG_FILE_PATH,
    NEMO_JOB_STEP_CONFIG_FILE_PATH_ENVVAR,
    PERSISTENT_JOB_STORAGE_PATH_ENVVAR,
)
from nmp.common.observability.otel import initialize_logging
from nmp.common.sdk_factory import get_async_platform_sdk
from nmp.evaluator.app.dataset_schemas import apply_column_mapping_to_row
from nmp.evaluator.app.datasets.loader import DatasetLoadError, load_dataset_from_ref_as_dicts
from nmp.evaluator.app.inference import get_platform_headers
from nmp.evaluator.app.inference_hooks import ProgressTrackingHook, new_hooks

# Use the same file naming convention as metrics for consistency
from nmp.evaluator.app.jobs.constants import (
    EVALUATION_RESULTS_AGG_SCORES_FILE_NAME,
    EVALUATION_RESULTS_ROW_SCORES_FILE_NAME,
)
from nmp.evaluator.app.jobs.metric_results import ResultsHandlerConfig, handle_results_async
from nmp.evaluator.app.jobs.progress_tracking import ProgressTracking
from nmp.evaluator.app.metrics.metric import new_metric
from nmp.evaluator.app.tasks.termination import register_task_signal_handlers
from nmp.evaluator.app.values import (
    BenchmarkEvaluationResult,
    BenchmarkJobAdapter,
    BenchmarkOfflineJob,
    BenchmarkOnlineAgentJob,
    BenchmarkOnlineJob,
)

log = logging.getLogger(__name__)


_BenchmarkJob = BenchmarkOfflineJob | BenchmarkOnlineJob | BenchmarkOnlineAgentJob


def _apply_optional_fields_to_row(row: dict, optional_fields: set[str]) -> dict:
    normalized = dict(row)
    for field in optional_fields:
        normalized.setdefault(field, "")
    return normalized


# =============================================================================
# Artifacts
# =============================================================================


def job_artifacts_dump(
    job: _BenchmarkJob,
    evaluation_result: BenchmarkEvaluationResult,
    row_scores: list[RowScore],
    results_dir: str,
):
    """Write job artifacts to file.

    * job.json: job configuration
    * benchmark_row_scores.jsonl: row-level scores for each item
    * benchmark_results.json: aggregated evaluation for all metrics
    """
    os.makedirs(results_dir, exist_ok=True)

    with open(f"{results_dir}/job.json", "w") as f:
        f.write(job.model_dump_json(indent=2, exclude_none=True))

    with open(f"{results_dir}/{EVALUATION_RESULTS_ROW_SCORES_FILE_NAME}", "w") as f:
        for row in row_scores:
            f.write(row.model_dump_json() + "\n")

    with open(os.path.join(results_dir, EVALUATION_RESULTS_AGG_SCORES_FILE_NAME), "w") as f:
        f.write(evaluation_result.model_dump_json(indent=2, exclude_none=True))


# =============================================================================
# Entrypoint
# =============================================================================


def benchmark_evaluation_entrypoint() -> list[str]:
    """Entrypoint for benchmark evaluation job."""
    return ["python", "-m", "nmp.evaluator.tasks.evaluate_benchmark"]


def benchmark_evaluation_entrypoint_args(
    progress_tracking_url: str | None = None,
    progress_tracking_interval: int | None = None,
) -> list[str]:
    """Command args to run benchmark evaluation job."""
    command: list[str] = []
    if progress_tracking_url:
        command.extend(["--progress-tracking-url", progress_tracking_url])
    if progress_tracking_interval:
        command.extend(["--progress-tracking-interval", str(progress_tracking_interval)])
    return command


def _default_results_dir() -> str:
    return str(Path(os.environ.get(PERSISTENT_JOB_STORAGE_PATH_ENVVAR, DEFAULT_JOB_STORAGE_PATH)) / "results")


def _default_dataset_dir() -> str:
    return str(Path(os.environ.get(PERSISTENT_JOB_STORAGE_PATH_ENVVAR, DEFAULT_JOB_STORAGE_PATH)) / "datasets")


def _default_config_file() -> str:
    return os.environ.get(NEMO_JOB_STEP_CONFIG_FILE_PATH_ENVVAR, DEFAULT_NEMO_JOB_STEP_CONFIG_FILE_PATH)


def _build_results_handler_config(skip_upload_results: bool) -> ResultsHandlerConfig:
    """Build result-upload configuration from env or no-op placeholders.

    When uploads are enabled, this relies on ``BaseSettings`` environment
    resolution to populate the required Jobs MS fields.
    """
    if skip_upload_results:
        return ResultsHandlerConfig(NEMO_JOB_ID="", NEMO_JOB_WORKSPACE="")
    results_handler_config = cast(Any, ResultsHandlerConfig)()
    return results_handler_config


def _resolve_effective_params(
    job: _BenchmarkJob,
) -> RunConfig | RunConfigOnline | RunConfigOnlineModel:
    """Return a concrete params object for the benchmark job type.

    Benchmark jobs allow ``params=None`` in their schemas, but the execution
    path expects a concrete params model when reading fields like
    ``limit_samples`` or forwarding params into the SDK runtime.
    """
    if isinstance(job, BenchmarkOnlineAgentJob):
        return job.params or RunConfigOnline()
    if isinstance(job, BenchmarkOnlineJob):
        return job.params or RunConfigOnlineModel()
    return job.params or RunConfig()


# =============================================================================
# Dataset Loading
# =============================================================================


def _load_dataset_items(job: _BenchmarkJob, dataset_dir: str | None = None) -> list[dict]:
    """Load dataset items from the benchmark's dataset (downloaded file).

    Benchmark datasets are always FilesetRefs that should have been downloaded
    by a prior dataset-download step. The download step places files at:
    {dataset_dir}/{workspace}/{fileset-name}/

    The FilesetRef can include a fragment to specify which files to load:
        - workspace/fileset: Load all parsable files
        - workspace/fileset#file.json: Load a specific file
        - workspace/fileset#*.jsonl: Load files matching a glob pattern

    Args:
        job: The benchmark job containing the benchmark configuration.
        dataset_dir: Base directory for downloaded datasets. Defaults to the job runtime storage dataset directory.

    Returns:
        List of dataset items for evaluation.
    """
    effective_dir = dataset_dir or _default_dataset_dir()
    optional_fields = {
        field
        for benchmark_metric in job.benchmark.metrics
        for field in getattr(benchmark_metric.metric, "optional_fields", [])
    }

    # FilesetRef downloads to {dataset_dir}/{workspace}/{fileset-name}/
    # The dataset.root is in format "workspace/fileset-name[#pattern]"
    dataset_ref = job.benchmark.dataset.root

    try:
        items = load_dataset_from_ref_as_dicts(dataset_ref, base_dir=effective_dir)
    except DatasetLoadError as e:
        raise ValueError(
            f"Failed to load benchmark dataset '{dataset_ref}': {e}. "
            f"The dataset should have been downloaded by the dataset-download step."
        ) from e

    if not items:
        raise ValueError(f"Benchmark dataset '{dataset_ref}' is empty")

    log.info(f"Loaded {len(items)} items from benchmark dataset '{dataset_ref}'")
    return [
        _apply_optional_fields_to_row(apply_column_mapping_to_row(item, job.benchmark.field_mapping), optional_fields)
        for item in items
    ]


# =============================================================================
# Evaluation Logic
# =============================================================================


async def evaluate_benchmark(
    job: _BenchmarkJob,
    results_dir: str,
    progress_tracking: ProgressTracking | None = None,
    *,
    dataset_dir: str | None = None,
    inference_fn: InferenceFn | None = None,
) -> BenchmarkEvaluationResult:
    """Entrypoint to run benchmark evaluation with Jobs MS.

    Evaluates all metrics in the benchmark against the dataset.

    Args:
        job: The benchmark job configuration.
        results_dir: Directory to write evaluation results.
        progress_tracking: Optional progress tracking for job updates.
        dataset_dir: Directory containing downloaded dataset files.
        inference_fn: Function to make inference requests.

    Returns:
        BenchmarkEvaluationResult with aggregated results per metric.
    """
    judge_inference_fn: InferenceFn = inference_fn or make_inference_request
    effective_params = _resolve_effective_params(job)

    benchmark = job.benchmark
    log.info(
        "Starting benchmark evaluation",
        extra={
            "benchmark_name": benchmark.name,
            "metric_count": len(benchmark.metrics),
        },
    )

    # Load dataset items
    items = _load_dataset_items(job, dataset_dir=dataset_dir)

    if effective_params.limit_samples:
        log.debug("Limiting samples", extra={"limit": effective_params.limit_samples})
        items = items[: effective_params.limit_samples]

    log.debug("Evaluation configuration", extra={"results_dir": results_dir, "total_rows": len(items)})

    # Prepare target (model or agent) for online evaluation
    target: Model | Agent | None = None
    target_inference_fn: InferenceFn | AgentInferenceFn | None = None
    preprocess_hooks, postprocess_hooks = [], []
    default_headers: dict[str, str] | None = None

    # TODO: Hooks to be aware of agents as well.
    if isinstance(job, BenchmarkOnlineAgentJob):
        target = job.agent
        target_inference_fn = make_agent_inference_request
        default_headers = get_platform_headers(job.agent.url)
        preprocess_hooks, postprocess_hooks = new_hooks(effective_params)
    elif isinstance(job, BenchmarkOnlineJob):
        target = job.model
        target_inference_fn = judge_inference_fn
        default_headers = get_platform_headers(job.model.url)
        preprocess_hooks, postprocess_hooks = new_hooks(effective_params, target.format)

    if progress_tracking:
        progress_tracking.total_samples = len(items)
        progress_tracking.total_work = len(items) * len(benchmark.metrics)
        # Setup progress tracking as a hook
        postprocess_hooks.append(ProgressTrackingHook(progress_tracking))
        log.debug("Progress tracking configured", extra={"interval": progress_tracking.interval})

    metric_instances = []
    for bm in benchmark.metrics:
        metric = await new_metric(
            bm.metric,
            job.__job_type__,
            inference_fn=judge_inference_fn,
            run_preflight=True,
        )
        metric_instances.append(metric)

    metrics_built = [
        (bm.metric_ref.root, metric) for bm, metric in zip(benchmark.metrics, metric_instances, strict=True)
    ]

    try:
        sdk_result = await sdk_evaluate_benchmark(
            metrics=metrics_built,
            rows=items,
            target=target,
            inference_fn=target_inference_fn,
            params=effective_params,
            prompt_template=getattr(job, "prompt_template", None),
            preprocess_hooks=preprocess_hooks,
            postprocess_hooks=postprocess_hooks,
            default_headers=default_headers,
            progress=progress_tracking,
            logger=log,
        )
    except EvaluationError as exc:
        log.exception(
            "Benchmark evaluation failed",
            extra={
                "phase": exc.phase.value,
                "metric_key": exc.metric_key,
                "row_index": exc.index,
                "error": exc.message,
            },
        )
        raise
    except Exception as exc:
        # Anything here is not a structured row-level benchmark failure. Keep
        # the raw exception for unexpected SDK pipeline or aggregation errors.
        root = first_failure_cause(exc)
        log.exception(
            "Benchmark execution failed with an unexpected pipeline error",
            extra={
                "root_error_type": type(root).__name__,
                "root_error": str(root),
                "raw_error_type": type(exc).__name__,
            },
        )
        raise

    row_scores: list[RowScore] = list(sdk_result.row_scores)
    evaluation_result = BenchmarkEvaluationResult.from_sdk_results(sdk_result, benchmark.metrics)

    for metric_result in evaluation_result.results:
        log.info(
            "Metric evaluation completed",
            extra={
                "metric_ref": metric_result.metric.root if metric_result.metric is not None else None,
                "scores": {s.name: (round(s.mean, 4) if s.mean is not None else None) for s in metric_result.scores},
            },
        )

    log.debug("Writing job artifacts to disk")
    job_artifacts_dump(job, evaluation_result, row_scores, results_dir)

    log.info("Benchmark evaluation completed", extra={"benchmark_name": benchmark.name})

    if progress_tracking:
        if isinstance(job, BenchmarkOfflineJob):
            # This is a placeholder until we resolve conflict with benchmark pipeline refactor
            progress_tracking.increment_samples_processed(len(items))
        progress_tracking.update_progress(100)

    return evaluation_result


# =============================================================================
# CLI Entry Point
# =============================================================================


async def main(
    args: Sequence[str] | None = None,
    *,
    sdk: AsyncNeMoPlatform | None = None,
) -> int:
    """Main entry point for the evaluate_benchmark task.

    Args:
        args: Optional list of CLI arguments (for testing). If None, uses sys.argv.
        sdk: Optional SDK instance for dependency injection (for testing).

    Returns:
        Exit code (0 for success, non-zero for failure).
    """
    import argparse

    initialize_logging()

    parser = argparse.ArgumentParser(description="Evaluate a benchmark")
    parser.add_argument(
        "--progress-tracking-url",
        type=str,
        default=os.getenv("EVALUATIONS_CALLBACK_URL"),
        help="Optional callback URL to update progress tracking details.",
    )
    parser.add_argument(
        "--progress-tracking-interval",
        type=int,
        default=50,
        help="Interval to update progress tracking details.",
    )
    parser.add_argument(
        "--progress-tracking-interval-seconds",
        type=int,
        default=60,
        help="Time interval (seconds) to update progress tracking details.",
    )
    parser.add_argument(
        "--skip-upload-results",
        action="store_true",
        default=False,
        help="Skip uploading results to Jobs MS",
    )
    parsed_args = parser.parse_args(args)
    results_dir = _default_results_dir()
    config_file = _default_config_file()

    results_handler_config = _build_results_handler_config(parsed_args.skip_upload_results)

    with open(config_file, "r") as f:
        job_config = json.load(f)

    job: _BenchmarkJob = BenchmarkJobAdapter.validate_python(job_config)

    progress_tracking = None
    try:
        if parsed_args.progress_tracking_url:
            progress_tracking = ProgressTracking(
                parsed_args.progress_tracking_url,
                parsed_args.progress_tracking_interval,
                parsed_args.progress_tracking_interval_seconds,
            )
        else:
            log.warning("Progress tracking is not configured.")

        evaluation_result = await evaluate_benchmark(job, results_dir, progress_tracking)

        if not parsed_args.skip_upload_results:
            effective_sdk = sdk or get_async_platform_sdk()
            await handle_results_async(job, results_handler_config, results_dir, sdk=effective_sdk)

        # Check if any metrics have results
        has_results = any(
            any(score.count > 0 for score in metric_result.scores) for metric_result in evaluation_result.results
        )

        if not has_results:
            raise ValueError(
                f"Job {results_handler_config.NEMO_JOB_ID} completed but no evaluation results detected. "
                f"Job marked as failed."
            )

        return 0
    finally:
        if progress_tracking:
            progress_tracking.stop()


def run(
    args: Sequence[str] | None = None,
    *,
    sdk: AsyncNeMoPlatform | None = None,
) -> int:
    """Synchronous wrapper for main() - for task_harness compatibility.

    Args:
        args: Optional list of CLI arguments (for testing). If None, uses sys.argv.
        sdk: Optional SDK instance for dependency injection (for testing).

    Returns:
        Exit code (0 for success, non-zero for failure).
    """
    register_task_signal_handlers()
    try:
        return asyncio.run(main(args, sdk=sdk))
    except KeyboardInterrupt:
        log.info("Received termination signal. Exiting task gracefully.")
        return 0
    except BaseException as exc:
        root = first_failure_cause(exc)
        log.exception(
            "Error in evaluate_benchmark task",
            extra={"root_error_type": type(root).__name__, "root_error": str(root)},
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(run())
