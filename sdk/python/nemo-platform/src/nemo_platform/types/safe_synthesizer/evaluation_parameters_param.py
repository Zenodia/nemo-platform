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

from typing_extensions import TypedDict

from ..._types import SequenceNotStr

__all__ = ["EvaluationParametersParam"]


class EvaluationParametersParam(TypedDict, total=False):
    """Configuration for evaluating synthetic data quality and privacy.

    This class controls which evaluation metrics are computed and how they are configured.
    It includes privacy attack evaluations, statistical quality metrics, and downstream
    machine learning performance assessments.
    """

    aia_enabled: bool
    """Enable attribute inference attack evaluation for privacy assessment."""

    enabled: bool
    """Enable or disable evaluation."""

    mandatory_columns: int
    """Number of mandatory columns that must be used in evaluation."""

    mia_enabled: bool
    """Enable membership inference attack evaluation for privacy assessment."""

    pii_replay_columns: SequenceNotStr[str]
    """List of columns for PII Replay. If not provided, only entities will be used."""

    pii_replay_enabled: bool
    """Enable PII Replay detection."""

    pii_replay_entities: SequenceNotStr[str]
    """List of entities for PII Replay.

    If not provided, default entities will be used.
    """

    quasi_identifier_count: int
    """Number of quasi-identifiers to sample for privacy attacks."""

    sqs_report_columns: int
    """Number of columns to include in statistical quality reports."""

    sqs_report_rows: int
    """Number of rows to include in statistical quality reports."""
