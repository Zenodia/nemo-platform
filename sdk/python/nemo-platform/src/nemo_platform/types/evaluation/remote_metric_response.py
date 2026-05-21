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

from typing import Dict, List, Optional
from datetime import datetime
from typing_extensions import Literal

from ..._models import BaseModel
from .remote_score import RemoteScore
from ..files.secret_ref import SecretRef

__all__ = ["RemoteMetricResponse"]


class RemoteMetricResponse(BaseModel):
    """Response type for RemoteMetric."""

    body: Dict[str, object]
    """Jinja template for request payload"""

    scores: List[RemoteScore]
    """List of scores to extract from the remote response"""

    url: str
    """The URL of the remote endpoint."""

    id: Optional[str] = None
    """Entity name within the workspace"""

    api_key_secret: Optional[SecretRef] = None
    """Reference to a secret.

    Format: 'secret_name' (uses request workspace) or 'workspace/secret_name'
    (explicit workspace).
    """

    created_at: Optional[datetime] = None

    description: Optional[str] = None
    """Human-readable description of the metric."""

    labels: Optional[Dict[str, str]] = None
    """Labels are key-value pairs that can be used for grouping and filtering."""

    max_retries: Optional[int] = None
    """Maximum number of retry attempts."""

    name: Optional[str] = None
    """Entity name within the workspace"""

    parent: Optional[str] = None

    project: Optional[str] = None
    """The name of the project associated with this entity."""

    supported_job_types: Optional[List[Literal["online", "offline"]]] = None
    """
    A metric can evaluate model outputs for online evaluations or pre-generated
    outputs for offline evaluations.
    """

    timeout_seconds: Optional[float] = None
    """Request timeout in seconds."""

    type: Optional[Literal["remote"]] = None

    updated_at: Optional[datetime] = None

    workspace: Optional[str] = None
    """Workspace identifier"""
