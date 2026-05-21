# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Tests for fileset download job step utilities."""

import json
from typing import Any, cast
from unittest.mock import patch

from nemo_evaluator_sdk.values import DatasetRows
from nmp.common.files.storage_config import HuggingfaceStorageConfig
from nmp.common.jobs.constants import (
    DEFAULT_NEMO_JOB_STEP_CONFIG_FILE_PATH,
    EPHEMERAL_TASK_STORAGE_PATH_ENVVAR,
    PERSISTENT_JOB_STORAGE_PATH_ENVVAR,
)
from nmp.evaluator.app.jobs.fileset import (
    fileset_entrypoint,
    fileset_entrypoint_args,
    get_fileset_step,
)
from nmp.evaluator.app.values import Fileset, FilesetRef


def make_hf_storage_config() -> HuggingfaceStorageConfig:
    """Create a test HuggingfaceStorageConfig."""
    return HuggingfaceStorageConfig(
        repo_id="test-org/test-repo",
        repo_type="dataset",
    )


class TestFilesetEntrypoint:
    def test_returns_python_task_entrypoint(self):
        """Test that fileset_entrypoint returns python module entrypoint."""
        result = fileset_entrypoint()
        assert result == ["python", "-m", "nmp.evaluator.tasks.download_fileset"]


class TestFilesetEntrypointArgs:
    def test_fileset_ref_serializes_root_string(self):
        """Test that FilesetRef serializes just the root string."""
        dataset = FilesetRef(root="workspace/my-fileset")
        result = fileset_entrypoint_args(dataset, "/target/dir", "/scratch")

        assert len(result) == 6
        assert result[4] == "--dataset"
        assert json.loads(result[5]) == "workspace/my-fileset"
        assert result[result.index("--local-dir") + 1] == "/scratch"
        assert result[result.index("--target-dir") + 1] == "/target/dir"

    def test_inline_dataset_serializes_model_dump(self):
        """Test that DatasetRows serializes the full model dump."""
        dataset = DatasetRows(rows=[{"a": 1}])
        result = fileset_entrypoint_args(dataset, "/target/dir", "/scratch")

        assert len(result) == 6
        assert result[4] == "--dataset-file"
        assert result[5] == DEFAULT_NEMO_JOB_STEP_CONFIG_FILE_PATH
        assert result[result.index("--local-dir") + 1] == "/scratch"
        assert result[result.index("--target-dir") + 1] == "/target/dir"

    def test_inline_fileset_serializes_model_dump(self):
        """Test that Fileset serializes the full model dump."""
        dataset = Fileset(storage=make_hf_storage_config(), path="data/file.json")
        result = fileset_entrypoint_args(dataset, "/target/dir", "/scratch")

        assert len(result) == 6
        dataset_arg = json.loads(result[5])
        assert dataset_arg["storage"]["repo_id"] == "test-org/test-repo"
        assert dataset_arg["path"] == "data/file.json"

    def test_scratch_path_with_env_var_is_preserved(self):
        """Test that env var references in scratch_path are passed through."""
        dataset = FilesetRef(root="workspace/my-fileset")
        scratch_path = "${SCRATCH_DIR}"
        result = fileset_entrypoint_args(dataset, "/target/dir", scratch_path)

        assert result[result.index("--local-dir") + 1] == "${SCRATCH_DIR}"
        assert result[result.index("--target-dir") + 1] == "/target/dir"


