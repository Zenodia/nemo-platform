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

from typing_extensions import Literal, TypedDict

from .validation_parameters_param import ValidationParametersParam

__all__ = ["GenerateParametersParam"]


class GenerateParametersParam(TypedDict, total=False):
    """Configuration parameters for synthetic data generation.

    These parameters control how synthetic data is generated after the model is trained.
    They affect the quality, diversity, and validity of the generated synthetic records.
    """

    attention_backend: str
    """The attention backend for the vLLM engine.

    Common values: 'FLASHINFER', 'FLASH_ATTN', 'TRITON_ATTN', 'FLEX_ATTENTION'. If
    `None` or 'auto', vLLM will auto-select the best available backend.
    """

    enforce_timeseries_fidelity: bool
    """
    Enforce time-series fidelity by enforcing order, intervals, start and end times
    of the records.
    """

    invalid_fraction_threshold: float
    """
    The fraction of invalid records that will stop generation after the `patience`
    limit is reached. Must be in [0, 1].
    """

    num_records: int
    """Number of records to generate."""

    patience: int
    """
    Number of consecutive generations where the `invalid_fraction_threshold` is
    reached before stopping generation. Must be >= 1.
    """

    repetition_penalty: float
    """The value used to control the likelihood of the model repeating the same token.

    Must be > 0.
    """

    structured_generation_backend: Literal["auto", "xgrammar", "guidance", "outlines", "lm-format-enforcer"]
    """The backend used by vLLM when `use_structured_generation` is `True`.

    Supported backends: 'outlines', 'guidance', 'xgrammar', 'lm-format-enforcer'.
    'auto' will allow vLLM to choose the backend.
    """

    structured_generation_schema_method: Literal["regex", "json_schema"]
    """
    The method used to generate the schema from your dataset and pass it to the
    generation backend. 'regex' uses a custom regex construction method that tends
    to be more comprehensive than 'json_schema' at the cost of speed.
    """

    structured_generation_use_single_sequence: bool
    """
    Whether to use a regex that matches exactly one sequence or record if
    `max_sequences_per_example` is 1.
    """

    temperature: float
    """Sampling temperature for controlling randomness (higher = more random)."""

    top_p: float
    """Nucleus sampling probability for token selection. Must be in (0, 1]."""

    use_structured_generation: bool
    """Whether to use structured generation for better format control."""

    validation: ValidationParametersParam
    """Configuration for record and sequence validation.

    These parameters control the validation and automatic fixes when going from LLM
    output to tabular data.
    """
