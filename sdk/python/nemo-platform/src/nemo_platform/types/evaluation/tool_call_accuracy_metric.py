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

__all__ = ["ToolCallAccuracyMetric"]


class ToolCallAccuracyMetric(BaseModel):
    """RAGAS metric for measuring tool call accuracy."""

    id: str

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

    description: Optional[str] = None
    """Human-readable description of the metric."""

    input_template: Optional[Dict[str, object]] = None
    """Optional Jinja template for rendering the input payload for RAGAS evaluation."""

    labels: Optional[Dict[str, str]] = None
    """Labels are key-value pairs that can be used for grouping and filtering."""

    name: Optional[str] = None
    """Entity name within the workspace"""

    project: Optional[str] = None
    """The name of the project associated with this entity."""

    supported_job_types: Optional[List[Literal["online", "offline"]]] = None
    """
    A metric can evaluate model outputs for online evaluations or pre-generated
    outputs for offline evaluations.
    """

    type: Optional[Literal["tool_call_accuracy"]] = None
