# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Tests for ``nemo agents leaderboard`` CLI integration via :class:`CliRunner`."""

from __future__ import annotations


def test_leaderboard_help(app, runner) -> None:
    result = runner.invoke(app, ["leaderboard", "--help"])

    assert result.exit_code == 0, result.output
    assert "Commands for usage leaderboard workflows." in result.output


def test_leaderboard_with_no_args_prints_help(app, runner) -> None:
    result = runner.invoke(app, ["leaderboard"])

    assert result.exit_code in (0, 2), result.output


def test_leaderboard_show_help(app, runner) -> None:
    result = runner.invoke(app, ["leaderboard", "show", "--help"])

    assert result.exit_code == 0, result.output
    assert "Show a ranked leaderboard from local usage report files." in result.output


def test_leaderboard_show_ranks_reports_from_files(app, runner, sample_reports_dir) -> None:
    result = runner.invoke(app, ["leaderboard", "show", str(sample_reports_dir)])

    assert result.exit_code == 0, result.output
    assert "Usage Leaderboard" in result.output
    assert "workspace-basic-mcp" in result.output
    assert "secrets-crud-cli" in result.output
    assert result.output.index("workspace-basic-mcp") < result.output.index("secrets-crud-cli")


def test_leaderboard_show_supports_compact_flag(app, runner, fixtures_dir, tmp_path) -> None:
    report = tmp_path / "report.json"
    report.write_text((fixtures_dir / "report-alpha.json").read_text())

    result = runner.invoke(app, ["leaderboard", "show", str(report), "--compact"])

    assert result.exit_code == 0, result.output
    assert "Compute Units" in result.output
    assert "CU/Token" not in result.output


def test_leaderboard_show_with_invalid_path_exits_nonzero(app, runner, tmp_path) -> None:
    result = runner.invoke(app, ["leaderboard", "show", str(tmp_path / "no-such-dir")])

    assert result.exit_code == 1
    assert "error" in result.output.lower()


def test_leaderboard_show_with_invalid_json_exits_nonzero(app, runner, write_report) -> None:
    report = write_report("report.json", "{not valid json")

    result = runner.invoke(app, ["leaderboard", "show", str(report)])

    assert result.exit_code == 1
    assert "failed to parse json report file" in result.output.lower()
