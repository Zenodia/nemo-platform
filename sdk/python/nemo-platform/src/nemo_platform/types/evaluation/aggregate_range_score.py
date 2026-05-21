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
from typing_extensions import Literal

from ..._models import BaseModel
from .histogram import Histogram
from .percentiles import Percentiles

__all__ = ["AggregateRangeScore"]


class AggregateRangeScore(BaseModel):
    """Aggregated statistics for a range-type score with percentiles and histogram."""

    count: int
    """Number of samples evaluated (excluding NaN)."""

    name: str
    """Name of the score."""

    nan_count: int
    """Number of samples that produced NaN scores."""

    histogram: Optional[Histogram] = None
    """Histogram of score distribution."""

    max: Optional[float] = None
    """Maximum score value."""

    mean: Optional[float] = None
    """Mean score value."""

    min: Optional[float] = None
    """Minimum score value."""

    percentiles: Optional[Percentiles] = None
    """Percentile distribution of scores."""

    score_type: Optional[Literal["range"]] = None
    """Type of score."""

    std_dev: Optional[float] = None
    """Standard deviation of the scores."""

    sum: Optional[float] = None
    """Sum of all score values."""

    variance: Optional[float] = None
    """Variance of the scores."""
