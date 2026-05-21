# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""``TraceParser`` for Claude Code session JSONL.

Parses what the Claude Code CLI emits — keyed on agent, not runner. Works
for any runner whose agent is Claude Code: Harbor today, NAT's claude-code
backend (``nat_runner.py --backend claude-code``) likewise. The session
JSONL lives at ``<trial_dir>/agent/sessions/projects/-app/<id>.jsonl``
regardless of who launched the container.

Wraps the module-level functions in ``claude_code.py`` behind the
``TraceParser`` protocol so every consumer of trace-derived data
(analysis layer + ``runners/_harbor_results.py`` at result-parse time)
goes through the same seam.
"""

from __future__ import annotations

from pathlib import Path

from .base import TraceSummary
from .claude_code import (
    analyze_tool_calls,
    extract_error_patterns,
    extract_skill_names,
    extract_token_usage,
    extract_trace_excerpt,
    find_session_files,
)


def _find_trial_dir(job_dir: Path) -> Path | None:
    """Locate the directory holding a Claude Code session.

    Harbor's job directory contains a trial subdirectory which holds ``agent/``.
    Tests sometimes pass the trial directory directly, so accept either shape.
    Returns ``None`` if *job_dir* is not a directory or has no agent dir.
    """
    if not job_dir.is_dir():
        return None
    if (job_dir / "agent").exists():
        return job_dir
    for child in job_dir.iterdir():
        if child.is_dir() and (child / "agent").exists():
            return child
    return None


class ClaudeCodeTraceParser:
    """Parses Claude Code session.jsonl produced by Harbor (and other runners)."""

    name = "claude-code"
    supports_skills = True

    def summarize(self, output_dir: Path, eval_name: str) -> TraceSummary:
        """Build a ``TraceSummary`` from the session JSONL inside *output_dir*.

        Accepts either a per-trial dir (with ``agent/`` directly inside) or
        a job dir whose children are trial dirs — ``_find_trial_dir`` walks
        one level if needed.
        """
        trial_dir = _find_trial_dir(output_dir)
        if trial_dir is None:
            return TraceSummary(eval_name=eval_name)
        session_files = find_session_files(trial_dir)
        return TraceSummary(
            eval_name=eval_name,
            tool_calls=analyze_tool_calls(trial_dir),
            error_excerpts=extract_error_patterns(trial_dir),
            skill_names=extract_skill_names(trial_dir),
            trace_excerpt=extract_trace_excerpt(trial_dir, max_turns=30),
            token_usage=extract_token_usage(trial_dir),
            session_file=session_files[0] if session_files else None,
        )
