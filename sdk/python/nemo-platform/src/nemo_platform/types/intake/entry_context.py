# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime

from ..._models import BaseModel

__all__ = ["EntryContext"]


class EntryContext(BaseModel):
    """Contextual metadata attached to every entry record.

    Keeping these grouped in a dedicated object avoids polluting the top-level
    entity schema and makes it trivial to extend without breaking compatibility.
    """

    app: str
    """Reference to the app that produced this entry, in the form `workspace/name`.

    If the app doesn't exist, it will be automatically created when the entry is
    ingested.
    """

    task: str
    """Name of the task within the app (e.g., 'chat', 'completion', 'tool-call').

    If the task doesn't exist, it will be automatically created when the entry is
    ingested.
    """

    created_at: Optional[datetime] = None
    """UTC timestamp when the entry was created."""

    session_id: Optional[str] = None
    """Long-lived session identifier (e.g., user account or browser session).

    Stored for post-processing analytics; not used by the Intake service at runtime.
    """

    thread_id: Optional[str] = None
    """
    Logical thread identifier that groups related entries in a multi-turn
    conversation. If provided, entries with the same thread_id are treated as part
    of the same conversation. If omitted, the entry is treated as a single-turn
    interaction (e.g., a standalone tool call or completion).
    """

    trace_id: Optional[str] = None
    """Distributed trace identifier (e.g., W3C traceparent).

    Intake stores it verbatim and does not use it at ingestion time; helps with
    later cross-system joins.
    """

    user_id: Optional[str] = None
    """Identifier of the application's end-user who triggered this LLM interaction.

    This represents the person using your application (e.g., 'customer_123',
    'employee@company.com'), NOT the service account that created the entry record
    (see ownership.created_by for that). Use this to track which of your users a
    conversation belongs to, filter entries by user, and enable per-user analytics.
    Format is application-defined.
    """
