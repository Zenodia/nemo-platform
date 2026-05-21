# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
# property and proprietary rights in and to this material, related
# documentation and any modifications thereto. Any use, reproduction,
# disclosure or distribution of this material and related documentation
# without an express license agreement from NVIDIA CORPORATION or
# its affiliates is strictly prohibited.

"""Unit tests for job-waiting utilities.

Tests the refactored wait_for_platform_job() which delegates to
poll_until_terminal() so that image-pull time (pending status) is not
counted against the main job-execution timeout.
"""

from unittest.mock import MagicMock, patch

import pytest
from nmp.testing.e2e.jobs import TERMINAL_STATUSES, wait_for_platform_job

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_sdk(*statuses: str) -> MagicMock:
    """Return an SDK mock whose retrieve() cycles through *statuses* on each call."""
    sdk = MagicMock()
    jobs = []
    for s in statuses:
        j = MagicMock()
        j.status = s
        jobs.append(j)
    sdk.jobs.retrieve.side_effect = jobs
    sdk.jobs.get_status.return_value = MagicMock(model_dump=MagicMock(return_value={}))
    return sdk


# ---------------------------------------------------------------------------
# Basic terminal-status behaviour
# ---------------------------------------------------------------------------


class TestWaitForPlatformJobTerminalStatus:
    """Tests that wait_for_platform_job returns on terminal statuses."""

    def test_returns_immediately_on_completed(self):
        """Returns as soon as job is 'completed'."""
        sdk = _make_sdk("completed")
        job = wait_for_platform_job(sdk, "my-job", "ws", timeout=5.0)
        assert job.status == "completed"

    def test_returns_immediately_on_error(self):
        """Returns (without raising) when job is 'error'."""
        sdk = _make_sdk("error")
        job = wait_for_platform_job(sdk, "my-job", "ws", timeout=5.0)
        assert job.status == "error"

    def test_returns_immediately_on_cancelled(self):
        """Returns when job is 'cancelled'."""
        sdk = _make_sdk("cancelled")
        job = wait_for_platform_job(sdk, "my-job", "ws", timeout=5.0)
        assert job.status == "cancelled"

    def test_returns_job_object(self):
        """Returns the actual job object from sdk.jobs.retrieve (not a copy)."""
        sdk = MagicMock()
        expected_job = MagicMock()
        expected_job.status = "completed"
        sdk.jobs.retrieve.return_value = expected_job
        sdk.jobs.get_status.return_value = MagicMock(model_dump=MagicMock(return_value={}))
        job = wait_for_platform_job(sdk, "my-job", "ws", timeout=5.0)
        assert job is expected_job


# ---------------------------------------------------------------------------
# status_to_check behaviour
# ---------------------------------------------------------------------------


class TestWaitForPlatformJobStatusToCheck:
    """Tests that status_to_check stops the loop at a non-terminal status."""

    def test_stops_on_status_to_check(self):
        """Returns when the job reaches status_to_check before terminal."""
        sdk = _make_sdk("created", "pending", "active")
        job = wait_for_platform_job(sdk, "my-job", "ws", timeout=5.0, status_to_check="active")
        assert job.status == "active"

    def test_also_stops_on_terminal_when_status_to_check_set(self):
        """If job reaches a terminal status before status_to_check, still returns."""
        sdk = _make_sdk("created", "error")
        job = wait_for_platform_job(sdk, "my-job", "ws", timeout=5.0, status_to_check="active")
        assert job.status == "error"

    def test_terminal_set_includes_status_to_check(self):
        """poll_until_terminal is called with status_to_check merged into terminal set."""
        sdk = _make_sdk("paused")
        with patch("nmp.testing.e2e.jobs.poll_until_terminal") as mock_poll:
            # Simulate poll_until_terminal calling get_status once
            def fake_poll(get_status, label, terminal, timeout, image_pull_timeout, poll_interval):
                get_status()

            mock_poll.side_effect = fake_poll
            wait_for_platform_job(sdk, "my-job", "ws", status_to_check="paused")

        _, kwargs = mock_poll.call_args
        terminal_used = mock_poll.call_args[1]["terminal"] if mock_poll.call_args[1] else mock_poll.call_args[0][2]
        assert "paused" in terminal_used
        for ts in TERMINAL_STATUSES:
            assert ts in terminal_used


