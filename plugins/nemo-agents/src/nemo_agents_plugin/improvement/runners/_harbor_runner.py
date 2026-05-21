# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Async eval runner — orchestrates `harbor run` subprocesses with bounded concurrency."""

import asyncio
import json
import os
import statistics
from datetime import datetime, timezone
from pathlib import Path

from nemo_agents_plugin.improvement._agentic_base import build_agentic_base_image
from nemo_agents_plugin.improvement._runner_reporting import (
    generate_csv_report,
    generate_json_report,
    generate_markdown_report,
)
from nemo_agents_plugin.improvement.baselines import load_baselines, save_baselines, update_baselines
from nemo_agents_plugin.improvement.models import (
    BatchResult,
    EvalResult,
    EvalSpec,
    EvalStatus,
    EvalTiming,
    TokenUsage,
    ToolCallSummary,
)
from nemo_agents_plugin.improvement.runners._harbor_results import parse_trial_result
from rich.console import Console
from rich.table import Table

console = Console()

DEFAULT_MODEL = "aws/anthropic/bedrock-claude-sonnet-4-5-v1"


async def run_single_eval(
    eval_spec: EvalSpec,
    batch_dir: Path,
    batch_id: str,
    semaphore: asyncio.Semaphore,
    model: str = DEFAULT_MODEL,
    agent: str = "claude-code",
    n_tasks: int = 1,
    project_root: Path | None = None,
    base_url: str | None = None,
    repeats: int = 1,
) -> EvalResult:
    """Run a single eval via ``harbor run`` (N times if repeats > 1, then aggregate).

    Trials are sequential within a single eval; outer concurrency (the
    semaphore) parallelises across DIFFERENT evals. This keeps the parallelism
    model simple and the cold-cache behaviour predictable per-eval.

    Returns:
        Single EvalResult — either the raw trial (repeats=1) or a median
        aggregate of N trials (repeats>1, with ``trials_count`` set).
    """
    if repeats < 1:
        raise ValueError(f"repeats must be >= 1, got {repeats}")

    async with semaphore:
        if repeats == 1:
            return await _run_one_trial(
                eval_spec,
                batch_dir,
                batch_id,
                model=model,
                agent=agent,
                n_tasks=n_tasks,
                project_root=project_root,
                base_url=base_url,
                trial_suffix="",
            )

        # Multi-trial: run sequentially within this eval
        trials: list[EvalResult] = []
        for i in range(repeats):
            trial = await _run_one_trial(
                eval_spec,
                batch_dir,
                batch_id,
                model=model,
                agent=agent,
                n_tasks=n_tasks,
                project_root=project_root,
                base_url=base_url,
                trial_suffix=f"__trial-{i}",
                trial_idx=i,
                trial_total=repeats,
            )
            trials.append(trial)

        return _aggregate_trials(eval_spec, trials, batch_dir)


async def _run_one_trial(
    eval_spec: EvalSpec,
    batch_dir: Path,
    batch_id: str,
    *,
    model: str,
    agent: str,
    n_tasks: int,
    project_root: Path | None,
    base_url: str | None,
    trial_suffix: str,
    trial_idx: int = 0,
    trial_total: int = 1,
) -> EvalResult:
    """Run one trial of one eval. Returns the parsed EvalResult (no aggregation)."""
    root = (project_root or Path.cwd()).resolve()
    job_name = f"{batch_id}__{eval_spec.name}{trial_suffix}"
    log_file = batch_dir / f"{eval_spec.name}{trial_suffix}.log"

    started_at = datetime.now(timezone.utc)
    label = eval_spec.name if trial_total == 1 else f"{eval_spec.name} (trial {trial_idx + 1}/{trial_total})"
    console.print(f"[{started_at.strftime('%H:%M:%S')}] START: {label}")

    try:
        relative_batch_dir = batch_dir.resolve().relative_to(root)
    except ValueError:
        relative_batch_dir = batch_dir

    env = {**os.environ}
    if base_url:
        env["ANTHROPIC_BASE_URL"] = base_url
    proc = await asyncio.create_subprocess_exec(
        "harbor",
        "run",
        "-p",
        str(eval_spec.path),
        "--agent",
        agent,
        "--model",
        model,
        "--n-tasks",
        str(n_tasks),
        "--job-name",
        job_name,
        "--jobs-dir",
        str(relative_batch_dir),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
        cwd=str(root),
        env=env,
    )
    stdout_bytes, _ = await proc.communicate()
    finished_at = datetime.now(timezone.utc)
    duration = (finished_at - started_at).total_seconds()

    if stdout_bytes:
        log_file.write_bytes(stdout_bytes)

    job_dir = batch_dir / job_name
    result = parse_trial_result(job_dir, eval_name=eval_spec.name)
    if result is None:
        result = EvalResult(
            eval_name=eval_spec.name,
            status=EvalStatus.ERROR,
            timing=EvalTiming(started_at=started_at, finished_at=finished_at, duration_sec=duration),
            exception=f"harbor exited with code {proc.returncode}",
            job_dir=job_dir,
        )

    status_color = {EvalStatus.PASS: "green", EvalStatus.FAIL: "red", EvalStatus.ERROR: "yellow"}.get(
        result.status, "white"
    )
    console.print(
        f"[{finished_at.strftime('%H:%M:%S')}] DONE:  {label} "
        f"[{status_color}]{result.status.value.upper()}[/{status_color}] "
        f"({duration:.0f}s, {result.tool_calls.total} tools)"
    )
    return result


