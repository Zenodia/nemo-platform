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

from .job_status import JobStatus
from ...shared_params.datetime_filter import DatetimeFilter

__all__ = ["ExportJobFilterParam"]


class ExportJobFilterParam(TypedDict, total=False):
    """Filter for ExportJobs."""

    id: str
    """Filter by export job ID."""

    created_at: DatetimeFilter
    """Filter entities based on creation date."""

    name: str
    """Filter by export job name."""

    output_file_url: str
    """Filter by output file URL."""

    status: JobStatus
    """Job status enum."""

    updated_at: DatetimeFilter
    """Filter entities based on update date."""

    workspace: str
    """Filter by workspace id."""
