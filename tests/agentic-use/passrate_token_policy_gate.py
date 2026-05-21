#!/usr/bin/env python3
# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Pass-rate/token policy gate for agentic-use benchmark runs.

This gate uses verifier outcomes from task-local pytest checks and aggregates:
1) pass-rate (`reward`/`passed` from nat_runner result.json)
2) token usage totals (primary optimization objective)
3) runtime totals (secondary tie-breaker when token totals are tied)

It intentionally avoids LLM-as-a-judge scoring so quality/cost comparisons are
stable and reproducible across runs.

For deterministic comparisons, point this gate at fresh comparable artifacts
(same manifest and runner generation). Mixed historical outputs may have
different metric fields available.
"""

from __future__ import annotations

import argparse
import fnmatch
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

TASKS_DIR = Path(__file__).resolve().parent


@dataclass
class GateCheck:
    name: str
    passed: bool
    details: str


def _read_manifest(manifest_path: Path) -> list[str]:
    if not manifest_path.is_absolute():
        manifest_path = (TASKS_DIR / manifest_path).resolve()
    if not manifest_path.exists():
        raise FileNotFoundError(f"Task manifest not found: {manifest_path}")

    patterns: list[str] = []
    for raw_line in manifest_path.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        patterns.append(line)
    return patterns


def _resolve_manifest_tasks(patterns: list[str]) -> set[str]:
    candidates = {
        d.name
        for d in TASKS_DIR.iterdir()
        if d.is_dir() and (d / "instruction.md").exists() and d.name != "example-test-template"
    }
    selected: set[str] = set()
    for pattern in patterns:
        if "*" in pattern or "?" in pattern:
            selected.update(name for name in candidates if fnmatch.fnmatch(name, pattern))
            continue
        if pattern not in candidates:
            raise ValueError(f"Unknown task {pattern!r}. Available: {sorted(candidates)}")
        selected.add(pattern)
    return selected


def _load_results(jobs_dir: Path, tasks_filter: set[str] | None, latest_per_task: bool) -> list[dict[str, Any]]:
    if not jobs_dir.exists():
        raise FileNotFoundError(f"Jobs directory not found: {jobs_dir}")

    # Support both layouts:
    # 1) nat-jobs/<timestamp>-<task>/result.json
    # 2) nat-jobs/<run-batch>/<timestamp>-<task>/result.json
    result_files = sorted(jobs_dir.rglob("result.json"))
    loaded: list[tuple[Path, dict[str, Any]]] = []
    for result_file in result_files:
        try:
            payload = json.loads(result_file.read_text())
        except json.JSONDecodeError:
            continue
        if not isinstance(payload, dict):
            continue
        task_name = payload.get("task")
        if not isinstance(task_name, str):
            continue
        if tasks_filter is not None and task_name not in tasks_filter:
            continue
        loaded.append((result_file, payload))

    if not latest_per_task:
        return [payload for _, payload in loaded]

    latest: dict[str, tuple[float, dict[str, Any]]] = {}
    for result_file, payload in loaded:
        task_name = payload["task"]
        mtime = result_file.stat().st_mtime
        current = latest.get(task_name)
        if current is None or mtime > current[0]:
            latest[task_name] = (mtime, payload)
    return [item[1] for item in sorted(latest.values(), key=lambda x: x[1]["task"])]


_PROVENANCE_FIELDS: tuple[str, ...] = (
    "commit_sha",
    "commit_short",
    "commit_dirty",
    "branch",
    "remote_url",
    "agentic_base_image_digest",
    "pinned",
    "pinned_to_commit",
    "pinned_image_tag",
)


def _aggregate_provenance(results: list[dict[str, Any]]) -> dict[str, Any]:
    """Collapse per-task provenance into a single run-level summary.

    For each known field, if every result reports the same non-None value we
    keep it as a scalar. If results disagree we set the field to ``None`` and
    record the distinct values in ``<field>_observed`` so callers can see the
    inconsistency. If no result reported a value the scalar stays ``None``.
    """
    observed: dict[str, set] = {field: set() for field in _PROVENANCE_FIELDS}
    has_provenance = False
    for result in results:
        prov = result.get("provenance")
        if not isinstance(prov, dict):
            continue
        has_provenance = True
        for field in _PROVENANCE_FIELDS:
            value = prov.get(field)
            if value is not None:
                observed[field].add(value)

    aggregated: dict[str, Any] = {"available": has_provenance}
    for field in _PROVENANCE_FIELDS:
        values = observed[field]
        if len(values) == 1:
            aggregated[field] = next(iter(values))
        else:
            aggregated[field] = None
            if len(values) > 1:
                aggregated[f"{field}_observed"] = sorted(map(str, values))
    return aggregated


def _compute_summary(results: list[dict[str, Any]], selected_tasks: set[str] | None) -> dict[str, Any]:
    # When a manifest is supplied, the manifest defines the denominator: tasks
    # that never produced a parsable result.json count as failures with no
    # token/runtime data, so a partial run cannot false-pass on the surviving
    # subset.
    present_tasks = {task_name for result in results if isinstance((task_name := result.get("task")), str)}
    if selected_tasks is not None:
        missing_tasks = sorted(selected_tasks - present_tasks)
        total = len(selected_tasks)
    else:
        missing_tasks = []
        total = len(results)

    passed = 0
    token_sum = 0
    token_count = 0
    token_unavailable_tasks: list[str] = []
    runtime_sum = 0.0
    runtime_count = 0
    runtime_unavailable_tasks: list[str] = []

    for result in results:
        reward = result.get("reward")
        passed_flag = result.get("passed")
        reward_value = 0.0
        try:
            reward_value = float(reward) if reward is not None else 0.0
        except (TypeError, ValueError):
            reward_value = 0.0
        if passed_flag is True or reward_value >= 1.0:
            passed += 1

        task_name = str(result.get("task"))
        metrics = result.get("metrics", {})
        total_tokens = metrics.get("total_tokens") if isinstance(metrics, dict) else None
        if isinstance(total_tokens, int):
            token_sum += total_tokens
            token_count += 1
        else:
            token_unavailable_tasks.append(task_name)

        runtime_sec = result.get("runtime_sec")
        if isinstance(runtime_sec, int | float):
            runtime_sum += float(runtime_sec)
            runtime_count += 1
        else:
            runtime_unavailable_tasks.append(task_name)

    # Manifest tasks that produced no result.json have no metrics either; mark
    # them unavailable so coverage and metrics-available checks still notice.
    token_unavailable_tasks.extend(missing_tasks)
    runtime_unavailable_tasks.extend(missing_tasks)

    pass_rate = (passed / total) if total else 0.0
    token_coverage = (token_count / total) if total else 0.0
    runtime_coverage = (runtime_count / total) if total else 0.0
    avg_total_tokens = (token_sum / token_count) if token_count else None
    avg_runtime_sec = (runtime_sum / runtime_count) if runtime_count else None

    return {
        "total_tasks": total,
        "passed_tasks": passed,
        "pass_rate": pass_rate,
        "missing_tasks": missing_tasks,
        # ``task_names`` is the canonical observed task set; baseline
        # comparisons require these to match before pass-rate / token / runtime
        # regressions are meaningful.
        "task_names": sorted(present_tasks),
        "total_tokens_sum": token_sum if token_count else None,
        "avg_total_tokens": avg_total_tokens,
        "token_metrics_coverage": token_coverage,
        "token_metrics_available_tasks": token_count,
        "token_metrics_unavailable_tasks": sorted(token_unavailable_tasks),
        "runtime_sec_sum": runtime_sum if runtime_count else None,
        "avg_runtime_sec": avg_runtime_sec,
        "runtime_metrics_coverage": runtime_coverage,
        "runtime_metrics_available_tasks": runtime_count,
        "runtime_metrics_unavailable_tasks": sorted(runtime_unavailable_tasks),
        "selected_tasks": sorted(selected_tasks) if selected_tasks is not None else None,
        "provenance": _aggregate_provenance(results),
    }


def _run_gate_checks(
    summary: dict[str, Any],
    *,
    min_pass_rate: float,
    require_token_metrics: bool,
    baseline_summary: dict[str, Any] | None,
    max_pass_rate_drop: float,
    max_token_regression_pct: float,
    max_runtime_regression_pct: float,
    allow_cross_commit: bool = False,
) -> list[GateCheck]:
    checks: list[GateCheck] = []

    total_tasks = int(summary["total_tasks"])
    pass_rate = float(summary["pass_rate"])
    token_coverage = float(summary["token_metrics_coverage"])
    total_tokens_sum = summary["total_tokens_sum"]
    runtime_coverage = float(summary["runtime_metrics_coverage"])
    runtime_sec_sum = summary["runtime_sec_sum"]
    provenance = summary.get("provenance") or {}
    missing_tasks = summary.get("missing_tasks") or []
    selected_tasks = summary.get("selected_tasks")

    checks.append(
        GateCheck(
            name="non_empty_result_set",
            passed=total_tasks > 0,
            details=f"total_tasks={total_tasks}",
        )
    )
    # When a manifest was supplied, all selected tasks must have produced a
    # result.json. Anything else means the canonical denominator and the
    # observed numerator disagree.
    if selected_tasks is not None:
        checks.append(
            GateCheck(
                name="manifest_tasks_all_present",
                passed=not missing_tasks,
                details=(
                    f"missing_tasks={missing_tasks}"
                    if missing_tasks
                    else f"all {len(selected_tasks)} manifest tasks produced a result.json"
                ),
            )
        )
    checks.append(
        GateCheck(
            name="min_pass_rate",
            passed=pass_rate >= min_pass_rate,
            details=f"pass_rate={pass_rate:.3f}, min_pass_rate={min_pass_rate:.3f}",
        )
    )

    # Provenance: every task in a single run should report the same commit_sha.
    # When provenance is missing entirely we treat that as legacy/skip rather
    # than fail, but we surface the absence in `details`.
    commit_observed = provenance.get("commit_sha_observed")
    if isinstance(commit_observed, list) and len(commit_observed) > 1:
        checks.append(
            GateCheck(
                name="commit_sha_consistent_within_run",
                passed=False,
                details=(
                    "Multiple commit_sha values observed across tasks: "
                    f"{commit_observed}. Re-run the suite from a single commit."
                ),
            )
        )
    elif provenance.get("commit_sha"):
        pinned_label = ""
        if provenance.get("pinned"):
            pinned_label = f", pinned_to={provenance.get('pinned_to_commit') or 'unknown'}"
        checks.append(
            GateCheck(
                name="commit_sha_consistent_within_run",
                passed=True,
                details=(
                    f"commit={provenance.get('commit_short') or provenance['commit_sha'][:12]}"
                    f", branch={provenance.get('branch') or 'detached'}"
                    f", dirty={provenance.get('commit_dirty')}"
                    f"{pinned_label}"
                ),
            )
        )
    else:
        checks.append(
            GateCheck(
                name="commit_sha_consistent_within_run",
                passed=True,
                details="provenance not recorded by runner (legacy artifacts); skipping commit consistency check.",
            )
        )

    if require_token_metrics:
        checks.append(
            GateCheck(
                name="token_metrics_available_for_all_tasks",
                passed=token_coverage == 1.0,
                details=f"token_metrics_coverage={token_coverage:.3f}",
            )
        )
        runtime_detail = f"runtime_metrics_coverage={runtime_coverage:.3f}"
        if runtime_coverage == 0.0:
            runtime_detail += (
                "; no runtime_sec values were found in this result set. "
                "This often indicates older artifacts mixed with newer runs."
            )
        checks.append(
            GateCheck(
                name="runtime_metrics_available_for_all_tasks",
                passed=runtime_coverage == 1.0,
                details=runtime_detail,
            )
        )

    if baseline_summary is not None:
        # Task-set equality: pass-rate, token, and runtime regression checks
        # are only meaningful when baseline and candidate measured the same
        # set of tasks. If the task names differ we short-circuit with a
        # single failing check; the operator must rerun on a matching
        # manifest before regressions can be evaluated.
        baseline_task_names = baseline_summary.get("task_names")
        candidate_task_names = summary.get("task_names")
        task_sets_comparable = True
        if isinstance(baseline_task_names, list) and isinstance(candidate_task_names, list):
            if sorted(baseline_task_names) != sorted(candidate_task_names):
                task_sets_comparable = False
                checks.append(
                    GateCheck(
                        name="baseline_candidate_task_sets_match",
                        passed=False,
                        details=(
                            f"baseline tasks={sorted(baseline_task_names)} "
                            f"candidate tasks={sorted(candidate_task_names)}; "
                            "regression checks short-circuited (rerun on matching manifest)."
                        ),
                    )
                )
            else:
                checks.append(
                    GateCheck(
                        name="baseline_candidate_task_sets_match",
                        passed=True,
                        details=f"both runs measured {len(baseline_task_names)} tasks: {sorted(baseline_task_names)}",
                    )
                )
        else:
            checks.append(
                GateCheck(
                    name="baseline_candidate_task_sets_match",
                    passed=True,
                    details=(
                        "task_names not present on baseline and/or candidate; skipping equality guard "
                        "(legacy summary or unscoped run)."
                    ),
                )
            )

        # Commit-pin check: refuse to compare candidate to baseline when the
        # source tree drifted, unless the operator explicitly opts out.
        baseline_provenance = baseline_summary.get("provenance") or {}
        baseline_commit = baseline_provenance.get("commit_sha")
        candidate_commit = provenance.get("commit_sha")
        if baseline_commit and candidate_commit:
            commits_match = baseline_commit == candidate_commit
            if commits_match:
                detail = f"both runs at commit={baseline_commit[:12]}"
            elif allow_cross_commit:
                detail = (
                    f"baseline_commit={baseline_commit[:12]} != "
                    f"candidate_commit={candidate_commit[:12]}; "
                    "comparison allowed by --allow-cross-commit (numbers may not be apples-to-apples)."
                )
            else:
                detail = (
                    f"baseline_commit={baseline_commit[:12]} != "
                    f"candidate_commit={candidate_commit[:12]}. "
                    "Re-run candidate at the baseline commit, or pass --allow-cross-commit "
                    "to compare anyway (and accept that codebase drift may invalidate the comparison)."
                )
            checks.append(
                GateCheck(
                    name="commit_sha_matches_baseline",
                    passed=commits_match or allow_cross_commit,
                    details=detail,
                )
            )
        else:
            checks.append(
                GateCheck(
                    name="commit_sha_matches_baseline",
                    passed=True,
                    details=(
                        "commit_sha not present on baseline and/or candidate; skipping cross-commit guard "
                        "(legacy artifacts or runner without provenance)."
                    ),
                )
            )

        if not task_sets_comparable:
            # Baseline and candidate measured different task sets; skip the
            # numerical regression checks since their denominators don't
            # match. The single failing ``baseline_candidate_task_sets_match``
            # check above already gates the overall result.
            return checks

        baseline_pass_rate = float(baseline_summary.get("pass_rate", 0.0))
        min_allowed_pass_rate = baseline_pass_rate - max_pass_rate_drop
        checks.append(
            GateCheck(
                name="no_pass_rate_regression_vs_baseline",
                passed=pass_rate >= min_allowed_pass_rate,
                details=(
                    f"pass_rate={pass_rate:.3f}, baseline_pass_rate={baseline_pass_rate:.3f}, "
                    f"max_drop={max_pass_rate_drop:.3f}"
                ),
            )
        )

        baseline_tokens = baseline_summary.get("total_tokens_sum")
        if isinstance(total_tokens_sum, int) and isinstance(baseline_tokens, int):
            max_allowed_tokens = baseline_tokens * (1.0 + max_token_regression_pct / 100.0)
            checks.append(
                GateCheck(
                    name="tokens_not_worse_than_baseline",
                    passed=total_tokens_sum <= max_allowed_tokens,
                    details=(
                        f"total_tokens_sum={total_tokens_sum}, baseline_total_tokens_sum={baseline_tokens}, "
                        f"max_regression_pct={max_token_regression_pct:.2f}"
                    ),
                )
            )
        else:
            checks.append(
                GateCheck(
                    name="tokens_not_worse_than_baseline",
                    passed=False,
                    details=(
                        "Missing token totals for candidate or baseline; cannot run deterministic token comparison."
                    ),
                )
            )

        baseline_runtime = baseline_summary.get("runtime_sec_sum")
        if (
            isinstance(total_tokens_sum, int)
            and isinstance(baseline_tokens, int)
            and total_tokens_sum == baseline_tokens
        ):
            if isinstance(runtime_sec_sum, int | float) and isinstance(baseline_runtime, int | float):
                max_allowed_runtime = float(baseline_runtime) * (1.0 + max_runtime_regression_pct / 100.0)
                checks.append(
                    GateCheck(
                        name="runtime_tie_breaker_not_worse_than_baseline",
                        passed=float(runtime_sec_sum) <= max_allowed_runtime,
                        details=(
                            f"runtime_sec_sum={float(runtime_sec_sum):.3f}, "
                            f"baseline_runtime_sec_sum={float(baseline_runtime):.3f}, "
                            f"max_regression_pct={max_runtime_regression_pct:.2f}"
                        ),
                    )
                )
            else:
                checks.append(
                    GateCheck(
                        name="runtime_tie_breaker_not_worse_than_baseline",
                        passed=False,
                        details=(
                            "Token totals are tied with baseline but runtime totals are missing; "
                            "cannot run deterministic tie-breaker."
                        ),
                    )
                )
        else:
            checks.append(
                GateCheck(
                    name="runtime_tie_breaker_not_worse_than_baseline",
                    passed=True,
                    details=(
                        "Not applicable (token totals differ from baseline); "
                        "runtime tie-breaker only applies when token totals are tied."
                    ),
                )
            )

    return checks


def _normalize_baseline_summary(payload: dict[str, Any]) -> dict[str, Any]:
    """Accept either a raw summary payload or full gate output payload."""
    summary = payload.get("summary")
    if isinstance(summary, dict):
        return summary
    return payload


def _validate_baseline_summary(summary: dict[str, Any], source_path: Path) -> None:
    """Validate baseline summary schema used by deterministic comparisons."""
    missing = [key for key in ("pass_rate", "total_tokens_sum", "runtime_sec_sum") if key not in summary]
    if missing:
        raise ValueError(
            f"Baseline summary {source_path} is missing required key(s): {', '.join(missing)}. "
            "Expected either a gate output JSON with `summary` or a raw summary object."
        )

    pass_rate = summary.get("pass_rate")
    if not isinstance(pass_rate, (int, float)):
        raise ValueError(f"Baseline summary {source_path} has invalid `pass_rate` ({pass_rate!r}); expected number.")

    total_tokens_sum = summary.get("total_tokens_sum")
    if not isinstance(total_tokens_sum, int):
        raise ValueError(
            f"Baseline summary {source_path} has invalid `total_tokens_sum` ({total_tokens_sum!r}); "
            "expected integer token total."
        )

    runtime_sec_sum = summary.get("runtime_sec_sum")
    if runtime_sec_sum is not None and not isinstance(runtime_sec_sum, (int, float)):
        raise ValueError(
            f"Baseline summary {source_path} has invalid `runtime_sec_sum` ({runtime_sec_sum!r}); "
            "expected number or null."
        )


def main() -> int:
    parser = argparse.ArgumentParser(description="Pass-rate/token policy gate for nat_runner outputs.")
    parser.add_argument(
        "--jobs-dir", type=Path, required=True, help="Directory containing nat_runner task output dirs."
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        help="Optional task manifest to scope gate checks to a benchmark suite.",
    )
    parser.add_argument(
        "--latest-per-task",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Use only the latest result.json per task (default: true).",
    )
    parser.add_argument(
        "--min-pass-rate",
        type=float,
        default=1.0,
        help="Absolute pass-rate floor (default: 1.0).",
    )
    parser.add_argument(
        "--require-token-metrics",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Require token metrics to be present for all gated tasks (default: false).",
    )
    parser.add_argument(
        "--baseline-summary",
        type=Path,
        help="Optional JSON summary output from a previous gate run to compare against.",
    )
    parser.add_argument(
        "--max-pass-rate-drop",
        type=float,
        default=0.0,
        help="Allowed pass-rate drop versus baseline summary (default: 0.0).",
    )
    parser.add_argument(
        "--max-token-regression-pct",
        type=float,
        default=0.0,
        help="Allowed token regression percentage versus baseline summary (default: 0.0).",
    )
    parser.add_argument(
        "--max-runtime-regression-pct",
        type=float,
        default=0.0,
        help=(
            "Allowed runtime regression percentage versus baseline summary when token totals are tied (default: 0.0)."
        ),
    )
    parser.add_argument(
        "--allow-cross-commit",
        action="store_true",
        help=(
            "Allow candidate-vs-baseline comparison when the two runs were produced from different "
            "commits. By default the gate fails the comparison so that drift in task definitions, "
            "verifiers, or framework code cannot silently invalidate the numbers."
        ),
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional path to write summary JSON.",
    )
    args = parser.parse_args()

    selected_tasks: set[str] | None = None
    if args.manifest is not None:
        patterns = _read_manifest(args.manifest)
        selected_tasks = _resolve_manifest_tasks(patterns)

    results = _load_results(args.jobs_dir, selected_tasks, args.latest_per_task)
    summary = _compute_summary(results, selected_tasks)

    baseline_summary: dict[str, Any] | None = None
    if args.baseline_summary is not None:
        baseline_payload = json.loads(args.baseline_summary.read_text())
        if not isinstance(baseline_payload, dict):
            raise ValueError(f"Baseline summary must be a JSON object: {args.baseline_summary}")
        baseline_summary = _normalize_baseline_summary(baseline_payload)
        _validate_baseline_summary(baseline_summary, args.baseline_summary)

    checks = _run_gate_checks(
        summary,
        min_pass_rate=args.min_pass_rate,
        require_token_metrics=args.require_token_metrics,
        baseline_summary=baseline_summary,
        max_pass_rate_drop=args.max_pass_rate_drop,
        max_token_regression_pct=args.max_token_regression_pct,
        max_runtime_regression_pct=args.max_runtime_regression_pct,
        allow_cross_commit=args.allow_cross_commit,
    )

    gate_passed = all(check.passed for check in checks)
    payload = {
        "gate_passed": gate_passed,
        "summary": summary,
        "checks": [asdict(check) for check in checks],
    }

    rendered = json.dumps(payload, indent=2)
    print(rendered)
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n")
        print(f"\nWrote pass-rate/token policy gate summary to {args.output}")

    return 0 if gate_passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
