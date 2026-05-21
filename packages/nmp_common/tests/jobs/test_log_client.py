# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Tests for JobLogsClient SDK wrapper and PageCursor."""

from unittest.mock import AsyncMock, MagicMock

import pytest
from nemo_platform import NotFoundError
from nmp.common.jobs.log_client import JobLogsClient
from nmp.common.jobs.schemas import (
    PageCursor,
    PaginationDirection,
    PlatformJobLogPage,
)

# =============================================================================
# PageCursor Tests
# =============================================================================


def test_encode_decode_forward():
    """Test encoding and decoding a forward pagination cursor."""
    cursor = PageCursor(start_id=5, direction=PaginationDirection.FORWARD)
    encoded = cursor.encode()
    decoded = PageCursor.decode(encoded)

    assert decoded.start_id == 5
    assert decoded.direction == PaginationDirection.FORWARD


def test_encode_decode_backward():
    """Test encoding and decoding a backward pagination cursor."""
    cursor = PageCursor(start_id=3, direction=PaginationDirection.BACKWARD)
    encoded = cursor.encode()
    decoded = PageCursor.decode(encoded)

    assert decoded.start_id == 3
    assert decoded.direction == PaginationDirection.BACKWARD


def test_decode_invalid_cursor():
    """Test decoding an invalid cursor raises ValueError."""
    with pytest.raises(ValueError, match="Invalid page cursor"):
        PageCursor.decode("invalid_cursor_string")


# =============================================================================
# JobLogsClient Tests
# =============================================================================


@pytest.fixture
def mock_sdk():
    """Create a mock SDK for testing."""
    sdk = MagicMock()
    sdk.files.otlp.logs.query = AsyncMock()
    return sdk


@pytest.fixture
def log_client(mock_sdk):
    """Create a JobLogsClient with a mock SDK."""
    return JobLogsClient(sdk=mock_sdk)


async def test_query_logs_success(log_client, mock_sdk):
    """Test successful log query via SDK."""
    # Mock SDK response (SDK returns its own PlatformJobLogPage type)
    mock_log = MagicMock()
    mock_log.timestamp = "2024-01-01T12:00:00"
    mock_log.job = "job-123"
    mock_log.job_step = "step1"
    mock_log.job_task = "task1"
    mock_log.message = "Test log message"

    mock_response = MagicMock()
    mock_response.data = [mock_log]
    mock_response.total = 1
    mock_response.next_page = ""
    mock_response.prev_page = ""
    mock_response.model_dump.return_value = {
        "data": [
            {
                "timestamp": "2024-01-01T12:00:00",
                "job": "job-123",
                "job_step": "step1",
                "job_task": "task1",
                "message": "Test log message",
            }
        ],
        "total": 1,
        "next_page": None,
        "prev_page": None,
    }

    mock_sdk.files.otlp.logs.query.return_value = mock_response

    result = await log_client.query_logs(
        fileset="logs",
        workspace="test-workspace",
        filters={"job": "job-123"},
        page_size=100,
    )

    # Verify result
    assert isinstance(result, PlatformJobLogPage)
    assert len(result.data) == 1
    assert result.total == 1

    # Verify SDK call
    mock_sdk.files.otlp.logs.query.assert_called_once()
    call_kwargs = mock_sdk.files.otlp.logs.query.call_args.kwargs
    assert call_kwargs["name"] == "logs"
    assert call_kwargs["workspace"] == "test-workspace"
    assert call_kwargs["filters"] == {"job": "job-123"}
    assert call_kwargs["limit"] == 100


async def test_query_logs_with_pagination_cursor(log_client, mock_sdk):
    """Test query_logs passes pagination cursor correctly."""
    mock_response = MagicMock()
    mock_response.model_dump.return_value = {
        "data": [],
        "total": 0,
        "next_page": None,
        "prev_page": None,
    }
    mock_sdk.files.otlp.logs.query.return_value = mock_response

    cursor = PageCursor(start_id=2, direction=PaginationDirection.FORWARD).encode()

    await log_client.query_logs(
        fileset="logs",
        workspace="test-workspace",
        page_cursor=cursor,
    )

    # Verify cursor is passed to SDK
    call_kwargs = mock_sdk.files.otlp.logs.query.call_args.kwargs
    assert call_kwargs["page_cursor"] == cursor


async def test_query_logs_404_returns_empty_page(log_client, mock_sdk):
    """Test that NotFoundError returns an empty page."""
    mock_sdk.files.otlp.logs.query.side_effect = NotFoundError(
        "Not found",
        response=MagicMock(status_code=404),
        body=None,
    )

    result = await log_client.query_logs(
        fileset="logs",
        workspace="test-workspace",
    )

    # Should return empty page, not raise
    assert result.data == []
    assert result.total == 0
    assert result.next_page is None
    assert result.prev_page is None


async def test_query_logs_other_error_raises(log_client, mock_sdk):
    """Test that other errors are raised to the caller."""
    mock_sdk.files.otlp.logs.query.side_effect = RuntimeError("Unexpected error")

    with pytest.raises(RuntimeError, match="Unexpected error"):
        await log_client.query_logs(
            fileset="logs",
            workspace="test-workspace",
        )


async def test_query_logs_empty_filters(log_client, mock_sdk):
    """Test query_logs with no filters."""
    mock_response = MagicMock()
    mock_response.model_dump.return_value = {
        "data": [],
        "total": 0,
        "next_page": None,
        "prev_page": None,
    }
    mock_sdk.files.otlp.logs.query.return_value = mock_response

    await log_client.query_logs(
        fileset="logs",
        workspace="test-workspace",
        filters=None,
    )

    # Verify empty filters dict is sent
    call_kwargs = mock_sdk.files.otlp.logs.query.call_args.kwargs
    assert call_kwargs["filters"] == {}


def test_sdk_created_in_constructor(mock_sdk):
    """Test that SDK is set in constructor."""
    client = JobLogsClient(sdk=mock_sdk)
    assert client._sdk is mock_sdk
