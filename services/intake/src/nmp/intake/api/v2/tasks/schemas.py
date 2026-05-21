# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""API schemas for Task endpoints."""

from datetime import datetime
from enum import StrEnum
from typing import Optional

from nmp.common.entities.values import DatetimeFilter, Filter
from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Task Request/Response schemas
# ---------------------------------------------------------------------------


class TaskInput(BaseModel):
    """Schema for creating a new Task.

    Note: workspace and app are automatically set from the URL path.
    """

    name: str = Field(..., description="Task name")
    description: str | None = Field(default=None, description="Task description")
    project: str | None = Field(default=None, description="The name of the project associated with this task")
    locked: bool = Field(
        default=False,
        description="If true, this record cannot be automatically updated when entries are ingested.",
    )


class TaskUpdate(BaseModel):
    """Schema for updating an existing Task."""

    description: str | None = Field(default=None, description="Task description")
    project: str | None = Field(default=None, description="The name of the project associated with this task")
    locked: bool | None = Field(default=None, description="Lock status")


class Task(BaseModel):
    """Schema for Task responses."""

    id: str = Field(..., description="Unique identifier")
    name: str = Field(..., description="Task name")
    workspace: str = Field(..., validation_alias="workspace", description="Workspace identifier")
    app: str = Field(..., description="Parent app reference (workspace/name)")
    description: str | None = Field(default=None, description="Task description")
    project: str | None = Field(default=None, description="The name of the project associated with this task")
    locked: bool = Field(default=False, description="Lock status")
    created_at: datetime | None = Field(default=None, description="Creation timestamp")
    updated_at: datetime | None = Field(default=None, description="Last update timestamp")


# ---------------------------------------------------------------------------
# Sort enums
# ---------------------------------------------------------------------------


class TaskSortField(StrEnum):
    """Sort fields for Tasks."""

    CREATED_AT_ASC = "created_at"
    CREATED_AT_DESC = "-created_at"
    NAME_ASC = "name"
    NAME_DESC = "-name"
    UPDATED_AT_ASC = "updated_at"
    UPDATED_AT_DESC = "-updated_at"


# ---------------------------------------------------------------------------
# Filter schemas
# ---------------------------------------------------------------------------


class TaskFilter(Filter):
    """Filter for Tasks."""

    workspace: Optional[str] = Field(None, description="Filter by workspace id.")
    name: Optional[str] = Field(None, description="Filter by task name.")
    app: Optional[str] = Field(None, description="Filter by app reference (workspace/name).")
    project: Optional[str] = Field(None, description="Filter by project name.")
    description: Optional[str] = Field(None, description="Filter by task description.")
    created_at: Optional[DatetimeFilter] = Field(None, description="Filter entities based on creation date.")
    updated_at: Optional[DatetimeFilter] = Field(None, description="Filter entities based on update date.")
