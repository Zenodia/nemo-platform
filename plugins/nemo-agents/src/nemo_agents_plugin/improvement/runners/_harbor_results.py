# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Parse Harbor eval result.json files and session traces into structured models."""

import json
from datetime import datetime, timezone
from pathlib import Path

from nemo_agents_plugin.improvement.models import (
    BatchResult,
    EvalResult,
    EvalStatus,
    EvalTiming,
    TokenUsage,
)
from nemo_agents_plugin.improvement.traces.claude_code_parser import ClaudeCodeTraceParser


def _parse_timestamp(ts: str) -> datetime | None:
    """Parse an ISO 8601 timestamp string. Returns UTC-aware datetime."""
    if not ts:
        return None
    # Try fromisoformat first — handles offset formats like +00:00
    try:
        dt = datetime.fromisoformat(ts)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except ValueError:
        pass
    # Fallback for Z-suffix (Python < 3.11 doesn't handle Z in fromisoformat)
    if ts.endswith("Z"):
        try:
            dt = datetime.fromisoformat(ts[:-1])
            return dt.replace(tzinfo=timezone.utc)
        except ValueError:
            pass
    return None


def _duration_sec(start: datetime | None, end: datetime | None) -> float:
    if start and end:
        return max((end - start).total_seconds(), 0.0)
    return 0.0


def _reward_to_status(reward: float | None) -> EvalStatus:
    if reward is None:
        return EvalStatus.ERROR
    if reward >= 1.0:
        return EvalStatus.PASS
    return EvalStatus.FAIL


def _find_trial_result_file(job_dir: Path) -> Path | None:
    """Find the trial-level result.json (has task_name field) within a job directory.

    Harbor writes two result.json files:
      - job-level: <job_dir>/result.json (no task_name)
      - trial-level: <job_dir>/<trial_id>/result.json (has task_name)

    We want the trial-level one.
    """
    for result_file in sorted(job_dir.rglob("result.json")):
        try:
            data = json.loads(result_file.read_text())
            if "task_name" in data:
                return result_file
        except (json.JSONDecodeError, OSError):
            continue
    return None


def parse_trial_result(job_dir: Path, eval_name: str | None = None) -> EvalResult | None:
    """Parse a trial result from a job directory.

    Args:
        job_dir: Path to the job directory (e.g., jobs/batch-xxx/batch-xxx__eval-name/)
        eval_name: Override for eval name (otherwise extracted from result.json task_name)

    Returns:
        EvalResult or None if no valid trial result found.
    """
    result_file = _find_trial_result_file(job_dir)
    if result_file is None:
        return None

    try:
        data = json.loads(result_file.read_text())
    except (json.JSONDecodeError, OSError):
        return None

    trial_dir = result_file.parent
    task_name = eval_name or data.get("task_name", "")

    # Extract reward
    reward: float | None = None
    verifier = data.get("verifier_result", {})
    if verifier and "rewards" in verifier:
        reward = verifier["rewards"].get("reward")

    # Total timing
    total_start = _parse_timestamp(data.get("started_at", ""))
    total_end = _parse_timestamp(data.get("finished_at", ""))

    # Agent timing
    agent_exec = data.get("agent_execution", {})
    agent_start = _parse_timestamp(agent_exec.get("started_at", ""))
    agent_end = _parse_timestamp(agent_exec.get("finished_at", ""))

    # Trace-derived fields go through the parser — single seam for every
    # consumer of trace-derived data (analysis layer reads other fields off
    # the same TraceSummary later). Harbor only runs claude-code today.
    summary = ClaudeCodeTraceParser().summarize(trial_dir, task_name)

    # Token usage. Harbor populates agent_result.n_*_tokens for runners that
    # report usage, but the Claude Code runner currently leaves them null —
    # fall back to the parser's session-JSONL summation.
    agent_result = data.get("agent_result", {})
    tokens = TokenUsage(
        input_tokens=agent_result.get("n_input_tokens") or 0,
        output_tokens=agent_result.get("n_output_tokens") or 0,
        cache_tokens=agent_result.get("n_cache_tokens") or 0,
    )
    if tokens.input_tokens == 0 and tokens.output_tokens == 0 and tokens.cache_tokens == 0:
        if summary.token_usage is not None:
            tokens = summary.token_usage

    # Exception info
    exception = None
    exc_info = data.get("exception_info")
    if exc_info:
        exception = str(exc_info)[:1000]

    return EvalResult(
        eval_name=task_name,
        status=_reward_to_status(reward),
        reward=reward,
        timing=EvalTiming(
            started_at=total_start,
            finished_at=total_end,
            duration_sec=_duration_sec(total_start, total_end),
        ),
        agent_timing=EvalTiming(
            started_at=agent_start,
            finished_at=agent_end,
            duration_sec=_duration_sec(agent_start, agent_end),
        ),
        tokens=tokens,
        tool_calls=summary.tool_calls,
        exception=exception,
        job_dir=job_dir,
        session_file=summary.session_file,
    )


def parse_batch_results(batch_dir: Path) -> BatchResult:
    """Parse all trial results from a batch directory.

    Scans for result.json files with task_name field. Useful for analyzing
    existing batch runs without re-running.

    Args:
        batch_dir: Path to the batch directory (e.g., jobs/batch-2026-03-30__14-30-00/)

    Returns:
        BatchResult with all parsed trial results.
    """
    batch_id = batch_dir.name

    # Read batch config if available
    model = ""
    agent = "claude-code"
    batch_config = batch_dir / "batch_config.json"
    started_at = datetime.now(timezone.utc)
    if batch_config.exists():
        try:
            config = json.loads(batch_config.read_text())
            model = config.get("model", "")
            agent = config.get("agent", "claude-code")
            ts = _parse_timestamp(config.get("started_at", ""))
            if ts:
                started_at = ts
        except (json.JSONDecodeError, OSError):
            pass

    # Read batch summary for finished_at
    finished_at = None
    batch_summary = batch_dir / "batch_summary.json"
    if batch_summary.exists():
        try:
            summary = json.loads(batch_summary.read_text())
            finished_at = _parse_timestamp(summary.get("finished_at", ""))
        except (json.JSONDecodeError, OSError):
            pass

    # Find all job directories and parse trial results
    results: list[EvalResult] = []
    for child in sorted(batch_dir.iterdir()):
        if not child.is_dir():
            continue
        result = parse_trial_result(child)
        if result:
            results.append(result)

    return BatchResult(
        batch_id=batch_id,
        started_at=started_at,
        finished_at=finished_at,
        model=model,
        agent=agent,
        results=results,
    )
