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

from ...._models import BaseModel
from .job_status import JobStatus
from .export_config import ExportConfig
from .export_status_details import ExportStatusDetails

__all__ = ["ExportJob"]


class ExportJob(BaseModel):
    """Export job tracking entry exports to external datastores.

    Export jobs track the status of background export tasks.
    """

    id: str

    config: ExportConfig
    """Configuration for an export job.

    Defines what entries to export and how to format them.
    """

    created_at: datetime

    created_by: Optional[str] = None

    entity_id: str
    """Alias for id for backwards compatibility."""

    parent: str
    """Parent entity ID for nested entities."""

    updated_at: datetime

    updated_by: Optional[str] = None

    workspace: str
    """Workspace identifier"""

    name: Optional[str] = None
    """Entity name within the workspace"""

    output_file_url: Optional[str] = None
    """
    The place where the exported file should be written (file://, hf://, nds://,
    etc.)
    """

    project: Optional[str] = None
    """The name of the project associated with this entity."""

    status: Optional[JobStatus] = None
    """Job status enum."""

    status_details: Optional[ExportStatusDetails] = None
    """Detailed status information for an export job."""
