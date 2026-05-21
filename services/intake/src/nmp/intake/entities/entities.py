# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Entity definitions for the Intake service using EntityBase.

These entities use the new EntityClient pattern with EntityBase for
compatibility with the v2 Entity Store.
"""

from typing import Any, Dict, List, Optional

from nmp.common.entities.client import EntityBase
from pydantic import AnyUrl, Field, model_validator

from .enums import JobStatus
from .values import (
    EntryContext,
    EntryData,
    EntryEvent,
    ExportConfig,
    ExportStatusDetails,
    Usage,
    UserRating,
)


class App(EntityBase):
    """Application that sends data to the Intake service.

    Apps are scoped by workspace, identified by workspace/name.
    """

    __entity_type__ = "intake_app"

    description: str | None = Field(default=None, description="App description")
    locked: bool = Field(
        default=False,
        description=(
            "If true, this record cannot be automatically updated when entries are ingested. "
            "When an entry is created, the system normally auto-updates the app's metadata (name, description). "
            "Set locked=true to prevent these automatic updates and preserve manually curated information. "
            "The record can still be modified via explicit PATCH requests."
        ),
    )


class Task(EntityBase):
    """Logical task within an application.

    Tasks are scoped by workspace, but also sub-entities of Apps.
    Task names must be unique within their parent app.
    """

    __entity_type__ = "intake_task"

    description: str | None = Field(default=None, description="Task description")
    app: str = Field(..., description="The app this task belongs to, in the form `workspace/name`.")
    locked: bool = Field(
        default=False,
        description=(
            "If true, this record cannot be automatically updated when entries are ingested. "
            "When an entry is created, the system normally auto-updates the task's metadata (name, description). "
            "Set locked=true to prevent these automatic updates and preserve manually curated information. "
            "The record can still be modified via explicit PATCH requests."
        ),
    )


class Entry(EntityBase):
    """LLM completion entry stored in the Intake service.

    Entries have auto-generated names and can optionally have an external_id
    for referencing by client-provided identifiers.
    """

    __entity_type__ = "intake_entry"

    # External identifier (e.g., completion_id from LLM provider)
    external_id: Optional[str] = Field(
        default=None,
        description=(
            "Optional client-provided identifier (e.g., completion_id from an LLM provider like OpenAI or NIM). "
            "Must be globally unique if provided—attempting to create an entry with a duplicate external_id will fail with a 409 error. "
            "If your service provides unique IDs (like 'chatcmpl-abc123'), you should use them here for easier lookups. "
            "Entries can be retrieved using external_id via the prefix syntax: GET /entries/external:chatcmpl-abc123"
        ),
    )

    # Primary artifacts
    data: EntryData = Field(..., description="Entry data containing request and response.")

    # Usage metrics
    usage: Optional[Usage] = Field(
        default=None,
        description="Structured usage metrics (model served, latency, cost, token counts).",
    )

    # Contextual metadata
    context: EntryContext = Field(..., description="Metadata describing producer, task, trace.")

    # User feedback and events
    user_rating: Optional[UserRating] = Field(default=None, description="User's rating/evaluation of the AI response.")
    events: List[EntryEvent] = Field(default_factory=list, description="All events associated with this entry.")

    # Free-form metadata bag for client-defined fields (e.g., experiment metadata
    # from external eval frameworks). Stored as a JSON column on the entity store.
    custom_fields: Optional[Dict[str, Any]] = Field(
        default=None,
        description=(
            "Free-form metadata bag for client-defined fields. "
            "Use this to attach structured client metadata (e.g., experiment provenance, "
            "external job IDs) that doesn't fit elsewhere on the entry."
        ),
    )

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


class ExportJob(EntityBase):
    """Export job tracking entry exports to external datastores.

    Export jobs track the status of background export tasks.
    """

    __entity_type__ = "intake_export_job"

    status: JobStatus = Field(default=JobStatus.PENDING, description="Job status")

    config: ExportConfig = Field(
        ...,
        description="The export configuration defining filters, search criteria, and format options.",
    )

    output_file_url: Optional[AnyUrl] = Field(
        default=None,
        description="The place where the exported file should be written (file://, hf://, nds://, etc.)",
    )

    status_details: Optional[ExportStatusDetails] = Field(
        default_factory=ExportStatusDetails,
        description="Details about the status of the export job.",
    )
