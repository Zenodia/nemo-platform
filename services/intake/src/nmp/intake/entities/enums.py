# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Enums for the Intake service."""

from enum import Enum


class EntryEventType(str, Enum):
    """High-level categorization of events linked to an entry.

    ### Values

    #### user_feedback
    User-supplied opinion about the generated entry. Examples:

    - **Thumbs-up / thumbs-down** – simple binary rating.
    - **Chosen response** – the user selected one of several responses.
    - **Rewrite / edit** – the user provided an improved version.

    #### user_action
    Arbitrary client-defined action taken after the entry is shown. Examples:

    - **share_clicked** – user clicked a *Share* button.
    - **code_copied** – user copied a code snippet to the clipboard.
    - **purchase_made** – user purchased an item recommended by the assistant.

    #### reviewer_annotation
    Reviewer-supplied opinion about the existing entry. Examples:
    - **Thumbs-up / thumbs-down** – simple binary rating.
    - **Chosen response** – the reviewer selected one of several responses.
    - **Rewrite / edit** – the reviewer provided an improved version.

    #### evaluator_result
    Score produced by an automated evaluator (verifier, judge, auditor,
    external eval framework, etc.). Examples:

    - **Verifier reward** – numeric reward from an eval framework's verifier.
    - **LLM-judge score** – numeric or categorical judgement.
    - **Auditor probe result** – pass/fail or graded score from a security probe.
    """

    user_feedback = "user_feedback"
    user_action = "user_action"
    reviewer_annotation = "reviewer_annotation"
    evaluator_result = "evaluator_result"


class MessageRole(str, Enum):
    """Valid role values for entry request messages."""

    user = "user"
    system = "system"
    assistant = "assistant"
    developer = "developer"
    tool = "tool"
    function = "function"


class ThumbDirection(str, Enum):
    """Possible thumb feedback choices."""

    up = "up"
    down = "down"


class ExportMode(str, Enum):
    """Export and search modes for retrieving entry data.

    Currently only 'entries' mode is supported. Future modes may be added.
    """

    entries = "entries"


class ExportStatus(str, Enum):
    """Status values for export jobs."""

    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"
    failed = "failed"


class RowTransformation(str, Enum):
    """Supported transformations for exported rows.

    ### Values

    #### use_annotation_rewrite
    Use reviewer annotation response_override to replace the original response when available.
    Note: The 'rewrite' field contains end-user suggestions and does not modify exports.
    Reviewers should use 'response_override' for corrections.
    """

    use_annotation_rewrite = "use_annotation_rewrite"


class JobStatus(str, Enum):
    """Job status enum."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
