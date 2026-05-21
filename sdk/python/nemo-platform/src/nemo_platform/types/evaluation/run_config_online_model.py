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

from typing import Dict, Optional

from ..._models import BaseModel
from .inference_params import InferenceParams
from .reasoning_params import ReasoningParams

__all__ = ["RunConfigOnlineModel"]


class RunConfigOnlineModel(BaseModel):
    """Job parameters for model online evaluation."""

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

    limit_samples: Optional[int] = None
    """
    Limit number of evaluation samples, taking the first `limit` samples from the
    dataset.
    """

    max_retries: Optional[int] = None
    """Maximum number of retries for failed requests."""

    parallelism: Optional[int] = None
    """Parallelism to be used for the evaluation job.

    Typically, this represents the maximum number of concurrent requests made to the
    model.
    """

    reasoning: Optional[ReasoningParams] = None
    """Custom settings that control the model's reasoning behavior."""

    request_timeout: Optional[int] = None
    """The timeout to be used for requests made to the model."""

    structured_output: Optional[Dict[str, object]] = None
    """JSON schema to apply structured output for the model."""

    system_prompt: Optional[str] = None
    """
    Initial instructions that define the model's role and behavior for the
    conversation.
    """
