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

from typing import Dict
from typing_extensions import Required, TypedDict

from ..._types import SequenceNotStr
from .metric_ref import MetricRef
from .fileset_ref import FilesetRef
from .field_mapping_param import FieldMappingParam

__all__ = ["BenchmarkCreateParams"]


class BenchmarkCreateParams(TypedDict, total=False):
    workspace: str

    dataset: Required[FilesetRef]
    """Reference to a Fileset in the Files API.

    A reference is a string with format 'workspace/fileset-name' that points to a
    persisted fileset entity. When used as a dataset source, all files within the
    fileset will be downloaded to the job container.

    See [Entity references](docs/get-started/concepts/entity-references.md) for the
    general entity reference pattern used across the platform.
    """

    description: Required[str]
    """The description of the benchmark."""

    metrics: Required[SequenceNotStr[MetricRef]]
    """The metrics that comprise this benchmark (format: workspace/metric_name)."""

    name: Required[str]
    """The name of the benchmark."""

    extended_response: bool
    """Whether to return the extended benchmark."""

    field_mapping: FieldMappingParam
    """
    Maps canonical evaluator fields to raw dataset column paths. Example: {'input':
    'question', 'output': 'answer', 'reference': 'gold', 'trajectory': 'steps'}
    """

    labels: Dict[str, str]
    """Labels are key-value pairs that can be used for grouping and filtering."""
