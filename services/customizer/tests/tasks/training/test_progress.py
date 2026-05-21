# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Unit tests for training progress reporting."""

from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

from nmp.customizer.app.jobs.context import NMPJobContext
from nmp.customizer.tasks.training.progress import JobsServiceProgressReporter
from pytest import MonkeyPatch
from pytest_mock import MockerFixture


class TestJobsServiceProgressReporter:
    """Tests for JobsServiceProgressReporter."""

    def _make_reporter(
        self, mocker: MockerFixture, monkeypatch: MonkeyPatch, tmp_path: Path, **ctx_overrides: Any
    ) -> tuple[JobsServiceProgressReporter, MagicMock]:
        mock_sdk = mocker.MagicMock()
        mocker.patch("nmp.customizer.tasks.training.progress.get_task_sdk", return_value=mock_sdk)
        monkeypatch.setenv("RANK", "0")
        defaults: dict[str, Any] = dict(
            workspace="ws",
            job_id="job-1",
            attempt_id="attempt-0",
            step="training",
            task="abc123",
            jobs_url="http://jobs:8080",
            files_url="http://files:8000",
            storage_path=tmp_path,
            config_path=tmp_path / "config.json",
        )
        defaults.update(ctx_overrides)
        job_ctx = NMPJobContext(**defaults)
        return JobsServiceProgressReporter(job_ctx), mock_sdk

    def test_update_task_uses_normalized_task_name(
        self, mocker: MockerFixture, monkeypatch: MonkeyPatch, tmp_path: Path
    ):
        """Should send normalized task name in create_or_update callbacks."""
        raw_task = "22ae6989-fcbe-4be2-8c89-37ef9da06aec"
        reporter, mock_sdk = self._make_reporter(
            mocker, monkeypatch, tmp_path, workspace="test-workspace", job_id="job-123", task=raw_task
        )

        reporter.update_task(status="active", status_details={"phase": "training"})

        mock_sdk.jobs.tasks.create_or_update.assert_called_once_with(
            name=f"task-{raw_task}",
            workspace="test-workspace",
            job="job-123",
            step="training",
            status="active",
            status_details={"phase": "training"},
            error_details={},
        )

    def test_report_completed_includes_phase(self, mocker: MockerFixture, monkeypatch: MonkeyPatch, tmp_path: Path):
        """report_completed should set phase='completed' so it isn't left stale."""
        reporter, mock_sdk = self._make_reporter(mocker, monkeypatch, tmp_path)

        reporter.report_completed("Training completed")

        call_kwargs = mock_sdk.jobs.tasks.create_or_update.call_args.kwargs
        assert call_kwargs["status"] == "completed"
        assert call_kwargs["status_details"]["phase"] == "completed"
        assert call_kwargs["status_details"]["message"] == "Training completed"

    def test_fetch_current_metrics_returns_server_data(
        self, mocker: MockerFixture, monkeypatch: MonkeyPatch, tmp_path: Path
    ):
        """fetch_current_metrics should return metrics from the server task."""
        reporter, mock_sdk = self._make_reporter(mocker, monkeypatch, tmp_path)
        mock_task = mocker.MagicMock()
        mock_task.status_details = {
            "phase": "training",
            "metrics": {
                "train_loss": [{"step": 1, "epoch": 1, "value": 3.21}],
                "val_loss": [{"step": 1, "epoch": 1, "value": 3.50}],
            },
        }
        mock_sdk.jobs.tasks.retrieve.return_value = mock_task

        result = reporter.fetch_current_metrics()

        mock_sdk.jobs.tasks.retrieve.assert_called_once_with(
            name="task-abc123",
            workspace="ws",
            job="job-1",
            step="training",
        )
        assert result["train_loss"] == [{"step": 1, "epoch": 1, "value": 3.21}]
        assert result["val_loss"] == [{"step": 1, "epoch": 1, "value": 3.50}]

    def test_fetch_current_metrics_returns_empty_on_error(
        self, mocker: MockerFixture, monkeypatch: MonkeyPatch, tmp_path: Path
    ):
        """fetch_current_metrics should return empty lists if the server call fails."""
        reporter, mock_sdk = self._make_reporter(mocker, monkeypatch, tmp_path)
        mock_sdk.jobs.tasks.retrieve.side_effect = Exception("Not found")

        result = reporter.fetch_current_metrics()

        assert result == {"train_loss": [], "val_loss": []}
