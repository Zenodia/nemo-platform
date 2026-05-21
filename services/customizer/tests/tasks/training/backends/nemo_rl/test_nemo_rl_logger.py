# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Unit tests for the NemoRLLogger migration.

Tests verify that NemoRLLogger correctly delegates to TrainingProgressCallback
for progress reporting via the NeMo Platform SDK.
"""

import math

import pytest

# Skip entire module if nemo_rl dependencies are not available
pytest.importorskip("nemo_rl")

from nmp.customizer.app.jobs.context import NMPJobContext
from nmp.customizer.tasks.training.backends.nemo_rl.nemo_rl_logger import (
    NemoRLLogger,
    has_metric_value,
)
from pytest_mock import MockerFixture

pytestmark = pytest.mark.nemo_rl

# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def mock_job_ctx(mocker: MockerFixture) -> NMPJobContext:
    """Create a mock NMPJobContext with jobs_url configured."""
    return NMPJobContext(
        workspace="test-workspace",
        job_id="job-123",
        attempt_id="attempt-1",
        step="training",
        task="dpo",
        jobs_url="http://jobs-service:8080",
        files_url="http://files-service:8080",
        storage_path=mocker.MagicMock(),
        config_path=mocker.MagicMock(),
    )


@pytest.fixture
def mock_job_ctx_disabled(mocker: MockerFixture) -> NMPJobContext:
    """Create a mock NMPJobContext without jobs_url (disabled)."""
    return NMPJobContext(
        workspace="test-workspace",
        job_id="job-123",
        attempt_id="attempt-1",
        step="training",
        task="dpo",
        jobs_url=None,
        files_url=None,
        storage_path=mocker.MagicMock(),
        config_path=mocker.MagicMock(),
    )


@pytest.fixture
def mock_callback(mocker: MockerFixture):
    """Create a mock TrainingProgressCallback."""
    return mocker.MagicMock()


@pytest.fixture
def mock_reporter(mocker: MockerFixture):
    """Create a mock JobsServiceProgressReporter."""
    return mocker.MagicMock()


# ============================================================================
# TestHasMetricValue
# ============================================================================


class TestHasMetricValue:
    """Tests for has_metric_value helper function."""

    @pytest.mark.parametrize(
        ("value", "expected"),
        [
            (0.0, True),
            (1.0, True),
            (-1.0, True),
            (0.5, True),
            (100, True),
            (None, False),
            (float("nan"), False),
            (math.nan, False),
        ],
        ids=[
            "zero",
            "positive",
            "negative",
            "fraction",
            "integer",
            "none",
            "float_nan",
            "math_nan",
        ],
    )
    def test_has_metric_value(self, value, expected):
        """Should correctly identify valid metric values."""
        assert has_metric_value(value) == expected


# ============================================================================
# TestNemoRLLoggerInit
# ============================================================================


class TestNemoRLLoggerInit:
    """Tests for NemoRLLogger initialization."""

    def test_init_creates_callback_with_reporter(self, mock_job_ctx: NMPJobContext, mocker: MockerFixture):
        """Should create TrainingProgressCallback with JobsServiceProgressReporter."""
        mock_reporter_class = mocker.patch(
            "nmp.customizer.tasks.training.backends.nemo_rl.nemo_rl_logger.JobsServiceProgressReporter"
        )
        mock_callback_class = mocker.patch(
            "nmp.customizer.tasks.training.backends.nemo_rl.nemo_rl_logger.TrainingProgressCallback"
        )

        logger = NemoRLLogger(job_ctx=mock_job_ctx, steps_per_epoch=10)

        mock_reporter_class.assert_called_once_with(mock_job_ctx)
        mock_callback_class.assert_called_once_with(mock_reporter_class.return_value)
        assert logger._callback is mock_callback_class.return_value

    def test_init_stores_parameters(self, mock_job_ctx: NMPJobContext, mocker: MockerFixture):
        """Should store all initialization parameters."""
        mocker.patch("nmp.customizer.tasks.training.backends.nemo_rl.nemo_rl_logger.JobsServiceProgressReporter")
        mocker.patch("nmp.customizer.tasks.training.backends.nemo_rl.nemo_rl_logger.TrainingProgressCallback")

        logger = NemoRLLogger(
            job_ctx=mock_job_ctx,
            log_interval=20,
            max_steps=1000,
            num_epochs=5,
            steps_per_epoch=10,
        )

        assert logger._job_ctx is mock_job_ctx
        assert logger._log_interval == 20
        assert logger._max_steps == 1000
        assert logger._num_epochs == 5

    def test_init_defaults_to_from_env(self, mocker: MockerFixture):
        """Should use NMPJobContext.from_env() when no job_ctx provided."""
        mock_from_env = mocker.patch.object(NMPJobContext, "from_env")
        mocker.patch("nmp.customizer.tasks.training.backends.nemo_rl.nemo_rl_logger.JobsServiceProgressReporter")
        mocker.patch("nmp.customizer.tasks.training.backends.nemo_rl.nemo_rl_logger.TrainingProgressCallback")

        logger = NemoRLLogger(steps_per_epoch=10)

        mock_from_env.assert_called_once()
        assert logger._job_ctx is mock_from_env.return_value


# ============================================================================
# TestNemoRLLoggerLogMetrics
# ============================================================================


class TestNemoRLLoggerLogMetrics:
    """Tests for NemoRLLogger.log_metrics method."""

    def test_log_metrics_training_loss_calls_report_train_step(
        self, mock_job_ctx: NMPJobContext, mocker: MockerFixture
    ):
        """Should call report_train_step for training metrics at log interval."""
        mocker.patch("nmp.customizer.tasks.training.backends.nemo_rl.nemo_rl_logger.JobsServiceProgressReporter")
        mock_callback = mocker.MagicMock()
        mocker.patch(
            "nmp.customizer.tasks.training.backends.nemo_rl.nemo_rl_logger.TrainingProgressCallback",
            return_value=mock_callback,
        )

        logger = NemoRLLogger(job_ctx=mock_job_ctx, log_interval=10, steps_per_epoch=100)
        # Step 9 (0-indexed) becomes step 10 (1-indexed), which is divisible by log_interval=10
        logger.log_metrics(metrics={"loss": 0.5, "lr": 1e-4}, step=9, prefix="train")

        mock_callback.report_train_step.assert_called_once_with(step=10, epoch=1, loss=0.5, lr=1e-4, grad_norm=None)

    def test_log_metrics_training_loss_skips_non_interval_steps(
        self, mock_job_ctx: NMPJobContext, mocker: MockerFixture
    ):
        """Should not call report_train_step for steps not at log interval."""
        mocker.patch("nmp.customizer.tasks.training.backends.nemo_rl.nemo_rl_logger.JobsServiceProgressReporter")
        mock_callback = mocker.MagicMock()
        mocker.patch(
            "nmp.customizer.tasks.training.backends.nemo_rl.nemo_rl_logger.TrainingProgressCallback",
            return_value=mock_callback,
        )

        logger = NemoRLLogger(job_ctx=mock_job_ctx, log_interval=10, steps_per_epoch=100)
        # Step 4 (0-indexed) becomes step 5 (1-indexed), which is NOT divisible by 10
        logger.log_metrics(metrics={"loss": 0.5}, step=4, prefix="train")

        mock_callback.report_train_step.assert_not_called()

    def test_log_metrics_validation_loss_calls_report_validation(
        self, mock_job_ctx: NMPJobContext, mocker: MockerFixture
    ):
        """Should call report_validation for validation metrics."""
        mocker.patch("nmp.customizer.tasks.training.backends.nemo_rl.nemo_rl_logger.JobsServiceProgressReporter")
        mock_callback = mocker.MagicMock()
        mocker.patch(
            "nmp.customizer.tasks.training.backends.nemo_rl.nemo_rl_logger.TrainingProgressCallback",
            return_value=mock_callback,
        )

        logger = NemoRLLogger(job_ctx=mock_job_ctx, steps_per_epoch=100)
        logger.log_metrics(metrics={"loss": 0.3}, step=99, prefix="validation")

        mock_callback.report_validation.assert_called_once_with(step=100, epoch=1, val_loss=0.3)

    def test_log_metrics_validation_prefix_variants(self, mock_job_ctx: NMPJobContext, mocker: MockerFixture):
        """Should handle various validation prefix formats."""
        mocker.patch("nmp.customizer.tasks.training.backends.nemo_rl.nemo_rl_logger.JobsServiceProgressReporter")
        mock_callback = mocker.MagicMock()
        mocker.patch(
            "nmp.customizer.tasks.training.backends.nemo_rl.nemo_rl_logger.TrainingProgressCallback",
            return_value=mock_callback,
        )

        logger = NemoRLLogger(job_ctx=mock_job_ctx, steps_per_epoch=100)

        # Test various validation prefix formats
        logger.log_metrics(metrics={"loss": 0.1}, step=0, prefix="validation")
        logger.log_metrics(metrics={"loss": 0.2}, step=1, prefix="validation_default")
        logger.log_metrics(metrics={"loss": 0.3}, step=2, prefix="validation/subset")

        assert mock_callback.report_validation.call_count == 3

    def test_log_metrics_ignores_invalid_metrics(self, mock_job_ctx: NMPJobContext, mocker: MockerFixture):
        """Should ignore metrics with None or NaN values."""
        mocker.patch("nmp.customizer.tasks.training.backends.nemo_rl.nemo_rl_logger.JobsServiceProgressReporter")
        mock_callback = mocker.MagicMock()
        mocker.patch(
            "nmp.customizer.tasks.training.backends.nemo_rl.nemo_rl_logger.TrainingProgressCallback",
            return_value=mock_callback,
        )

        logger = NemoRLLogger(job_ctx=mock_job_ctx, log_interval=1, steps_per_epoch=100)
        logger.log_metrics(metrics={"loss": None}, step=0, prefix="train")
        logger.log_metrics(metrics={"loss": float("nan")}, step=1, prefix="train")

        mock_callback.report_train_step.assert_not_called()

    def test_log_metrics_computes_epoch_from_steps(self, mock_job_ctx: NMPJobContext, mocker: MockerFixture):
        """Should compute epoch from step using steps_per_epoch."""
        mocker.patch("nmp.customizer.tasks.training.backends.nemo_rl.nemo_rl_logger.JobsServiceProgressReporter")
        mock_callback = mocker.MagicMock()
        mocker.patch(
            "nmp.customizer.tasks.training.backends.nemo_rl.nemo_rl_logger.TrainingProgressCallback",
            return_value=mock_callback,
        )

        # 50 steps per epoch
        logger = NemoRLLogger(job_ctx=mock_job_ctx, log_interval=10, max_steps=100, num_epochs=2, steps_per_epoch=50)
        # Step 59 (0-indexed) becomes 60 (1-indexed), epoch = ((60 - 1) // 50) + 1 = (59 // 50) + 1 = 1 + 1 = 2
        logger.log_metrics(metrics={"loss": 0.5}, step=59, prefix="train")

        mock_callback.report_train_step.assert_called_once()
        call_kwargs = mock_callback.report_train_step.call_args.kwargs
        assert call_kwargs["epoch"] == 2

    def test_log_metrics_tracks_best_validation_loss(self, mock_job_ctx: NMPJobContext, mocker: MockerFixture):
        """Should track best validation loss."""
        mocker.patch("nmp.customizer.tasks.training.backends.nemo_rl.nemo_rl_logger.JobsServiceProgressReporter")
        mock_callback = mocker.MagicMock()
        mocker.patch(
            "nmp.customizer.tasks.training.backends.nemo_rl.nemo_rl_logger.TrainingProgressCallback",
            return_value=mock_callback,
        )

        logger = NemoRLLogger(job_ctx=mock_job_ctx, steps_per_epoch=100)
        assert logger._best_metric_value == float("inf")

        logger.log_metrics(metrics={"loss": 0.5}, step=0, prefix="validation")
        assert logger._best_metric_value == 0.5
        assert logger._best_epoch == 1

        logger.log_metrics(metrics={"loss": 0.3}, step=1, prefix="validation")
        assert logger._best_metric_value == 0.3

        # Worse loss should not update best
        logger.log_metrics(metrics={"loss": 0.8}, step=2, prefix="validation")
        assert logger._best_metric_value == 0.3


# ============================================================================
# TestNemoRLLoggerLogHyperparams
# ============================================================================


class TestNemoRLLoggerLogHyperparams:
    """Tests for NemoRLLogger.log_hyperparams method."""

    def test_log_hyperparams_calls_report_training_start(self, mock_job_ctx: NMPJobContext, mocker: MockerFixture):
        """Should call report_training_start with max_steps and num_epochs."""
        mocker.patch("nmp.customizer.tasks.training.backends.nemo_rl.nemo_rl_logger.JobsServiceProgressReporter")
        mock_callback = mocker.MagicMock()
        mocker.patch(
            "nmp.customizer.tasks.training.backends.nemo_rl.nemo_rl_logger.TrainingProgressCallback",
            return_value=mock_callback,
        )

        logger = NemoRLLogger(job_ctx=mock_job_ctx, max_steps=500, num_epochs=3, steps_per_epoch=10)
        logger.log_hyperparams({"learning_rate": 1e-4})

        mock_callback.report_training_start.assert_called_once_with(max_steps=500, num_epochs=3)

    def test_log_hyperparams_extracts_from_params(self, mock_job_ctx: NMPJobContext, mocker: MockerFixture):
        """Should extract max_steps and num_epochs from params if not set."""
        mocker.patch("nmp.customizer.tasks.training.backends.nemo_rl.nemo_rl_logger.JobsServiceProgressReporter")
        mock_callback = mocker.MagicMock()
        mocker.patch(
            "nmp.customizer.tasks.training.backends.nemo_rl.nemo_rl_logger.TrainingProgressCallback",
            return_value=mock_callback,
        )

        logger = NemoRLLogger(job_ctx=mock_job_ctx, steps_per_epoch=10)
        logger.log_hyperparams({"max_steps": 200, "num_epochs": 4})

        mock_callback.report_training_start.assert_called_once_with(max_steps=200, num_epochs=4)
        # Should also update internal tracking
        assert logger._max_steps == 200
        assert logger._num_epochs == 4


# ============================================================================
# TestNemoRLLoggerClose
# ============================================================================


class TestNemoRLLoggerClose:
    """Tests for NemoRLLogger.close method."""

    def test_close_calls_callback_close(self, mock_job_ctx: NMPJobContext, mocker: MockerFixture):
        """Should call close on the callback."""
        mocker.patch("nmp.customizer.tasks.training.backends.nemo_rl.nemo_rl_logger.JobsServiceProgressReporter")
        mock_callback = mocker.MagicMock()
        mocker.patch(
            "nmp.customizer.tasks.training.backends.nemo_rl.nemo_rl_logger.TrainingProgressCallback",
            return_value=mock_callback,
        )

        logger = NemoRLLogger(job_ctx=mock_job_ctx, steps_per_epoch=10)
        logger.close()

        mock_callback.close.assert_called_once()


# ============================================================================
# TestNemoRLLoggerAdditionalMetrics
# ============================================================================


class TestNemoRLLoggerAdditionalMetrics:
    """Tests for additional metrics forwarding."""

    def test_log_metrics_training_with_additional_metrics(self, mock_job_ctx: NMPJobContext, mocker: MockerFixture):
        """Should forward additional training metrics to callback."""
        mocker.patch("nmp.customizer.tasks.training.backends.nemo_rl.nemo_rl_logger.JobsServiceProgressReporter")
        mock_callback = mocker.MagicMock()
        mocker.patch(
            "nmp.customizer.tasks.training.backends.nemo_rl.nemo_rl_logger.TrainingProgressCallback",
            return_value=mock_callback,
        )

        logger = NemoRLLogger(job_ctx=mock_job_ctx, log_interval=10, steps_per_epoch=10)
        logger.log_metrics(
            metrics={
                "loss": 0.5,
                "lr": 1e-4,
                "grad_norm": 0.1,
                "num_valid_samples": 100.0,
                "preference_loss": 0.3,
                "rewards_rejected_mean": -1.5,
                "global_valid_seqs": 200.0,
                "global_valid_toks": 5000.0,
            },
            step=9,
            prefix="train",
        )

        mock_callback.report_train_step.assert_called_once()
        call_kwargs = mock_callback.report_train_step.call_args.kwargs
        assert call_kwargs["step"] == 10
        assert call_kwargs["epoch"] == 1
        assert call_kwargs["loss"] == 0.5
        assert call_kwargs["lr"] == 1e-4
        assert call_kwargs["grad_norm"] == 0.1
        assert call_kwargs["num_valid_samples"] == 100.0
        assert call_kwargs["preference_loss"] == 0.3
        assert call_kwargs["rewards_rejected_mean"] == -1.5
        assert call_kwargs["global_valid_seqs"] == 200.0
        assert call_kwargs["global_valid_toks"] == 5000.0

    def test_log_metrics_validation_with_additional_metrics(self, mock_job_ctx: NMPJobContext, mocker: MockerFixture):
        """Should forward additional validation metrics to callback."""
        mocker.patch("nmp.customizer.tasks.training.backends.nemo_rl.nemo_rl_logger.JobsServiceProgressReporter")
        mock_callback = mocker.MagicMock()
        mocker.patch(
            "nmp.customizer.tasks.training.backends.nemo_rl.nemo_rl_logger.TrainingProgressCallback",
            return_value=mock_callback,
        )

        logger = NemoRLLogger(job_ctx=mock_job_ctx, steps_per_epoch=10)
        logger.log_metrics(
            metrics={
                "loss": 0.3,
                "preference_loss": 0.25,
                "num_valid_samples": 50.0,
            },
            step=9,
            prefix="validation",
        )

        mock_callback.report_validation.assert_called_once()
        call_kwargs = mock_callback.report_validation.call_args.kwargs
        assert call_kwargs["step"] == 10
        assert call_kwargs["epoch"] == 1
        assert call_kwargs["val_loss"] == 0.3
        assert call_kwargs["preference_loss"] == 0.25
        assert call_kwargs["num_valid_samples"] == 50.0

    def test_log_metrics_filters_invalid_additional_metrics(self, mock_job_ctx: NMPJobContext, mocker: MockerFixture):
        """Should filter out None, NaN values, and non-whitelisted metrics from additional metrics."""
        mocker.patch("nmp.customizer.tasks.training.backends.nemo_rl.nemo_rl_logger.JobsServiceProgressReporter")
        mock_callback = mocker.MagicMock()
        mocker.patch(
            "nmp.customizer.tasks.training.backends.nemo_rl.nemo_rl_logger.TrainingProgressCallback",
            return_value=mock_callback,
        )

        logger = NemoRLLogger(job_ctx=mock_job_ctx, log_interval=10, steps_per_epoch=10)
        logger.log_metrics(
            metrics={
                "loss": 0.5,
                "num_valid_samples": 100.0,  # Whitelisted - should be included
                "preference_loss": None,  # Whitelisted but None - should be filtered
                "rewards_rejected_mean": float("nan"),  # Whitelisted but NaN - should be filtered
                "non_whitelisted_metric": 1.0,  # Not whitelisted - should be filtered
            },
            step=9,
            prefix="train",
        )

        call_kwargs = mock_callback.report_train_step.call_args.kwargs
        assert "num_valid_samples" in call_kwargs
        assert call_kwargs["num_valid_samples"] == 100.0
        assert "preference_loss" not in call_kwargs
        assert "rewards_rejected_mean" not in call_kwargs
        assert "non_whitelisted_metric" not in call_kwargs

    def test_log_metrics_timing_reports_to_jobs_service(self, mock_job_ctx: NMPJobContext, mocker: MockerFixture):
        """Should report timing metrics to jobs service."""
        mock_reporter = mocker.MagicMock()
        mocker.patch(
            "nmp.customizer.tasks.training.backends.nemo_rl.nemo_rl_logger.JobsServiceProgressReporter",
            return_value=mock_reporter,
        )
        mock_callback = mocker.MagicMock()
        mock_callback._reporter = mock_reporter
        mocker.patch(
            "nmp.customizer.tasks.training.backends.nemo_rl.nemo_rl_logger.TrainingProgressCallback",
            return_value=mock_callback,
        )

        logger = NemoRLLogger(job_ctx=mock_job_ctx, steps_per_epoch=10)
        logger.log_metrics(
            metrics={
                "policy_training": 4.0,
                "total_step_time": 4.5,
                "valid_tokens_per_sec_per_gpu": 2400.0,
            },
            step=9,
            prefix="timing/train",
        )

        mock_reporter.report_running.assert_called_once()
        call_kwargs = mock_reporter.report_running.call_args.kwargs
        assert call_kwargs["phase"] == "timing"
        assert call_kwargs["step"] == 10
        assert call_kwargs["epoch"] == 1
        assert call_kwargs["policy_training"] == 4.0
        assert call_kwargs["total_step_time"] == 4.5
        assert call_kwargs["valid_tokens_per_sec_per_gpu"] == 2400.0
