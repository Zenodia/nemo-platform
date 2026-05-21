# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import json
from enum import Enum

import base58
from nemo_platform_plugin.jobs.schemas import FileStorageType as FileStorageType
from nemo_platform_plugin.jobs.schemas import PlatformJobListResultResponse as PlatformJobListResultResponse
from nemo_platform_plugin.jobs.schemas import PlatformJobLog as PlatformJobLog
from nemo_platform_plugin.jobs.schemas import PlatformJobLogPage as PlatformJobLogPage
from nemo_platform_plugin.jobs.schemas import PlatformJobResultCreateRequest as PlatformJobResultCreateRequest
from nemo_platform_plugin.jobs.schemas import PlatformJobResultResponse as PlatformJobResultResponse
from nemo_platform_plugin.jobs.schemas import PlatformJobStatus as PlatformJobStatus
from nemo_platform_plugin.jobs.schemas import PlatformJobStatusResponse as PlatformJobStatusResponse
from nemo_platform_plugin.jobs.schemas import PlatformJobStepStatusResponse as PlatformJobStepStatusResponse
from nemo_platform_plugin.jobs.schemas import PlatformJobTaskStatusResponse as PlatformJobTaskStatusResponse
from pydantic import BaseModel, Field

# =============================================================================
# Pagination (stays in nmp-common — depends on base58)
# =============================================================================


class PaginationDirection(int, Enum):
    """Direction for cursor-based pagination."""

    FORWARD = 0
    BACKWARD = 1


class PageCursor(BaseModel):
    """Schema for cursor-based pagination."""

    start_id: int = Field(description="The ID to start pagination from")
    direction: PaginationDirection = Field(description="The direction of pagination")

    def encode(self) -> str:
        """Encode a page cursor from start_id and direction using compact tuple format with base58."""
        cursor_data = [self.start_id, self.direction]
        json_str = json.dumps(cursor_data)
        encoded = base58.b58encode(json_str.encode()).decode()
        return encoded

    @staticmethod
    def decode(page_cursor: str) -> "PageCursor":
        """Decode a page cursor to get PageCursor object using Pydantic schema with base58."""
        try:
            decoded = base58.b58decode(page_cursor.encode()).decode()
            start_id, direction_int = json.loads(decoded)
            direction = PaginationDirection(direction_int)
            return PageCursor(start_id=start_id, direction=direction)
        except (ValueError, TypeError, Exception):
            raise ValueError("Invalid page cursor")


class InvalidPageCursorError(Exception):
    """Custom exception for invalid page cursor errors."""

    pass
