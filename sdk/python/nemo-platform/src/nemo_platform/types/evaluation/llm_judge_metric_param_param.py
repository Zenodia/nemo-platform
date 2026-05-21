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

from typing import Dict, List, Union, Iterable
from typing_extensions import Literal, Required, TypeAlias, TypedDict

from ..._types import SequenceNotStr
from .model_ref import ModelRef
from .model_param import ModelParam
from .range_score_param import RangeScoreParam
from .rubric_score_param import RubricScoreParam
from .inference_params_param import InferenceParamsParam
from .reasoning_params_param import ReasoningParamsParam

__all__ = ["LLMJudgeMetricParamParam", "Model", "Score"]

Model: TypeAlias = Union[ModelParam, ModelRef]

Score: TypeAlias = Union[RubricScoreParam, RangeScoreParam]


class LLMJudgeMetricParamParam(TypedDict, total=False):
    """Request type for creating LLM Judge metrics."""

    model: Required[Model]
    """The model configuration."""

    scores: Required[Iterable[Score]]
    """Definitions of scores that will be extracted from the judge's output."""

    description: str
    """Human-readable description of the metric."""

    ignore_request_failure: bool
    """If True, request failures will be ignored and the result will be marked as NaN.

    If False (default), request failures will raise an exception.
    """

    inference: InferenceParamsParam
    """Parameters for model inference.

    Extra fields can be supplied for additional options applied to the inference
    request directly. Fields not supported by the model may cause inference errors
    during evaluation.
    """

    labels: Dict[str, str]
    """Labels are key-value pairs that can be used for grouping and filtering."""

    optional_fields: SequenceNotStr[str]
    """
    Prompt template fields that should remain in the inferred input schema but not
    be required. Use this for fields like 'reference' when the metric can still run
    without them.
    """

    prompt_template: Union[str, Dict[str, object]]
    """The prompt template for the judge.

    Can be either a simple string or a structured object (e.g., OpenAI messages
    format). Use Jinja template variables like {{sample.output_text}} to use the
    model output within the template or {{item.xxx}} to reference input columns from
    the dataset.
    """

    reasoning: ReasoningParamsParam
    """Custom settings that control the model's reasoning behavior."""

    structured_output: Dict[str, object]
    """JSON schema to apply structured output for the judge model evaluation.

    Structured output is derived from scores when omitted. Use this option if there
    are custom requirements for the output of the judge.
    """

    supported_job_types: List[Literal["online", "offline"]]
    """
    A metric can evaluate model outputs for online evaluations or pre-generated
    outputs for offline evaluations.
    """

    system_prompt: str
    """
    Initial instructions that define the judge model's role and behavior for the
    conversation. This is prepended to the messages as a system message.
    """

    type: Literal["llm-judge"]
