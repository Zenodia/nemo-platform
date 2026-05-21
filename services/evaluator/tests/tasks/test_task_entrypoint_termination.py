# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

from pathlib import Path
from typing import Any, Coroutine

import pytest
from nmp.common.jobs.constants import NEMO_JOB_STEP_CONFIG_FILE_PATH_ENVVAR, PERSISTENT_JOB_STORAGE_PATH_ENVVAR
from nmp.evaluator.tasks.download_fileset import __main__ as download_fileset_task
from nmp.evaluator.tasks.evaluate_benchmark import __main__ as evaluate_benchmark_task
from nmp.evaluator.tasks.evaluate_metric import __main__ as evaluate_metric_task
from nmp.evaluator.tasks.metric_results import __main__ as metric_results_task
from pytest_mock import MockerFixture


def _raise_keyboard_interrupt(main_coro: Coroutine[Any, Any, int]) -> None:
    main_coro.close()
    raise KeyboardInterrupt


def _raise_runtime_error(main_coro: Coroutine[Any, Any, int]) -> None:
    main_coro.close()
    raise RuntimeError("boom")


@pytest.mark.parametrize(
    "task_module",
    [
        pytest.param(download_fileset_task, id="download_fileset"),
        pytest.param(evaluate_metric_task, id="evaluate_metric"),
        pytest.param(evaluate_benchmark_task, id="evaluate_benchmark"),
        pytest.param(metric_results_task, id="metric_results"),
    ],
)
class TestRun:
    def test_returns_zero_on_keyboard_interrupt(self, mocker: MockerFixture, task_module):
        register_handlers = mocker.patch.object(task_module, "register_task_signal_handlers")
        mocker.patch.object(task_module.asyncio, "run", side_effect=_raise_keyboard_interrupt)

        result = task_module.run()

        assert result == 0
        register_handlers.assert_called_once_with()

    def test_returns_one_on_exception(self, mocker: MockerFixture, task_module):
        register_handlers = mocker.patch.object(task_module, "register_task_signal_handlers")
        mocker.patch.object(task_module.asyncio, "run", side_effect=_raise_runtime_error)

        result = task_module.run()

        assert result == 1
        register_handlers.assert_called_once_with()


@pytest.mark.parametrize(
    ("task_module", "job_config_cls", "validate_method", "eval_fn", "config_filename", "extra_args"),
    [
        pytest.param(
            evaluate_metric_task,
            evaluate_metric_task.MetricJobAdapter,
            "validate_python",
            "evaluate_metric",
            "metric-job.json",
            ["--skip-upload-results", "true"],
            id="evaluate_metric",
        ),
        pytest.param(
            evaluate_benchmark_task,
            evaluate_benchmark_task.BenchmarkJobAdapter,
            "validate_python",
            "evaluate_benchmark",
            "benchmark-job.json",
            ["--skip-upload-results"],
            id="evaluate_benchmark",
        ),
    ],
)
class TestMainStopsProgressTrackingOnKeyboardInterrupt:
    @pytest.mark.asyncio
    async def test_stops_progress_tracking_on_keyboard_interrupt(
        self,
        tmp_path: Path,
        mocker: MockerFixture,
        task_module,
        job_config_cls,
        validate_method,
        eval_fn,
        config_filename,
        extra_args,
        monkeypatch: pytest.MonkeyPatch,
    ):
        config_path = tmp_path / config_filename
        config_path.write_text("{}")
        monkeypatch.setenv(NEMO_JOB_STEP_CONFIG_FILE_PATH_ENVVAR, str(config_path))
        monkeypatch.setenv(PERSISTENT_JOB_STORAGE_PATH_ENVVAR, str(tmp_path))

        progress_tracking = mocker.Mock()
        mocker.patch.object(task_module, "ProgressTracking", return_value=progress_tracking)
        mocker.patch.object(job_config_cls, validate_method, return_value=mocker.Mock())
        mocker.patch.object(task_module, eval_fn, new=mocker.AsyncMock(side_effect=KeyboardInterrupt))

        with pytest.raises(KeyboardInterrupt):
            await task_module.main(
                [
                    "--progress-tracking-url",
                    "http://example.com/progress",
                    *extra_args,
                ]
            )

        progress_tracking.stop.assert_called_once()
