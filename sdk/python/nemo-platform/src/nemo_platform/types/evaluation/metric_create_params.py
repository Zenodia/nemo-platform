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
from ..files.secret_ref import SecretRef
from .range_score_param import RangeScoreParam
from .remote_score_param import RemoteScoreParam
from .rubric_score_param import RubricScoreParam
from .inference_params_param import InferenceParamsParam
from .reasoning_params_param import ReasoningParamsParam

__all__ = [
    "MetricCreateParams",
    "LLMJudgeMetricParam",
    "LLMJudgeMetricParamModel",
    "LLMJudgeMetricParamScore",
    "TopicAdherenceMetricParam",
    "TopicAdherenceMetricParamJudgeModel",
    "AgentGoalAccuracyMetricParam",
    "AgentGoalAccuracyMetricParamJudgeModel",
    "AnswerAccuracyMetricParam",
    "AnswerAccuracyMetricParamJudgeModel",
    "ContextRelevanceMetricParam",
    "ContextRelevanceMetricParamJudgeModel",
    "ResponseGroundednessMetricParam",
    "ResponseGroundednessMetricParamJudgeModel",
    "ContextRecallMetricParam",
    "ContextRecallMetricParamJudgeModel",
    "ContextPrecisionMetricParam",
    "ContextPrecisionMetricParamJudgeModel",
    "ContextEntityRecallMetricParam",
    "ContextEntityRecallMetricParamJudgeModel",
    "ResponseRelevancyMetricParam",
    "ResponseRelevancyMetricParamEmbeddingsModel",
    "ResponseRelevancyMetricParamJudgeModel",
    "FaithfulnessMetricParam",
    "FaithfulnessMetricParamJudgeModel",
    "NoiseSensitivityMetricParam",
    "NoiseSensitivityMetricParamJudgeModel",
    "ToolCallAccuracyMetricParam",
    "BleuMetricParam",
    "ExactMatchMetricParam",
    "F1MetricParam",
    "NumberCheckMetricParam",
    "RemoteMetricParam",
    "NeMoAgentToolkitRemoteMetricParam",
    "RougeMetricParam",
    "StringCheckMetricParam",
    "ToolCallingMetricParam",
]


class LLMJudgeMetricParam(TypedDict, total=False):
    workspace: str

    model: Required[LLMJudgeMetricParamModel]
    """The model configuration."""

    scores: Required[Iterable[LLMJudgeMetricParamScore]]
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


LLMJudgeMetricParamModel: TypeAlias = Union[ModelParam, ModelRef]

LLMJudgeMetricParamScore: TypeAlias = Union[RubricScoreParam, RangeScoreParam]


class TopicAdherenceMetricParam(TypedDict, total=False):
    workspace: str

    judge_model: Required[TopicAdherenceMetricParamJudgeModel]
    """The judge model configuration."""

    description: str
    """Human-readable description of the metric."""

    ignore_request_failure: bool
    """
    If True, request failures to the judge model are ignored and the metric result
    is marked as NaN. Parse/output formatting failures are always converted to NaN.
    """

    inference: InferenceParamsParam
    """Parameters for model inference.

    Extra fields can be supplied for additional options applied to the inference
    request directly. Fields not supported by the model may cause inference errors
    during evaluation.
    """

    input_template: Dict[str, object]
    """Optional Jinja template for rendering the input payload for RAGAS evaluation."""

    labels: Dict[str, str]
    """Labels are key-value pairs that can be used for grouping and filtering."""

    metric_mode: Literal["f1", "precision", "recall"]
    """The mode for computing topic adherence score."""

    supported_job_types: List[Literal["online", "offline"]]
    """
    A metric can evaluate model outputs for online evaluations or pre-generated
    outputs for offline evaluations.
    """

    type: Literal["topic_adherence"]


TopicAdherenceMetricParamJudgeModel: TypeAlias = Union[ModelParam, ModelRef]


