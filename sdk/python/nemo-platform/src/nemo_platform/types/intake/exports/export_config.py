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

from typing import Dict, Optional

from ...._models import BaseModel

__all__ = ["ExportConfig"]


class ExportConfig(BaseModel):
    """Configuration for an export job.

    Defines what entries to export and how to format them.
    """

    filters: Optional[Dict[str, object]] = None
    """
    Filter criteria for selecting entries (workspace, app, task, thread_id,
    external_id, has_thumb, has_rating, longest_per_thread, model, etc.)
    """

    format_options: Optional[Dict[str, object]] = None
    """Format options for the export (e.g., row_transformation)"""

    limit: Optional[int] = None
    """Maximum number of entries to export. None means no limit."""

    search: Optional[Dict[str, object]] = None
    """Search criteria for finding entries"""
