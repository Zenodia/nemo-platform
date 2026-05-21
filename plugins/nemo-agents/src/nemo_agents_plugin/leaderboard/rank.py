# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Ranking rules for normalized usage leaderboard entries.

This module is deliberately small and deterministic: given already
normalized entries, it applies the default ordering used by
``nemo agents leaderboard show`` and returns a freshly ordered tuple
without mutating the input objects.
"""

from __future__ import annotations

from datetime import datetime

from nemo_agents_plugin.leaderboard.types import AgentLeaderboard, AgentLeaderboardEntry


def rank_entries(entries: tuple[AgentLeaderboardEntry, ...]) -> tuple[AgentLeaderboardEntry, ...]:
    """Rank usage reports using the default ordering.

    Default ranking:
    - compute_units ascending
    - token_count ascending when present
    - created_at descending when present
    - entry_id ascending as a final stable tiebreak
    """

    return tuple(sorted(entries, key=_ranking_key))


def rank_leaderboard(leaderboard: AgentLeaderboard) -> AgentLeaderboard:
    """Return a new leaderboard with entries sorted by default ranking rules."""

    return AgentLeaderboard(
        entries=rank_entries(leaderboard.entries),
        warnings=leaderboard.warnings,
    )


def _ranking_key(entry: AgentLeaderboardEntry) -> tuple[float, float, float, str]:
    return (
        entry.compute_units,
        _token_value(entry.token_count),
        -_timestamp_value(entry.created_at),
        entry.entry_id,
    )


def _token_value(value: int | None) -> float:
    if value is None:
        return float("inf")
    return float(value)


def _timestamp_value(value: datetime | None) -> float:
    if value is None:
        return float("-inf")
    return value.timestamp()
