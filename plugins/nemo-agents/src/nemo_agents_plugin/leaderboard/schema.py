# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Schema contract for usage leaderboard report files.

The leaderboard now ranks raw usage-report payloads directly. Each input
file must match one of Max's finalized usage models:

- :class:`nemo_agents_plugin.usage.models.UsageReport`
- :class:`nemo_agents_plugin.usage.models.BatchUsageReport`
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

SUPPORTED_REPORT_EXTENSIONS: tuple[str, ...] = (".json",)

USAGE_REPORT_SINGLE_TASK_FIELD = "task"
USAGE_REPORT_BATCH_RUNS_FIELD = "runs"
SCHEMA_VERSION_FIELD = "schema_version"
CREATED_AT_FIELD = "created_at"


@dataclass(frozen=True, slots=True)
class AgentLeaderboardSchemaAssessment:
    """Assessment of whether a raw report matches the expected schema."""

    can_rank: bool
    missing_fields: tuple[str, ...]


def is_supported_report_path(path: str | Path) -> bool:
    """Return True when the file path has the supported report extension."""
    return Path(path).suffix.lower() in SUPPORTED_REPORT_EXTENSIONS


def assess_report_schema(report: Mapping[str, object]) -> AgentLeaderboardSchemaAssessment:
    """Assess whether a raw report satisfies the usage-report schema."""

    missing_fields: list[str] = []
    if report.get(SCHEMA_VERSION_FIELD) is None:
        missing_fields.append(SCHEMA_VERSION_FIELD)
    if not _has_supported_usage_shape(report):
        missing_fields.append(f"{USAGE_REPORT_SINGLE_TASK_FIELD}|{USAGE_REPORT_BATCH_RUNS_FIELD}")

    return AgentLeaderboardSchemaAssessment(
        can_rank=not missing_fields,
        missing_fields=tuple(missing_fields),
    )


def _has_supported_usage_shape(report: Mapping[str, object]) -> bool:
    return (
        report.get(USAGE_REPORT_SINGLE_TASK_FIELD) is not None or report.get(USAGE_REPORT_BATCH_RUNS_FIELD) is not None
    )
