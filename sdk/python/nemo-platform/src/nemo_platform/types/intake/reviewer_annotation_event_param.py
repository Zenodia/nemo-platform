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

from typing import Dict, Union
from datetime import datetime
from typing_extensions import Literal, Annotated, TypedDict

from ..._utils import PropertyInfo
from .thumb_direction import ThumbDirection

__all__ = ["ReviewerAnnotationEventParam"]


class ReviewerAnnotationEventParam(TypedDict, total=False):
    """Structured annotation supplied by a reviewer or expert evaluator.

    A reviewer annotation is similar to user feedback but includes an additional capability
    to provide a complete replacement response. This is useful when human experts need to
    correct not just the text but also structured elements like tool calls, function outputs,
    or other response metadata.

    Inherits all feedback fields from UserFeedbackEvent (thumb, rating, opinion, rewrite,
    chosen_index, categories) and adds response_override for full response replacement.
    """

    id: str
    """Unique identifier for the event. Populated when retrieved from database."""

    categories: Dict[str, Union[float, str]]
    """Application-specific category ratings as key-value pairs.

    Use this for custom rating dimensions (e.g., {'helpfulness': 4, 'accuracy': 5,
    'tone': 'professional'}). Useful for radio buttons, dropdowns, or
    multi-dimensional rating systems.
    """

    chosen_index: int
    """
    Zero-based index of the response option the user selected when multiple
    responses were returned. Use this when showing users multiple completion choices
    and tracking which one they picked.
    """

    created_at: Annotated[Union[str, datetime], PropertyInfo(format="iso8601")]
    """UTC timestamp when the record was created."""

    created_by: Dict[str, str]
    """Identifier of the user or system that generated the record.

    Can be set of key-value pairs.
    """

    event_type: Literal["reviewer_annotation"]

    opinion: str
    """Free-text comment from the end user describing their opinion of the response."""

    rating: float
    """Numeric rating (e.g., 1-5 stars) provided by the end user.

    Mutually exclusive with `thumb`. Use this for star ratings or numeric scales.
    """

    response_override: Dict[str, object]
    """
    Complete JSON object that replaces the original model response when exporting
    data. Unlike the `rewrite` field (which is just text), this can include tool
    calls, function outputs, and all other response metadata. When an entry with
    response_override is exported, you can choose to use this corrected response
    instead of the original. Example: {'choices': [{'message': {'role': 'assistant',
    'content': 'Corrected text', 'tool_calls': [...]}}]}
    """

    rewrite: str
    """End-user's suggested text replacement for the generated response.

    This is the user's idea of what the response should have been.
    """

    thumb: ThumbDirection
    """Possible thumb feedback choices."""
