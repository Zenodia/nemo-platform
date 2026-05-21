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

__all__ = ["Row"]


class Row(BaseModel):
    """Rule matcher for selecting rows by name, condition, entity, or type."""

    condition: Optional[str] = None
    """Row condition match."""

    description: Optional[str] = None
    """Rule description for human consumption."""

    entity: Union[str, List[str], None] = None
    """Row entity match."""

    fallback_value: Optional[str] = None
    """Row fallback value."""

    foreach: Optional[str] = None
    """Foreach expression."""

    name: Union[str, List[str], None] = None
    """Row name."""

    type: Union[str, List[str], None] = None
    """Row type match."""

    value: Optional[str] = None
    """Row value definition."""
