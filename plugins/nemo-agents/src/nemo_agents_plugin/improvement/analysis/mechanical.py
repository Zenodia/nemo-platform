# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Mechanical analysis of eval results — pure Python, no LLM needed."""

from collections import defaultdict

from nemo_agents_plugin.improvement.baselines import find_regressions
from nemo_agents_plugin.improvement.models import (
    BaselineEntry,
    BatchResult,
    EvalCluster,
    EvalStatus,
    MechanicalAnalysis,
    SkillUsage,
)
from nemo_agents_plugin.improvement.traces.base import TraceParser

# Absolute thresholds for "passing but should be optimized" — fire even on a
# single-eval batch where the relative-to-average outlier logic can't.
ABS_SLOW_DURATION_SEC = 60.0
ABS_HIGH_TOOL_COUNT = 10
ABS_HIGH_TOKEN_COUNT = 5000


def mechanical_analysis(
    batch: BatchResult,
    parser: TraceParser | None,
    baselines: dict[str, BaselineEntry] | None = None,
) -> MechanicalAnalysis:
    """Analyze batch results without LLM assistance.

    Identifies:
    - Failing evals
    - Slowest evals (by agent execution time)
    - Highest tool call counts
    - Error patterns from per-agent trace summaries
    - Regressions vs baseline
    - Overall tool usage distribution

    *parser* is the ``TraceParser`` to use, picked by the caller. Pass
    ``None`` for batches whose traces have no parser yet — trace-derived
    signals (error_patterns, skill_usage) will be empty/None; the
    runner-agnostic signals (failing/slowest/regressions/tool counts from
    EvalResult) populate as usual.
    """
    failing_evals: list[str] = []
    duration_pairs: list[tuple[str, float]] = []
    tool_count_pairs: list[tuple[str, int]] = []
    error_patterns: dict[str, list[str]] = {}
    tool_distribution: dict[str, int] = {}
    skills_by_eval: dict[str, list[str]] = {}
    evals_without_skills: list[str] = []

    for result in batch.results:
        # Failing evals
        if result.status != EvalStatus.PASS:
            failing_evals.append(result.eval_name)

        # Duration tracking
        if result.agent_timing.duration_sec > 0:
            duration_pairs.append((result.eval_name, result.agent_timing.duration_sec))

        # Tool call tracking
        if result.tool_calls.total > 0:
            tool_count_pairs.append((result.eval_name, result.tool_calls.total))
            for tool_name, count in result.tool_calls.by_name.items():
                tool_distribution[tool_name] = tool_distribution.get(tool_name, 0) + count

        # Error patterns and skill usage from traces (only when a parser is available)
        if parser is not None and result.job_dir and result.job_dir.exists():
            summary = parser.summarize(result.job_dir, result.eval_name)
            for err in summary.error_excerpts:
                # Extract first line as the pattern key
                pattern = err.split("\n")[0][:100]
                if pattern not in error_patterns:
                    error_patterns[pattern] = []
                if result.eval_name not in error_patterns[pattern]:
                    error_patterns[pattern].append(result.eval_name)

            if parser.supports_skills:
                if summary.skill_names:
                    skills_by_eval[result.eval_name] = summary.skill_names
                else:
                    evals_without_skills.append(result.eval_name)

    # Sort by worst performance
    slowest = sorted(duration_pairs, key=lambda x: x[1], reverse=True)[:10]
    highest_tools = sorted(tool_count_pairs, key=lambda x: x[1], reverse=True)[:10]

    # Regressions
    regressions: list[str] = []
    if baselines:
        regressions = find_regressions(batch, baselines)

    # Skill usage is only meaningful when we have a skill-aware parser; otherwise
    # leave the field at its default (None) so downstream cluster gating sees
    # the absence (suppresses missing_skill).
    skill_usage = (
        SkillUsage(skills_by_eval=skills_by_eval, evals_without_skills=evals_without_skills)
        if parser is not None and parser.supports_skills
        else None
    )

    return MechanicalAnalysis(
        failing_evals=failing_evals,
        slowest_evals=slowest,
        highest_tool_count=highest_tools,
        error_patterns=error_patterns,
        regressions=regressions,
        tool_usage_distribution=dict(sorted(tool_distribution.items(), key=lambda x: x[1], reverse=True)),
        skill_usage=skill_usage,
    )


