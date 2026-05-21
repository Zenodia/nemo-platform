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

from typing import Iterable
from typing_extensions import Required, TypedDict

from .flexible_message_param import FlexibleMessageParam

__all__ = ["FlexibleEntryRequestParam"]


class FlexibleEntryRequestParam(TypedDict, total=False, extra_items=object):  # type: ignore[call-arg]
    """Flexible entry request that accepts any object shape.

    This flexibility enables the Intake service to store requests from various LLM providers
    (OpenAI, Anthropic, NIM, etc.) and future model types (embeddings, multimodal, etc.)
    without requiring schema updates.

    Required fields: `messages` and `model`
    Common optional fields: `temperature`, `max_tokens`, `top_p`, `tools`, `tool_choice`,
    `stream`, `response_format`, etc.
    """

    messages: Required[Iterable[FlexibleMessageParam]]
    """A list of messages comprising the conversation.

    Each message must have a valid role. Additional fields like `content`,
    `tool_calls`, etc. are provider-specific.
    """

    model: Required[str]
    """
    The model identifier used for this request (e.g., 'gpt-4', 'llama-3-70b',
    'claude-3-opus').
    """
