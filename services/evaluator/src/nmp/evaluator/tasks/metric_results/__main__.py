# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import argparse
import asyncio
import json
import logging
import os
from collections.abc import Sequence
from pathlib import Path

from nmp.common.jobs.constants import (
    DEFAULT_JOB_STORAGE_PATH,
    DEFAULT_NEMO_JOB_STEP_CONFIG_FILE_PATH,
    NEMO_JOB_STEP_CONFIG_FILE_PATH_ENVVAR,
    PERSISTENT_JOB_STORAGE_PATH_ENVVAR,
)
from nmp.common.observability.otel import initialize_logging
from nmp.common.sdk_factory import get_async_platform_sdk
from nmp.evaluator.app.jobs.metric_results import ResultsHandlerConfig, handle_results_async
from nmp.evaluator.app.jobs.progress_tracking import ProgressTracking
from nmp.evaluator.app.tasks.termination import register_task_signal_handlers
from nmp.evaluator.app.values import (
    BenchmarkJobAdapter,
    MetricJobAdapter,
)

log = logging.getLogger(__name__)


def _default_results_dir() -> str:
    return str(Path(os.environ.get(PERSISTENT_JOB_STORAGE_PATH_ENVVAR, DEFAULT_JOB_STORAGE_PATH)) / "results")


def _default_config_file() -> str:
    return os.environ.get(NEMO_JOB_STEP_CONFIG_FILE_PATH_ENVVAR, DEFAULT_NEMO_JOB_STEP_CONFIG_FILE_PATH)


async def main(args: Sequence[str] | None = None) -> int:
    """Async implementation of the metric_results task.

    Args:
        args: Optional list of CLI arguments (for testing). If None, uses sys.argv.

    Returns:
        Exit code (0 for success, 1 for failure).
    """
    # Configure logging using platform's standard setup for consistent formatting
    initialize_logging()

    parser = argparse.ArgumentParser(description="Process evaluation results")

    parser.add_argument(
        "--progress-tracking-url",
        type=str,
        default=None,
        help="Optional callback URL to update progress tracking details.",
    )

    parsed_args = parser.parse_args(args)
    results_dir = _default_results_dir()
    config_file = _default_config_file()
    progress_tracking = None

    with open(config_file, "r") as f:
        job_config = json.load(f)

    if "benchmark" in job_config:
        job = BenchmarkJobAdapter.validate_python(job_config)
    else:
        job = MetricJobAdapter.validate_python(job_config)

    try:
        sdk = get_async_platform_sdk(
            as_service="evaluator",
            internal=True,
        )
        await handle_results_async(
            job,
            ResultsHandlerConfig(),  # ty: ignore[missing-argument]
            results_dir,
            sdk=sdk,
        )

        if parsed_args.progress_tracking_url:
            progress_tracking = ProgressTracking(parsed_args.progress_tracking_url)
            # Update job progress to 100% when contains results
            progress_tracking.update_progress(100)
        else:
            log.warning("Progress tracking is not configured.")

        return 0
    except Exception:
        log.exception("Error handling results")
        return 1
    finally:
        if progress_tracking:
            progress_tracking.stop()


def run(args: Sequence[str] | None = None) -> int:
    """Synchronous entry point for the metric_results task.

    Args:
        args: Optional list of CLI arguments (for testing). If None, uses sys.argv.

    Returns:
        Exit code (0 for success, 1 for failure).
    """
    register_task_signal_handlers()
    try:
        return asyncio.run(main(args))
    except KeyboardInterrupt:
        log.info("Received termination signal. Exiting task gracefully.")
        return 0
    except Exception:
        log.exception("Error in metric_results task")
        return 1


if __name__ == "__main__":
    raise SystemExit(run())
