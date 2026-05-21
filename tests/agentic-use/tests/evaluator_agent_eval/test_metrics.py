# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Tests for evaluator_agent_eval.metrics."""

from math import isnan

import pytest
from evaluator_agent_eval.metrics import (
    DeterministicTaskSuccessMetric,
    LegacySurfaceAvoidanceMetric,
    OutputSchemaValidMetric,
    SurfaceAdherenceMetric,
    SurfaceGatedSuccessMetric,
    TrajectoryEvidenceMetric,
    VerificationScoreMetric,
    default_agent_eval_metrics,
)
from evaluator_agent_eval.schemas import EvaluatorScoringRow
from nemo_evaluator_sdk.metrics.base import Metric

SURFACE_FIELD_KEYS = {
    "observed_surfaces_key": "observed_surfaces",
    "allowed_surfaces_key": "allowed_surfaces",
    "forbidden_surfaces_key": "forbidden_surfaces",
    "forbidden_surface_hits_key": "forbidden_surface_hits",
}
TRAJECTORY_FIELD_KEYS = {
    "trajectory_summary_key": "trajectory_summary",
    "tool_call_count_key": "tool_call_count",
    "failed_command_count_key": "failed_command_count",
    "recovery_event_count_key": "recovery_event_count",
}


def _row(**overrides: object) -> EvaluatorScoringRow:
    data = {
        "task_id": "run-simple-exact-match",
        "agent_runtime": "codex",
        "agent_model": "gpt-5.4",
        "surface_constraint": "standalone_sdk",
        "allowed_surfaces": ["standalone_sdk"],
        "forbidden_surfaces": ["legacy_service"],
        "output_text": "Used nemo_evaluator_sdk only.",
        "task_success": True,
        "verification_score": 1.0,
        "output_schema_valid": True,
        "observed_surfaces": ["standalone_sdk"],
        "trajectory_summary": {"tool_call_count": 3, "failed_command_count": 1, "recovery_event_count": 1},
    }
    data.update(overrides)
    return EvaluatorScoringRow.model_validate(data)


def _scores_by_name(result) -> dict[str, float]:
    return {score.name: score.value for score in result.scores}


@pytest.mark.asyncio
async def test_task_success_metric_can_use_configured_success_key():
    metric = DeterministicTaskSuccessMetric(success_key="verifier_passed")
    result = await metric.compute_scores({"verifier_passed": True}, {})

    assert _scores_by_name(result)["task_success"] == 1.0


@pytest.mark.asyncio
async def test_surface_adherence_penalizes_forbidden_surface_hits():
    metric = SurfaceAdherenceMetric(**SURFACE_FIELD_KEYS)
    result = await metric.compute_scores(
        _row(
            observed_surfaces=["standalone_sdk", "legacy_service"], forbidden_surface_hits=["services/"]
        ).to_dataset_row(),
        {},
    )

    scores = _scores_by_name(result)
    assert scores["surface_adherence"] == 0.0
    assert scores["surface_violation_count"] == 2.0


@pytest.mark.asyncio
async def test_surface_gated_success_requires_task_success_and_adherence():
    metric = SurfaceGatedSuccessMetric(success_key="task_success", **SURFACE_FIELD_KEYS)
    clean = await metric.compute_scores(_row().to_dataset_row(), {})
    violated = await metric.compute_scores(
        _row(observed_surfaces=["standalone_sdk", "legacy_service"]).to_dataset_row(), {}
    )
    failed = await metric.compute_scores(_row(task_success=False).to_dataset_row(), {})

    assert _scores_by_name(clean)["surface_gated_success"] == 1.0
    assert _scores_by_name(violated)["surface_gated_success"] == 0.0
    assert _scores_by_name(failed)["surface_gated_success"] == 0.0


@pytest.mark.asyncio
async def test_surface_gated_success_can_use_configured_success_key():
    metric = SurfaceGatedSuccessMetric(success_key="verifier_passed", **SURFACE_FIELD_KEYS)
    result = await metric.compute_scores(
        _row(task_success=False).to_dataset_row() | {"verifier_passed": True},
        {},
    )

    assert _scores_by_name(result)["surface_gated_success"] == 1.0


@pytest.mark.asyncio
async def test_legacy_surface_avoidance_scans_output_text():
    metric = LegacySurfaceAvoidanceMetric(
        observed_surfaces_key="observed_surfaces",
        forbidden_surface_hits_key="forbidden_surface_hits",
        output_text_key="output_text",
        legacy_surface="legacy_service",
        legacy_text_patterns=("services/", "services\\"),
    )
    result = await metric.compute_scores(
        _row(output_text="I inspected services/evaluator to solve it.").to_dataset_row(), {}
    )

    scores = _scores_by_name(result)
    assert scores["legacy_surface_avoidance"] == 0.0
    assert scores["legacy_surface_hit_count"] == 1.0


@pytest.mark.asyncio
async def test_legacy_surface_avoidance_ignores_negated_mentions():
    metric = LegacySurfaceAvoidanceMetric(
        observed_surfaces_key="observed_surfaces",
        forbidden_surface_hits_key="forbidden_surface_hits",
        output_text_key="output_text",
        legacy_surface="legacy_service",
        legacy_text_patterns=("services/", "services\\"),
    )
    result = await metric.compute_scores(
        _row(output_text="Do not use services/evaluator or any legacy services path.").to_dataset_row(),
        {},
    )

    scores = _scores_by_name(result)
    assert scores["legacy_surface_avoidance"] == 1.0
    assert scores["legacy_surface_hit_count"] == 0.0


