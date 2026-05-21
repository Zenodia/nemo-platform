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

from typing import Dict, List, Iterable
from typing_extensions import Literal, TypedDict

from .parameter_param import ParameterParam

__all__ = ["SystemMetricParamParam"]


class SystemMetricParamParam(TypedDict, total=False):
    """Metric entity for system metric that have pre-defined dataset."""

    description: str
    """Human-readable description of the metric."""

    labels: Dict[str, str]
    """Labels are key-value pairs that can be used for grouping and filtering."""

    name: str

    optional_params: Iterable[ParameterParam]
    """List of optional parameters for running an evaluation with the metric."""

    required_params: Iterable[ParameterParam]
    """List of required parameters for running an evaluation with the metric."""

    supported_job_types: List[Literal["online", "offline", "retriever"]]
    """
    A metric can evaluate model outputs for online evaluations or pre-generated
    outputs for offline evaluations.
    """

    type: Literal["system", "system-retriever"]
