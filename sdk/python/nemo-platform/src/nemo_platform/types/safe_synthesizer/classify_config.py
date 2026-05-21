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

from typing import List, Optional

from ..._models import BaseModel

__all__ = ["ClassifyConfig"]


class ClassifyConfig(BaseModel):
    """Configuration for column classification using an LLM."""

    classify_model_provider: Optional[str] = None
    """Name of the model provider in the Inference Gateway for column classification.

    The job compiler will resolve this to the appropriate endpoint URL.
    """

    enable_classify: Optional[bool] = None
    """Enable column classification."""

    entities: Optional[List[str]] = None
    """List of entity types to classify."""

    num_samples: Optional[int] = None
    """Number of column values to sample for classification."""
