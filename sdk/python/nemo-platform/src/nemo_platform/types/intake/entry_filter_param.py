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
from typing_extensions import TypedDict

from .entry_context_filter_param import EntryContextFilterParam
from ..shared_params.datetime_filter import DatetimeFilter
from .entry_user_rating_filter_param import EntryUserRatingFilterParam

__all__ = ["EntryFilterParam"]


class EntryFilterParam(TypedDict, total=False):
    """Filter for Entries."""

    id: Union[str, Dict[str, object]]
    """Filter by entry ID.

    Supports operators like {'in': ['entry-ABC', 'entry-XYZ']} for multiple IDs.
    """

    context: EntryContextFilterParam
    """Filter for entry context fields."""

    created_at: DatetimeFilter
    """Filter entities based on creation date."""

    external_id: Union[str, Dict[str, object]]
    """Filter by external ID.

    Supports operators like {'in': ['id1', 'id2']} for multiple IDs.
    """

    has_events: bool
    """Filter by presence of any events."""

    has_opinion: bool
    """Filter by presence of opinion."""

    has_rating: bool
    """Filter by presence of rating."""

    has_rewrite: bool
    """Filter by presence of rewrite."""

    has_thumb: bool
    """Filter by presence of thumb feedback."""

    longest_per_thread: bool
    """If true, return only the longest entry per thread (based on message count)."""

    model: str
    """
    Filter by the served model recorded in usage (e.g., 'gpt-4o',
    'meta/llama-3.1-70b-instruct').
    """

    project: str
    """Filter by project name."""

    updated_at: DatetimeFilter
    """Filter entities based on update date."""

    user_rating: EntryUserRatingFilterParam
    """Filter for entry user rating fields."""

    workspace: str
    """Filter by workspace id."""
