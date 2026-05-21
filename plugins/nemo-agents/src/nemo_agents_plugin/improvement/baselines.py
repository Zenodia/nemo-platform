# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Baseline tracking for eval performance over time."""

import copy
import json
from datetime import datetime, timezone
from pathlib import Path

from nemo_agents_plugin.improvement.models import BaselineEntry, BaselineSnapshot, BatchResult, EvalStatus


def load_baselines(path: Path) -> dict[str, BaselineEntry]:
    """Load baselines.json. Returns empty dict if file doesn't exist."""
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text())
    except (json.JSONDecodeError, OSError):
        return {}

    if not isinstance(data, list):
        return {}

    baselines: dict[str, BaselineEntry] = {}
    for entry in data:
        try:
            history = []
            for h in entry.get("history", []):
                history.append(
                    BaselineSnapshot(
                        timestamp=h["timestamp"],
                        batch_id=h["batch_id"],
                        status=h["status"],
                        duration_sec=h["duration_sec"],
                        tool_calls=h["tool_calls"],
                    )
                )
            baselines[entry["eval_name"]] = BaselineEntry(
                eval_name=entry["eval_name"],
                best_duration_sec=entry["best_duration_sec"],
                best_batch_id=entry["best_batch_id"],
                pass_count=entry["pass_count"],
                total_count=entry["total_count"],
                avg_duration_sec=entry["avg_duration_sec"],
                avg_tool_calls=entry["avg_tool_calls"],
                history=history,
            )
        except (KeyError, TypeError):
            continue
    return baselines


def _serialize_baselines(baselines: dict[str, BaselineEntry]) -> list[dict]:
    data = []
    for bl in sorted(baselines.values(), key=lambda b: b.eval_name):
        entry: dict = {
            "eval_name": bl.eval_name,
            "best_duration_sec": round(bl.best_duration_sec, 1),
            "best_batch_id": bl.best_batch_id,
            "pass_count": bl.pass_count,
            "total_count": bl.total_count,
            "avg_duration_sec": round(bl.avg_duration_sec, 1),
            "avg_tool_calls": bl.avg_tool_calls,
        }
        if bl.history:
            entry["history"] = [
                {
                    "timestamp": h.timestamp,
                    "batch_id": h.batch_id,
                    "status": h.status,
                    "duration_sec": round(h.duration_sec, 1),
                    "tool_calls": h.tool_calls,
                }
                for h in bl.history
            ]
        data.append(entry)
    return data


def save_baselines(baselines: dict[str, BaselineEntry], path: Path) -> None:
    """Save baselines to JSON file and write a date-time versioned snapshot."""
    data = _serialize_baselines(baselines)
    content = json.dumps(data, indent=2) + "\n"

    # Write atomically via tmp file to avoid corruption on interruption
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(".tmp")
    tmp_path.write_text(content)
    tmp_path.replace(path)

    # Write versioned snapshot so we never lose historical data
    history_dir = path.parent / "baselines"
    history_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d__%H-%M-%S")
    snapshot_path = history_dir / f"baselines-{timestamp}.json"
    snapshot_path.write_text(content)


def update_baselines(
    current: dict[str, BaselineEntry],
    batch: BatchResult,
) -> dict[str, BaselineEntry]:
    """Merge batch results into baselines, keeping best-known performance.

    Only updates baseline for evals that passed in this batch.
    Records every run (pass or fail) in the per-eval history.
    """
    updated = copy.deepcopy(current)
    now = datetime.now(timezone.utc).isoformat()

    for result in batch.results:
        snapshot = BaselineSnapshot(
            timestamp=now,
            batch_id=batch.batch_id,
            status=result.status.value,
            duration_sec=result.agent_timing.duration_sec,
            tool_calls=result.tool_calls.total,
        )

        if result.status != EvalStatus.PASS:
            # Still update counts and record the observation
            if result.eval_name in updated:
                updated[result.eval_name].total_count += 1
                updated[result.eval_name].history.append(snapshot)
            else:
                # First time seeing this eval and it failed — record it
                updated[result.eval_name] = BaselineEntry(
                    eval_name=result.eval_name,
                    best_duration_sec=0,
                    best_batch_id="",
                    pass_count=0,
                    total_count=1,
                    avg_duration_sec=0,
                    avg_tool_calls=0,
                    history=[snapshot],
                )
            continue

        duration = result.agent_timing.duration_sec
        tool_count = result.tool_calls.total

        if result.eval_name in updated:
            bl = updated[result.eval_name]
            bl.pass_count += 1
            bl.total_count += 1
            bl.history.append(snapshot)
            # Running average for duration and tool calls
            n = bl.pass_count
            bl.avg_duration_sec = bl.avg_duration_sec * (n - 1) / n + duration / n
            bl.avg_tool_calls = int(bl.avg_tool_calls * (n - 1) / n + tool_count / n)
            # Update best if this run was faster
            if duration < bl.best_duration_sec or bl.best_duration_sec <= 0:
                bl.best_duration_sec = duration
                bl.best_batch_id = batch.batch_id
        else:
            updated[result.eval_name] = BaselineEntry(
                eval_name=result.eval_name,
                best_duration_sec=duration,
                best_batch_id=batch.batch_id,
                pass_count=1,
                total_count=1,
                avg_duration_sec=duration,
                avg_tool_calls=tool_count,
                history=[snapshot],
            )

    return updated


def find_regressions(
    batch: BatchResult,
    baselines: dict[str, BaselineEntry],
    threshold_pct: float = 20.0,
) -> list[str]:
    """Find evals that regressed vs baseline.

    An eval is considered regressed if:
    - It previously passed but now fails, OR
    - It passes but is >threshold_pct% slower than baseline

    Returns list of eval names that regressed.
    """
    regressions: list[str] = []

    for result in batch.results:
        bl = baselines.get(result.eval_name)
        if bl is None:
            continue

        # Previously passing but now failing
        if bl.pass_count > 0 and result.status != EvalStatus.PASS:
            regressions.append(result.eval_name)
            continue

        # Significantly slower
        if result.status == EvalStatus.PASS and bl.best_duration_sec > 0 and result.agent_timing.duration_sec > 0:
            slowdown_pct = (result.agent_timing.duration_sec - bl.best_duration_sec) / bl.best_duration_sec * 100
            if slowdown_pct > threshold_pct:
                regressions.append(result.eval_name)

    return regressions