class AgentGoalAccuracyMetricParam(TypedDict, total=False):
    workspace: str

    judge_model: Required[AgentGoalAccuracyMetricParamJudgeModel]
    """The judge model configuration."""

    description: str
    """Human-readable description of the metric."""

    ignore_request_failure: bool
    """
    If True, request failures to the judge model are ignored and the metric result
    is marked as NaN. Parse/output formatting failures are always converted to NaN.
    """

    inference: InferenceParamsParam
    """Parameters for model inference.

    Extra fields can be supplied for additional options applied to the inference
    request directly. Fields not supported by the model may cause inference errors
    during evaluation.
    """

    input_template: Dict[str, object]
    """Optional Jinja template for rendering the input payload for RAGAS evaluation."""

    labels: Dict[str, str]
    """Labels are key-value pairs that can be used for grouping and filtering."""

    supported_job_types: List[Literal["online", "offline"]]
    """
    A metric can evaluate model outputs for online evaluations or pre-generated
    outputs for offline evaluations.
    """

    type: Literal["agent_goal_accuracy"]

    use_reference: bool
    """Whether to use reference for goal accuracy evaluation."""


AgentGoalAccuracyMetricParamJudgeModel: TypeAlias = Union[ModelParam, ModelRef]


class AnswerAccuracyMetricParam(TypedDict, total=False):
    workspace: str

    judge_model: Required[AnswerAccuracyMetricParamJudgeModel]
    """The judge model configuration."""

    description: str
    """Human-readable description of the metric."""

    ignore_request_failure: bool
    """
    If True, request failures to the judge model are ignored and the metric result
    is marked as NaN. Parse/output formatting failures are always converted to NaN.
    """

    inference: InferenceParamsParam
    """Parameters for model inference.

    Extra fields can be supplied for additional options applied to the inference
    request directly. Fields not supported by the model may cause inference errors
    during evaluation.
    """

    input_template: Dict[str, object]
    """Optional Jinja template for rendering the input payload for RAGAS evaluation."""

    labels: Dict[str, str]
    """Labels are key-value pairs that can be used for grouping and filtering."""

    supported_job_types: List[Literal["online", "offline"]]
    """
    A metric can evaluate model outputs for online evaluations or pre-generated
    outputs for offline evaluations.
    """

    type: Literal["answer_accuracy"]


AnswerAccuracyMetricParamJudgeModel: TypeAlias = Union[ModelParam, ModelRef]


class ContextRelevanceMetricParam(TypedDict, total=False):
    workspace: str

    judge_model: Required[ContextRelevanceMetricParamJudgeModel]
    """The judge model configuration."""

    description: str
    """Human-readable description of the metric."""

    ignore_request_failure: bool
    """
    If True, request failures to the judge model are ignored and the metric result
    is marked as NaN. Parse/output formatting failures are always converted to NaN.
    """

    inference: InferenceParamsParam
    """Parameters for model inference.

    Extra fields can be supplied for additional options applied to the inference
    request directly. Fields not supported by the model may cause inference errors
    during evaluation.
    """

    input_template: Dict[str, object]
    """Optional Jinja template for rendering the input payload for RAGAS evaluation."""

    labels: Dict[str, str]
    """Labels are key-value pairs that can be used for grouping and filtering."""

    supported_job_types: List[Literal["online", "offline"]]
    """
    A metric can evaluate model outputs for online evaluations or pre-generated
    outputs for offline evaluations.
    """

    type: Literal["context_relevance"]


ContextRelevanceMetricParamJudgeModel: TypeAlias = Union[ModelParam, ModelRef]


class ResponseGroundednessMetricParam(TypedDict, total=False):
    workspace: str

    judge_model: Required[ResponseGroundednessMetricParamJudgeModel]
    """The judge model configuration."""

    description: str
    """Human-readable description of the metric."""

    ignore_request_failure: bool
    """
    If True, request failures to the judge model are ignored and the metric result
    is marked as NaN. Parse/output formatting failures are always converted to NaN.
    """

    inference: InferenceParamsParam
    """Parameters for model inference.

    Extra fields can be supplied for additional options applied to the inference
    request directly. Fields not supported by the model may cause inference errors
    during evaluation.
    """

    input_template: Dict[str, object]
    """Optional Jinja template for rendering the input payload for RAGAS evaluation."""

    labels: Dict[str, str]
    """Labels are key-value pairs that can be used for grouping and filtering."""

    supported_job_types: List[Literal["online", "offline"]]
    """
    A metric can evaluate model outputs for online evaluations or pre-generated
    outputs for offline evaluations.
    """

    type: Literal["response_groundedness"]


