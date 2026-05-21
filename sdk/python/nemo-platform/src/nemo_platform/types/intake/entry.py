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

from typing import Dict, List, Union, Optional
from datetime import datetime
from typing_extensions import Annotated, TypeAlias

from .usage import Usage
from ..._utils import PropertyInfo
from ..._models import BaseModel
from .entry_data import EntryData
from .user_rating import UserRating
from .entry_context import EntryContext
from .user_action_event import UserActionEvent
from .user_feedback_event import UserFeedbackEvent
from .evaluator_result_event import EvaluatorResultEvent
from .reviewer_annotation_event import ReviewerAnnotationEvent

__all__ = ["Entry", "Event"]

Event: TypeAlias = Annotated[
    Union[UserFeedbackEvent, UserActionEvent, ReviewerAnnotationEvent, EvaluatorResultEvent],
    PropertyInfo(discriminator="event_type"),
]


class Entry(BaseModel):
    """Schema for Entry responses."""

    id: str
    """Unique identifier"""

    context: EntryContext
    """Contextual metadata attached to every entry record.

    Keeping these grouped in a dedicated object avoids polluting the top-level
    entity schema and makes it trivial to extend without breaking compatibility.
    """

    data: EntryData
    """Entry data containing the request and response for an LLM interaction."""

    name: str
    """Entry name (auto-generated)"""

    workspace: str
    """Workspace identifier"""

    created_at: Optional[datetime] = None
    """Creation timestamp"""

    custom_fields: Optional[Dict[str, object]] = None
    """Free-form metadata bag for client-defined fields."""

    events: Optional[List[Event]] = None
    """Events associated with this entry"""

    external_id: Optional[str] = None
    """Client-provided identifier"""

    project: Optional[str] = None
    """The name of the project associated with this entry"""

    updated_at: Optional[datetime] = None
    """Last update timestamp"""

    usage: Optional[Usage] = None
    """Structured usage metrics captured at log time.

    Every field is optional so producers can populate whatever they have without
    schema breakage. Stored as the entry-level `usage` field so filters can reach it
    via `data.usage.<field>` entity-store paths.
    """

    user_rating: Optional[UserRating] = None
    """User's rating/evaluation of an AI response.

    This captures various forms of end-user feedback about a model's response,
    including binary thumbs up/down ratings, numeric scores, free-text opinions,
    suggested rewrites, and structured category ratings.

    Either `thumb` or `rating` should be provided (they are mutually exclusive), but
    all fields are optional to accommodate different feedback collection patterns.
    """
