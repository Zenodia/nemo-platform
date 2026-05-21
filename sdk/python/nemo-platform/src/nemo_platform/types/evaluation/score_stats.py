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

from typing import List, Union, Optional

from ..._models import BaseModel
from .rubric_score_stat import RubricScoreStat

__all__ = ["ScoreStats"]


class ScoreStats(BaseModel):
    """Stats for a score.

    Fields that are NaN are serialized as the string "NaN" in the API response.
    """

    count: Optional[int] = None
    """The number of values used for computing the score."""

    max: Union[float, str, None] = None
    """The maximum of all values used for computing the score."""

    mean: Union[float, str, None] = None
    """The mean of all values used for computing the score."""

    min: Union[float, str, None] = None
    """The minimum of all values used for computing the score."""

    nan_count: Optional[int] = None
    """
    The number of values that are not a number (NaN) and are excluded from the score
    stats calculations.
    """

    rubric_distribution: Optional[List[RubricScoreStat]] = None
    """The distribution of the rubric grading criteria for the score."""

    stddev: Union[float, str, None] = None
    """The population standard deviation, (note: not the sample standard deviation)."""

    stderr: Union[float, str, None] = None
    """The standard error."""

    sum: Union[float, str, None] = None
    """The sum of all values used for computing the score."""

    sum_squared: Union[float, str, None] = None
    """The sum of the square of all values used for computing the score."""

    variance: Union[float, str, None] = None
    """The population variance, (note: not the sample variance)."""
