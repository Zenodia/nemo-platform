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

from typing import Dict, Optional

from ..._models import BaseModel

__all__ = ["MetricEvaluationRowScore"]


class MetricEvaluationRowScore(BaseModel):
    """Result for a single evaluated row.

    Contains either scores (on success) or error (on failure), facilitating
    easy manipulation where each row represents one evaluation.
    """

    index: int
    """Position of this row in the original input dataset (0-based)."""

    row: Dict[str, object]
    """The original dataset row."""

    error: Optional[str] = None
    """Error message if evaluation failed. Null if evaluation succeeded."""

    scores: Optional[Dict[str, float]] = None
    """Score name to value mapping for this row.

    Non-finite values are serialized as null. Null if evaluation failed.
    """
