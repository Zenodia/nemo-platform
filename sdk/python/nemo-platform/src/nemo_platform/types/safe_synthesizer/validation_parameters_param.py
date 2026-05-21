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

from typing_extensions import TypedDict

__all__ = ["ValidationParametersParam"]


class ValidationParametersParam(TypedDict, total=False):
    """Configuration for record and sequence validation.

    These parameters control the validation and automatic fixes when going
    from LLM output to tabular data.
    """

    group_by_accept_no_delineator: bool
    """
    Whether to accept completions without both beginning and end of sequence
    delineators as a single sequence.
    """

    group_by_fix_non_unique_value: bool
    """
    Whether to automatically fix non-unique group-by values in a sequence by using
    the first unique value for all records.
    """

    group_by_fix_unordered_records: bool
    """
    Whether to automatically fix unordered records in a sequence by sorting the
    records.
    """

    group_by_ignore_invalid_records: bool
    """
    Whether to ignore invalid records in a sequence and proceed with the valid
    records.
    """
