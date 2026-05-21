# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Trace protocol — normalize per-trace-format shapes for the rest of the plugin.

A trace describes what an agent did during an eval run. Different agents
emit different trace formats; ``TraceParser`` is the seam every consumer
that wants trace-derived signal goes through — both at result-parse time
(``runners/_harbor_results.py`` populating ``EvalResult`` fields) and at
analysis time (``analysis/mechanical.py``, ``analysis/llm.py``). Today
the only concrete implementation is ``ClaudeCodeTraceParser`` (Claude
Code's session.jsonl). Future trace formats add their own ``TraceParser``;
callers pick which one to use at the call site.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol, runtime_checkable

from nemo_agents_plugin.improvement.models import TokenUsage, ToolCallSummary


@dataclass
class TraceSummary:
    """Normalized trace summary populated by a ``TraceParser``.

    Fields are best-effort: a parser populates what its trace format
    supports and leaves the rest at defaults / None. Analysis-layer
    consumers read ``error_excerpts`` / ``skill_names`` / ``trace_excerpt``;
    the runner result-parser reads ``tool_calls`` / ``token_usage`` /
    ``session_file`` to populate ``EvalResult`` fields.
    """

    eval_name: str
    tool_calls: ToolCallSummary = field(default_factory=ToolCallSummary)
    error_excerpts: list[str] = field(default_factory=list)
    skill_names: list[str] = field(default_factory=list)
    trace_excerpt: str = ""
    token_usage: TokenUsage | None = None
    session_file: Path | None = None


@runtime_checkable
class TraceParser(Protocol):
    """Protocol for agent-specific trace parsers.

    ``supports_skills`` is a class-level capability flag: True when *this
    parser* can reliably extract skill-load events from its trace source.
    It's a statement about parser visibility, not about the agent — a NAT
    workflow could host a skill-using agent, but a parser that can't see
    those events should still report False so the analysis layer suppresses
    ``missing_skill`` clustering (absence of evidence is not evidence of
    absence).
    """

    name: str
    supports_skills: bool

    def summarize(self, output_dir: Path, eval_name: str) -> TraceSummary:
        """Produce a normalized summary from a trial or job output dir.

        Implementations should handle either shape: a per-trial dir holding
        ``agent/`` directly, or a job dir whose children are trial dirs.
        Must populate ``error_excerpts``, ``skill_names`` (empty list when
        ``supports_skills`` is False), ``trace_excerpt``, and ``tool_calls``
        on the returned ``TraceSummary``.
        """
        ...
