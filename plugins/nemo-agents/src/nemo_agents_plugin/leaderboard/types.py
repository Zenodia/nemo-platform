# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Internal data shapes for usage leaderboard workflows.

These dataclasses are the canonical in-memory representation shared by the
normalize, rank, and render steps. They preserve a copy of the original
raw payload so the CLI can keep a typed working model without losing
access to the source report content.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Mapping


@dataclass(frozen=True, slots=True)
class AgentLeaderboardEntry:
    """Canonical internal representation of one ranked usage report."""

    entry_id: str
    task_name: str
    compute_units: float
    compute_units_formula_version: str | None = None
    token_count: int | None = None
    runtime_image: str | None = None
    created_at: datetime | None = None
    source_path: str | None = None
    source_dir: str | None = None
    run_count: int = 1
    raw_report: Mapping[str, object] = field(default_factory=dict)

    @property
    def compute_units_per_token(self) -> float | None:
        """Return compute-units per token when both values are positive."""
        if self.compute_units <= 0 or self.token_count is None or self.token_count <= 0:
            return None
        return self.compute_units / self.token_count


@dataclass(frozen=True, slots=True)
class AgentLeaderboardWarning:
    """Non-fatal warning captured while building a leaderboard."""

    message: str
    source_path: str | None = None


@dataclass(frozen=True, slots=True)
class AgentLeaderboard:
    """Normalized leaderboard payload ready for ranking and rendering."""

    entries: tuple[AgentLeaderboardEntry, ...]
    warnings: tuple[AgentLeaderboardWarning, ...] = ()
