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

from typing import Dict
from typing_extensions import TypedDict

__all__ = ["FieldMappingParam"]


class FieldMappingParam(TypedDict, total=False):
    """
    Maps canonical evaluator fields to raw dataset column paths.
    Example: {'input': 'question', 'output': 'answer', 'reference': 'gold', 'trajectory': 'steps'}
    """

    context: str
    """Binding for the canonical 'context' evaluator field."""

    custom: Dict[str, str]
    """Additional evaluator field bindings keyed by canonical field name."""

    input: str
    """Binding for the canonical 'input' evaluator field."""

    messages: str
    """Binding for the canonical 'messages' evaluator field."""

    output: str
    """Binding for the canonical 'output' evaluator field."""

    reference: str
    """Binding for the canonical 'reference' evaluator field."""

    tool_calls: str
    """Binding for the canonical 'tool_calls' evaluator field."""

    tools: str
    """Binding for the canonical 'tools' evaluator field."""

    trajectory: str
    """Binding for the canonical 'trajectory' evaluator field."""
