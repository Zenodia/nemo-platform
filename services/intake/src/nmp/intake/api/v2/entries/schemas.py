# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""API schemas for Entry endpoints."""

from datetime import datetime
from enum import StrEnum
from typing import Annotated, Any, Dict, List, Optional, Union

from nmp.common.entities.values import DatetimeFilter, Filter, map_entity_field
from nmp.intake.entities import EntryContext, EntryData, EntryEvent, ThumbDirection, Usage, UserRating
from pydantic import BaseModel, Field, model_validator

# ---------------------------------------------------------------------------
# Entry Request/Response schemas
# ---------------------------------------------------------------------------


class EntryInput(BaseModel):
    """Schema for creating a new Entry."""

    # Note: workspace comes from workspace in the URL path, not the body
    external_id: str | None = Field(
        default=None,
        description="Optional client-provided identifier (e.g., completion_id from an LLM provider)",
    )
    project: str | None = Field(default=None, description="The name of the project associated with this entry")
    data: EntryData = Field(..., description="Entry data containing request and response")
    usage: Usage | None = Field(
        default=None,
        description="Structured usage metrics (model served, latency, cost, token counts).",
    )
    context: EntryContext = Field(..., description="Metadata describing producer, task, trace")
    user_rating: UserRating | None = Field(default=None, description="User's rating/evaluation of the AI response")
    events: List[EntryEvent] = Field(default_factory=list, description="Events associated with this entry")
    custom_fields: Dict[str, Any] | None = Field(
        default=None,
        description="Free-form metadata bag for client-defined fields (e.g., external experiment metadata).",
    )


class EntryUpdate(BaseModel):
    """Schema for updating an existing Entry."""

    data: EntryData | None = Field(default=None, description="Entry data containing request and response")
    usage: Usage | None = Field(
        default=None,
        description="Structured usage metrics (model served, latency, cost, token counts).",
    )
    context: EntryContext | None = Field(default=None, description="Metadata describing producer, task, trace")
    user_rating: UserRating | None = Field(default=None, description="User's rating/evaluation of the AI response")
    events: List[EntryEvent] | None = Field(default=None, description="Events associated with this entry")
    custom_fields: Dict[str, Any] | None = Field(
        default=None,
        description="Free-form metadata bag for client-defined fields (replaces existing value when provided).",
    )


class Entry(BaseModel):
    """Schema for Entry responses."""

    id: str = Field(..., description="Unique identifier")
    name: str = Field(..., description="Entry name (auto-generated)")
    workspace: str = Field(..., description="Workspace identifier")
    external_id: str | None = Field(default=None, description="Client-provided identifier")
    project: str | None = Field(default=None, description="The name of the project associated with this entry")
    data: EntryData = Field(..., description="Entry data containing request and response")
    usage: Usage | None = Field(
        default=None,
        description="Structured usage metrics (model served, latency, cost, token counts).",
    )
    context: EntryContext = Field(..., description="Metadata describing producer, task, trace")
    user_rating: UserRating | None = Field(default=None, description="User's rating/evaluation")
    events: List[EntryEvent] = Field(default_factory=list, description="Events associated with this entry")
    custom_fields: Dict[str, Any] | None = Field(
        default=None,
        description="Free-form metadata bag for client-defined fields.",
    )
    created_at: datetime | None = Field(default=None, description="Creation timestamp")
    updated_at: datetime | None = Field(default=None, description="Last update timestamp")

    @model_validator(mode="before")
    @classmethod
    def _coerce_nested_models(cls, data: Any) -> Any:
        """Coerce nested dict fields to their proper Pydantic model types.

        When entities are loaded from the Entity Store, nested Pydantic models
        come back as raw dicts. This validator ensures they are properly coerced
        to avoid Pydantic serialization warnings.
        """
        if isinstance(data, dict) and isinstance(data.get("user_rating"), dict):
            data["user_rating"] = UserRating(**data["user_rating"])
        return data


# ---------------------------------------------------------------------------
# Events Sub-resource schemas
# ---------------------------------------------------------------------------


class EventsCreateRequest(BaseModel):
    """Request to add events to an entry."""

    events: List[EntryEvent] = Field(..., min_length=1, description="List of events to add to the entry.")


# ---------------------------------------------------------------------------
# Sort enums
# ---------------------------------------------------------------------------


class EntrySortField(StrEnum):
    """Sort fields for Entries."""

    CREATED_AT_ASC = "created_at"
    CREATED_AT_DESC = "-created_at"
    UPDATED_AT_ASC = "updated_at"
    UPDATED_AT_DESC = "-updated_at"


# ---------------------------------------------------------------------------
# Filter schemas
# ---------------------------------------------------------------------------


class EntryContextFilter(BaseModel):
    """Filter for entry context fields."""

    app: Optional[str] = Field(None, description="Filter by app reference (workspace/name).")
    task: Optional[str] = Field(None, description="Filter by task reference.")
    thread_id: Optional[str] = Field(None, description="Filter by thread ID.")
    user_id: Optional[str] = Field(None, description="Filter by user ID.")
    session_id: Optional[str] = Field(None, description="Filter by session ID.")


class EntryUserRatingFilter(BaseModel):
    """Filter for entry user rating fields."""

    thumb: Optional[ThumbDirection] = Field(None, description="Filter by thumb direction.")


class EntryFilter(Filter):
    """Filter for Entries."""

    id: Optional[Union[str, Dict[str, Any]]] = Field(
        None,
        description="Filter by entry ID. Supports operators like {'in': ['entry-ABC', 'entry-XYZ']} for multiple IDs.",
    )
    workspace: Optional[str] = Field(None, description="Filter by workspace id.")
    project: Optional[str] = Field(None, description="Filter by project name.")
    external_id: Optional[Union[str, Dict[str, Any]]] = Field(
        None,
        description="Filter by external ID. Supports operators like {'in': ['id1', 'id2']} for multiple IDs.",
    )

    # Nested context filters — persisted under the entity row JSON `data` blob (`data.context.*`).
    context: Optional[EntryContextFilter] = Field(None, description="Filter by context fields.")

    user_rating: Optional[EntryUserRatingFilter] = Field(None, description="Filter by user rating fields.")

    # Only model is currently supported in usage -- numeric filter support coming in FP-59
    model: Annotated[Optional[str], map_entity_field("data.usage.model")] = Field(
        None,
        description="Filter by the served model recorded in usage (e.g., 'gpt-4o', 'meta/llama-3.1-70b-instruct').",
    )

    # Feedback filters (non-nested convenience filters)
    has_thumb: Optional[bool] = Field(None, description="Filter by presence of thumb feedback.")
    has_rating: Optional[bool] = Field(None, description="Filter by presence of rating.")
    has_opinion: Optional[bool] = Field(None, description="Filter by presence of opinion.")
    has_rewrite: Optional[bool] = Field(None, description="Filter by presence of rewrite.")
    has_events: Optional[bool] = Field(None, description="Filter by presence of any events.")

    # Thread aggregation filter
    longest_per_thread: Optional[bool] = Field(
        None, description="If true, return only the longest entry per thread (based on message count)."
    )

    # Timestamp filters
    created_at: Optional[DatetimeFilter] = Field(None, description="Filter entities based on creation date.")
    updated_at: Optional[DatetimeFilter] = Field(None, description="Filter entities based on update date.")
