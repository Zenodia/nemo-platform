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

from typing import List, Union
from typing_extensions import Literal, Required, TypeAlias, TypedDict

from .metric_ref import MetricRef
from .f1_metric_param_param import F1MetricParamParam
from .bleu_metric_param_param import BleuMetricParamParam
from .rouge_metric_param_param import RougeMetricParamParam
from .remote_metric_param_param import RemoteMetricParamParam
from .evaluate_dataset_rows_param import EvaluateDatasetRowsParam
from .llm_judge_metric_param_param import LLMJudgeMetricParamParam
from .exact_match_metric_param_param import ExactMatchMetricParamParam
from .faithfulness_metric_param_param import FaithfulnessMetricParamParam
from .number_check_metric_param_param import NumberCheckMetricParamParam
from .string_check_metric_param_param import StringCheckMetricParamParam
from .tool_calling_metric_param_param import ToolCallingMetricParamParam
from .context_recall_metric_param_param import ContextRecallMetricParamParam
from .answer_accuracy_metric_param_param import AnswerAccuracyMetricParamParam
from .topic_adherence_metric_param_param import TopicAdherenceMetricParamParam
from .context_precision_metric_param_param import ContextPrecisionMetricParamParam
from .context_relevance_metric_param_param import ContextRelevanceMetricParamParam
from .noise_sensitivity_metric_param_param import NoiseSensitivityMetricParamParam
from .response_relevancy_metric_param_param import ResponseRelevancyMetricParamParam
from .tool_call_accuracy_metric_param_param import ToolCallAccuracyMetricParamParam
from .agent_goal_accuracy_metric_param_param import AgentGoalAccuracyMetricParamParam
from .context_entity_recall_metric_param_param import ContextEntityRecallMetricParamParam
from .response_groundedness_metric_param_param import ResponseGroundednessMetricParamParam
from .nemo_agent_toolkit_remote_metric_param_param import NeMoAgentToolkitRemoteMetricParamParam

__all__ = ["MetricEvaluateParams", "Metric"]


class MetricEvaluateParams(TypedDict, total=False):
    workspace: str

    dataset: Required[EvaluateDatasetRowsParam]
    """Inline dataset for evaluation with a maximum of 10 rows."""

    metric: Required[Metric]
    """The metric to use for evaluation.

    Can be a reference (workspace/metric_name) or an inline metric definition.
    """

    aggregate_fields: List[
        Literal[
            "nan_count",
            "sum",
            "mean",
            "min",
            "max",
            "std_dev",
            "variance",
            "score_type",
            "percentiles",
            "histogram",
            "rubric_distribution",
            "mode_category",
        ]
    ]
    """Aggregate score fields to include in the response (comma-separated or repeated).

    Default: ('nan_count', 'sum', 'mean', 'min', 'max'). Available: ('nan_count',
    'sum', 'mean', 'min', 'max', 'std_dev', 'variance', 'score_type', 'percentiles',
    'histogram', 'rubric_distribution', 'mode_category').
    """


Metric: TypeAlias = Union[
    MetricRef,
    LLMJudgeMetricParamParam,
    TopicAdherenceMetricParamParam,
    AgentGoalAccuracyMetricParamParam,
    AnswerAccuracyMetricParamParam,
    ContextRelevanceMetricParamParam,
    ResponseGroundednessMetricParamParam,
    ContextRecallMetricParamParam,
    ContextPrecisionMetricParamParam,
    ContextEntityRecallMetricParamParam,
    ResponseRelevancyMetricParamParam,
    FaithfulnessMetricParamParam,
    NoiseSensitivityMetricParamParam,
    ToolCallAccuracyMetricParamParam,
    BleuMetricParamParam,
    ExactMatchMetricParamParam,
    F1MetricParamParam,
    NumberCheckMetricParamParam,
    RemoteMetricParamParam,
    NeMoAgentToolkitRemoteMetricParamParam,
    RougeMetricParamParam,
    StringCheckMetricParamParam,
    ToolCallingMetricParamParam,
]
