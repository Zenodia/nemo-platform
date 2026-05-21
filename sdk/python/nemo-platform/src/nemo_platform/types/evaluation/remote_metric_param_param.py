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

from typing import Dict, List, Iterable
from typing_extensions import Literal, Required, TypedDict

from ..files.secret_ref import SecretRef
from .remote_score_param import RemoteScoreParam

__all__ = ["RemoteMetricParamParam"]


class RemoteMetricParamParam(TypedDict, total=False):
    """Request type for RemoteMetric.

    A metric that computes scores via a remote endpoint.
    """

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
