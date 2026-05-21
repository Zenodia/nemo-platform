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

from typing import Optional

from ...._models import BaseModel
from .safe_synthesizer_timing import SafeSynthesizerTiming

__all__ = ["SafeSynthesizerSummary"]


class SafeSynthesizerSummary(BaseModel):
    """Aggregated quality, privacy, and record-count metrics for a pipeline run."""

    timing: SafeSynthesizerTiming
    """Wall-clock durations for each pipeline stage."""

    attribute_inference_protection_score: Optional[float] = None
    """
    Resistance to attacks that try to infer sensitive attributes from
    quasi-identifiers.
    """

    column_correlation_stability_score: Optional[float] = None
    """
    How closely pairwise column correlations in synthetic data match the original
    for numeric and categorical columns.
    """

    column_distribution_stability_score: Optional[float] = None
    """
    Per-column Jensen-Shannon distance between training and synthetic distributions
    averaged across all numeric and categorical columns.
    """

    data_privacy_score: Optional[float] = None
    """Composite of MIA and AIA protection scores."""

    deep_structure_stability_score: Optional[float] = None
    """
    PCA-based comparison of multivariate structure between real and synthetic data
    for numeric and categorical columns.
    """

    membership_inference_protection_score: Optional[float] = None
    """
    Resistance to attacks that try to determine whether a record was in the training
    set.
    """

    num_invalid_records: Optional[int] = None
    """Count of synthetic records filtered out during validation."""

    num_prompts: Optional[int] = None
    """Total LLM generation prompts issued."""

    num_valid_records: Optional[int] = None
    """Count of synthetic records that passed schema and format validation."""

    synthetic_data_quality_score: Optional[float] = None
    """Weighted composite of the five sub-scores below (SQS).

    Higher is better (0--10 scale).
    """

    text_semantic_similarity_score: Optional[float] = None
    """
    Embedding-based semantic closeness between real and synthetic free-text columns.
    """

    text_structure_similarity_score: Optional[float] = None
    """
    Jensen-Shannon divergence over sentence count, words-per-sentence, and
    characters-per-word distributions between real and synthetic free-text columns.
    """

    valid_record_fraction: Optional[float] = None
    """
    Ratio of valid records:
    `num_valid_records / (num_valid_records + num_invalid_records)`.
    """
