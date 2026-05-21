# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Generate human-readable markdown reports from analysis results."""

from nemo_agents_plugin.improvement.models import GapAnalysis, GapCategory, MechanicalAnalysis


def _fmt_duration(seconds: float) -> str:
    if seconds <= 0:
        return "-"
    minutes = int(seconds) // 60
    secs = int(seconds) % 60
    return f"{minutes}:{secs:02d}"


def _category_label(cat: GapCategory) -> str:
    return {
        GapCategory.MISSING_SKILL: "Missing skill",
        GapCategory.INADEQUATE_SKILL: "Inadequate skill",
        GapCategory.CLI_GAP: "CLI gap",
        GapCategory.CLI_ERGONOMICS: "CLI ergonomics",
        GapCategory.FUNDAMENTAL: "Fundamental",
    }.get(cat, cat.value)


def generate_mechanical_report(mechanical: MechanicalAnalysis) -> str:
    """Markdown report for mechanical-only analysis."""
    lines: list[str] = []

    lines.append("# Mechanical Analysis")
    lines.append("")

    # Summary
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- **Failing evals:** {len(mechanical.failing_evals)}")
    lines.append(f"- **Regressions:** {len(mechanical.regressions)}")
    lines.append(f"- **Error patterns:** {len(mechanical.error_patterns)}")
    lines.append("")

    # Failing evals
    if mechanical.failing_evals:
        lines.append("## Failing Evals")
        lines.append("")
        for name in sorted(mechanical.failing_evals):
            lines.append(f"- {name}")
        lines.append("")

    # Regressions
    if mechanical.regressions:
        lines.append("## Regressions vs Baseline")
        lines.append("")
        for name in sorted(mechanical.regressions):
            lines.append(f"- {name}")
        lines.append("")

    # Error patterns
    if mechanical.error_patterns:
        lines.append("## Error Patterns")
        lines.append("")
        for pattern, eval_names in sorted(mechanical.error_patterns.items(), key=lambda x: -len(x[1])):
            lines.append(f"### {len(eval_names)} evals")
            lines.append("```")
            lines.append(pattern)
            lines.append("```")
            lines.append(f"Affected: {', '.join(sorted(eval_names))}")
            lines.append("")

    # Slowest evals
    if mechanical.slowest_evals:
        lines.append("## Slowest Evals")
        lines.append("")
        lines.append("| Eval | Duration |")
        lines.append("|------|----------|")
        for name, duration in mechanical.slowest_evals:
            lines.append(f"| {name} | {_fmt_duration(duration)} |")
        lines.append("")

    # Highest tool count
    if mechanical.highest_tool_count:
        lines.append("## Most Tool Calls")
        lines.append("")
        lines.append("| Eval | Tool Calls |")
        lines.append("|------|------------|")
        for name, count in mechanical.highest_tool_count:
            lines.append(f"| {name} | {count} |")
        lines.append("")

    # Tool distribution
    if mechanical.tool_usage_distribution:
        lines.append("## Tool Usage Distribution")
        lines.append("")
        lines.append("| Tool | Total Calls |")
        lines.append("|------|-------------|")
        for tool, count in mechanical.tool_usage_distribution.items():
            lines.append(f"| {tool} | {count} |")
        lines.append("")

    # Skill usage
    if mechanical.skill_usage:
        if mechanical.skill_usage.evals_without_skills:
            lines.append("## Evals Without Skills")
            lines.append("")
            for name in sorted(mechanical.skill_usage.evals_without_skills):
                lines.append(f"- {name}")
            lines.append("")

        if mechanical.skill_usage.skills_by_eval:
            lines.append("## Skill Usage by Eval")
            lines.append("")
            lines.append("| Eval | Skills Loaded |")
            lines.append("|------|---------------|")
            for name, skills in sorted(mechanical.skill_usage.skills_by_eval.items()):
                lines.append(f"| {name} | {', '.join(skills)} |")
            lines.append("")

    return "\n".join(lines)


def generate_gap_report(gap: GapAnalysis) -> str:
    """Markdown report for full gap analysis (mechanical + clusters + hypotheses)."""
    lines: list[str] = []

    lines.append("# Gap Analysis")
    lines.append("")
    lines.append(f"**Batch:** `{gap.batch_id}`")
    lines.append(f"**Generated:** {gap.generated_at.strftime('%Y-%m-%d %H:%M:%S UTC')}")
    lines.append("")

    # High-level summary
    m = gap.mechanical
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- **Failing evals:** {len(m.failing_evals)}")
    lines.append(f"- **Regressions:** {len(m.regressions)}")
    lines.append(f"- **Clusters:** {len(gap.clusters)}")
    lines.append(f"- **Hypotheses:** {len(gap.hypotheses)}")
    lines.append("")

    # Clusters
    if gap.clusters:
        lines.append("## Clusters")
        lines.append("")
        for cluster in gap.clusters:
            lines.append(f"### {cluster.cluster_id} — {cluster.signal_type} ({len(cluster.eval_names)} evals)")
            lines.append("")
            lines.append(f"Evals: {', '.join(cluster.eval_names)}")
            if cluster.description:
                lines.append(f"  {cluster.description}")
            if cluster.shared_patterns:
                lines.append("")
                lines.append("Shared error patterns:")
                for p in cluster.shared_patterns[:3]:
                    lines.append("```")
                    lines.append(p)
                    lines.append("```")
            lines.append("")

    # Hypotheses — the main output
    if gap.hypotheses:
        lines.append("## Hypotheses (ranked by confidence)")
        lines.append("")
        for i, h in enumerate(gap.hypotheses, 1):
            confidence_bar = "█" * int(h.confidence * 10) + "░" * (10 - int(h.confidence * 10))
            lines.append(
                f"### {i}. {h.cluster_id} — {_category_label(h.category)} [{confidence_bar}] {h.confidence:.0%}"
            )
            lines.append("")
            lines.append(f"**Evals:** {', '.join(h.eval_names)}")
            lines.append(f"**Root cause:** {h.root_cause}")
            lines.append(f"**Proposed fix:** {h.proposed_fix}")
            if h.affected_files:
                lines.append(f"**Files:** {', '.join(f'`{f}`' for f in h.affected_files)}")
            if h.expected_impact:
                lines.append(f"**Expected impact:** {h.expected_impact}")
            lines.append("")

    # Mechanical details (collapsed for full analysis)
    lines.append("## Mechanical Details")
    lines.append("")

    if m.error_patterns:
        lines.append("### Error Patterns")
        lines.append("")
        for pattern, eval_names in sorted(m.error_patterns.items(), key=lambda x: -len(x[1])):
            lines.append(f"- **{len(eval_names)} evals:** {', '.join(sorted(eval_names))}")
            lines.append(f"  `{pattern[:80]}`")
        lines.append("")

    if m.slowest_evals:
        lines.append("### Slowest Evals")
        lines.append("")
        lines.append("| Eval | Duration |")
        lines.append("|------|----------|")
        for name, duration in m.slowest_evals:
            lines.append(f"| {name} | {_fmt_duration(duration)} |")
        lines.append("")

    if m.tool_usage_distribution:
        lines.append("### Tool Usage Distribution")
        lines.append("")
        lines.append("| Tool | Total Calls |")
        lines.append("|------|-------------|")
        for tool, count in m.tool_usage_distribution.items():
            lines.append(f"| {tool} | {count} |")
        lines.append("")

    return "\n".join(lines)
