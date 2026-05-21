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

from typing_extensions import TypedDict

__all__ = ["RunConfigOnlineParam"]


class RunConfigOnlineParam(TypedDict, total=False):
    """Job parameters for online evaluation."""

    ignore_request_failure: bool
    """If True, request failures will be ignored and the result will be marked as NaN.

    If False (default), request failures will raise an exception.
    """

    limit_samples: int
    """
    Limit number of evaluation samples, taking the first `limit` samples from the
    dataset.
    """

    max_retries: int
    """Maximum number of retries for failed requests."""

    parallelism: int
    """Parallelism to be used for the evaluation job.

    Typically, this represents the maximum number of concurrent requests made to the
    model.
    """

    request_timeout: int
    """The timeout to be used for requests made to the model."""
