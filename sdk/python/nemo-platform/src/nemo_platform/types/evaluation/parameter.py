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
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["Parameter"]


class Parameter(BaseModel):
    name: str
    """Name of the parameter."""

    type: Literal["boolean", "string", "number", "integer", "object", "secret"]
    """The value type of the parameter."""

    default: Union[bool, str, float, None] = None
    """The default value of the parameter."""

    description: Optional[str] = None
    """Description of the parameter."""

    schema_: Optional[Dict[str, object]] = FieldInfo(alias="schema", default=None)
    """The JSON schema for parameters with object type."""
