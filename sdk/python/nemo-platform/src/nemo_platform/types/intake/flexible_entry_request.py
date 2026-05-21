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

from typing import TYPE_CHECKING, Dict, List

from pydantic import Field as FieldInfo

from ..._models import BaseModel
from .flexible_message import FlexibleMessage

__all__ = ["FlexibleEntryRequest"]


class FlexibleEntryRequest(BaseModel):
    """Flexible entry request that accepts any object shape.

    This flexibility enables the Intake service to store requests from various LLM providers
    (OpenAI, Anthropic, NIM, etc.) and future model types (embeddings, multimodal, etc.)
    without requiring schema updates.

    Required fields: `messages` and `model`
    Common optional fields: `temperature`, `max_tokens`, `top_p`, `tools`, `tool_choice`,
    `stream`, `response_format`, etc.
    """

    messages: List[FlexibleMessage]
    """A list of messages comprising the conversation.

    Each message must have a valid role. Additional fields like `content`,
    `tool_calls`, etc. are provider-specific.
    """

    model: str
    """
    The model identifier used for this request (e.g., 'gpt-4', 'llama-3-70b',
    'claude-3-opus').
    """

    if TYPE_CHECKING:
        # Some versions of Pydantic <2.8.0 have a bug and don’t allow assigning a
        # value to this field, so for compatibility we avoid doing it at runtime.
        __pydantic_extra__: Dict[str, object] = FieldInfo(init=False)  # pyright: ignore[reportIncompatibleVariableOverride]

        # Stub to indicate that arbitrary properties are accepted.
        # To access properties that are not valid identifiers you can use `getattr`, e.g.
        # `getattr(obj, '$type')`
        def __getattr__(self, attr: str) -> object: ...
    else:
        __pydantic_extra__: Dict[str, object]
