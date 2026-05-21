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

from typing import List
from typing_extensions import Literal

from ..._models import BaseModel
from .field_error import FieldError

__all__ = ["ErrorResponse"]


class ErrorResponse(BaseModel):
    detail: str
    """Human-readable error message describing what went wrong."""

    error_code: Literal[
        "METRIC_NOT_FOUND",
        "METRIC_ALREADY_EXISTS",
        "METRIC_NAME_INVALID",
        "METRIC_IMMUTABLE",
        "BENCHMARK_NOT_FOUND",
        "BENCHMARK_ALREADY_EXISTS",
        "BENCHMARK_IMMUTABLE",
    ]
    """Machine-readable error code."""

    field_errors: List[FieldError]
    """Validation errors for specific fields."""

    suggestions: List[str]
    """Actionable suggestions on how to resolve the error."""
