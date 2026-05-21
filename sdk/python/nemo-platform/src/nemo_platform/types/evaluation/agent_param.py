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
from typing_extensions import Literal, Required, TypedDict

from ..files.secret_ref import SecretRef

__all__ = ["AgentParam"]


class AgentParam(TypedDict, total=False):
    """Agent definition for inference in online evaluation jobs.

    An agent is an endpoint that accepts a request and returns a response,
    potentially with a trajectory. Two formats are supported:

    - ``generic``: configurable HTTP POST with Jinja-templated body and
      JSONPath extraction for response and trajectory.
    - ``nemo_agent_toolkit``: NeMo Agent Toolkit SSE streaming protocol
      (``/generate/full?filter_steps=none``).
    """

    name: Required[str]
    """Agent name / identifier."""

    url: Required[str]
    """Base URL of the agent endpoint."""

    api_key_secret: SecretRef
    """Reference to a secret.

    Format: 'secret_name' (uses request workspace) or 'workspace/secret_name'
    (explicit workspace).
    """

    body: Dict[str, object]
    """Jinja template for the request payload. Required for generic agents."""

    format: Literal["generic", "nemo_agent_toolkit"]
    """Agent format that determines the execution path."""

    response_path: str
    """JSONPath expression to extract the response text from the agent's response body.

    Required for generic agents.
    """

    trajectory_path: str
    """JSONPath expression to extract the trajectory from the agent's response body.

    Optional.
    """
