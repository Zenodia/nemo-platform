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
from typing_extensions import TypeAlias

from .rubric import Rubric
from ..._models import BaseModel
from .json_score_parser import JsonScoreParser
from .regex_score_parser import RegexScoreParser

__all__ = ["RubricScore", "Parser"]

Parser: TypeAlias = Union[JsonScoreParser, RegexScoreParser]


class RubricScore(BaseModel):
    """Score definition for a rubric with optional parser.

    If no parser is set, JSONScoreParser is the default parser inferred from the score parameters
    """

    name: str
    """The name of the score.

    Only lowercase letters, numbers, and underscores allowed.
    """

    rubric: List[Rubric]
    """The rubric for the score."""

    description: Optional[str] = None
    """Human-readable description of the score."""

    parser: Optional[Parser] = None
    """The method to parse the score.

    When used with llm-judge metric, and no parser is set, JSONScoreParser is the
    default parser inferred from the score parameters.
    """
