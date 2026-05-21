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

from typing import Union
from datetime import datetime
from typing_extensions import Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["UsageParam"]


class UsageParam(TypedDict, total=False):
    """Structured usage metrics captured at log time.

    Every field is optional so producers can populate whatever they have without
    schema breakage. Stored as the entry-level ``usage`` field so filters can
    reach it via ``data.usage.<field>`` entity-store paths.
    """

    cached_tokens: int
    """Number of input tokens served from a prompt cache (subset of input_tokens)."""

    cost_input_usd: float
    """Estimated cost attributed to input tokens, in USD."""

    cost_output_usd: float
    """Estimated cost attributed to output tokens, in USD."""

    cost_usd: float
    """Total estimated cost of this call, in USD."""

    ended_at: Annotated[Union[str, datetime], PropertyInfo(format="iso8601")]
    """UTC timestamp when the upstream LLM call ended."""

    input_tokens: int
    """Number of input tokens consumed."""

    latency_ms: int
    """Wall-clock latency of the upstream LLM call, in milliseconds."""

    model: str
    """The actual model that served the request (after any routing).

    May differ from the model in the request body.
    """

    output_tokens: int
    """Number of output tokens produced."""

    started_at: Annotated[Union[str, datetime], PropertyInfo(format="iso8601")]
    """UTC timestamp when the upstream LLM call started."""
