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

from ..._models import BaseModel

__all__ = ["Column"]


class Column(BaseModel):
    """
    Rule matcher for selecting columns by name, position, condition, entity, or type.
    """

    condition: Optional[str] = None
    """Column condition."""

    entity: Union[str, List[str], None] = None
    """Column entity match."""

    name: Optional[str] = None
    """Column name."""

    position: Union[int, List[int], None] = None
    """Column position."""

    type: Union[str, List[str], None] = None
    """Column type match."""

    value: Optional[str] = None
    """Rename to value."""
