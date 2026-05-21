# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Tests for evaluator_agent_eval.atif."""

import json
from pathlib import Path

import pytest
from evaluator_agent_eval.atif import load_atif_trajectory, summarize_atif_trajectory


def test_load_atif_trajectory_validates_with_nat_atif(tmp_path: Path, atif_payload: dict[str, object]):
    path = tmp_path / "trajectory.json"
    path.write_text(json.dumps(atif_payload), encoding="utf-8")

    trajectory = load_atif_trajectory(path)

    assert trajectory.schema_version == "ATIF-v1.6"
    assert trajectory.session_id == "session-1"
    assert len(trajectory.steps) == 3


def test_load_atif_trajectory_rejects_invalid_shape(tmp_path: Path):
    path = tmp_path / "trajectory.json"
    path.write_text(json.dumps({"steps": []}), encoding="utf-8")

    with pytest.raises(ValueError, match="Invalid ATIF trajectory"):
        load_atif_trajectory(path)


def test_summarize_atif_trajectory_counts_tool_calls_failures_and_recovery(
    tmp_path: Path,
    atif_payload: dict[str, object],
):
    path = tmp_path / "trajectory.json"
    path.write_text(json.dumps(atif_payload), encoding="utf-8")

    summary = summarize_atif_trajectory(path)

    assert summary.tool_call_count == 2
    assert summary.failed_command_count == 1
    assert summary.recovery_event_count == 1
