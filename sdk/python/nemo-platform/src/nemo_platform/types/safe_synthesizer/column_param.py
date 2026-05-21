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
from typing_extensions import TypedDict

from ..._types import SequenceNotStr

__all__ = ["ColumnParam"]


class ColumnParam(TypedDict, total=False):
    """
    Rule matcher for selecting columns by name, position, condition, entity, or type.
    """

    condition: str
    """Column condition."""

    entity: Union[str, SequenceNotStr[str]]
    """Column entity match."""

    name: str
    """Column name."""

    position: Union[int, Iterable[int]]
    """Column position."""

    type: Union[str, SequenceNotStr[str]]
    """Column type match."""

    value: str
    """Rename to value."""