ResponseGroundednessMetricParamJudgeModel: TypeAlias = Union[ModelParam, ModelRef]


class ContextRecallMetricParam(TypedDict, total=False):
    workspace: str

    judge_model: Required[ContextRecallMetricParamJudgeModel]
    """The judge model configuration."""

    description: str
    """Human-readable description of the metric."""

    ignore_request_failure: bool
    """
    If True, request failures to the judge model are ignored and the metric result
    is marked as NaN. Parse/output formatting failures are always converted to NaN.
    """

    inference: InferenceParamsParam
    """Parameters for model inference.

    Extra fields can be supplied for additional options applied to the inference
    request directly. Fields not supported by the model may cause inference errors
    during evaluation.
    """

    input_template: Dict[str, object]
    """Optional Jinja template for rendering the input payload for RAGAS evaluation."""

    labels: Dict[str, str]
    """Labels are key-value pairs that can be used for grouping and filtering."""

    supported_job_types: List[Literal["online", "offline"]]
    """
    A metric can evaluate model outputs for online evaluations or pre-generated
    outputs for offline evaluations.
    """

    type: Literal["context_recall"]


ContextRecallMetricParamJudgeModel: TypeAlias = Union[ModelParam, ModelRef]


class ContextPrecisionMetricParam(TypedDict, total=False):
    workspace: str

    judge_model: Required[ContextPrecisionMetricParamJudgeModel]
    """The judge model configuration."""

    description: str
    """Human-readable description of the metric."""

    ignore_request_failure: bool
    """
    If True, request failures to the judge model are ignored and the metric result
    is marked as NaN. Parse/output formatting failures are always converted to NaN.
    """

    inference: InferenceParamsParam
    """Parameters for model inference.

    Extra fields can be supplied for additional options applied to the inference
    request directly. Fields not supported by the model may cause inference errors
    during evaluation.
    """

    input_template: Dict[str, object]
    """Optional Jinja template for rendering the input payload for RAGAS evaluation."""

    labels: Dict[str, str]
    """Labels are key-value pairs that can be used for grouping and filtering."""

    supported_job_types: List[Literal["online", "offline"]]
    """
    A metric can evaluate model outputs for online evaluations or pre-generated
    outputs for offline evaluations.
    """

    type: Literal["context_precision"]


ContextPrecisionMetricParamJudgeModel: TypeAlias = Union[ModelParam, ModelRef]


class ContextEntityRecallMetricParam(TypedDict, total=False):
    workspace: str

    judge_model: Required[ContextEntityRecallMetricParamJudgeModel]
    """The judge model configuration."""

    description: str
    """Human-readable description of the metric."""

    ignore_request_failure: bool
    """
    If True, request failures to the judge model are ignored and the metric result
    is marked as NaN. Parse/output formatting failures are always converted to NaN.
    """

    inference: InferenceParamsParam
    """Parameters for model inference.

    Extra fields can be supplied for additional options applied to the inference
    request directly. Fields not supported by the model may cause inference errors
    during evaluation.
    """

    input_template: Dict[str, object]
    """Optional Jinja template for rendering the input payload for RAGAS evaluation."""

    labels: Dict[str, str]
    """Labels are key-value pairs that can be used for grouping and filtering."""

    supported_job_types: List[Literal["online", "offline"]]
    """
    A metric can evaluate model outputs for online evaluations or pre-generated
    outputs for offline evaluations.
    """

    type: Literal["context_entity_recall"]


ContextEntityRecallMetricParamJudgeModel: TypeAlias = Union[ModelParam, ModelRef]


