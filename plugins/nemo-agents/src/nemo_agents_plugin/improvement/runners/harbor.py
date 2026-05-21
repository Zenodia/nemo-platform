# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Harbor runner — Claude Code as the agent under test.

Marker file: ``task.toml``. Delegates to ``harbor run`` per task.
"""

from __future__ import annotations

from pathlib import Path
from typing import ClassVar

from nemo_agents_plugin.improvement.models import BatchResult, EvalSpec

from . import _harbor_discovery, _harbor_runner


class HarborRunner:
    """Runner for the existing Harbor eval suite (Claude Code agent)."""

    name = "harbor"
    supports_repeats: ClassVar[bool] = True

    def discover(self, evals_dir: Path) -> list[EvalSpec]:
        """Find Harbor eval tasks (directories with ``task.toml``)."""
        return _harbor_discovery.discover_evals(evals_dir)

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
        """Run *evals* via ``harbor run``; aggregates trials when ``repeats > 1``."""
        return await _harbor_runner.run_batch(
            evals=evals,
            batch_dir=batch_dir,
            concurrency=concurrency,
            skip_build=skip_build,
            project_root=project_root,
            repeats=repeats,
        )

    def eval_input_paths(self, eval_dir: Path) -> list[Path]:
        """Files the loop must not modify for a Harbor task."""
        return [
            eval_dir / "task.toml",
            eval_dir / "instruction.md",
            eval_dir / "tests",
        ]