def _aggregate_trials(eval_spec: EvalSpec, trials: list[EvalResult], batch_dir: Path) -> EvalResult:
    """Collapse N trials of one eval into a single representative EvalResult.

    Aggregation rules:
    - status: any ERROR -> ERROR; else majority vote (ties go to FAIL — conservative)
    - duration / tokens / tool calls: median across all trials
    - trial_pass_count + trials_count populated for transparency
    - raw per-trial values written to ``<batch_dir>/<eval_name>__trials.json``
    """
    statuses = [t.status for t in trials]
    if EvalStatus.ERROR in statuses:
        status = EvalStatus.ERROR
    else:
        pass_count = sum(1 for s in statuses if s == EvalStatus.PASS)
        # Tie goes to FAIL (conservative — don't claim a flaky eval as passing)
        status = EvalStatus.PASS if pass_count > len(statuses) / 2 else EvalStatus.FAIL

    pass_count = sum(1 for s in statuses if s == EvalStatus.PASS)

    durations = [t.timing.duration_sec for t in trials if t.timing.duration_sec > 0]
    agent_durations = [t.agent_timing.duration_sec for t in trials if t.agent_timing.duration_sec > 0]
    input_tokens = [t.tokens.input_tokens for t in trials]
    output_tokens = [t.tokens.output_tokens for t in trials]
    cache_tokens = [t.tokens.cache_tokens for t in trials]
    tool_totals = [t.tool_calls.total for t in trials]
    rewards = [t.reward for t in trials if t.reward is not None]

    def _median(xs: list[float]) -> float:
        return float(statistics.median(xs)) if xs else 0.0

    def _median_int(xs: list[int]) -> int:
        return int(statistics.median(xs)) if xs else 0

    aggregate = EvalResult(
        eval_name=eval_spec.name,
        status=status,
        reward=_median(rewards) if rewards else None,
        timing=EvalTiming(duration_sec=_median(durations)),
        agent_timing=EvalTiming(duration_sec=_median(agent_durations)),
        tokens=TokenUsage(
            input_tokens=_median_int(input_tokens),
            output_tokens=_median_int(output_tokens),
            cache_tokens=_median_int(cache_tokens),
        ),
        tool_calls=ToolCallSummary(total=_median_int(tool_totals)),
        job_dir=trials[0].job_dir,
        trials_count=len(trials),
        trial_pass_count=pass_count,
    )

    # Save raw trial data for transparency
    trials_path = batch_dir / f"{eval_spec.name}__trials.json"
    trials_data = {
        "eval_name": eval_spec.name,
        "trials_count": len(trials),
        "trial_pass_count": pass_count,
        "aggregated_status": status.value,
        "trials": [
            {
                "trial_idx": i,
                "status": t.status.value,
                "reward": t.reward,
                "duration_sec": t.timing.duration_sec,
                "agent_duration_sec": t.agent_timing.duration_sec,
                "tokens_total": t.tokens.total,
                "tool_calls_total": t.tool_calls.total,
                "exception": t.exception,
            }
            for i, t in enumerate(trials)
        ],
    }
    trials_path.write_text(json.dumps(trials_data, indent=2) + "\n")

    # Summary line for the aggregate
    color = {EvalStatus.PASS: "green", EvalStatus.FAIL: "red", EvalStatus.ERROR: "yellow"}.get(status, "white")
    span = ""
    if agent_durations:
        span = f", agent {min(agent_durations):.0f}-{max(agent_durations):.0f}s"
    console.print(
        f"  [bold]AGGREGATE: {eval_spec.name}[/bold] "
        f"[{color}]{status.value.upper()}[/{color}] ({pass_count}/{len(trials)} passed) "
        f"median {aggregate.agent_timing.duration_sec:.0f}s{span}, "
        f"median {aggregate.tool_calls.total} tools"
    )
    return aggregate


