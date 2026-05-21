# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import asyncio
import logging
import os
from http.client import HTTPMessage
from unittest import mock
from unittest.mock import patch

import pytest
from nmp.common.jobs.constants import NEMO_JOB_ID_ENVVAR, NEMO_JOB_WORKSPACE_ENVVAR
from nmp.evaluator.app.jobs.progress_tracking import ProgressTracking, get_progress_tracking_url
from nmp.evaluator.app.values import EvaluationStatusDetails
from nmp.testing.pytest_outcomes import pytest_skip


@mock.patch.dict(
    os.environ,
    {
        "NMP_JOBS_URL": "http://localhost:8000",
        NEMO_JOB_ID_ENVVAR: "test-job-id",
        NEMO_JOB_WORKSPACE_ENVVAR: "default",
    },
)
def test_url_env():
    # Test URL with env var is resolved
    url = get_progress_tracking_url()
    assert url == "${NMP_JOBS_URL}/apis/jobs/v2/workspaces/${NEMO_JOB_WORKSPACE}/jobs/${NEMO_JOB_ID}/status-details"
    progress_tracking = ProgressTracking(progress_tracking_url=url)
    assert (
        progress_tracking._progress_tracking_url
        == "http://localhost:8000/apis/jobs/v2/workspaces/default/jobs/test-job-id/status-details"
    )


@pytest.mark.parametrize(
    "interval,total_samples,expected_interval,desc",
    [
        (None, None, 50, "default"),
        (20, None, 20, "set interval"),
        (200, None, 200, "set large interval"),
        (20, 100, 20, "set interval with total samples"),
        (None, 30, 7, "default to total samples // 4"),
        (100, 60, 15, "interval defaults to lower total samples // 4"),
    ],
)
def test_interval(subtests, interval: int, total_samples: int, expected_interval: int, desc: str):
    url = get_progress_tracking_url()

    with subtests.test(msg="init"):
        progress_tracking = ProgressTracking(url, progress_tracking_interval=interval, total_samples=total_samples)
        assert progress_tracking.interval == expected_interval, desc

    with subtests.test(msg="total_samples setter"):
        if total_samples is None:
            pytest_skip()
        progress_tracking = ProgressTracking(url, progress_tracking_interval=interval)
        assert progress_tracking.interval == interval or 50
        progress_tracking.total_samples = total_samples
        assert progress_tracking.interval == expected_interval, desc


@patch("requests.Session")
@mock.patch.dict(
    os.environ,
    {
        "NMP_JOBS_URL": "http://localhost:8000",
        NEMO_JOB_ID_ENVVAR: "test-job-id",
        NEMO_JOB_WORKSPACE_ENVVAR: "default",
    },
)
def test_increment(mock_session):
    mock_session_request = mock.MagicMock(return_value=mock.MagicMock(status_code=200))
    mock_session.return_value.__enter__.return_value.request = mock_session_request

    url = get_progress_tracking_url()
    rendered_url = "http://localhost:8000/apis/jobs/v2/workspaces/default/jobs/test-job-id/status-details"
    progress_tracking = ProgressTracking(url, progress_tracking_interval=2)

    assert progress_tracking._status_details.samples_processed == 0
    progress_tracking.increment_samples_processed()
    assert progress_tracking._status_details.samples_processed == 1
    progress_tracking.increment_samples_processed()
    assert progress_tracking._status_details.samples_processed == 2
    mock_session_request.assert_called_once_with("PATCH", rendered_url, json={"samples_processed": 2})

    progress_tracking.update_progress(100)
    assert progress_tracking._status_details.samples_processed == 2, "post_eval_hook does not increment"
    mock_session_request.assert_called_with("PATCH", rendered_url, json={"samples_processed": 2, "progress": 100.0})


@patch("requests.Session")
@mock.patch.dict(
    os.environ,
    {
        "NMP_JOBS_URL": "http://localhost:8000",
        NEMO_JOB_ID_ENVVAR: "test-job-id",
        NEMO_JOB_WORKSPACE_ENVVAR: "default",
    },
)
def test_update_progress_exclude_unset(mock_session):
    mock_session_request = mock.MagicMock(return_value=mock.MagicMock(status_code=200))
    mock_session.return_value.__enter__.return_value.request = mock_session_request

    url = get_progress_tracking_url()
    rendered_url = "http://localhost:8000/apis/jobs/v2/workspaces/default/jobs/test-job-id/status-details"
    progress_tracking = ProgressTracking(url, progress_tracking_interval=2)

    # Verify "samples_processed": None is not serialized with exclude_unset=True
    progress_tracking.update_progress(0)
    mock_session_request.assert_called_once_with("PATCH", rendered_url, json={"progress": 0.0})


