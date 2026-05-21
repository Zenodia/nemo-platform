# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Tests for ``nemo_agents_plugin.usage.render``."""

from __future__ import annotations

import json

from nemo_agents_plugin.usage.models import (
    BatchUsageReport,
    TaskUsage,
    UsageReport,
)
from nemo_agents_plugin.usage.render import render_json


def _task(*, compute_units: int | None = None) -> TaskUsage:
    return TaskUsage(
        task="t",
        timestamp="20260429T120000Z",
        image="img",
        reward=1,
        build_status="ok",
        agent_status="ok",
        verify_status="ok",
        prompt_tokens=100,
        completion_tokens=50,
        total_tokens=150,
        compute_units=compute_units,
        source_dir="/tmp/t",
    )


def test_render_json_emits_compute_units() -> None:
    """``compute_units`` is the canonical optimization metric and is always rendered."""
    report = UsageReport(task=_task(compute_units=1200))

    output = json.loads(render_json(report))

    assert output["task"]["compute_units"] == 1200


def test_render_json_emits_compute_units_total_for_batch() -> None:
    batch = BatchUsageReport(
        runs=[_task(compute_units=1200)],
        prompt_tokens_total=100,
        completion_tokens_total=50,
        total_tokens_total=150,
        compute_units_total=1200,
        null_token_runs=0,
    )

    output = json.loads(render_json(batch))

    assert output["compute_units_total"] == 1200
    assert output["runs"][0]["compute_units"] == 1200


def test_render_json_preserves_null_compute_units() -> None:
    """When --total-params wasn't passed, compute_units is null but the field renders."""
    report = UsageReport(task=_task(compute_units=None))

    output = json.loads(render_json(report))

    assert output["task"]["compute_units"] is None