async def run_batch(
    evals: list[EvalSpec],
    batch_dir: Path,
    concurrency: int = 2,
    model: str = DEFAULT_MODEL,
    agent: str = "claude-code",
    skip_build: bool = False,
    project_root: Path | None = None,
    repeats: int = 1,
) -> BatchResult:
    """Run all evals with bounded concurrency.

    Args:
        evals: List of eval specs to run.
        batch_dir: Directory to store results.
        concurrency: Max parallel harbor runs (across distinct evals).
        model: Model identifier for the agent.
        agent: Agent type (default: claude-code).
        skip_build: Skip Docker image build step.
        project_root: Path to monorepo root.
        repeats: Trials per eval. >1 enables median aggregation per eval.

    Returns:
        BatchResult with one EvalResult per eval (median aggregate when
        repeats>1).
    """
    if concurrency < 1:
        raise ValueError(f"concurrency must be >= 1, got {concurrency}")
    root = (project_root or Path.cwd()).resolve()
    batch_id = batch_dir.name
    started_at = datetime.now(timezone.utc)

    # Validate env
    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise RuntimeError("ANTHROPIC_API_KEY environment variable must be set")

    base_url = os.environ.get("ANTHROPIC_BASE_URL", "")
    if not base_url:
        console.print(
            "[yellow]WARNING: ANTHROPIC_BASE_URL not set, defaulting to https://inference-api.nvidia.com[/yellow]"
        )
        base_url = "https://inference-api.nvidia.com"

    # Build Docker image
    if not skip_build:
        await build_agentic_base_image(root)

    # Create batch directory — refuse to reuse an existing one to avoid mixing results
    if batch_dir.exists():
        raise RuntimeError(f"Batch directory already exists: {batch_dir}. Use a unique --output name.")
    batch_dir.mkdir(parents=True)
    config = {
        "started_at": started_at.isoformat(),
        "max_jobs": concurrency,
        "total_evals": len(evals),
        "evals": [e.name for e in evals],
        "model": model,
        "agent": agent,
    }
    (batch_dir / "batch_config.json").write_text(json.dumps(config, indent=2) + "\n")

    # Print summary
    console.print()
    table = Table(title="Harbor CLI Eval Batch Run")
    table.add_column("Setting", style="bold")
    table.add_column("Value")
    table.add_row("Evals to run", str(len(evals)))
    table.add_row("Max parallel", str(concurrency))
    table.add_row("Output dir", str(batch_dir))
    table.add_row("Model", model)
    console.print(table)
    console.print()

    # Run evals with bounded concurrency
    semaphore = asyncio.Semaphore(concurrency)
    tasks = [
        run_single_eval(
            eval_spec=spec,
            batch_dir=batch_dir,
            batch_id=batch_id,
            semaphore=semaphore,
            model=model,
            agent=agent,
            project_root=root,
            base_url=base_url,
            repeats=repeats,
        )
        for spec in evals
    ]

    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Process results (handle any exceptions from gather)
    eval_results: list[EvalResult] = []
    for i, result in enumerate(results):
        if isinstance(result, BaseException):
            eval_results.append(
                EvalResult(
                    eval_name=evals[i].name,
                    status=EvalStatus.ERROR,
                    exception=str(result),
                )
            )
        else:
            eval_results.append(result)

    finished_at = datetime.now(timezone.utc)

    # Write batch summary
    summary = {
        "finished_at": finished_at.isoformat(),
        "total": len(eval_results),
        "completed": sum(1 for r in eval_results if r.status != EvalStatus.ERROR),
        "passed": sum(1 for r in eval_results if r.status == EvalStatus.PASS),
        "failed": sum(1 for r in eval_results if r.status == EvalStatus.FAIL),
        "errors": sum(1 for r in eval_results if r.status == EvalStatus.ERROR),
    }
    (batch_dir / "batch_summary.json").write_text(json.dumps(summary, indent=2) + "\n")

    batch = BatchResult(
        batch_id=batch_id,
        started_at=started_at,
        finished_at=finished_at,
        model=model,
        agent=agent,
        results=eval_results,
    )

    # Always write reports to the batch directory so we never lose data
    baseline_path = root / "baselines.json"
    baselines = load_baselines(baseline_path)

    (batch_dir / "report.md").write_text(generate_markdown_report(batch, baselines=baselines))
    (batch_dir / "report.csv").write_text(generate_csv_report(batch))
    (batch_dir / "report.json").write_text(generate_json_report(batch))

    # Auto-update baselines with this run's results
    updated_baselines = update_baselines(baselines, batch)
    save_baselines(updated_baselines, baseline_path)

    # Print final summary
    console.print()
    summary_table = Table(title="Batch Run Complete")
    summary_table.add_column("Metric", style="bold")
    summary_table.add_column("Value")
    summary_table.add_row("Total", str(len(eval_results)))
    summary_table.add_row("Passed", f"[green]{batch.pass_count}[/green]")
    summary_table.add_row("Failed", f"[red]{batch.fail_count}[/red]")
    summary_table.add_row("Errors", f"[yellow]{batch.error_count}[/yellow]")
    summary_table.add_row("Pass rate", f"{batch.pass_rate * 100:.0f}%")
    summary_table.add_row("Results", str(batch_dir))
    summary_table.add_row("Baselines", str(baseline_path))
    console.print(summary_table)

    return batch
