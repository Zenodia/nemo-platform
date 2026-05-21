# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Intake entities package.

This package contains all entity definitions, value types, and enums for the Intake service.
"""

# Enums
# Entity classes
from .entities import (
    App,
    Entry,
    ExportJob,
    Task,
)
from .enums import (
    EntryEventType,
    ExportMode,
    ExportStatus,
    JobStatus,
    MessageRole,
    RowTransformation,
    ThumbDirection,
)

# Value types
from .values import (
    EntryContext,
    EntryData,
    EntryEvent,
    EvaluatorResultEvent,
    ExportConfig,
    ExportStatusDetails,
    FlexibleEntryRequest,
    FlexibleEntryResponse,
    FlexibleMessage,
    ReviewerAnnotationEvent,
    Usage,
    UserActionEvent,
    UserFeedbackEvent,
    UserRating,
)

__all__ = [
    # Enums
    "EntryEventType",
    "ExportMode",
    "ExportStatus",
    "JobStatus",
    "MessageRole",
    "RowTransformation",
    "ThumbDirection",
    # Value types
    "EntryContext",
    "EntryData",
    "EntryEvent",
    "EvaluatorResultEvent",
    "ExportConfig",
    "ExportStatusDetails",
    "FlexibleEntryRequest",
    "FlexibleEntryResponse",
    "FlexibleMessage",
    "ReviewerAnnotationEvent",
    "Usage",
    "UserActionEvent",
    "UserFeedbackEvent",
    "UserRating",
    # Entity classes
    "App",
    "Entry",
    "ExportJob",
    "Task",
]