def cluster_evals(
    mechanical: MechanicalAnalysis,
    baselines: dict[str, BaselineEntry] | None = None,
    batch: BatchResult | None = None,
    slow_outlier_factor: float = 1.5,
) -> list[EvalCluster]:
    """Group evals into clusters for hypothesis generation.

    Clusters three types of evals:
    1. Failing evals — grouped by shared error patterns (union-find).
    2. New evals — passing but no baseline entry (need initial optimization).
    3. Slow outliers — passing but duration/tool count significantly above average.
    """
    failing = set(mechanical.failing_evals)

    # --- Failing eval clusters (union-find on shared error patterns) ---

    parent: dict[str, str] = {name: name for name in failing}

    def find(x: str) -> str:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a: str, b: str) -> None:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb

    eval_to_patterns: dict[str, set[str]] = {}
    for pattern, eval_names in mechanical.error_patterns.items():
        failing_in_pattern = [n for n in eval_names if n in failing]
        for name in failing_in_pattern:
            eval_to_patterns.setdefault(name, set()).add(pattern)
        for i in range(1, len(failing_in_pattern)):
            union(failing_in_pattern[0], failing_in_pattern[i])

    groups: dict[str, list[str]] = defaultdict(list)
    for name in failing:
        groups[find(name)].append(name)

    clusters: list[EvalCluster] = []
    for i, (_, members) in enumerate(sorted(groups.items(), key=lambda x: -len(x[1]))):
        shared = set()
        for m in members:
            shared |= eval_to_patterns.get(m, set())
        clusters.append(
            EvalCluster(
                cluster_id=f"cluster-{i}",
                eval_names=sorted(members),
                shared_patterns=sorted(shared),
                signal_type="error_pattern" if shared else "unclustered",
            )
        )

    # Add "no skill loaded" cluster for failing evals not yet clustered
    if mechanical.skill_usage:
        already_clustered = {e for c in clusters for e in c.eval_names}
        no_skill = [
            e for e in mechanical.skill_usage.evals_without_skills if e in failing and e not in already_clustered
        ]
        if no_skill:
            clusters.append(
                EvalCluster(
                    cluster_id=f"cluster-{len(clusters)}",
                    eval_names=sorted(no_skill),
                    shared_patterns=[],
                    signal_type="missing_skill",
                    description="Evals that failed without any skill being loaded",
                )
            )

    # --- Optimization clusters from full batch data ---

    if batch is None:
        return clusters

    passing_results = [r for r in batch.results if r.status == EvalStatus.PASS]
    if not passing_results:
        return clusters

    all_passing_names = {r.eval_name for r in passing_results}

    # --- New eval cluster (passing, no baseline) ---

    if baselines is not None:
        new_evals = sorted(name for name in all_passing_names if name not in baselines)
        if new_evals:
            clusters.append(
                EvalCluster(
                    cluster_id=f"cluster-{len(clusters)}",
                    eval_names=new_evals,
                    shared_patterns=[],
                    signal_type="new_eval",
                    description="Passing evals with no baseline — optimize initial performance",
                )
            )

    # --- Slow outlier clusters (passing, but unusually slow or tool-heavy) ---

    durations = {r.eval_name: r.agent_timing.duration_sec for r in passing_results if r.agent_timing.duration_sec > 0}
    tool_counts = {r.eval_name: r.tool_calls.total for r in passing_results if r.tool_calls.total > 0}

    avg_duration = sum(durations.values()) / len(durations) if durations else 0
    avg_tools = sum(tool_counts.values()) / len(tool_counts) if tool_counts else 0
    duration_threshold = avg_duration * slow_outlier_factor
    tool_threshold = avg_tools * slow_outlier_factor

    already_clustered = {e for c in clusters for e in c.eval_names}

    # Slow by duration — relative-to-average OR absolute threshold (whichever fires)
    slow_evals = sorted(
        name
        for name, dur in durations.items()
        if (dur > duration_threshold or dur > ABS_SLOW_DURATION_SEC) and name not in already_clustered
    )
    if slow_evals:
        clusters.append(
            EvalCluster(
                cluster_id=f"cluster-{len(clusters)}",
                eval_names=slow_evals,
                shared_patterns=[],
                signal_type="slow_outlier",
                description=f"Passing evals slower than {max(duration_threshold, ABS_SLOW_DURATION_SEC):.0f}s "
                f"(batch avg {avg_duration:.0f}s, abs threshold {ABS_SLOW_DURATION_SEC:.0f}s, "
                f"{len(slow_evals)} outliers)",
            )
        )
        already_clustered.update(slow_evals)

    # High tool count — relative-to-average OR absolute threshold
    tool_heavy = sorted(
        name
        for name, count in tool_counts.items()
        if (count > tool_threshold or count > ABS_HIGH_TOOL_COUNT) and name not in already_clustered
    )
    if tool_heavy:
        clusters.append(
            EvalCluster(
                cluster_id=f"cluster-{len(clusters)}",
                eval_names=tool_heavy,
                shared_patterns=[],
                signal_type="tool_heavy",
                description=f"Passing evals using more than {max(tool_threshold, ABS_HIGH_TOOL_COUNT):.0f} tool calls "
                f"(batch avg {avg_tools:.0f}, abs threshold {ABS_HIGH_TOOL_COUNT}, "
                f"{len(tool_heavy)} outliers)",
            )
        )
        already_clustered.update(tool_heavy)

    # High token count — only absolute threshold (tokens vary widely; avg is unreliable as a comparator)
    token_counts = {r.eval_name: r.tokens.total for r in passing_results if r.tokens.total > 0}
    token_heavy = sorted(
        name for name, tok in token_counts.items() if tok > ABS_HIGH_TOKEN_COUNT and name not in already_clustered
    )
    if token_heavy:
        clusters.append(
            EvalCluster(
                cluster_id=f"cluster-{len(clusters)}",
                eval_names=token_heavy,
                shared_patterns=[],
                signal_type="token_heavy",
                description=f"Passing evals using more than {ABS_HIGH_TOKEN_COUNT} tokens "
                f"({len(token_heavy)} candidates for token-cost optimization)",
            )
        )

    return clusters
