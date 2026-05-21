# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Tests for agent leaderboard local report discovery."""

from __future__ import annotations

from pathlib import Path

import pytest
from nemo_agents_plugin.leaderboard.discovery import discover_report_paths


def test_discover_report_paths_accepts_explicit_json_file(tmp_path: Path):
    report = tmp_path / "result.json"
    report.write_text("{}")

    discovered = discover_report_paths([report])

    assert discovered == (report.resolve(),)


def test_discover_report_paths_rejects_unsupported_explicit_file(tmp_path: Path):
    report = tmp_path / "result.jsonl"
    report.write_text("{}")

    with pytest.raises(ValueError, match="Unsupported report file extension"):
        discover_report_paths([report])


def test_discover_report_paths_rejects_missing_input(tmp_path: Path):
    missing = tmp_path / "missing.json"

    with pytest.raises(FileNotFoundError, match="Input path does not exist"):
        discover_report_paths([missing])


def test_discover_report_paths_recurses_directories_and_ignores_non_json(tmp_path: Path):
    top_level = tmp_path / "result.json"
    top_level.write_text("{}")

    nested_dir = tmp_path / "nested" / "deeper"
    nested_dir.mkdir(parents=True)
    nested_report = nested_dir / "nested-result.json"
    nested_report.write_text("{}")

    ignored = nested_dir / "notes.txt"
    ignored.write_text("ignore me")

    discovered = discover_report_paths([tmp_path])

    assert discovered == tuple(sorted((top_level.resolve(), nested_report.resolve())))


def test_discover_report_paths_deduplicates_explicit_and_directory_hits(tmp_path: Path):
    report = tmp_path / "result.json"
    report.write_text("{}")

    discovered = discover_report_paths([report, tmp_path])

    assert discovered == (report.resolve(),)


def test_discover_report_paths_expands_user_home(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    home = tmp_path / "home"
    home.mkdir()
    report = home / "result.json"
    report.write_text("{}")
    monkeypatch.setenv("HOME", str(home))

    discovered = discover_report_paths(["~/result.json"])

    assert discovered == (report.resolve(),)
