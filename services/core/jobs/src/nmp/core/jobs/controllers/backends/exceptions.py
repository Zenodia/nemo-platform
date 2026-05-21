# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0


class FailedToScheduleError(Exception):
    """Exception raised when a job fails to be scheduled."""

    def __init__(self, message, error_details: dict | None = None) -> None:
        super().__init__(message)
        self.error_details = error_details


class ResourceAllocationError(Exception):
    """Exception raised when a resource allocation fails."""

    def __init__(self, message: str = "Failed to allocate resource"):
        super().__init__(message)
        self.message = message


class JobStorageError(Exception):
    """Exception raised when there's an issue with job storage."""
