# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Normalize raw usage report JSON into canonical leaderboard entries.

The normalizer is the contract boundary between loosely typed JSON and the
internal entry shape used by ranking and rendering. It validates that each
input matches a usage-report model, derives stable display fields, and
preserves the original raw payload for downstream inspection.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Mapping

from nemo_agents_plugin.leaderboard.schema import assess_report_schema
from nemo_agents_plugin.leaderboard.types import AgentLeaderboardEntry
from nemo_agents_plugin.usage.models import BatchUsageReport, UsageReport
from pydantic import ValidationError

_USAGE_TIMESTAMP_FORMAT = "%Y%m%dT%H%M%SZ"
_COMPUTE_UNITS_FORMULA_VERSION = "usage_report_v0_compute_units"


def normalize_report(
    report: Mapping[str, object],
    *,
    source_path: str | Path | None = None,
) -> AgentLeaderboardEntry:
    """Normalize a raw usage report into the canonical leaderboard entry shape."""

    assessment = assess_report_schema(report)
    if not assessment.can_rank:
        raise ValueError(f"Report does not satisfy leaderboard schema: {', '.join(assessment.missing_fields)}")

    resolved_source_path = str(Path(source_path).expanduser().resolve()) if source_path is not None else None
    usage_report = _usage_report(report)
    return _entry_from_usage_report(usage_report, source_path=resolved_source_path)


def normalize_reports(
    reports: tuple[Mapping[str, object], ...],
    *,
    source_paths: tuple[str | Path, ...] | None = None,
) -> tuple[AgentLeaderboardEntry, ...]:
    """Normalize multiple raw usage reports in order."""

    if source_paths is not None and len(source_paths) != len(reports):
        raise ValueError("source_paths length must match reports length")

    return tuple(
        normalize_report(
            report,
            source_path=None if source_paths is None else source_paths[index],
        )
        for index, report in enumerate(reports)
    )


def _usage_report(value: Mapping[str, object]) -> UsageReport | BatchUsageReport:
    try:
        if "task" in value:
            return UsageReport.model_validate(value)
        if "runs" in value:
            return BatchUsageReport.model_validate(value)
    except ValidationError as exc:
        raise ValueError("Report does not satisfy usage report schema") from exc

    raise ValueError("Report must match the UsageReport or BatchUsageReport shape")


def _entry_from_usage_report(
    usage_report: UsageReport | BatchUsageReport,
    *,
    source_path: str | None,
) -> AgentLeaderboardEntry:
    if isinstance(usage_report, UsageReport):
        task = usage_report.task
        if task.compute_units is None:
            raise ValueError("Field 'task.compute_units' must be set for leaderboard ranking")
        created_at = _parse_usage_timestamp(task.timestamp)
        entry_id = _entry_id_from_source(source_path, fallback=f"{task.timestamp}-{task.task}")
        return AgentLeaderboardEntry(
            entry_id=entry_id,
            task_name=task.task,
            compute_units=float(task.compute_units),
            compute_units_formula_version=_COMPUTE_UNITS_FORMULA_VERSION,
            token_count=task.total_tokens,
            runtime_image=task.image,
            created_at=created_at,
            source_path=source_path,
            source_dir=task.source_dir,
            run_count=1,
            raw_report=usage_report.model_dump(mode="python"),
        )

    if usage_report.compute_units_total is None:
        raise ValueError("Field 'compute_units_total' must be set for leaderboard ranking")

    task_names = sorted({run.task for run in usage_report.runs}) or ["batch"]
    newest_run = max(usage_report.runs, key=lambda run: run.timestamp, default=None)
    created_at = None if newest_run is None else _parse_usage_timestamp(newest_run.timestamp)
    entry_id = _entry_id_from_source(source_path, fallback=_batch_fallback_id(usage_report))
    return AgentLeaderboardEntry(
        entry_id=entry_id,
        task_name=_batch_task_label(task_names, run_count=len(usage_report.runs)),
        compute_units=float(usage_report.compute_units_total),
        compute_units_formula_version=_COMPUTE_UNITS_FORMULA_VERSION,
        token_count=usage_report.total_tokens_total,
        runtime_image=_shared_batch_image(usage_report),
        created_at=created_at,
        source_path=source_path,
        source_dir=None,
        run_count=len(usage_report.runs),
        raw_report=usage_report.model_dump(mode="python"),
    )


def _parse_usage_timestamp(value: str) -> datetime:
    try:
        return datetime.strptime(value, _USAGE_TIMESTAMP_FORMAT).replace(tzinfo=timezone.utc)
    except ValueError as exc:
        raise ValueError(f"Report contains an invalid usage timestamp: {value}") from exc


def _shared_batch_image(usage_report: BatchUsageReport) -> str | None:
    images = [run.image for run in usage_report.runs if run.image]
    if not images:
        return None
    first_image = images[0]
    if all(image == first_image for image in images):
        return first_image
    return None


def _entry_id_from_source(source_path: str | None, *, fallback: str) -> str:
    if source_path is None:
        return fallback
    return Path(source_path).name


def _batch_task_label(task_names: list[str], *, run_count: int) -> str:
    if not task_names:
        return f"Batch ({run_count} runs)"
    if len(task_names) == 1:
        return f"{task_names[0]} ({run_count} runs)"
    return f"{task_names[0]} +{len(task_names) - 1} more ({run_count} runs)"


def _batch_fallback_id(usage_report: BatchUsageReport) -> str:
    if not usage_report.runs:
        return "batch"
    newest_run = max(usage_report.runs, key=lambda run: run.timestamp)
    return f"{newest_run.timestamp}-batch"