@patch("requests.Session")
@pytest.mark.asyncio
async def test_timer(mock_session):
    mock_session_request = mock.MagicMock(return_value=mock.MagicMock(status_code=200))
    mock_session.return_value.__enter__.return_value.request = mock_session_request

    url = "http://localhost:8080/apis/jobs/v2/workspaces/default/jobs/test-job-id/status-details"
    progress_tracking = ProgressTracking(url, progress_tracking_interval_seconds=0.01)

    # Verify first timer interval calls update
    assert progress_tracking._status_details.samples_processed == 0
    progress_tracking.increment_samples_processed()
    progress_tracking.increment_samples_processed()
    assert progress_tracking._status_details.samples_processed == 2
    # Use shorter sleep - just need to wait for timer callback, not real timing
    await asyncio.sleep(0.05)
    (
        mock_session_request.assert_called_once_with("PATCH", url, json={"samples_processed": 2, "progress": 0.0}),
        "update is only called once and not on each interval",
    )

    # Verify subsequent timer interval calls update
    progress_tracking.increment_samples_processed()
    assert progress_tracking._status_details.samples_processed == 3
    await asyncio.sleep(0.05)
    mock_session_request.assert_called_with("PATCH", url, json={"samples_processed": 3, "progress": 0.0})
    assert mock_session_request.call_count == 2, "update is only called on new payloads and not on each interval"

    # No calls to update after timer is stopped
    progress_tracking.stop()
    progress_tracking.increment_samples_processed()
    assert progress_tracking._status_details.samples_processed == 4
    await asyncio.sleep(0.05)
    assert mock_session_request.call_count == 2, "update is not called after timer is stopped"


@patch("urllib3.connectionpool.HTTPConnectionPool._get_conn")
@pytest.mark.asyncio
async def test_non_retry_status_code(getconn_mock, caplog):
    getconn_mock.return_value.getresponse.return_value = mock.MagicMock(status=404, msg=HTTPMessage())

    url_path = "/apis/jobs/v2/workspaces/default/jobs/test-job-id/status-details"
    url = f"http://localhost:8080{url_path}"

    with caplog.at_level(logging.INFO, logger=__name__):
        progress_tracking = ProgressTracking(url, logger=logging.getLogger(__name__))
        progress_tracking._send_progress(EvaluationStatusDetails(progress=100))
        assert "Failed to update job progress" in caplog.text

    assert getconn_mock.return_value.request.call_count == 1, "no retry for 404 status code"


@patch("urllib3.connectionpool.HTTPConnectionPool._get_conn")
@pytest.mark.asyncio
async def test_retry_status_code(getconn_mock, caplog):
    getconn_mock.return_value.getresponse.side_effect = [
        mock.MagicMock(status=409, msg=HTTPMessage(), headers={"Retry-After": "1"}),
        mock.MagicMock(status=200, msg=HTTPMessage()),
    ]
    url_path = "/apis/jobs/v2/workspaces/default/jobs/test-job-id/status-details"
    url = f"http://localhost:8080{url_path}"

    with caplog.at_level(logging.INFO, logger=__name__):
        progress_tracking = ProgressTracking(url, logger=logging.getLogger(__name__))
        progress_tracking._send_progress(EvaluationStatusDetails(progress=100))
        assert "Failed to update job progress" not in caplog.text

    assert getconn_mock.return_value.request.call_count == 2, "verify retries attempted"
    assert getconn_mock.return_value.request.mock_calls == [
        mock.call(
            "PATCH",
            url_path,
            body=b'{"progress": 100.0}',
            headers=mock.ANY,
            chunked=False,
            preload_content=False,
            decode_content=False,
            enforce_content_length=True,
        ),
        mock.call(
            "PATCH",
            url_path,
            body=b'{"progress": 100.0}',
            headers=mock.ANY,
            chunked=False,
            preload_content=False,
            decode_content=False,
            enforce_content_length=True,
        ),
    ]


@patch("urllib3.connectionpool.HTTPConnectionPool._get_conn")
@pytest.mark.asyncio
async def test_retry_fails(getconn_mock, caplog):
    getconn_mock.return_value.getresponse.return_value = mock.MagicMock(
        status=409, msg=HTTPMessage(), headers={"Retry-After": "1"}
    )

    url_path = "/apis/jobs/v2/workspaces/default/jobs/test-job-id/status-details"
    url = f"http://localhost:8080{url_path}"

    with caplog.at_level(logging.INFO, logger=__name__):
        progress_tracking = ProgressTracking(url, logger=logging.getLogger(__name__))
        progress_tracking._send_progress(EvaluationStatusDetails(progress=100))
        assert "Failed to communicate with progress tracking server" in caplog.text

    assert getconn_mock.return_value.request.call_count == 6, "verify max retries attempted"
    getconn_mock.return_value.request.assert_called_with(
        "PATCH",
        url_path,
        body=b'{"progress": 100.0}',
        headers=mock.ANY,
        chunked=False,
        preload_content=False,
        decode_content=False,
        enforce_content_length=True,
    )
