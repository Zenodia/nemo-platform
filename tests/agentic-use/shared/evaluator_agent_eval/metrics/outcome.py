# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Outcome metrics for evaluator agent benchmark rows."""

import logging
from math import nan

from nemo_evaluator_sdk.values.results import MetricResult, MetricScore

logger = logging.getLogger(__name__)


class DeterministicTaskSuccessMetric:
    """Score task success from task-local deterministic checks."""

    def __init__(self, success_key: str) -> None:
        self.success_key = success_key

    @property
    def type(self) -> str:
        return "agent_eval/task_success"

    def score_names(self) -> list[str]:
        return ["task_success"]

    async def compute_scores(self, item: dict, sample: dict) -> MetricResult:
        return MetricResult(scores=[MetricScore(name="task_success", value=float(item.get(self.success_key) is True))])


class VerificationScoreMetric:
    """Pass through a normalized task-specific verification score."""

    def __init__(self, score_key: str) -> None:
        self.score_key = score_key

    @property
    def type(self) -> str:
        return "agent_eval/verification_score"

    def score_names(self) -> list[str]:
        return ["verification_score"]

    async def compute_scores(self, item: dict, sample: dict) -> MetricResult:
        value = item.get(self.score_key)
        if isinstance(value, bool) or not isinstance(value, int | float) or value < 0.0 or value > 1.0:
            return MetricResult(scores=[MetricScore(name="verification_score", value=nan)])
        return MetricResult(scores=[MetricScore(name="verification_score", value=float(value))])


class OutputSchemaValidMetric:
    """Score whether the task-specific checker accepted the output shape."""

    def __init__(self, valid_key: str) -> None:
        self.valid_key = valid_key

    @property
    def type(self) -> str:
        return "agent_eval/output_schema_valid"

    def score_names(self) -> list[str]:
        return ["output_schema_valid"]

    async def compute_scores(self, item: dict, sample: dict) -> MetricResult:
        return MetricResult(
            scores=[MetricScore(name="output_schema_valid", value=float(item.get(self.valid_key) is True))]
        )


class SurfaceGatedSuccessMetric:
    """Score success only when task success and surface adherence both pass."""

    def __init__(
        self,
        *,
        success_key: str,
        observed_surfaces_key: str,
        allowed_surfaces_key: str,
        forbidden_surfaces_key: str,
        forbidden_surface_hits_key: str,
    ) -> None:
        self.success_key = success_key
        self.observed_surfaces_key = observed_surfaces_key
        self.allowed_surfaces_key = allowed_surfaces_key
        self.forbidden_surfaces_key = forbidden_surfaces_key
        self.forbidden_surface_hits_key = forbidden_surface_hits_key

    @property
    def type(self) -> str:
        return "agent_eval/surface_gated_success"

    def score_names(self) -> list[str]:
        return ["surface_gated_success"]

    async def compute_scores(self, item: dict, sample: dict) -> MetricResult:
        try:
            observed_surfaces = item[self.observed_surfaces_key]
            allowed_surfaces = item[self.allowed_surfaces_key]
            forbidden_surfaces = item[self.forbidden_surfaces_key]
            forbidden_surface_hits = item[self.forbidden_surface_hits_key]
            if (
                not isinstance(observed_surfaces, list)
                or not isinstance(allowed_surfaces, list)
                or not isinstance(forbidden_surfaces, list)
                or not isinstance(forbidden_surface_hits, list)
                or not all(isinstance(entry, str) for entry in observed_surfaces)
                or not all(isinstance(entry, str) for entry in allowed_surfaces)
                or not all(isinstance(entry, str) for entry in forbidden_surfaces)
                or not all(isinstance(entry, str) for entry in forbidden_surface_hits)
            ):
                raise TypeError("Surface fields must be list[str]")
            observed = set(observed_surfaces)
            allowed = set(allowed_surfaces)
            forbidden = set(forbidden_surfaces)
            disallowed_observed = observed.difference(allowed)
            forbidden_observed = observed.intersection(forbidden)
            violation_count = len(disallowed_observed.union(forbidden_observed)) + len(forbidden_surface_hits)
            adherence = 1.0 if violation_count == 0 else 0.0
        except (KeyError, TypeError) as exc:
            logger.warning("Unable to compute surface-gated success score: %s", exc)
            return MetricResult(scores=[MetricScore(name="surface_gated_success", value=nan)])
        success = item.get(self.success_key) is True and adherence == 1.0
        return MetricResult(scores=[MetricScore(name="surface_gated_success", value=float(success))])