class ResponseRelevancyMetricParam(TypedDict, total=False):
    workspace: str

    embeddings_model: Required[ResponseRelevancyMetricParamEmbeddingsModel]
    """The embeddings model configuration."""

    judge_model: Required[ResponseRelevancyMetricParamJudgeModel]
    """The judge model configuration."""

    description: str
    """Human-readable description of the metric."""

    ignore_request_failure: bool
    """
    If True, request failures to the judge model are ignored and the metric result
    is marked as NaN. Parse/output formatting failures are always converted to NaN.
    """

    inference: InferenceParamsParam
    """Parameters for model inference.

    Extra fields can be supplied for additional options applied to the inference
    request directly. Fields not supported by the model may cause inference errors
    during evaluation.
    """

    input_template: Dict[str, object]
    """Optional Jinja template for rendering the input payload for RAGAS evaluation."""

    labels: Dict[str, str]
    """Labels are key-value pairs that can be used for grouping and filtering."""

    strictness: int
    """Number of parallel questions generated. NIM can only generate 1."""

    supported_job_types: List[Literal["online", "offline"]]
    """
    A metric can evaluate model outputs for online evaluations or pre-generated
    outputs for offline evaluations.
    """

    type: Literal["response_relevancy"]


ResponseRelevancyMetricParamEmbeddingsModel: TypeAlias = Union[ModelParam, ModelRef]

ResponseRelevancyMetricParamJudgeModel: TypeAlias = Union[ModelParam, ModelRef]


class FaithfulnessMetricParam(TypedDict, total=False):
    workspace: str

    judge_model: Required[FaithfulnessMetricParamJudgeModel]
    """The judge model configuration."""

    description: str
    """Human-readable description of the metric."""

    ignore_request_failure: bool
    """
    If True, request failures to the judge model are ignored and the metric result
    is marked as NaN. Parse/output formatting failures are always converted to NaN.
    """

    inference: InferenceParamsParam
    """Parameters for model inference.

    Extra fields can be supplied for additional options applied to the inference
    request directly. Fields not supported by the model may cause inference errors
    during evaluation.
    """

    input_template: Dict[str, object]
    """Optional Jinja template for rendering the input payload for RAGAS evaluation."""

    labels: Dict[str, str]
    """Labels are key-value pairs that can be used for grouping and filtering."""

    supported_job_types: List[Literal["online", "offline"]]
    """
    A metric can evaluate model outputs for online evaluations or pre-generated
    outputs for offline evaluations.
    """

    type: Literal["faithfulness"]


FaithfulnessMetricParamJudgeModel: TypeAlias = Union[ModelParam, ModelRef]


class NoiseSensitivityMetricParam(TypedDict, total=False):
    workspace: str

    judge_model: Required[NoiseSensitivityMetricParamJudgeModel]
    """The judge model configuration."""

    description: str
    """Human-readable description of the metric."""

    ignore_request_failure: bool
    """
    If True, request failures to the judge model are ignored and the metric result
    is marked as NaN. Parse/output formatting failures are always converted to NaN.
    """

    inference: InferenceParamsParam
    """Parameters for model inference.

    Extra fields can be supplied for additional options applied to the inference
    request directly. Fields not supported by the model may cause inference errors
    during evaluation.
    """

    input_template: Dict[str, object]
    """Optional Jinja template for rendering the input payload for RAGAS evaluation."""

    labels: Dict[str, str]
    """Labels are key-value pairs that can be used for grouping and filtering."""

    supported_job_types: List[Literal["online", "offline"]]
    """
    A metric can evaluate model outputs for online evaluations or pre-generated
    outputs for offline evaluations.
    """

    type: Literal["noise_sensitivity"]


NoiseSensitivityMetricParamJudgeModel: TypeAlias = Union[ModelParam, ModelRef]


class ToolCallAccuracyMetricParam(TypedDict, total=False):
    workspace: str

    description: str
    """Human-readable description of the metric."""

    input_template: Dict[str, object]
    """Optional Jinja template for rendering the input payload for RAGAS evaluation."""

    labels: Dict[str, str]
    """Labels are key-value pairs that can be used for grouping and filtering."""

    supported_job_types: List[Literal["online", "offline"]]
    """
    A metric can evaluate model outputs for online evaluations or pre-generated
    outputs for offline evaluations.
    """

    type: Literal["tool_call_accuracy"]


