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

from ..._models import BaseModel

__all__ = ["Percentiles"]


class Percentiles(BaseModel):
    """Percentile distribution of scores."""

    p10: float
    """10th percentile."""

    p100: float
    """100th percentile."""

    p20: float
    """20th percentile."""

    p30: float
    """30th percentile."""

    p40: float
    """40th percentile."""

    p50: float
    """50th percentile (median)."""

    p60: float
    """60th percentile."""

    p70: float
    """70th percentile."""

    p80: float
    """80th percentile."""

    p90: float
    """90th percentile."""
