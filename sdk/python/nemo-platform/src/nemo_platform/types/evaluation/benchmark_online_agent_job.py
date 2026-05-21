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

from typing import Dict, List, Union, Optional

from .agent import Agent
from ..._models import BaseModel
from .benchmark_ref import BenchmarkRef
from .run_config_online import RunConfigOnline

__all__ = ["BenchmarkOnlineAgentJob"]


class BenchmarkOnlineAgentJob(BaseModel):
    """Input for an online benchmark evaluation job targeting an agent.

    Evaluates an agent by prompting it with the benchmark's dataset and then evaluating
    the responses against all metrics in the benchmark.
    """

    agent: Agent
    """Agent definition for inference in online evaluation jobs.

    An agent is an endpoint that accepts a request and returns a response,
    potentially with a trajectory. Two formats are supported:

    - `generic`: configurable HTTP POST with Jinja-templated body and JSONPath
      extraction for response and trajectory.
    - `nemo_agent_toolkit`: NeMo Agent Toolkit SSE streaming protocol
      (`/generate/full?filter_steps=none`).
    """

    benchmark: BenchmarkRef
    """Reference to a benchmark in the Benchmarks API.

    A reference is a string with format 'workspace/benchmark-name' that points to a
    persisted benchmark entity. See
    [Entity references](docs/get-started/concepts/entity-references.md) for the
    general entity reference pattern used across the platform.
    """

    prompt_template: Union[str, Dict[str, object]]
    """The jinja template to prompt the agent for evaluation.

    Can be either a simple string or a structured object (e.g., OpenAI messages
    format). Use Jinja template variables like {{input}}, {{output}}, {{context}},
    {{reference}} to reference input columns.
    """

    optional_fields: Optional[List[str]] = None
    """
    Prompt template fields that should remain available to the prompt template but
    not be required by dataset schema validation.
    """

    params: Optional[RunConfigOnline] = None
    """Job parameters for online evaluation."""
