# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""API schemas for App endpoints."""

from datetime import datetime
from enum import StrEnum
from typing import Optional

from nmp.common.entities.values import DatetimeFilter, Filter
from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# App Request/Response schemas
# ---------------------------------------------------------------------------


class AppInput(BaseModel):
    """Schema for creating a new App."""

    name: str = Field(..., description="App name (unique within workspace)")
    # Note: workspace comes from workspace in the URL path, not the body
    description: str | None = Field(default=None, description="App description")
    project: str | None = Field(default=None, description="The name of the project associated with this app")
    locked: bool = Field(
        default=False,
        description="If true, this record cannot be automatically updated when entries are ingested.",
    )


class AppUpdate(BaseModel):
    """Schema for updating an existing App."""

    description: str | None = Field(default=None, description="App description")
    project: str | None = Field(default=None, description="The name of the project associated with this app")
    locked: bool | None = Field(default=None, description="Lock status")


class App(BaseModel):
    """Schema for App responses."""

    id: str = Field(..., description="Unique identifier")
    name: str = Field(..., description="App name")
    workspace: str = Field(..., description="Workspace identifier")
    description: str | None = Field(default=None, description="App description")
    project: str | None = Field(default=None, description="The name of the project associated with this app")
    locked: bool = Field(default=False, description="Lock status")
    created_at: datetime | None = Field(default=None, description="Creation timestamp")
    updated_at: datetime | None = Field(default=None, description="Last update timestamp")


# ---------------------------------------------------------------------------
# Sort enums
# ---------------------------------------------------------------------------


class AppSortField(StrEnum):
    """Sort fields for Apps."""

    CREATED_AT_ASC = "created_at"
    CREATED_AT_DESC = "-created_at"
    NAME_ASC = "name"
    NAME_DESC = "-name"
    UPDATED_AT_ASC = "updated_at"
    UPDATED_AT_DESC = "-updated_at"


# ---------------------------------------------------------------------------
# Filter schemas
# ---------------------------------------------------------------------------


class AppFilter(Filter):
    """Filter for Apps."""

    workspace: Optional[str] = Field(None, description="Filter by workspace id.")
    name: Optional[str] = Field(None, description="Filter by app name.")
    project: Optional[str] = Field(None, description="Filter by project name.")
    description: Optional[str] = Field(None, description="Filter by app description.")
    created_at: Optional[DatetimeFilter] = Field(None, description="Filter entities based on creation date.")
    updated_at: Optional[DatetimeFilter] = Field(None, description="Filter entities based on update date.")
