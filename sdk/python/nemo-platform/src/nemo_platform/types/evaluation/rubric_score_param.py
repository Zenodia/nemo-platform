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

from typing import Union, Iterable
from typing_extensions import Required, TypeAlias, TypedDict

from .rubric_param import RubricParam
from .json_score_parser_param import JsonScoreParserParam
from .regex_score_parser_param import RegexScoreParserParam

__all__ = ["RubricScoreParam", "Parser"]

Parser: TypeAlias = Union[JsonScoreParserParam, RegexScoreParserParam]


class RubricScoreParam(TypedDict, total=False):
    """Score definition for a rubric with optional parser.

    If no parser is set, JSONScoreParser is the default parser inferred from the score parameters
    """

    name: Required[str]
    """The name of the score.

    Only lowercase letters, numbers, and underscores allowed.
    """

    rubric: Required[Iterable[RubricParam]]
    """The rubric for the score."""

    description: str
    """Human-readable description of the score."""

    parser: Parser
    """The method to parse the score.

    When used with llm-judge metric, and no parser is set, JSONScoreParser is the
    default parser inferred from the score parameters.
    """