class BleuMetricParam(TypedDict, total=False):
    workspace: str

    references: Required[SequenceNotStr[str]]
    """The templates for the ground truth references to calculate BLEU metric with."""

    candidate: str
    """The template for the candidate to calculate BLEU metric on.

    If not provided, the output text from the model is used.
    """

    description: str
    """Human-readable description of the metric."""

    labels: Dict[str, str]
    """Labels are key-value pairs that can be used for grouping and filtering."""

    supported_job_types: List[Literal["online", "offline"]]
    """
    A metric can evaluate model outputs for online evaluations or pre-generated
    outputs for offline evaluations.
    """

    type: Literal["bleu"]


class ExactMatchMetricParam(TypedDict, total=False):
    workspace: str

    reference: Required[str]
    """
    The template for the ground truth reference to calculate the exact match metric
    with.
    """

    candidate: str
    """The template for the candidate to evaluate the exact match metric on.

    If not provided, the output text from the model is used.
    """

    description: str
    """Human-readable description of the metric."""

    labels: Dict[str, str]
    """Labels are key-value pairs that can be used for grouping and filtering."""

    supported_job_types: List[Literal["online", "offline"]]
    """
    A metric can evaluate model outputs for online evaluations or pre-generated
    outputs for offline evaluations.
    """

    type: Literal["exact-match"]


class F1MetricParam(TypedDict, total=False):
    workspace: str

    reference: Required[str]
    """The template for the ground truth reference to calculate the F1 metric with."""

    candidate: str
    """The template for the candidate to evaluate the F1 metric on.

    If not provided, the output text from the model is used.
    """

    description: str
    """Human-readable description of the metric."""

    labels: Dict[str, str]
    """Labels are key-value pairs that can be used for grouping and filtering."""

    supported_job_types: List[Literal["online", "offline"]]
    """
    A metric can evaluate model outputs for online evaluations or pre-generated
    outputs for offline evaluations.
    """

    type: Literal["f1"]


class NumberCheckMetricParam(TypedDict, total=False):
    workspace: str

    left_template: Required[str]
    """
    The template to use for rendering the left value of the operator to compute the
    metric.
    """

    operation: Required[
        Literal[
            "equals",
            "==",
            "!=",
            "<>",
            "not equals",
            ">=",
            "gte",
            "greater than or equal",
            ">",
            "gt",
            "greater than",
            "<=",
            "lte",
            "less than or equal",
            "<",
            "lt",
            "less than",
            "absolute difference",
        ]
    ]
    """The operation to compute for the metric."""

    right_template: Required[str]
    """
    The template to use for rendering the right value of the operator to compute the
    metric.
    """

    description: str
    """Human-readable description of the metric."""

    epsilon: float
    """Specify the tolerance for the absolute difference of values."""

    labels: Dict[str, str]
    """Labels are key-value pairs that can be used for grouping and filtering."""

    supported_job_types: List[Literal["online", "offline"]]
    """
    A metric can evaluate model outputs for online evaluations or pre-generated
    outputs for offline evaluations.
    """

    type: Literal["number-check"]


class RemoteMetricParam(TypedDict, total=False):
    workspace: str

    body: Required[Dict[str, object]]
    """Jinja template for request payload"""

    scores: Required[Iterable[RemoteScoreParam]]
    """List of scores to extract from the remote response"""

    url: Required[str]
    """The URL of the remote endpoint."""

    api_key_secret: SecretRef
    """Reference to a secret.

    Format: 'secret_name' (uses request workspace) or 'workspace/secret_name'
    (explicit workspace).
    """

    description: str
    """Human-readable description of the metric."""

    labels: Dict[str, str]
    """Labels are key-value pairs that can be used for grouping and filtering."""

    max_retries: int
    """Maximum number of retry attempts."""

    supported_job_types: List[Literal["online", "offline"]]
    """
    A metric can evaluate model outputs for online evaluations or pre-generated
    outputs for offline evaluations.
    """

    timeout_seconds: float
    """Request timeout in seconds."""

    type: Literal["remote"]