@pytest.mark.asyncio
async def test_surface_metrics_can_use_configured_field_keys():
    metric = SurfaceAdherenceMetric(
        observed_surfaces_key="actual",
        allowed_surfaces_key="allowed",
        forbidden_surfaces_key="blocked",
        forbidden_surface_hits_key="blocked_hits",
    )
    result = await metric.compute_scores(
        {
            "actual": ["standalone_sdk", "legacy_service"],
            "allowed": ["standalone_sdk"],
            "blocked": ["legacy_service"],
            "blocked_hits": ["services/"],
        },
        {},
    )

    scores = _scores_by_name(result)
    assert scores["surface_adherence"] == 0.0
    assert scores["surface_violation_count"] == 2.0


@pytest.mark.asyncio
async def test_surface_adherence_returns_nan_for_malformed_surface_fields():
    metric = SurfaceAdherenceMetric(**SURFACE_FIELD_KEYS)
    result = await metric.compute_scores(
        _row().to_dataset_row() | {"observed_surfaces": "standalone_sdk"},
        {},
    )

    scores = _scores_by_name(result)
    assert isnan(scores["surface_adherence"])
    assert isnan(scores["surface_violation_count"])


@pytest.mark.asyncio
async def test_surface_gated_success_returns_nan_for_malformed_surface_fields():
    metric = SurfaceGatedSuccessMetric(success_key="task_success", **SURFACE_FIELD_KEYS)
    result = await metric.compute_scores(
        _row().to_dataset_row() | {"forbidden_surface_hits": [1]},
        {},
    )

    assert isnan(_scores_by_name(result)["surface_gated_success"])


@pytest.mark.asyncio
async def test_surface_gated_success_logs_malformed_surface_error(caplog):
    metric = SurfaceGatedSuccessMetric(success_key="task_success", **SURFACE_FIELD_KEYS)

    with caplog.at_level("WARNING", logger="evaluator_agent_eval.metrics.outcome"):
        result = await metric.compute_scores(
            _row().to_dataset_row() | {"forbidden_surface_hits": [1]},
            {},
        )

    assert isnan(_scores_by_name(result)["surface_gated_success"])
    assert "Surface fields must be list[str]" in caplog.text


@pytest.mark.asyncio
async def test_legacy_surface_avoidance_returns_nan_for_malformed_fields():
    metric = LegacySurfaceAvoidanceMetric(
        observed_surfaces_key="observed_surfaces",
        forbidden_surface_hits_key="forbidden_surface_hits",
        output_text_key="output_text",
        legacy_surface="legacy_service",
        legacy_text_patterns=("services/", "services\\"),
    )
    result = await metric.compute_scores(
        _row().to_dataset_row() | {"output_text": 123},
        {},
    )

    scores = _scores_by_name(result)
    assert isnan(scores["legacy_surface_avoidance"])
    assert isnan(scores["legacy_surface_hit_count"])


def test_metrics_implement_sdk_protocol():
    for metric in default_agent_eval_metrics():
        assert isinstance(metric, Metric)


@pytest.mark.asyncio
async def test_trajectory_metric_requires_summary_not_just_path():
    metric = TrajectoryEvidenceMetric(**TRAJECTORY_FIELD_KEYS)
    with_summary = await metric.compute_scores(_row().to_dataset_row(), {})
    path_only = await metric.compute_scores(
        _row(trajectory_summary=None, atif_trajectory_path="/tmp/trajectory.json").to_dataset_row(),
        {},
    )

    assert _scores_by_name(with_summary)["trajectory_present"] == 1.0
    assert _scores_by_name(path_only)["trajectory_present"] == 0.0


@pytest.mark.asyncio
async def test_trajectory_metric_can_use_configured_field_keys():
    metric = TrajectoryEvidenceMetric(
        trajectory_summary_key="trace_counts",
        tool_call_count_key="tools",
        failed_command_count_key="failures",
        recovery_event_count_key="recoveries",
    )
    result = await metric.compute_scores(
        {"trace_counts": {"tools": 2, "failures": 1, "recoveries": 1}},
        {},
    )

    scores = _scores_by_name(result)
    assert scores["trajectory_present"] == 1.0
    assert scores["tool_call_count"] == 2.0
    assert scores["failed_command_count"] == 1.0
    assert scores["recovery_event_count"] == 1.0


@pytest.mark.asyncio
async def test_trajectory_metric_returns_nan_for_malformed_summary():
    metric = TrajectoryEvidenceMetric(**TRAJECTORY_FIELD_KEYS)
    result = await metric.compute_scores(
        _row().to_dataset_row() | {"trajectory_summary": {"tool_call_count": -1}},
        {},
    )

    scores = _scores_by_name(result)
    assert isnan(scores["trajectory_present"])
    assert isnan(scores["tool_call_count"])
    assert isnan(scores["failed_command_count"])
    assert isnan(scores["recovery_event_count"])


@pytest.mark.asyncio
async def test_verification_score_metric_passes_through_configured_score_key():
    metric = VerificationScoreMetric(score_key="score")
    result = await metric.compute_scores({"score": 0.75}, {})

    assert _scores_by_name(result)["verification_score"] == 0.75


@pytest.mark.asyncio
async def test_verification_score_metric_returns_nan_for_bad_score():
    metric = VerificationScoreMetric(score_key="score")
    result = await metric.compute_scores({"score": 1.5}, {})

    assert isnan(_scores_by_name(result)["verification_score"])


@pytest.mark.asyncio
async def test_output_schema_valid_metric_can_use_configured_key():
    metric = OutputSchemaValidMetric(valid_key="schema_ok")
    result = await metric.compute_scores({"schema_ok": True}, {})

    assert _scores_by_name(result)["output_schema_valid"] == 1.0