# ---------------------------------------------------------------------------
# image_pull_timeout behaviour
# ---------------------------------------------------------------------------


class TestWaitForPlatformJobImagePullTimeout:
    """Tests that pending time is handled by poll_until_terminal's image_pull_timeout."""

    def test_pending_status_does_not_consume_main_timeout(self):
        """A job stuck in pending does not exhaust the execution timeout."""
        # pending -> completed: pending time should NOT count against timeout=5.0
        sdk = _make_sdk("pending", "completed")
        job = wait_for_platform_job(sdk, "my-job", "ws", timeout=5.0, image_pull_timeout=60.0)
        assert job.status == "completed"

    def test_image_pull_timeout_parameter_passed_to_poll_until_terminal(self):
        """image_pull_timeout is forwarded to poll_until_terminal."""
        sdk = _make_sdk("completed")
        with patch("nmp.testing.e2e.jobs.poll_until_terminal") as mock_poll:

            def fake_poll(get_status, label, terminal, timeout, image_pull_timeout, poll_interval):
                get_status()

            mock_poll.side_effect = fake_poll
            wait_for_platform_job(sdk, "my-job", "ws", timeout=30.0, image_pull_timeout=999.0)

        args = mock_poll.call_args
        # image_pull_timeout may be positional or keyword
        if args[1]:
            assert args[1]["image_pull_timeout"] == 999.0
        else:
            assert args[0][4] == 999.0

    def test_default_image_pull_timeout_is_600(self):
        """Default image_pull_timeout is 600 seconds."""
        sdk = _make_sdk("completed")
        with patch("nmp.testing.e2e.jobs.poll_until_terminal") as mock_poll:

            def fake_poll(get_status, label, terminal, timeout, image_pull_timeout, poll_interval):
                get_status()

            mock_poll.side_effect = fake_poll
            wait_for_platform_job(sdk, "my-job", "ws")

        args = mock_poll.call_args
        if args[1]:
            assert args[1]["image_pull_timeout"] == 600.0
        else:
            assert args[0][4] == 600.0


# ---------------------------------------------------------------------------
# Timeout error enrichment
# ---------------------------------------------------------------------------


class TestWaitForPlatformJobTimeoutError:
    """Tests that TimeoutError from poll_until_terminal is enriched with context."""

    def test_raises_timeout_error_when_poll_times_out(self):
        """TimeoutError propagates when poll_until_terminal raises it."""
        sdk = _make_sdk("created")
        with patch("nmp.testing.e2e.jobs.poll_until_terminal") as mock_poll:
            mock_poll.side_effect = TimeoutError("'my-job' timed out after 5.0s. Status: created")
            with pytest.raises(TimeoutError):
                wait_for_platform_job(sdk, "my-job", "ws", timeout=5.0)

    def test_timeout_error_includes_status_history(self):
        """TimeoutError message includes the accumulated status history."""
        sdk = _make_sdk("created", "pending")

        def fake_poll(get_status, label, terminal, timeout, image_pull_timeout, poll_interval):
            # Call get_status twice to populate history, then timeout
            get_status()
            get_status()
            raise TimeoutError(f"'{label}' timed out after {timeout}s. Status: pending")

        with patch("nmp.testing.e2e.jobs.poll_until_terminal", side_effect=fake_poll):
            with pytest.raises(TimeoutError) as exc_info:
                wait_for_platform_job(sdk, "my-job", "ws", timeout=5.0)

        assert "Status history:" in str(exc_info.value)
        assert "created" in str(exc_info.value)
        assert "pending" in str(exc_info.value)

    def test_timeout_error_includes_job_status_details(self):
        """TimeoutError message includes detailed job status from get_status API."""
        sdk = _make_sdk("pending")
        sdk.jobs.get_status.return_value = MagicMock(
            model_dump=MagicMock(return_value={"status": "pending", "message": "pulling image"})
        )

        def fake_poll(get_status, label, terminal, timeout, image_pull_timeout, poll_interval):
            get_status()
            raise TimeoutError(f"'{label}' timed out")

        with patch("nmp.testing.e2e.jobs.poll_until_terminal", side_effect=fake_poll):
            with pytest.raises(TimeoutError) as exc_info:
                wait_for_platform_job(sdk, "my-job", "ws", timeout=5.0)

        assert "Job status details:" in str(exc_info.value)
