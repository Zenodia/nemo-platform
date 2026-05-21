# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
# property and proprietary rights in and to this material, related
# documentation and any modifications thereto. Any use, reproduction,
# disclosure or distribution of this material and related documentation
# without an express license agreement from NVIDIA CORPORATION or
# its affiliates is strictly prohibited.

"""Unit tests for evaluator E2E test helpers.

Tests the raise-on-error behaviour of wait_for_evaluation_job() and the
non-completed-job guard in get_job_outputs().
"""

from unittest.mock import MagicMock

import pytest
from nmp.testing.e2e.evaluator import get_job_outputs, wait_for_evaluation_job


def _make_sdk(job_status: str) -> MagicMock:
    """Return a minimal SDK mock whose metric job has *job_status*."""
    sdk = MagicMock()
    job = MagicMock()
    job.status = job_status
    sdk.evaluation.metric_jobs.retrieve.return_value = job
    sdk.evaluation.metric_jobs.get_status.return_value = MagicMock()
    return sdk


# ---------------------------------------------------------------------------
# wait_for_evaluation_job() — raise_on_error behaviour
# ---------------------------------------------------------------------------


class TestWaitForEvaluationJob:
    """Tests for the raise_on_error parameter added to wait_for_evaluation_job()."""

    # poll_until_terminal exits immediately when get_status() returns a terminal
    # value, so no real sleeping occurs in these tests.

    def test_raises_assertion_error_on_error_status_by_default(self):
        """Default raise_on_error=True raises AssertionError when job ends in 'error'."""
        sdk = _make_sdk("error")
        with pytest.raises(AssertionError, match="ended with status 'error'"):
            wait_for_evaluation_job(sdk, "test-job", "ws", timeout=5.0)

    def test_raises_assertion_error_on_failed_status_by_default(self):
        """Default raise_on_error=True raises AssertionError when job ends in 'failed'."""
        sdk = _make_sdk("failed")
        with pytest.raises(AssertionError, match="ended with status 'failed'"):
            wait_for_evaluation_job(sdk, "test-job", "ws", timeout=5.0)

    def test_assertion_error_includes_job_name(self):
        """AssertionError message contains the job name for easy identification."""
        sdk = _make_sdk("error")
        with pytest.raises(AssertionError, match="my-failing-job"):
            wait_for_evaluation_job(sdk, "my-failing-job", "ws", timeout=5.0)

    def test_no_raise_when_raise_on_error_false(self):
        """raise_on_error=False returns the job object without raising on error status."""
        sdk = _make_sdk("error")
        result = wait_for_evaluation_job(sdk, "test-job", "ws", timeout=5.0, raise_on_error=False)
        assert result.status == "error"

    def test_no_raise_when_raise_on_error_false_failed(self):
        """raise_on_error=False returns the job object without raising on failed status."""
        sdk = _make_sdk("failed")
        result = wait_for_evaluation_job(sdk, "test-job", "ws", timeout=5.0, raise_on_error=False)
        assert result.status == "failed"

    def test_no_raise_on_completed_status(self):
        """No exception is raised when the job completes successfully."""
        sdk = _make_sdk("completed")
        result = wait_for_evaluation_job(sdk, "test-job", "ws", timeout=5.0)
        assert result.status == "completed"

    def test_no_raise_when_expected_status_matches_error(self):
        """When expected_status is set, raise_on_error is bypassed (caller controls the check)."""
        sdk = _make_sdk("error")
        # Passing expected_status="error" tells poll_until_terminal to treat "error" as
        # the desired terminal state, so the raise_on_error guard must not fire.
        result = wait_for_evaluation_job(sdk, "test-job", "ws", timeout=5.0, expected_status="error")
        assert result.status == "error"

    def test_returns_job_object_on_success(self):
        """wait_for_evaluation_job returns the final job object on success."""
        sdk = _make_sdk("completed")
        job = wait_for_evaluation_job(sdk, "test-job", "ws", timeout=5.0)
        assert job is sdk.evaluation.metric_jobs.retrieve.return_value


# ---------------------------------------------------------------------------
# get_job_outputs() — guard against non-completed jobs
# ---------------------------------------------------------------------------


class TestGetJobOutputs:
    """Tests for the status guard added at the top of get_job_outputs()."""

    def test_raises_assertion_error_on_error_status(self):
        """get_job_outputs raises AssertionError (not a 404) when job status is 'error'."""
        sdk = _make_sdk("error")
        with pytest.raises(AssertionError, match="job status is 'error'"):
            get_job_outputs(sdk, "test-job", "ws")

    def test_raises_assertion_error_on_failed_status(self):
        """get_job_outputs raises AssertionError when job status is 'failed'."""
        sdk = _make_sdk("failed")
        with pytest.raises(AssertionError, match="job status is 'failed'"):
            get_job_outputs(sdk, "test-job", "ws")

    def test_raises_assertion_error_on_cancelled_status(self):
        """get_job_outputs raises AssertionError when job status is 'cancelled'."""
        sdk = _make_sdk("cancelled")
        with pytest.raises(AssertionError, match="job status is 'cancelled'"):
            get_job_outputs(sdk, "test-job", "ws")

    def test_error_message_includes_job_name(self):
        """AssertionError message includes the job name."""
        sdk = _make_sdk("error")
        with pytest.raises(AssertionError, match="special-job"):
            get_job_outputs(sdk, "special-job", "ws")

    def test_error_message_indicates_expected_completed(self):
        """AssertionError message communicates that 'completed' was expected."""
        sdk = _make_sdk("error")
        with pytest.raises(AssertionError, match="expected 'completed'"):
            get_job_outputs(sdk, "test-job", "ws")

    def test_metric_job_results_not_called_on_non_completed_job(self):
        """The guard prevents the 404-causing metric_job_results.retrieve call."""
        sdk = _make_sdk("error")
        with pytest.raises(AssertionError):
            get_job_outputs(sdk, "test-job", "ws")
        sdk.evaluation.metric_job_results.retrieve.assert_not_called()
