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

from typing import Dict, List, Union
from typing_extensions import Literal, Required, TypeAlias, TypedDict

from .model_ref import ModelRef
from .model_param import ModelParam
from .inference_params_param import InferenceParamsParam

__all__ = ["ResponseGroundednessMetricParamParam", "JudgeModel"]

JudgeModel: TypeAlias = Union[ModelParam, ModelRef]


class ResponseGroundednessMetricParamParam(TypedDict, total=False):
    """Request type for ResponseGroundedness metrics."""

    judge_model: Required[JudgeModel]
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
