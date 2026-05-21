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

from ..._models import BaseModel

__all__ = ["ReasoningParams"]


class ReasoningParams(BaseModel):
    """Custom settings that control the model's reasoning behavior."""

    effort: Optional[str] = None
    """Option for OpenAI models to specify low, medium, or high reasoning effort."""

    end_token: Optional[str] = None
    """
    Configure the end token to trim reasoning context based on the model's reasoning
    API. Example for Nemotron models: '</think>'
    """

    include_if_not_finished: Optional[bool] = None
    """
    Configure whether to include reasoning context if the model has not finished
    reasoning.
    """
