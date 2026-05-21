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

from typing_extensions import Required, TypedDict

from .safe_synthesizer_parameters_param import SafeSynthesizerParametersParam

__all__ = ["SafeSynthesizerJobConfigParam"]


class SafeSynthesizerJobConfigParam(TypedDict, total=False):
    """Configuration model for Safe Synthesizer jobs.

    Used primarily internally to configure a run submitted to the NeMo Jobs
    Microservice.
    """

    config: Required[SafeSynthesizerParametersParam]
    """Main configuration class for the Safe Synthesizer pipeline.

    This is the top-level configuration class that orchestrates all aspects of
    synthetic data generation including training, generation, privacy, evaluation,
    and data handling. It provides validation to ensure parameter compatibility.
    """

    data_source: Required[str]
    """The data source for the job."""

    enable_synthesis: bool
    """Whether to run LLM training and generation phases.

    When False the task only performs PII replacement and returns the processed
    data.
    """

    hf_token_secret: str
    """Name of platform secret containing the HuggingFace token.

    Must exist in the same workspace as the job.
    """
