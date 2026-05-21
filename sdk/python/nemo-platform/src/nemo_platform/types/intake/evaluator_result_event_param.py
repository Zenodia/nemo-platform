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

from typing import Dict, Union
from datetime import datetime
from typing_extensions import Literal, Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["EvaluatorResultEventParam"]


class EvaluatorResultEventParam(TypedDict, total=False):
    """Result produced by an automated evaluator.

    Use this for any non-human scorer that emits a judgement about an entry:
    eval-framework verifier rewards, LLM-judge ratings, auditor probe results, etc.
    Distinct from UserFeedbackEvent (human end-user feedback) and ReviewerAnnotationEvent
    (human expert annotation).
    """

    name: Required[str]
    """
    Identifier of the evaluator that produced this result (e.g., 'harbor.verifier',
    'evaluator.llm_judge', 'auditor.pii_probe').
    """

    id: str
    """Unique identifier for the event. Populated when retrieved from database."""

    created_at: Annotated[Union[str, datetime], PropertyInfo(format="iso8601")]
    """UTC timestamp when the record was created."""

    created_by: Dict[str, str]
    """Identifier of the user or system that generated the record.

    Can be set of key-value pairs.
    """

    event_type: Literal["evaluator_result"]

    metadata: Dict[str, object]
    """
    Free-form additional context about this result (e.g., supporting metrics,
    trial_name, rubric_version, evaluator config snapshot).
    """

    score: Union[float, str]
    """
    The result value: a number (e.g., reward, rating, probability) or a string
    (e.g., 'pass', 'fail', a category label). Semantics are defined by the
    evaluator.
    """
