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
from typing_extensions import TypeAlias

from ..._models import BaseModel
from .model_ref import ModelRef
from .metric_ref import MetricRef
from .fileset_ref import FilesetRef
from .aggregate_range_score import AggregateRangeScore
from .aggregate_rubric_score import AggregateRubricScore

__all__ = ["MetricJobResult", "Score"]

Score: TypeAlias = Union[AggregateRangeScore, AggregateRubricScore]


class MetricJobResult(BaseModel):
    """Response type for metric job result."""

    id: str

    created_at: datetime

    created_by: Optional[str] = None

    entity_id: str
    """Alias for id for backwards compatibility."""

    parent: str
    """Parent entity ID for nested entities."""

    scores: List[Score]
    """The list of aggregated scores."""

    updated_at: datetime

    updated_by: Optional[str] = None

    workspace: str
    """Workspace identifier"""

    dataset: Optional[FilesetRef] = None
    """Reference to a Fileset in the Files API.

    A reference is a string with format 'workspace/fileset-name' that points to a
    persisted fileset entity. When used as a dataset source, all files within the
    fileset will be downloaded to the job container.

    See [Entity references](docs/get-started/concepts/entity-references.md) for the
    general entity reference pattern used across the platform.
    """

    labels: Optional[Dict[str, str]] = None
    """Labels are key-value pairs that can be used for grouping and filtering."""

    metric: Optional[MetricRef] = None
    """Reference to a metric in the Metrics API.

    A reference is a string with format 'workspace/metric-name' that points to a
    persisted metric entity. See
    [Entity references](docs/get-started/concepts/entity-references.md) for the
    general entity reference pattern used across the platform.
    """

    model: Optional[ModelRef] = None
    """Reference to a Model in the Models API.

    See [Entity references](docs/get-started/concepts/entity-references.md) for the
    general entity reference pattern used across the platform.
    """

    name: Optional[str] = None
    """Entity name within the workspace"""

    project: Optional[str] = None
    """The name of the project associated with this entity."""
