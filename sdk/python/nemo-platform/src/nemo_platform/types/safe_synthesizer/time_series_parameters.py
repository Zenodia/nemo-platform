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

from typing import Union, Optional

from ..._models import BaseModel

__all__ = ["TimeSeriesParameters"]


class TimeSeriesParameters(BaseModel):
    """Configuration for time-series mode in the Safe Synthesizer pipeline.

    Controls whether a dataset is treated as time-series data, including
    timestamp column selection, interval inference, and format validation.
    The time-series pipeline is currently experimental.
    """

    is_timeseries: Optional[bool] = None
    """Whether to treat the dataset as time series.

    When enabled, either `timestamp_column` or `timestamp_interval_seconds` is
    required. For grouped time series, `group_training_examples_by` needs to be set.
    """

    start_timestamp: Union[str, int, None] = None
    """Start timestamp.

    If not provided, the first timestamp in the timestamp column will be used.
    """

    stop_timestamp: Union[str, int, None] = None
    """Stop timestamp.

    If not provided, the last timestamp in the timestamp column will be used.
    """

    timestamp_column: Optional[str] = None
    """
    Name of the column containing timestamps used to order records when
    `is_timeseries` is `True`. Required only when `is_timeseries` is `True` and
    `timestamp_interval_seconds` is not provided.
    """

    timestamp_format: Optional[str] = None
    """Format of the timestamp column.

    Accepts either: (1) Python strftime format codes for string timestamps (e.g.,
    '%Y-%m-%d %H:%M:%S', '%m/%d/%Y'), or (2) 'elapsed_seconds' for numeric
    (int/float) timestamps representing seconds as an increasing counter (e.g., 0,
    60, 120 for 1-minute intervals). If not provided, the format will be inferred
    from the data.
    """

    timestamp_interval_seconds: Optional[int] = None
    """Interval in seconds between timestamps.

    If not provided, the timestamp column will be used to infer the interval.
    """
