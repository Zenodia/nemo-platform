# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Tests for Intake value objects."""

from datetime import datetime, timezone

import pytest
from nmp.intake.entities.values import Usage
from pydantic import ValidationError


def test_usage_converts_naive_timestamps_to_utc() -> None:
    started_at = datetime(2026, 4, 30, 15, 0, 0)
    ended_at = datetime(2026, 4, 30, 15, 0, 1, 840000)

    usage = Usage(started_at=started_at, ended_at=ended_at)

    assert usage.started_at == started_at.replace(tzinfo=timezone.utc)
    assert usage.ended_at == ended_at.replace(tzinfo=timezone.utc)


def test_usage_rejects_reversed_timestamps() -> None:
    with pytest.raises(ValidationError, match="ended_at must be greater than or equal to started_at"):
        Usage(
            started_at=datetime(2026, 4, 30, 15, 0, 2, tzinfo=timezone.utc),
            ended_at=datetime(2026, 4, 30, 15, 0, 1, tzinfo=timezone.utc),
        )


def test_usage_rejects_cached_tokens_exceeding_input_tokens() -> None:
    Usage(input_tokens=10, cached_tokens=10)

    with pytest.raises(ValidationError, match="cached_tokens must be less than or equal to input_tokens"):
        Usage(input_tokens=10, cached_tokens=11)


def test_usage_json_schema_preserves_optional_field_constraints() -> None:
    properties = Usage.model_json_schema()["properties"]

    assert properties["started_at"]["format"] == "date-time"
    assert properties["ended_at"]["format"] == "date-time"
    for field_name in (
        "latency_ms",
        "cost_usd",
        "cost_input_usd",
        "cost_output_usd",
        "input_tokens",
        "output_tokens",
        "cached_tokens",
    ):
        assert properties[field_name]["minimum"] == 0
