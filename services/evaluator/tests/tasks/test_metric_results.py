# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import json
from pathlib import Path

import pytest
from nmp.common.jobs.constants import NEMO_JOB_STEP_CONFIG_FILE_PATH_ENVVAR, PERSISTENT_JOB_STORAGE_PATH_ENVVAR
from nmp.evaluator.tasks.metric_results.__main__ import main
from pytest_mock import MockerFixture


@pytest.mark.asyncio
async def test_defaults_to_job_runtime_environment(
    tmp_path: Path, mocker: MockerFixture, monkeypatch: pytest.MonkeyPatch
) -> None:
    config_file = tmp_path / "job_step_config.json"
    storage_dir = tmp_path / "job-storage"
    expected_results_dir = str(storage_dir / "results")
    config_file.write_text(json.dumps({}))
    job = mocker.Mock()
    results_config = mocker.Mock()
    sdk = mocker.Mock()

    monkeypatch.setenv(NEMO_JOB_STEP_CONFIG_FILE_PATH_ENVVAR, str(config_file))
    monkeypatch.setenv(PERSISTENT_JOB_STORAGE_PATH_ENVVAR, str(storage_dir))

    mocker.patch("nmp.evaluator.tasks.metric_results.__main__.MetricJobAdapter.validate_python", return_value=job)
    mocker.patch("nmp.evaluator.tasks.metric_results.__main__.ResultsHandlerConfig", return_value=results_config)
    mocker.patch("nmp.evaluator.tasks.metric_results.__main__.get_async_platform_sdk", return_value=sdk)
    handle_results = mocker.patch(
        "nmp.evaluator.tasks.metric_results.__main__.handle_results_async",
        new_callable=mocker.AsyncMock,
    )

    assert await main([]) == 0
    handle_results.assert_awaited_once_with(job, results_config, expected_results_dir, sdk=sdk)
