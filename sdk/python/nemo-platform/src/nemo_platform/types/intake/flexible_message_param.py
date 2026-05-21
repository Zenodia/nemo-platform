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

from typing_extensions import Required, TypedDict

from .message_role import MessageRole

__all__ = ["FlexibleMessageParam"]


class FlexibleMessageParam(TypedDict, total=False, extra_items=object):  # type: ignore[call-arg]
    """
    A flexible message model that requires a valid role field but allows any other fields.

    This flexibility enables the Intake service to store messages from various LLM providers
    and future model types without requiring schema updates. Additional fields like `content`,
    `name`, `tool_calls`, `tool_call_id`, etc. are all accepted.

    Examples of additional fields:
    - `content`: The message text or content
    - `name`: Name of the user or function
    - `tool_calls`: Tool/function calls in the message
    - `tool_call_id`: ID of the tool call being responded to
    """

    role: Required[MessageRole]
    """Valid role values for entry request messages."""
