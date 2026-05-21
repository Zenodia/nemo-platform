# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""
Job Result entity types for the evaluator service.

This module contains the persisted results reflecting job results from file artifacts.
These entities can be natively queried from Entity service.
"""

from __future__ import annotations

from typing import ClassVar

import nmp.evaluator.app.values as app
from nemo_evaluator_sdk.values import AggregateScore
from nmp.common.entities.client import EntityBase
from pydantic import BaseModel, Field


class BaseJobResult(BaseModel):
    dataset: app.FilesetRef | None = Field(
        default=None,
        description="The dataset used for the evaluation job to generate the result. This field is only populated when the job specifies a FilesetRef.",
    )
    model: app.ModelRef | None = Field(
        default=None,
        description="The model evaluated for the job to generate the result. This field is only populated when the job specifies a ModelRef.",
    )
    labels: dict[str, str] = Field(
        default_factory=dict, description="Labels are key-value pairs that can be used for grouping and filtering."
    )


# =============================================================================
# Metric Job Result
# =============================================================================


class MetricJobResult(BaseJobResult, EntityBase):
    """
    Result for Metric Job
    """

    __entity_type__: ClassVar[str] = "metric_job_result"

    metric: app.MetricRef | None = Field(
        default=None, description="The metric used for the evaluation job to generate the result."
    )
    scores: list[AggregateScore] = Field(description="The list of aggregated scores.")


# =============================================================================
# Benchmark Job Result
# =============================================================================


class BenchmarkJobResult(BaseJobResult, EntityBase):
    """Aggregated results for a benchmark evaluation."""

    __entity_type__: ClassVar[str] = "benchmark_job_result"

    benchmark: app.BenchmarkRef = Field(description="The benchmark used for the evaluation job to generate the result.")
    metrics: list[app.MetricRef] | None = Field(
        default=None, description="The list of metrics used for the evaluation job to generate the result."
    )
    results: list[app.BenchmarkMetricResult] = Field(description="Results for each metric in the benchmark.")
