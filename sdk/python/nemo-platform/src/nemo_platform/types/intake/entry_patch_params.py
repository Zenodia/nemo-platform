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

from __future__ import annotations

from typing import Dict, Union, Iterable
from typing_extensions import TypeAlias, TypedDict

from .usage_param import UsageParam
from .entry_data_param import EntryDataParam
from .user_rating_param import UserRatingParam
from .entry_context_param import EntryContextParam
from .user_action_event_param import UserActionEventParam
from .user_feedback_event_param import UserFeedbackEventParam
from .evaluator_result_event_param import EvaluatorResultEventParam
from .reviewer_annotation_event_param import ReviewerAnnotationEventParam

__all__ = ["EntryPatchParams", "Event"]


class EntryPatchParams(TypedDict, total=False):
    workspace: str

    context: EntryContextParam
    """Contextual metadata attached to every entry record.

    Keeping these grouped in a dedicated object avoids polluting the top-level
    entity schema and makes it trivial to extend without breaking compatibility.
    """

    custom_fields: Dict[str, object]
    """
    Free-form metadata bag for client-defined fields (replaces existing value when
    provided).
    """

    data: EntryDataParam
    """Entry data containing the request and response for an LLM interaction."""

    events: Iterable[Event]
    """Events associated with this entry"""

    usage: UsageParam
    """Structured usage metrics captured at log time.

    Every field is optional so producers can populate whatever they have without
    schema breakage. Stored as the entry-level `usage` field so filters can reach it
    via `data.usage.<field>` entity-store paths.
    """

    user_rating: UserRatingParam
    """User's rating/evaluation of an AI response.

    This captures various forms of end-user feedback about a model's response,
    including binary thumbs up/down ratings, numeric scores, free-text opinions,
    suggested rewrites, and structured category ratings.

    Either `thumb` or `rating` should be provided (they are mutually exclusive), but
    all fields are optional to accommodate different feedback collection patterns.
    """


Event: TypeAlias = Union[
    UserFeedbackEventParam, UserActionEventParam, ReviewerAnnotationEventParam, EvaluatorResultEventParam
]
