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
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["NumberCheckMetricParam"]


class NumberCheckMetricParam(BaseModel):
    """Request type for NumberCheckMetric.

    Numeric-comparison metric with template-driven operands.
    """

    left_template: str
    """
    The template to use for rendering the left value of the operator to compute the
    metric.
    """

    operation: Literal[
        "equals",
        "==",
        "!=",
        "<>",
        "not equals",
        ">=",
        "gte",
        "greater than or equal",
        ">",
        "gt",
        "greater than",
        "<=",
        "lte",
        "less than or equal",
        "<",
        "lt",
        "less than",
        "absolute difference",
    ]
    """The operation to compute for the metric."""

    right_template: str
    """
    The template to use for rendering the right value of the operator to compute the
    metric.
    """

    description: Optional[str] = None
    """Human-readable description of the metric."""

    epsilon: Optional[float] = None
    """Specify the tolerance for the absolute difference of values."""

    labels: Optional[Dict[str, str]] = None
    """Labels are key-value pairs that can be used for grouping and filtering."""

    supported_job_types: Optional[List[Literal["online", "offline"]]] = None
    """
    A metric can evaluate model outputs for online evaluations or pre-generated
    outputs for offline evaluations.
    """

    type: Optional[Literal["number-check"]] = None
