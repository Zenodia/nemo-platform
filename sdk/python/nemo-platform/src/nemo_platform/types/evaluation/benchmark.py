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

from ..._models import BaseModel
from .metric_ref import MetricRef
from .fileset_ref import FilesetRef
from .field_mapping import FieldMapping

__all__ = ["Benchmark"]


class Benchmark(BaseModel):
    """Benchmark response schema."""

    id: str

    created_at: datetime

    created_by: Optional[str] = None

    dataset: FilesetRef
    """Reference to a Fileset in the Files API.

    A reference is a string with format 'workspace/fileset-name' that points to a
    persisted fileset entity. When used as a dataset source, all files within the
    fileset will be downloaded to the job container.

    See [Entity references](docs/get-started/concepts/entity-references.md) for the
    general entity reference pattern used across the platform.
    """

    entity_id: str
    """Alias for id for backwards compatibility."""

    metrics: List[MetricRef]
    """The metrics that comprise this benchmark (format: workspace/metric_name)."""

    name: str
    """Benchmark name"""

    parent: str
    """Parent entity ID for nested entities."""

    updated_at: datetime

    updated_by: Optional[str] = None

    workspace: str
    """Workspace identifier"""

    description: Optional[str] = None
    """Human-readable description of the benchmark."""

    field_mapping: Optional[FieldMapping] = None
    """
    Maps canonical evaluator fields to raw dataset column paths. Example: {'input':
    'question', 'output': 'answer', 'reference': 'gold', 'trajectory': 'steps'}
    """

    labels: Optional[Dict[str, str]] = None
    """Labels are key-value pairs that can be used for grouping and filtering."""

    project: Optional[str] = None
    """The name of the project associated with this entity."""
