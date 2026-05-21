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

from typing import Dict, Union, Optional

from ..._models import BaseModel
from .thumb_direction import ThumbDirection

__all__ = ["UserRating"]


class UserRating(BaseModel):
    """User's rating/evaluation of an AI response.

    This captures various forms of end-user feedback about a model's response, including
    binary thumbs up/down ratings, numeric scores, free-text opinions, suggested rewrites,
    and structured category ratings.

    Either `thumb` or `rating` should be provided (they are mutually exclusive), but all
    fields are optional to accommodate different feedback collection patterns.
    """

    categories: Optional[Dict[str, Union[float, str]]] = None
    """Application-specific category ratings as key-value pairs.

    Use this for custom rating dimensions (e.g., {'helpfulness': 4, 'accuracy': 5,
    'tone': 'professional'}). Useful for radio buttons, dropdowns, or
    multi-dimensional rating systems.
    """

    chosen_index: Optional[int] = None
    """
    Zero-based index of the response option the user selected when multiple
    responses were returned. Use this when showing users multiple completion choices
    and tracking which one they picked.
    """

    opinion: Optional[str] = None
    """Free-text comment from the end user describing their opinion of the response."""

    rating: Optional[float] = None
    """Numeric rating (e.g., 1-5 stars) provided by the end user.

    Mutually exclusive with `thumb`. Use this for star ratings or numeric scales.
    """

    rewrite: Optional[str] = None
    """End-user's suggested text replacement for the generated response.

    This is the user's idea of what the response should have been.
    """

    thumb: Optional[ThumbDirection] = None
    """Possible thumb feedback choices."""
