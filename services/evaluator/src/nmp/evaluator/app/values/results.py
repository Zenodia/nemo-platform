# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Compatibility result types for the evaluator service.

Shared result-domain models are sourced from ``nemo_evaluator_sdk.values.results``.
Only legacy evaluator-only result types remain defined in this module.
"""

from __future__ import annotations

import math
from typing import Any

from nemo_evaluator_sdk.values.results import ScoreStats
from pydantic import AnyUrl, BaseModel, Field, field_serializer, field_validator

# ---------------------------------------------------------------------------
# Deprecated result types from v1
# ---------------------------------------------------------------------------


class DeprecatedScoreValue(BaseModel):
    """A score computed for a metric, as part of an evaluation."""

    value: float
    stats: ScoreStats | None = Field(
        default=None,
        description="Computed score statistics for the score.",
    )

    @field_validator("value", mode="before")
    @classmethod
    def convert_value(cls, v: Any) -> Any:
        """If incoming object is string with value "nan", it is converted to float nan."""
        if isinstance(v, str):
            if v.strip().lower() == "nan":
                return float("nan")
            raise ValueError("The only string value allowed for value is NaN")
        return v

    @field_serializer("value")
    def serialize_nan(self, v: float) -> float | str:
        """Float NaN are not accepted by postgres json structure.

        So they are serialized to string 'NaN' as suggested by postgres.
        https://www.postgresql.org/docs/9.3/datatype-numeric.html
        """
        if isinstance(v, float) and math.isnan(v):
            return "NaN"
        return v


class DeprecatedMetricResult(BaseModel):
    """The result coming from a metric, as part of an evaluation.

    It contains a mapping of score names to their value
    """

    scores: dict[str, DeprecatedScoreValue] = Field(
        default_factory=dict,
        description="The value for all the scores computed for the metric.",
    )


class TaskResult(BaseModel):
    """The evaluation results for a task."""

    metrics: dict[str, DeprecatedMetricResult] = Field(
        default_factory=dict,
        description="The value for all the metrics computed for the task.",
    )

    data: dict | None = Field(default=None, description="Additional data from the task")


class GroupResult(BaseModel):
    """The evaluation results for a group."""

    groups: dict[str, "GroupResult"] | None = Field(default=None, description="The results for the subgroups.")
    metrics: dict[str, DeprecatedMetricResult] = Field(
        default_factory=dict,
        description="The value for all the metrics computed for the group.",
    )


class EvaluationResult(BaseModel):
    """Result of an evaluation job.

    Contains task results, group results, and aggregate metrics.
    """

    # Override workspace to have a default for inline results
    workspace: str = Field(default="default", description="Workspace identifier")

    job: str = Field(
        description="The evaluation job associated with this results instance.",
    )

    # Results by task and group
    tasks: dict[str, TaskResult] | None = Field(
        default_factory=dict,
        description="The results at the task-level.",
    )
    groups: dict[str, GroupResult] | None = Field(
        default_factory=dict,
        description="The results at the group-level.",
    )

    # Output files
    files_url: AnyUrl | None = Field(
        default=None,
        description="The place for the output files, if any.",
    )

    @field_serializer("files_url")
    def serialize_url(self, value: AnyUrl | None) -> str | None:
        return str(value) if value else None