class TestGetFilesetStep:
    @patch("nmp.evaluator.app.jobs.fileset.get_qualified_image")
    @patch("nmp.evaluator.app.jobs.fileset.settings")
    def test_creates_platform_job_step(self, settings, mock_get_image):
        """Test that get_fileset_step creates a properly configured PlatformJobStep."""
        settings.jobs.dataset_dir = "/data/datasets"
        settings.jobs.volume_path = "/job/volume"
        mock_get_image.return_value = "registry/nmp-cpu-tasks:latest"

        dataset = FilesetRef(root="workspace/my-fileset")
        result = get_fileset_step(dataset, "download-step")

        assert result["name"] == "download-step"
        assert result["executor"]["provider"] == "cpu"
        container = _get_container(result)
        assert container["image"] == "registry/nmp-cpu-tasks:latest"
        assert container["entrypoint"] == [
            "python",
            "-m",
            "nmp.evaluator.tasks.download_fileset",
        ]
        mock_get_image.assert_called_once_with("nmp-cpu-tasks")

    @patch("nmp.evaluator.app.jobs.fileset.get_qualified_image")
    @patch("nmp.evaluator.app.jobs.fileset.settings")
    def test_sets_environment_variables(self, settings, mock_get_image):
        """Test that get_fileset_step sets the required environment variables."""
        settings.jobs.dataset_dir = "/data/datasets"
        settings.jobs.volume_path = "/job/volume"
        mock_get_image.return_value = "registry/nmp-cpu-tasks:latest"

        dataset = FilesetRef(root="workspace/my-fileset")
        result = get_fileset_step(dataset, "download-step")

        env_names = {env["name"] for env in result["environment"]}
        assert PERSISTENT_JOB_STORAGE_PATH_ENVVAR in env_names
        for env in result["environment"]:
            if env["name"] == PERSISTENT_JOB_STORAGE_PATH_ENVVAR:
                assert env["value"] == "/job/volume"

    @patch("nmp.evaluator.app.jobs.fileset.get_qualified_image")
    @patch("nmp.evaluator.app.jobs.fileset.settings")
    def test_uses_ephemeral_storage_for_scratch(self, settings, mock_get_image):
        """Test that get_fileset_step uses ephemeral storage env var for scratch path."""
        settings.jobs.dataset_dir = "/data/datasets"
        settings.jobs.volume_path = "/job/volume"
        mock_get_image.return_value = "registry/nmp-cpu-tasks:latest"

        dataset = FilesetRef(root="workspace/my-fileset")
        result = get_fileset_step(dataset, "download-step")

        command = _get_container(result)["command"]
        assert command[command.index("--local-dir") + 1] == f"${{{EPHEMERAL_TASK_STORAGE_PATH_ENVVAR}}}"

    @patch("nmp.evaluator.app.jobs.fileset.get_qualified_image")
    @patch("nmp.evaluator.app.jobs.fileset.settings")
    def test_command_targets_runtime_job_dataset_dir(self, settings, mock_get_image):
        """Test that get_fileset_step targets the runtime job storage dataset directory."""
        settings.jobs.dataset_dir = "/custom/dataset/path"
        settings.jobs.volume_path = "/job/volume"
        mock_get_image.return_value = "registry/nmp-cpu-tasks:latest"

        dataset = FilesetRef(root="workspace/my-fileset")
        result = get_fileset_step(dataset, "download-step")

        command = _get_container(result)["command"]
        assert command[command.index("--target-dir") + 1] == f"${{{PERSISTENT_JOB_STORAGE_PATH_ENVVAR}}}/datasets"

    @patch("nmp.evaluator.app.jobs.fileset.get_qualified_image")
    @patch("nmp.evaluator.app.jobs.fileset.settings")
    def test_works_with_inline_dataset(self, settings, mock_get_image):
        """Test that get_fileset_step works with DatasetRows."""
        settings.jobs.dataset_dir = "/data/datasets"
        settings.jobs.volume_path = "/job/volume"
        mock_get_image.return_value = "registry/nmp-cpu-tasks:latest"

        dataset = DatasetRows(rows=[{"a": 1}])
        result = get_fileset_step(dataset, "download-inline")

        assert result["name"] == "download-inline"
        command = _get_container(result)["command"]
        assert len(command) == 6
        assert command[4] == "--dataset-file"

    @patch("nmp.evaluator.app.jobs.fileset.get_qualified_image")
    @patch("nmp.evaluator.app.jobs.fileset.settings")
    def test_works_with_inline_fileset(self, settings, mock_get_image):
        """Test that get_fileset_step works with Fileset."""
        settings.jobs.dataset_dir = "/data/datasets"
        settings.jobs.volume_path = "/job/volume"
        mock_get_image.return_value = "registry/nmp-cpu-tasks:latest"

        dataset = Fileset(storage=make_hf_storage_config(), path="data/file.json")
        result = get_fileset_step(dataset, "download-hf")

        assert result["name"] == "download-hf"
        command = _get_container(result)["command"]
        dataset_arg = json.loads(command[command.index("--dataset") + 1])
        assert dataset_arg["storage"]["repo_id"] == "test-org/test-repo"


def _get_container(step: object) -> dict[str, Any]:
    step_dict = cast(dict[str, Any], step)
    return cast(dict[str, Any], step_dict["executor"]["container"])
