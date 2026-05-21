# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Pydantic models for `nemo agents usage` reports.

The data surface comes from `tests/agentic-use/nat_runner.py`'s ``result.json``,
which is intentionally thin: three nullable token scalars plus status flags
and a reward.  These models preserve that thinness — they do not pretend
to carry per-model breakdowns, latency, cache tokens, or trajectory data
that the upstream artifact does not contain.

``compute_units`` is the canonical optimization-ranking metric, computed by
:mod:`nemo_agents_plugin.usage.compute` after the parser produces a model.
The parser leaves it ``None``; the CLI populates it when ``--total-params``
is supplied.

The ``schema_version`` literal lets future versions add fields without
breaking consumers.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict


class TaskUsage(BaseModel):
    """One ``result.json`` from ``nat-jobs/<ts>-<task>/``."""

    model_config = ConfigDict(frozen=True)

    task: str
    timestamp: str
    image: str | None
    reward: int | None
    build_status: str | None
    agent_status: str | None
    verify_status: str | None
    prompt_tokens: int | None
    completion_tokens: int | None
    total_tokens: int | None
    compute_units: int | None
    source_dir: str


class UsageReport(BaseModel):
    """Single-task report — a thin envelope around :class:`TaskUsage`."""

    model_config = ConfigDict(frozen=True)

    schema_version: Literal["v0"] = "v0"
    task: TaskUsage


class BatchUsageReport(BaseModel):
    """Roll-up across N tasks (one ``nat-jobs/`` directory).

    Token totals (and ``compute_units_total``) are ``None`` if any run
    has missing usage *or* any sibling child was skipped/unparseable,
    preventing downstream consumers from treating a partial sum over
    a degraded batch as a real total.

    Three counters surface the kind of incompleteness:

    - ``null_token_runs``: parsed runs where any of prompt/completion/total
      is ``None`` (the agent backend didn't emit parseable usage).
    - ``skipped_runs``: child directories with no ``result.json`` at all
      (the run never produced an artifact — in-progress, missing write).
    - ``unparseable_runs``: child directories whose ``result.json`` was
      present but failed to decode (truncated write, schema mismatch).

    Any of the three being non-zero nulls all four token totals.
    """

    model_config = ConfigDict(frozen=True)

    schema_version: Literal["v0"] = "v0"
    runs: list[TaskUsage]
    prompt_tokens_total: int | None
    completion_tokens_total: int | None
    total_tokens_total: int | None
    compute_units_total: int | None
    null_token_runs: int
    skipped_runs: int = 0
    unparseable_runs: int = 0
