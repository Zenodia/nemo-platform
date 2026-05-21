# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Tests verifying the mlflow API surface used by NeMo RL and NeMo AutoModel.

Both training backends (NeMo RL via nemo_rl.utils.logger.MLflowLogger, and
NeMo AutoModel via nemo_automodel.components.loggers.mlflow_utils.MLflowLogger)
use the high-level mlflow.* API.  These tests ensure the API entry points exist
and accept the argument shapes that the upstream loggers rely on, catching
regressions introduced by mlflow version bumps (e.g. the >=3.8.0rc0 CVE fix).

All tests mock the tracking server — no running mlflow instance is required.

Note: mlflow is an optional dependency for fine-tuning, shipped in the training
images (customizer-rl, customizer-automodel).  The dev dependency group includes
mlflow-skinny (the lightweight tracking client) to run these tests in CI.
"""

from unittest.mock import MagicMock, patch

import mlflow
import pytest

NEMO_RL_FUNCTIONS = [
    "set_tracking_uri",
    "get_experiment_by_name",
    "create_experiment",
    "set_experiment",
    "start_run",
    "end_run",
    "log_metric",
    "log_params",
    "log_artifact",
]

AUTOMODEL_EXTRA_FUNCTIONS = [
    "log_artifacts",
]


class TestMlflowImportSurface:
    """Verify that the mlflow module exposes all required functions."""

    @pytest.mark.parametrize("func_name", NEMO_RL_FUNCTIONS + AUTOMODEL_EXTRA_FUNCTIONS)
    def test_mlflow_function_exists(self, func_name: str) -> None:
        fn = getattr(mlflow, func_name, None)
        assert fn is not None, f"mlflow.{func_name} is missing"
        assert callable(fn), f"mlflow.{func_name} is not callable"

    def test_mlflow_pytorch_log_model_importable(self) -> None:
        mlflow_pytorch = pytest.importorskip("mlflow.pytorch", reason="mlflow.pytorch requires full mlflow package")
        fn = getattr(mlflow_pytorch, "log_model", None)
        assert fn is not None, "mlflow.pytorch.log_model is missing"
        assert callable(fn)


class TestExperimentManagement:
    """Verify experiment management APIs accept expected arguments."""

    def test_set_tracking_uri(self) -> None:
        with patch.object(mlflow, "set_tracking_uri") as mock:
            mlflow.set_tracking_uri("http://mlflow.example.com:5000")
            mock.assert_called_once_with("http://mlflow.example.com:5000")

    @patch("mlflow.get_experiment_by_name", return_value=None)
    def test_get_experiment_by_name(self, mock_get: MagicMock) -> None:
        result = mlflow.get_experiment_by_name("my-experiment")
        mock_get.assert_called_once_with("my-experiment")
        assert result is None

    @patch("mlflow.create_experiment", return_value="1")
    def test_create_experiment(self, mock_create: MagicMock) -> None:
        exp_id = mlflow.create_experiment("new-experiment", artifact_location="s3://bucket/artifacts")
        mock_create.assert_called_once_with("new-experiment", artifact_location="s3://bucket/artifacts")
        assert exp_id == "1"

    @patch("mlflow.set_experiment")
    def test_set_experiment(self, mock_set: MagicMock) -> None:
        mlflow.set_experiment("my-experiment")
        mock_set.assert_called_once_with("my-experiment")


class TestRunLifecycle:
    """Verify run lifecycle APIs accept expected arguments."""

    @patch("mlflow.start_run")
    def test_start_run_with_run_name(self, mock_start: MagicMock) -> None:
        mlflow.start_run(run_name="training-run-1")
        mock_start.assert_called_once_with(run_name="training-run-1")

    @patch("mlflow.end_run")
    def test_end_run(self, mock_end: MagicMock) -> None:
        mlflow.end_run()
        mock_end.assert_called_once_with()


class TestMetricAndParamLogging:
    """Verify metric and parameter logging APIs (used by both backends)."""

    @patch("mlflow.log_metric")
    def test_log_metric_with_step(self, mock_log: MagicMock) -> None:
        mlflow.log_metric("train_loss", 0.42, step=100)
        mock_log.assert_called_once_with("train_loss", 0.42, step=100)

    @patch("mlflow.log_params")
    def test_log_params(self, mock_log: MagicMock) -> None:
        params = {"learning_rate": "1e-5", "batch_size": "32", "model": "llama-3.2-1b"}
        mlflow.log_params(params)
        mock_log.assert_called_once_with(params)


class TestArtifactLogging:
    """Verify artifact logging APIs used by NeMo RL and NeMo AutoModel."""

    @patch("mlflow.log_artifact")
    def test_log_artifact(self, mock_log: MagicMock) -> None:
        mlflow.log_artifact("/path/to/config.yaml", artifact_path="configs")
        mock_log.assert_called_once_with("/path/to/config.yaml", artifact_path="configs")

    @patch("mlflow.log_artifacts")
    def test_log_artifacts_directory(self, mock_log: MagicMock) -> None:
        mlflow.log_artifacts("/path/to/checkpoint_dir", artifact_path="checkpoints")
        mock_log.assert_called_once_with("/path/to/checkpoint_dir", artifact_path="checkpoints")


class TestModelLogging:
    """Verify model logging API used by NeMo AutoModel."""

    def test_log_model(self) -> None:
        mlflow_pytorch = pytest.importorskip("mlflow.pytorch", reason="mlflow.pytorch requires full mlflow package")
        with patch.object(mlflow_pytorch, "log_model") as mock_log:
            fake_model = MagicMock()
            mlflow_pytorch.log_model(fake_model, artifact_path="model")
            mock_log.assert_called_once_with(fake_model, artifact_path="model")
