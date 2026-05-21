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

from typing import Optional
from datetime import datetime

from ..._models import BaseModel

__all__ = ["Usage"]


class Usage(BaseModel):
    """Structured usage metrics captured at log time.

    Every field is optional so producers can populate whatever they have without
    schema breakage. Stored as the entry-level ``usage`` field so filters can
    reach it via ``data.usage.<field>`` entity-store paths.
    """

    cached_tokens: Optional[int] = None
    """Number of input tokens served from a prompt cache (subset of input_tokens)."""

    cost_input_usd: Optional[float] = None
    """Estimated cost attributed to input tokens, in USD."""

    cost_output_usd: Optional[float] = None
    """Estimated cost attributed to output tokens, in USD."""

    cost_usd: Optional[float] = None
    """Total estimated cost of this call, in USD."""

    ended_at: Optional[datetime] = None
    """UTC timestamp when the upstream LLM call ended."""

    input_tokens: Optional[int] = None
    """Number of input tokens consumed."""

    latency_ms: Optional[int] = None
    """Wall-clock latency of the upstream LLM call, in milliseconds."""

    model: Optional[str] = None
    """The actual model that served the request (after any routing).

    May differ from the model in the request body.
    """

    output_tokens: Optional[int] = None
    """Number of output tokens produced."""

    started_at: Optional[datetime] = None
    """UTC timestamp when the upstream LLM call started."""
