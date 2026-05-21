# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Runner protocol — backends that execute eval suites against an agent.

POC: thin protocol; the Harbor runner (``_harbor_runner.py``) and NAT runner
(``nat.py``) implement it. Future runners (custom backends, distributed
executors) plug in here.
"""

from __future__ import annotations

from pathlib import Path
from typing import ClassVar, Protocol, runtime_checkable

from nemo_agents_plugin.improvement.models import BatchResult, EvalSpec


@runtime_checkable
class Runner(Protocol):
    """Protocol every eval-suite runner implements."""

    name: str
    supports_repeats: ClassVar[bool]

    def discover(self, evals_dir: Path) -> list[EvalSpec]:
        """Find eval tasks in *evals_dir* (marker-file scan)."""
        ...

    async def run_batch(
        self,
        evals: list[EvalSpec],
        batch_dir: Path,
        *,
        concurrency: int = 4,
        skip_build: bool = False,
        project_root: Path | None = None,
        repeats: int = 1,
    ) -> BatchResult:
        """Execute a batch and return aggregate results.

        When ``repeats > 1``, runners with ``supports_repeats=True`` run each
        eval N times and return the median aggregate (with ``trials_count``
        populated). Runners with ``supports_repeats=False`` log a warning and
        run once. Callers can introspect ``supports_repeats`` to detect
        capability before requesting multi-trial.
        """
        ...

    def eval_input_paths(self, eval_dir: Path) -> list[Path]:
        """Per-eval files the loop must treat as immutable."""
        ...
