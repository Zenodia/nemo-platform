# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Tests for ``nemo_agents_plugin.usage.compute``."""

from __future__ import annotations

import pytest
from nemo_agents_plugin.usage.compute import compute_units_for


def test_returns_none_when_total_params_missing() -> None:
    """Without total_params_b, the metric is intentionally absent."""
    assert compute_units_for(None, 1000) is None


def test_returns_none_when_tokens_missing() -> None:
    assert compute_units_for(8.0, None) is None


def test_returns_none_when_both_missing() -> None:
    assert compute_units_for(None, None) is None


def test_multiplies_tokens_by_total_params() -> None:
    """The canonical formula: tokens × total_params_b."""
    # 2000 tokens × 8B = 16000
    assert compute_units_for(8.0, 2000) == 16000
    # 1000 tokens × 70B = 70000
    assert compute_units_for(70.0, 1000) == 70000


def test_rounds_to_int() -> None:
    """A fractional total_params produces an int."""
    # 1000 × 12.9 = 12900
    assert compute_units_for(12.9, 1000) == 12900
    # 1234 × 12.9 = 15918.6 → rounds to 15919
    assert compute_units_for(12.9, 1234) == 15919


def test_smaller_total_beats_larger_total_at_same_tokens() -> None:
    """The optimization signal: smaller-total beats larger-total at fixed tokens."""
    big = compute_units_for(70.0, 1000)
    small = compute_units_for(8.0, 1000)
    assert big is not None and small is not None
    assert small < big


def test_rejects_non_positive_total_params() -> None:
    """Zero or negative total_params is meaningless and rejected fast."""
    with pytest.raises(ValueError, match="finite positive"):
        compute_units_for(0.0, 1000)
    with pytest.raises(ValueError, match="finite positive"):
        compute_units_for(-8.0, 1000)


def test_rejects_non_finite_total_params() -> None:
    """NaN/inf would otherwise propagate as uncaught ValueError/OverflowError from int(round(...))."""
    with pytest.raises(ValueError, match="finite positive"):
        compute_units_for(float("nan"), 1000)
    with pytest.raises(ValueError, match="finite positive"):
        compute_units_for(float("inf"), 1000)
    with pytest.raises(ValueError, match="finite positive"):
        compute_units_for(float("-inf"), 1000)