class NeMoAgentToolkitRemoteMetricParam(TypedDict, total=False):
    workspace: str

    evaluator_name: Required[str]
    """The name of the evaluator (also used as the score name)."""

    url: Required[str]
    """The URL of the remote endpoint."""

    api_key_secret: SecretRef
    """Reference to a secret.

    Format: 'secret_name' (uses request workspace) or 'workspace/secret_name'
    (explicit workspace).
    """

    description: str
    """Human-readable description of the metric."""

    labels: Dict[str, str]
    """Labels are key-value pairs that can be used for grouping and filtering."""

    max_retries: int
    """Maximum number of retry attempts."""

    supported_job_types: List[Literal["online", "offline"]]
    """
    A metric can evaluate model outputs for online evaluations or pre-generated
    outputs for offline evaluations.
    """

    timeout_seconds: float
    """Request timeout in seconds."""

    type: Literal["nemo-agent-toolkit-remote"]


class RougeMetricParam(TypedDict, total=False):
    workspace: str

    reference: Required[str]
    """The template for the ground truth reference to evaluate the ROUGE metric with."""

    candidate: str
    """The template for the candidate to evaluate the ROUGE metric on.

    If not provided, the output text from the model is used.
    """

    description: str
    """Human-readable description of the metric."""

    labels: Dict[str, str]
    """Labels are key-value pairs that can be used for grouping and filtering."""

    supported_job_types: List[Literal["online", "offline"]]
    """
    A metric can evaluate model outputs for online evaluations or pre-generated
    outputs for offline evaluations.
    """

    type: Literal["rouge"]


class StringCheckMetricParam(TypedDict, total=False):
    workspace: str

    left_template: Required[str]
    """
    The template to use for rendering the left value of the operator to compute the
    metric.
    """

    operation: Required[
        Literal["equals", "==", "!=", "<>", "not equals", "contains", "not contains", "startswith", "endswith"]
    ]
    """The operation to compute for the metric."""

    right_template: Required[str]
    """
    The template to use for rendering the right value of the operator to compute the
    metric.
    """

    description: str
    """Human-readable description of the metric."""

    labels: Dict[str, str]
    """Labels are key-value pairs that can be used for grouping and filtering."""

    supported_job_types: List[Literal["online", "offline"]]
    """
    A metric can evaluate model outputs for online evaluations or pre-generated
    outputs for offline evaluations.
    """

    type: Literal["string-check"]


class ToolCallingMetricParam(TypedDict, total=False):
    workspace: str

    reference: Required[str]
    """The template for the ground truth reference to evaluate tool calling accuracy."""

    description: str
    """Human-readable description of the metric."""

    labels: Dict[str, str]
    """Labels are key-value pairs that can be used for grouping and filtering."""

    supported_job_types: List[Literal["online", "offline"]]
    """
    A metric can evaluate model outputs for online evaluations or pre-generated
    outputs for offline evaluations.
    """

    type: Literal["tool-calling"]


MetricCreateParams: TypeAlias = Union[
    LLMJudgeMetricParam,
    TopicAdherenceMetricParam,
    AgentGoalAccuracyMetricParam,
    AnswerAccuracyMetricParam,
    ContextRelevanceMetricParam,
    ResponseGroundednessMetricParam,
    ContextRecallMetricParam,
    ContextPrecisionMetricParam,
    ContextEntityRecallMetricParam,
    ResponseRelevancyMetricParam,
    FaithfulnessMetricParam,
    NoiseSensitivityMetricParam,
    ToolCallAccuracyMetricParam,
    BleuMetricParam,
    ExactMatchMetricParam,
    F1MetricParam,
    NumberCheckMetricParam,
    RemoteMetricParam,
    NeMoAgentToolkitRemoteMetricParam,
    RougeMetricParam,
    StringCheckMetricParam,
    ToolCallingMetricParam,
]
