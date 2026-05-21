# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Tests for agent leaderboard raw JSON loading."""

from __future__ import annotations

from pathlib import Path

import pytest
from nemo_agents_plugin.leaderboard.load import load_report, load_reports


def test_load_report_reads_single_json_object(tmp_path: Path):
    report = tmp_path / "result.json"
    report.write_text(
        """
        {
          "submission_id": "sub-1",
          "submission_name": "Submission 1",
          "agent_name": "hero-agent",
          "score": 0.91,
          "usage_report": {
            "schema_version": "v0",
            "task": {
              "task": "workspace-basic-mcp",
              "timestamp": "20260429T220000Z",
              "image": "llama-8b",
              "reward": 1,
              "build_status": "ok",
              "agent_status": "ok",
              "verify_status": "ok",
              "prompt_tokens": 1500,
              "completion_tokens": 500,
              "total_tokens": 2000,
              "compute_units": 16000,
              "source_dir": "/tmp/workspace-basic-mcp"
            }
          }
        }
        """
    )

    loaded = load_report(report)

    assert loaded == {
        "submission_id": "sub-1",
        "submission_name": "Submission 1",
        "agent_name": "hero-agent",
        "score": 0.91,
        "usage_report": {
            "schema_version": "v0",
            "task": {
                "task": "workspace-basic-mcp",
                "timestamp": "20260429T220000Z",
                "image": "llama-8b",
                "reward": 1,
                "build_status": "ok",
                "agent_status": "ok",
                "verify_status": "ok",
                "prompt_tokens": 1500,
                "completion_tokens": 500,
                "total_tokens": 2000,
                "compute_units": 16000,
                "source_dir": "/tmp/workspace-basic-mcp",
            },
        },
    }


def test_load_report_rejects_top_level_array(tmp_path: Path):
    report = tmp_path / "result.json"
    report.write_text('[{"submission_id": "sub-1"}]')

    with pytest.raises(ValueError, match="top-level JSON object"):
        load_report(report)


def test_load_report_raises_json_decode_error_for_invalid_json(tmp_path: Path):
    report = tmp_path / "result.json"
    report.write_text("{not valid json")

    with pytest.raises(ValueError, match=f"Failed to parse JSON report file {report}"):
        load_report(report)


def test_load_reports_preserves_input_order(tmp_path: Path):
    report1 = tmp_path / "a.json"
    report2 = tmp_path / "b.json"
    report1.write_text('{"submission_id": "a"}')
    report2.write_text('{"submission_id": "b"}')

    loaded = load_reports((report2, report1))

    assert loaded == (
        {"submission_id": "b"},
        {"submission_id": "a"},
    )
