# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Tests for the usage leaderboard report schema."""

from __future__ import annotations

from pathlib import Path

from nemo_agents_plugin.leaderboard.schema import (
    CREATED_AT_FIELD,
    SCHEMA_VERSION_FIELD,
    SUPPORTED_REPORT_EXTENSIONS,
    USAGE_REPORT_BATCH_RUNS_FIELD,
    USAGE_REPORT_SINGLE_TASK_FIELD,
    assess_report_schema,
    is_supported_report_path,
)


def test_supported_report_extensions_are_json_only():
    assert SUPPORTED_REPORT_EXTENSIONS == (".json",)


def test_report_path_support_is_case_insensitive(tmp_path: Path):
    json_path = tmp_path / "result.json"
    uppercase_json_path = tmp_path / "RESULT.JSON"
    jsonl_path = tmp_path / "result.jsonl"

    assert is_supported_report_path(str(json_path))
    assert is_supported_report_path(str(uppercase_json_path))
    assert not is_supported_report_path(str(jsonl_path))


def test_schema_constants_are_explicit():
    assert SCHEMA_VERSION_FIELD == "schema_version"
    assert USAGE_REPORT_SINGLE_TASK_FIELD == "task"
    assert USAGE_REPORT_BATCH_RUNS_FIELD == "runs"
    assert CREATED_AT_FIELD == "created_at"


def test_assessment_accepts_single_usage_report():
    assessment = assess_report_schema(
        {
            "schema_version": "v0",
            "task": {"task": "workspace-basic-mcp"},
        }
    )

    assert assessment.can_rank is True
    assert assessment.missing_fields == ()


def test_assessment_accepts_batch_usage_report():
    assessment = assess_report_schema(
        {
            "schema_version": "v0",
            "runs": [],
        }
    )

    assert assessment.can_rank is True
    assert assessment.missing_fields == ()


def test_assessment_rejects_report_missing_schema_version():
    assessment = assess_report_schema(
        {
            "task": {"task": "workspace-basic-mcp"},
        }
    )

    assert assessment.can_rank is False
    assert assessment.missing_fields == ("schema_version",)


def test_assessment_rejects_report_missing_usage_shape():
    assessment = assess_report_schema(
        {
            "schema_version": "v0",
        }
    )

    assert assessment.can_rank is False
    assert assessment.missing_fields == ("task|runs",)
