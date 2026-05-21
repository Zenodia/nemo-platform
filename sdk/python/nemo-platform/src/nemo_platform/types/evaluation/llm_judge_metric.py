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
from datetime import datetime
from typing_extensions import Literal, TypeAlias

from .model import Model
from ..._models import BaseModel
from .range_score import RangeScore
from .rubric_score import RubricScore
from .inference_params import InferenceParams
from .reasoning_params import ReasoningParams

__all__ = ["LLMJudgeMetric", "Score"]

Score: TypeAlias = Union[RubricScore, RangeScore]


class LLMJudgeMetric(BaseModel):
    """Persisted LLM-as-a-Judge metric."""

    id: str

    created_at: datetime

    created_by: Optional[str] = None

    entity_id: str
    """Alias for id for backwards compatibility."""

    model: Model
    """Model definition for use without persisting to the Models API."""

    parent: str
    """Parent entity ID for nested entities."""

    scores: List[Score]
    """Definitions of scores that will be extracted from the judge's output."""

    updated_at: datetime

    updated_by: Optional[str] = None

    workspace: str
    """Workspace identifier"""

    description: Optional[str] = None
    """Human-readable description of the metric."""

    ignore_request_failure: Optional[bool] = None
    """If True, request failures will be ignored and the result will be marked as NaN.

    If False (default), request failures will raise an exception.
    """

    inference: Optional[InferenceParams] = None
    """Parameters for model inference.

    Extra fields can be supplied for additional options applied to the inference
    request directly. Fields not supported by the model may cause inference errors
    during evaluation.
    """

    labels: Optional[Dict[str, str]] = None
    """Labels are key-value pairs that can be used for grouping and filtering."""

    name: Optional[str] = None
    """Entity name within the workspace"""

    optional_fields: Optional[List[str]] = None
    """
    Prompt template fields that should remain in the inferred input schema but not
    be required. Use this for fields like 'reference' when the metric can still run
    without them.
    """

    project: Optional[str] = None
    """The name of the project associated with this entity."""

    prompt_template: Union[str, Dict[str, object], None] = None
    """The prompt template for the judge.

    Can be either a simple string or a structured object (e.g., OpenAI messages
    format). Use Jinja template variables like {{sample.output_text}} to use the
    model output within the template or {{item.xxx}} to reference input columns from
    the dataset.
    """

    reasoning: Optional[ReasoningParams] = None
    """Custom settings that control the model's reasoning behavior."""

    structured_output: Optional[Dict[str, object]] = None
    """JSON schema to apply structured output for the judge model evaluation.

    Structured output is derived from scores when omitted. Use this option if there
    are custom requirements for the output of the judge.
    """

    supported_job_types: Optional[List[Literal["online", "offline"]]] = None
    """
    A metric can evaluate model outputs for online evaluations or pre-generated
    outputs for offline evaluations.
    """

    system_prompt: Optional[str] = None
    """
    Initial instructions that define the judge model's role and behavior for the
    conversation. This is prepended to the messages as a system message.
    """

    type: Optional[Literal["llm-judge"]] = None
