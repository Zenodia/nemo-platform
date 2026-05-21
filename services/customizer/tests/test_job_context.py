# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Unit tests for NMPJobContext."""

from pathlib import Path

import pytest
from nmp.common.entities.constants import DEFAULT_WORKSPACE
from nmp.common.jobs.constants import (
    DEFAULT_NEMO_JOB_STEP_CONFIG_FILE_PATH,
    NEMO_JOB_ATTEMPT_ID_ENVVAR,
    NEMO_JOB_ID_ENVVAR,
    NEMO_JOB_STEP_CONFIG_FILE_PATH_ENVVAR,
    NEMO_JOB_STEP_ENVVAR,
    NEMO_JOB_TASK_ENVVAR,
    NEMO_JOB_WORKSPACE_ENVVAR,
    PERSISTENT_JOB_STORAGE_PATH_ENVVAR,
)
from nmp.customizer.app.constants import (
    DEFAULT_JOB_STORAGE_PATH,
    NMP_FILES_URL_ENVVAR,
    NMP_JOBS_URL_ENVVAR,
)
from nmp.customizer.app.jobs.context import (
    DEFAULT_ATTEMPT_ID,
    DEFAULT_JOB_ID,
    DEFAULT_STEP,
    DEFAULT_TASK,
    NMPJobContext,
)


class TestNMPJobContextFromEnv:
    """Tests for NMPJobContext.from_env()"""

    def test_uses_defaults_when_env_vars_not_set(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Verify that from_env uses sane defaults when environment variables are not set."""
        # Clear all relevant environment variables
        env_vars = [
            NEMO_JOB_WORKSPACE_ENVVAR,
            NEMO_JOB_ID_ENVVAR,
            NEMO_JOB_ATTEMPT_ID_ENVVAR,
            NEMO_JOB_STEP_ENVVAR,
            NEMO_JOB_TASK_ENVVAR,
            NMP_JOBS_URL_ENVVAR,
            NMP_FILES_URL_ENVVAR,
            PERSISTENT_JOB_STORAGE_PATH_ENVVAR,
            NEMO_JOB_STEP_CONFIG_FILE_PATH_ENVVAR,
        ]
        for var in env_vars:
            monkeypatch.delenv(var, raising=False)

        ctx = NMPJobContext.from_env()

        # Required fields should have sane defaults
        assert ctx.workspace == DEFAULT_WORKSPACE
        assert ctx.job_id == DEFAULT_JOB_ID
        assert ctx.attempt_id == DEFAULT_ATTEMPT_ID
        assert ctx.step == DEFAULT_STEP
        assert ctx.task == DEFAULT_TASK

        # Optional service URLs should be None
        assert ctx.jobs_url is None
        assert ctx.files_url is None

        # Storage paths should have defaults
        assert ctx.storage_path == Path(DEFAULT_JOB_STORAGE_PATH)
        assert ctx.config_path == Path(DEFAULT_NEMO_JOB_STEP_CONFIG_FILE_PATH)

    def test_uses_env_vars_when_set(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Verify that from_env uses environment variable values when they are set."""
        monkeypatch.setenv(NEMO_JOB_WORKSPACE_ENVVAR, "test-workspace")
        monkeypatch.setenv(NEMO_JOB_ID_ENVVAR, "job-123")
        monkeypatch.setenv(NEMO_JOB_ATTEMPT_ID_ENVVAR, "attempt-5")
        monkeypatch.setenv(NEMO_JOB_STEP_ENVVAR, "training")
        monkeypatch.setenv(NEMO_JOB_TASK_ENVVAR, "train-model")
        monkeypatch.setenv(NMP_JOBS_URL_ENVVAR, "http://jobs.example.com")
        monkeypatch.setenv(NMP_FILES_URL_ENVVAR, "http://files.example.com")
        monkeypatch.setenv(PERSISTENT_JOB_STORAGE_PATH_ENVVAR, "/custom/storage")
        monkeypatch.setenv(NEMO_JOB_STEP_CONFIG_FILE_PATH_ENVVAR, "/custom/config.json")

        ctx = NMPJobContext.from_env()

        assert ctx.workspace == "test-workspace"
        assert ctx.job_id == "job-123"
        assert ctx.attempt_id == "attempt-5"
        assert ctx.step == "training"
        assert ctx.task == "train-model"
        assert ctx.jobs_url == "http://jobs.example.com"
        assert ctx.files_url == "http://files.example.com"
        assert ctx.storage_path == Path("/custom/storage")
        assert ctx.config_path == Path("/custom/config.json")

    def test_required_fields_are_never_none(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Verify that required fields are always strings, never None."""
        # Clear all environment variables
        env_vars = [
            NEMO_JOB_WORKSPACE_ENVVAR,
            NEMO_JOB_ID_ENVVAR,
            NEMO_JOB_ATTEMPT_ID_ENVVAR,
            NEMO_JOB_STEP_ENVVAR,
            NEMO_JOB_TASK_ENVVAR,
        ]
        for var in env_vars:
            monkeypatch.delenv(var, raising=False)

        ctx = NMPJobContext.from_env()

        # These fields must be strings, not None
        assert isinstance(ctx.workspace, str)
        assert isinstance(ctx.job_id, str)
        assert isinstance(ctx.attempt_id, str)
        assert isinstance(ctx.step, str)
        assert isinstance(ctx.task, str)

        # They should not be empty strings either
        assert ctx.workspace != ""
        assert ctx.job_id != ""
        assert ctx.attempt_id != ""
        assert ctx.step != ""
        assert ctx.task != ""

    def test_normalizes_raw_uuid_task_name(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Verify raw UUID-like task names are preserved on task."""
        raw_uuid = "22ae6989-fcbe-4be2-8c89-37ef9da06aec"
        monkeypatch.setenv(NEMO_JOB_TASK_ENVVAR, raw_uuid)

        ctx = NMPJobContext.from_env()

        assert ctx.task == raw_uuid
        assert ctx.normalized_task == f"task-{raw_uuid}"

    def test_keeps_prefixed_uuid_task_name(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Verify already-prefixed task names are preserved."""
        task_name = "task-22ae6989-fcbe-4be2-8c89-37ef9da06aec"
        monkeypatch.setenv(NEMO_JOB_TASK_ENVVAR, task_name)

        ctx = NMPJobContext.from_env()

        assert ctx.task == task_name
        assert ctx.normalized_task == task_name

    def test_prefixes_human_readable_task_name(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Verify non-prefixed task names are normalized with task- prefix."""
        monkeypatch.setenv(NEMO_JOB_TASK_ENVVAR, "train-model")

        ctx = NMPJobContext.from_env()

        assert ctx.task == "train-model"
        assert ctx.normalized_task == "task-train-model"

    def test_direct_constructor_preserves_raw_task_name(self, tmp_path: Path) -> None:
        """Verify direct constructor preserves raw task while exposing normalized_task."""
        raw_uuid = "22ae6989-fcbe-4be2-8c89-37ef9da06aec"
        ctx = NMPJobContext(
            workspace="test-workspace",
            job_id="job-123",
            attempt_id="attempt-0",
            step="training",
            task=raw_uuid,
            jobs_url="http://jobs.example.com",
            files_url="http://files.example.com",
            storage_path=tmp_path,
            config_path=tmp_path / "config.json",
        )

        assert ctx.task == raw_uuid
        assert ctx.normalized_task == f"task-{raw_uuid}"
