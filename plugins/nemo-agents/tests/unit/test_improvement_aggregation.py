# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Tests for the multi-trial aggregation logic in the Harbor runner."""

from __future__ import annotations

from pathlib import Path

from nemo_agents_plugin.improvement.models import (
    Difficulty,
    EvalResult,
    EvalSpec,
    EvalStatus,
    EvalTiming,
    TokenUsage,
    ToolCallSummary,
)
from nemo_agents_plugin.improvement.runners._harbor_runner import _aggregate_trials


def _spec(name: str = "x") -> EvalSpec:
    return EvalSpec(
        name=name,
        path=Path("/tmp/x"),
        difficulty=Difficulty.EASY,
        category="",
        tags=[],
        agent_timeout_sec=300.0,
        verifier_timeout_sec=60.0,
    )


def _trial(status: EvalStatus, duration: float, agent_duration: float, tokens: int, tools: int) -> EvalResult:
    return EvalResult(
        eval_name="x",
        status=status,
        timing=EvalTiming(duration_sec=duration),
        agent_timing=EvalTiming(duration_sec=agent_duration),
        tokens=TokenUsage(input_tokens=tokens, output_tokens=0, cache_tokens=0),
        tool_calls=ToolCallSummary(total=tools),
    )


def test_aggregate_majority_pass(tmp_path: Path) -> None:
    trials = [
        _trial(EvalStatus.PASS, 100, 80, 1000, 10),
        _trial(EvalStatus.PASS, 110, 90, 1100, 11),
        _trial(EvalStatus.FAIL, 120, 100, 1200, 12),
    ]
    agg = _aggregate_trials(_spec(), trials, tmp_path)
    assert agg.status == EvalStatus.PASS
    assert agg.trials_count == 3
    assert agg.trial_pass_count == 2
    assert agg.timing.duration_sec == 110  # median of 100, 110, 120
    assert agg.agent_timing.duration_sec == 90
    assert agg.tokens.input_tokens == 1100
    assert agg.tool_calls.total == 11


def test_aggregate_majority_fail_ties_go_fail(tmp_path: Path) -> None:
    """Tie (1 pass, 1 fail) is treated as FAIL — conservative."""
    trials = [
        _trial(EvalStatus.PASS, 100, 80, 1000, 10),
        _trial(EvalStatus.FAIL, 110, 90, 1100, 11),
    ]
    agg = _aggregate_trials(_spec(), trials, tmp_path)
    assert agg.status == EvalStatus.FAIL
    assert agg.trial_pass_count == 1


def test_aggregate_any_error_propagates(tmp_path: Path) -> None:
    """If any trial errored, aggregate is ERROR (don't mask infra problems)."""
    trials = [
        _trial(EvalStatus.PASS, 100, 80, 1000, 10),
        _trial(EvalStatus.PASS, 110, 90, 1100, 11),
        _trial(EvalStatus.ERROR, 0, 0, 0, 0),
    ]
    agg = _aggregate_trials(_spec(), trials, tmp_path)
    assert agg.status == EvalStatus.ERROR


def test_aggregate_writes_trials_json(tmp_path: Path) -> None:
    trials = [
        _trial(EvalStatus.PASS, 100, 80, 1000, 10),
        _trial(EvalStatus.PASS, 110, 90, 1100, 11),
    ]
    _aggregate_trials(_spec("eval-a"), trials, tmp_path)
    trials_path = tmp_path / "eval-a__trials.json"
    assert trials_path.exists()
    import json

    data = json.loads(trials_path.read_text())
    assert data["eval_name"] == "eval-a"
    assert data["trials_count"] == 2
    assert data["trial_pass_count"] == 2
    assert len(data["trials"]) == 2
    assert data["trials"][0]["status"] == "pass"
    assert data["trials"][0]["duration_sec"] == 100


def test_aggregate_handles_empty_durations(tmp_path: Path) -> None:
    """Edge case: trials with zero durations don't blow up."""
    trials = [_trial(EvalStatus.ERROR, 0, 0, 0, 0)]
    agg = _aggregate_trials(_spec(), trials, tmp_path)
    assert agg.status == EvalStatus.ERROR
    assert agg.timing.duration_sec == 0
    assert agg.agent_timing.duration_sec == 0


def test_aggregate_majority_with_3_pass(tmp_path: Path) -> None:
    """All 3 pass → PASS, trial_pass_count=3."""
    trials = [
        _trial(EvalStatus.PASS, 100, 80, 1000, 10),
        _trial(EvalStatus.PASS, 110, 90, 1100, 11),
        _trial(EvalStatus.PASS, 120, 100, 1200, 12),
    ]
    agg = _aggregate_trials(_spec(), trials, tmp_path)
    assert agg.status == EvalStatus.PASS
    assert agg.trial_pass_count == 3
    assert agg.trials_count == 3
