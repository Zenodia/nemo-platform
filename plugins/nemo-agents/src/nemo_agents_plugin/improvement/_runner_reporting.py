# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Generate markdown, CSV, and JSON reports from BatchResult data."""

import json
import statistics
from datetime import datetime, timezone

from nemo_agents_plugin.improvement.models import BaselineEntry, BatchResult, EvalResult, EvalStatus


def _fmt_duration(seconds: float) -> str:
    if seconds <= 0:
        return "-"
    minutes = int(seconds) // 60
    secs = int(seconds) % 60
    return f"{minutes}:{secs:02d}"


def _fmt_tokens(n: int) -> str:
    if not n:
        return "-"
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n / 1_000:.1f}k"
    return str(n)


def _fmt_status(result: EvalResult) -> str:
    return result.status.value.upper()


def _pct_diff(before: float, after: float) -> str:
    """Show percentage change. -X% = faster (improvement), +X% = slower (regression)."""
    if before <= 0 or after <= 0:
        return "-"
    pct = (before - after) / before * 100
    if pct >= 0:
        return f"-{pct:.0f}%"
    return f"+{abs(pct):.0f}%"


def generate_markdown_report(
    batch: BatchResult,
    baselines: dict[str, BaselineEntry] | None = None,
) -> str:
    """Produce a markdown report from batch results."""
    lines: list[str] = []

    lines.append("# Harbor CLI Eval Report")
    lines.append("")
    lines.append(f"**Batch:** `{batch.batch_id}`")
    lines.append(f"**Generated:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
    if batch.model:
        lines.append(f"**Model:** `{batch.model}`")
    lines.append(f"**Agent:** `{batch.agent}`")
    lines.append("")

    # Summary
    total = len(batch.results)
    lines.append("## Summary")
    lines.append("")
    lines.append("| Metric | Value |")
    lines.append("|--------|-------|")
    lines.append(f"| Total evals | {total} |")
    lines.append(f"| Passed | {batch.pass_count} |")
    lines.append(f"| Failed | {batch.fail_count} |")
    lines.append(f"| Errors | {batch.error_count} |")
    lines.append(f"| Pass rate | {batch.pass_rate * 100:.0f}% |")
    lines.append("")

    # Timing summary
    durations = [r.agent_timing.duration_sec for r in batch.results if r.agent_timing.duration_sec > 0]
    if durations:
        lines.append("### Timing (Agent Execution)")
        lines.append("")
        lines.append("| Stat | Value |")
        lines.append("|------|-------|")
        lines.append(f"| Mean | {_fmt_duration(statistics.mean(durations))} |")
        lines.append(f"| Median | {_fmt_duration(statistics.median(durations))} |")
        lines.append(f"| Min | {_fmt_duration(min(durations))} |")
        lines.append(f"| Max | {_fmt_duration(max(durations))} |")
        if len(durations) > 1:
            lines.append(f"| Std Dev | {_fmt_duration(statistics.stdev(durations))} |")
        lines.append("")

    # Detailed results table
    lines.append("## Results")
    lines.append("")
    header = "| Eval | Status | Time | Tokens (in) | Tools | Errors |"
    if baselines:
        header += " vs Baseline |"
    lines.append(header)
    sep = "|------|--------|------|-------------|-------|--------|"
    if baselines:
        sep += "-------------|"
    lines.append(sep)

    for r in sorted(batch.results, key=lambda r: r.eval_name):
        row = (
            f"| {r.eval_name} "
            f"| {_fmt_status(r)} "
            f"| {_fmt_duration(r.agent_timing.duration_sec)} "
            f"| {_fmt_tokens(r.tokens.input_tokens)} "
            f"| {r.tool_calls.total} "
            f"| {r.tool_calls.error_count} |"
        )
        if baselines:
            bl = baselines.get(r.eval_name)
            if bl and bl.best_duration_sec > 0 and r.agent_timing.duration_sec > 0:
                row += f" {_pct_diff(bl.best_duration_sec, r.agent_timing.duration_sec)} |"
            else:
                row += " - |"
        lines.append(row)

    lines.append("")

    # Failures section
    failures = [r for r in batch.results if r.status != EvalStatus.PASS]
    if failures:
        lines.append("## Failures & Errors")
        lines.append("")
        for r in failures:
            lines.append(f"### {r.eval_name} ({r.status.value})")
            if r.exception:
                lines.append("```")
                lines.append(r.exception[:500])
                lines.append("```")
            lines.append("")

    # Outcome matrix
    lines.append("## Outcome Matrix")
    lines.append("")
    lines.append("```")
    lines.append(f"{'Eval':<50} {'Status':>8} {'Time':>8}")
    lines.append("-" * 68)
    for r in sorted(batch.results, key=lambda r: r.eval_name):
        status_icon = {
            EvalStatus.PASS: "  PASS",
            EvalStatus.FAIL: "  FAIL",
            EvalStatus.ERROR: "   ERR",
            EvalStatus.SKIPPED: "  SKIP",
        }[r.status]
        lines.append(f"{r.eval_name:<50} {status_icon:>8} {_fmt_duration(r.agent_timing.duration_sec):>8}")
    lines.append("```")
    lines.append("")

    return "\n".join(lines)


def generate_csv_report(batch: BatchResult) -> str:
    """Generate a CSV report from batch results."""
    lines = [
        "eval_name,status,reward,agent_duration_sec,total_duration_sec,"
        "input_tokens,cache_tokens,output_tokens,tool_calls,tool_errors,exception"
    ]
    for r in sorted(batch.results, key=lambda r: r.eval_name):
        exc = (r.exception or "").replace('"', '""').replace("\n", " ").replace("\r", " ")
        lines.append(
            f"{r.eval_name},{r.status.value},{r.reward},"
            f"{r.agent_timing.duration_sec:.1f},{r.timing.duration_sec:.1f},"
            f"{r.tokens.input_tokens},{r.tokens.cache_tokens},{r.tokens.output_tokens},"
            f"{r.tool_calls.total},{r.tool_calls.error_count},"
            f'"{exc}"'
        )
    return "\n".join(lines)


def generate_json_report(batch: BatchResult) -> str:
    """Generate a JSON report from batch results."""
    data = []
    for r in sorted(batch.results, key=lambda r: r.eval_name):
        data.append(
            {
                "eval_name": r.eval_name,
                "status": r.status.value,
                "reward": r.reward,
                "agent_duration_sec": round(r.agent_timing.duration_sec, 1),
                "total_duration_sec": round(r.timing.duration_sec, 1),
                "input_tokens": r.tokens.input_tokens,
                "cache_tokens": r.tokens.cache_tokens,
                "output_tokens": r.tokens.output_tokens,
                "tool_calls": r.tool_calls.total,
                "tool_errors": r.tool_calls.error_count,
                "tool_calls_by_name": r.tool_calls.by_name,
                "exception": r.exception,
            }
        )
    return json.dumps(data, indent=2)
