# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Tests for analysis/mechanical.py — parser plumbing and skill-aware gating."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from nemo_agents_plugin.improvement.analysis.mechanical import cluster_evals, mechanical_analysis
from nemo_agents_plugin.improvement.models import (
    BatchResult,
    EvalResult,
    EvalStatus,
    EvalTiming,
)
from nemo_agents_plugin.improvement.traces.base import TraceSummary


@dataclass
class FakeTraceParser:
    """Test stand-in for ``TraceParser`` — a dict of pre-built summaries."""

    summaries: dict[str, TraceSummary] = field(default_factory=dict)
    name: str = "fake"
    supports_skills: bool = True

    def summarize(self, output_dir: Path, eval_name: str) -> TraceSummary:
        """Return the pre-built summary for *eval_name*, or an empty one."""
        return self.summaries.get(eval_name, TraceSummary(eval_name=eval_name))


def _failing_result(name: str, job_dir: Path) -> EvalResult:
    """Build a FAIL ``EvalResult`` whose ``job_dir`` exists on disk."""
    job_dir.mkdir(parents=True, exist_ok=True)
    return EvalResult(
        eval_name=name,
        status=EvalStatus.FAIL,
        timing=EvalTiming(duration_sec=10.0),
        agent_timing=EvalTiming(duration_sec=8.0),
        job_dir=job_dir,
    )


def _batch(results: list[EvalResult]) -> BatchResult:
    """Wrap *results* in a minimal ``BatchResult``."""
    return BatchResult(batch_id="b", started_at=datetime.now(timezone.utc), results=results)


def test_mechanical_uses_parser_for_error_patterns(tmp_path: Path) -> None:
    """Errors flow through the parser; pattern key is the first 100 chars of the first line."""
    parser = FakeTraceParser(
        summaries={
            "eval-a": TraceSummary(
                eval_name="eval-a",
                error_excerpts=["TimeoutError: deadline exceeded"],
                skill_names=["search"],
            ),
            "eval-b": TraceSummary(
                eval_name="eval-b",
                error_excerpts=["TimeoutError: deadline exceeded"],
                skill_names=["search"],
            ),
        }
    )
    batch = _batch(
        [
            _failing_result("eval-a", tmp_path / "a"),
            _failing_result("eval-b", tmp_path / "b"),
        ]
    )

    mech = mechanical_analysis(batch, parser)

    pattern = "TimeoutError: deadline exceeded"
    assert pattern in mech.error_patterns
    assert sorted(mech.error_patterns[pattern]) == ["eval-a", "eval-b"]


def test_mechanical_skips_skill_tracking_when_parser_does_not_support(tmp_path: Path) -> None:
    """Non-skill-aware parser → skill_usage stays None; no missing_skill cluster fires."""
    parser = FakeTraceParser(
        supports_skills=False,
        summaries={
            "eval-a": TraceSummary(eval_name="eval-a", error_excerpts=["boom"]),
            "eval-b": TraceSummary(eval_name="eval-b", error_excerpts=["boom"]),
        },
    )
    batch = _batch(
        [
            _failing_result("eval-a", tmp_path / "a"),
            _failing_result("eval-b", tmp_path / "b"),
        ]
    )

    mech = mechanical_analysis(batch, parser)
    clusters = cluster_evals(mech, batch=batch)

    assert mech.skill_usage is None
    assert all(c.signal_type != "missing_skill" for c in clusters)


def test_mechanical_populates_skill_usage_for_skill_aware_parser(tmp_path: Path) -> None:
    """Skill-aware parser → skill_usage is populated with per-eval skill names."""
    parser = FakeTraceParser(
        supports_skills=True,
        summaries={
            "eval-a": TraceSummary(eval_name="eval-a", skill_names=["search"]),
            "eval-b": TraceSummary(eval_name="eval-b", skill_names=[]),
        },
    )
    batch = _batch(
        [
            _failing_result("eval-a", tmp_path / "a"),
            _failing_result("eval-b", tmp_path / "b"),
        ]
    )

    mech = mechanical_analysis(batch, parser)

    assert mech.skill_usage is not None
    assert mech.skill_usage.skills_by_eval == {"eval-a": ["search"]}
    assert mech.skill_usage.evals_without_skills == ["eval-b"]


def test_mechanical_runs_without_a_parser(tmp_path: Path) -> None:
    """parser=None → trace-derived signals empty; runner-agnostic signals still populate.

    Used for batches whose agent has no registered parser. ``analyze-job`` then
    produces mechanical-only output instead of failing.
    """
    batch = _batch(
        [
            _failing_result("eval-a", tmp_path / "a"),
            _failing_result("eval-b", tmp_path / "b"),
        ]
    )

    mech = mechanical_analysis(batch, parser=None)

    # Trace-derived signals are empty
    assert mech.error_patterns == {}
    assert mech.skill_usage is None
    # Runner-agnostic signals still work
    assert sorted(mech.failing_evals) == ["eval-a", "eval-b"]
    # cluster_evals doesn't fire missing_skill (skill_usage is None)
    clusters = cluster_evals(mech, batch=batch)
    assert all(c.signal_type != "missing_skill" for c in clusters)
