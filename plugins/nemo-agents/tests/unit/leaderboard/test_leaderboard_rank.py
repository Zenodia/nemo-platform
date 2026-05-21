# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Tests for usage leaderboard ranking logic."""

from __future__ import annotations

from datetime import datetime, timezone

from nemo_agents_plugin.leaderboard.rank import rank_entries, rank_leaderboard
from nemo_agents_plugin.leaderboard.types import (
    AgentLeaderboard,
    AgentLeaderboardEntry,
    AgentLeaderboardWarning,
)


def _entry(
    entry_id: str,
    *,
    task_name: str = "workspace-basic-mcp",
    compute_units: float,
    token_count: int | None = None,
    created_at: datetime | None = None,
) -> AgentLeaderboardEntry:
    return AgentLeaderboardEntry(
        entry_id=entry_id,
        task_name=task_name,
        compute_units=compute_units,
        token_count=token_count,
        created_at=created_at,
    )


def test_rank_entries_orders_by_compute_units_then_token_count():
    entries = (
        _entry("run-1", compute_units=30, token_count=3000),
        _entry("run-2", compute_units=20, token_count=4000),
        _entry("run-3", compute_units=20, token_count=2000),
    )

    ranked = rank_entries(entries)

    assert [entry.entry_id for entry in ranked] == ["run-3", "run-2", "run-1"]


def test_rank_entries_prefers_newer_timestamp_when_cost_and_tokens_match():
    older = datetime(2026, 5, 1, 10, 0, 0, tzinfo=timezone.utc)
    newer = datetime(2026, 5, 1, 11, 0, 0, tzinfo=timezone.utc)
    entries = (
        _entry("run-1", compute_units=20, token_count=2000, created_at=older),
        _entry("run-2", compute_units=20, token_count=2000, created_at=newer),
    )

    ranked = rank_entries(entries)

    assert [entry.entry_id for entry in ranked] == ["run-2", "run-1"]


def test_rank_entries_prefers_present_token_count_over_missing_token_count():
    entries = (
        _entry("run-1", compute_units=20, token_count=None),
        _entry("run-2", compute_units=20, token_count=2000),
    )

    ranked = rank_entries(entries)

    assert [entry.entry_id for entry in ranked] == ["run-2", "run-1"]


def test_rank_entries_uses_entry_id_as_final_stable_tiebreak():
    entries = (
        _entry("run-b", compute_units=20, token_count=2000),
        _entry("run-a", compute_units=20, token_count=2000),
    )

    ranked = rank_entries(entries)

    assert [entry.entry_id for entry in ranked] == ["run-a", "run-b"]


def test_rank_leaderboard_preserves_warnings():
    warning = AgentLeaderboardWarning(message="warning")
    leaderboard = AgentLeaderboard(
        entries=(
            _entry("run-1", compute_units=30, token_count=3000),
            _entry("run-2", compute_units=20, token_count=2000),
        ),
        warnings=(warning,),
    )

    ranked = rank_leaderboard(leaderboard)

    assert [entry.entry_id for entry in ranked.entries] == ["run-2", "run-1"]
    assert ranked.warnings == (warning,)
