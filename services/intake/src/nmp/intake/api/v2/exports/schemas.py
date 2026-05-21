# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Export schemas for Intake API."""

from enum import StrEnum
from typing import Any, Dict, List, Optional

from nmp.common.entities.values import DatetimeFilter, Filter
from nmp.intake.entities import JobStatus
from pydantic import AnyUrl, BaseModel, Field

# ---------------------------------------------------------------------------
# Sort enums
# ---------------------------------------------------------------------------


class ExportJobSortField(StrEnum):
    """Sort fields for ExportJobs."""

    CREATED_AT_ASC = "created_at"
    CREATED_AT_DESC = "-created_at"
    UPDATED_AT_ASC = "updated_at"
    UPDATED_AT_DESC = "-updated_at"
    STATUS_ASC = "status"
    STATUS_DESC = "-status"


# ---------------------------------------------------------------------------
# Filter schemas
# ---------------------------------------------------------------------------


class ExportJobFilter(Filter):
    """Filter for ExportJobs."""

    id: Optional[str] = Field(None, description="Filter by export job ID.")
    workspace: Optional[str] = Field(None, description="Filter by workspace id.")
    name: Optional[str] = Field(None, description="Filter by export job name.")
    status: Optional[JobStatus] = Field(None, description="Filter by job status.")
    output_file_url: Optional[str] = Field(None, description="Filter by output file URL.")
    created_at: Optional[DatetimeFilter] = Field(None, description="Filter entities based on creation date.")
    updated_at: Optional[DatetimeFilter] = Field(None, description="Filter entities based on update date.")


# ---------------------------------------------------------------------------
# Request/Response schemas
# ---------------------------------------------------------------------------


class ExportConfigInput(BaseModel):
    """Input schema for export configuration.

    Defines what entries to export and how to format them.
    """

    filters: Optional[Dict[str, Any]] = Field(
        default=None,
        description=(
            "Filter criteria for selecting entries (workspace, app, task, thread_id, external_id, "
            "has_thumb, has_rating, longest_per_thread, model, etc.)"
        ),
    )

    search: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Search criteria for finding entries",
    )

    limit: Optional[int] = Field(
        default=1000,
        description="Maximum number of entries to export. None means no limit.",
    )

    format_options: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Format options for the export (e.g., row_transformation)",
    )


class ExportJobInput(BaseModel):
    """Request payload for creating an export job."""

    config: ExportConfigInput = Field(..., description="Export configuration")
    output_file_url: AnyUrl = Field(
        ...,
        description="The place where the exported file should be written (file://, hf://, nds://, etc.)",
    )


class ExportPreviewRequest(BaseModel):
    """Request payload for previewing export data without writing to a file."""

    config: ExportConfigInput = Field(..., description="Export configuration for preview")


class ExportPreviewResponse(BaseModel):
    """Response containing preview data from the export configuration."""

    data: List[Dict[str, Any]] = Field(..., description="Preview data (max 100 records)")
    count: int = Field(..., description="Number of records returned")
    config: ExportConfigInput = Field(..., description="The configuration used for this preview")
