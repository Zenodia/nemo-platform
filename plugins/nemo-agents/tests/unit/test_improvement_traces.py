# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Tests for the improvement/traces/ submodule."""

from __future__ import annotations

import json
from pathlib import Path

from nemo_agents_plugin.improvement.traces.claude_code import extract_token_usage
from nemo_agents_plugin.improvement.traces.claude_code_parser import ClaudeCodeTraceParser


def _write_jsonl(trial_dir: Path, entries: list[dict]) -> None:
    """Write *entries* as a Harbor-shaped session JSONL under *trial_dir*."""
    sessions_dir = trial_dir / "agent" / "sessions" / "projects" / "-app"
    sessions_dir.mkdir(parents=True)
    with (sessions_dir / "session.jsonl").open("w") as f:
        for entry in entries:
            f.write(json.dumps(entry) + "\n")


def test_extract_token_usage_sums_assistant_messages(tmp_path: Path) -> None:
    """Token usage is summed across assistant messages; cache_creation + cache_read combine into cache_tokens."""
    _write_jsonl(
        tmp_path,
        [
            {"type": "user", "message": {"content": "go"}},
            {
                "type": "assistant",
                "message": {
                    "usage": {
                        "input_tokens": 10,
                        "output_tokens": 100,
                        "cache_creation_input_tokens": 500,
                        "cache_read_input_tokens": 0,
                    }
                },
            },
            {
                "type": "assistant",
                "message": {
                    "usage": {
                        "input_tokens": 20,
                        "output_tokens": 200,
                        "cache_creation_input_tokens": 0,
                        "cache_read_input_tokens": 1000,
                    }
                },
            },
        ],
    )

    usage = extract_token_usage(tmp_path)

    assert usage is not None
    assert usage.input_tokens == 30
    assert usage.output_tokens == 300
    assert usage.cache_tokens == 1500


def test_extract_token_usage_returns_none_without_session(tmp_path: Path) -> None:
    """No JSONL → returns None so callers can keep their default zeros."""
    assert extract_token_usage(tmp_path) is None


def test_extract_token_usage_skips_messages_without_usage(tmp_path: Path) -> None:
    """Assistant messages without usage blocks don't contribute and don't crash."""
    _write_jsonl(
        tmp_path,
        [
            {"type": "assistant", "message": {}},
            {
                "type": "assistant",
                "message": {"usage": {"input_tokens": 5, "output_tokens": 7}},
            },
        ],
    )

    usage = extract_token_usage(tmp_path)

    assert usage is not None
    assert usage.input_tokens == 5
    assert usage.output_tokens == 7
    assert usage.cache_tokens == 0


# --- ClaudeCodeTraceParser ---


def test_claude_code_parser_summarizes_session_with_skills_and_errors(tmp_path: Path) -> None:
    """Wraps the existing extract_* helpers; populates skill_names, error_excerpts, trace_excerpt."""
    _write_jsonl(
        tmp_path,
        [
            {
                "type": "assistant",
                "message": {
                    "content": [
                        {"type": "tool_use", "id": "call-1", "name": "Skill", "input": {"skill": "search"}},
                        {"type": "tool_use", "id": "call-2", "name": "Bash", "input": {"command": "ls"}},
                    ]
                },
            },
            {
                "type": "user",
                "message": {
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": "call-2",
                            "content": "permission denied",
                            "is_error": True,
                        }
                    ]
                },
            },
        ],
    )

    parser = ClaudeCodeTraceParser()
    summary = parser.summarize(tmp_path, eval_name="my-eval")

    assert parser.supports_skills is True
    assert summary.eval_name == "my-eval"
    assert summary.skill_names == ["search"]
    assert summary.error_excerpts == ["permission denied"]
    assert "Bash" in summary.trace_excerpt
    assert summary.tool_calls.total == 2
    # session_file points at the JSONL we wrote
    assert summary.session_file is not None
    assert summary.session_file.suffix == ".jsonl"


def test_claude_code_parser_locates_trial_subdir(tmp_path: Path) -> None:
    """When job_dir wraps a trial subdirectory (the Harbor layout), the parser drills in."""
    trial_dir = tmp_path / "trial-0"
    trial_dir.mkdir()
    _write_jsonl(
        trial_dir,
        [
            {
                "type": "assistant",
                "message": {"content": [{"type": "tool_use", "id": "x", "name": "Skill", "input": {"skill": "alpha"}}]},
            }
        ],
    )

    summary = ClaudeCodeTraceParser().summarize(tmp_path, eval_name="harbor-eval")

    assert summary.skill_names == ["alpha"]


def test_claude_code_parser_returns_empty_for_missing_session(tmp_path: Path) -> None:
    """Empty job dir → empty summary, not a crash."""
    summary = ClaudeCodeTraceParser().summarize(tmp_path, eval_name="empty")

    assert summary.error_excerpts == []
    assert summary.skill_names == []
    assert summary.trace_excerpt == ""


def test_claude_code_parser_handles_file_path_as_job_dir(tmp_path: Path) -> None:
    """job_dir pointing at a file (not a dir) → empty summary, not NotADirectoryError."""
    file_path = tmp_path / "not_a_dir.txt"
    file_path.write_text("hello")

    summary = ClaudeCodeTraceParser().summarize(file_path, eval_name="oops")

    assert summary.error_excerpts == []
    assert summary.skill_names == []
    assert summary.trace_excerpt == ""
