# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Runner auto-detection — pick Harbor vs NAT from marker files in ``evals_dir``.

POC: scan tasks, count markers; majority wins; tie defaults to NAT (the
migration target). ``--prefer harbor|nat`` overrides the tiebreaker.
"""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from .base import Runner
from .harbor import HarborRunner
from .nat import NATRunner


def detect_runner(evals_dir: Path, prefer: Literal["harbor", "nat"] = "nat") -> Runner:
    """Return the appropriate Runner for *evals_dir*.

    Args:
        evals_dir: Directory containing eval tasks (one subdir per task).
        prefer: Tiebreaker when both markers are present per task.
    """
    harbor_count = 0
    nat_count = 0
    if evals_dir.is_dir():
        for child in evals_dir.iterdir():
            if not child.is_dir():
                continue
            has_task_toml = (child / "task.toml").exists()
            has_workflow_yml = (child / "workflow.yml").exists()
            if has_task_toml and not has_workflow_yml:
                harbor_count += 1
            elif has_workflow_yml and not has_task_toml:
                nat_count += 1
            elif has_task_toml and has_workflow_yml:
                # Tie — increment the preferred side
                if prefer == "harbor":
                    harbor_count += 1
                else:
                    nat_count += 1

    if harbor_count == 0 and nat_count == 0:
        raise RuntimeError(
            f"No eval tasks found in {evals_dir}. Each task subdirectory must have "
            "either task.toml (Harbor) or workflow.yml (NAT)."
        )

    # Overall tie also defers to ``prefer`` — not just per-task ties — so
    # callers can deterministically pin the runner choice for mixed suites.
    if harbor_count == nat_count:
        return HarborRunner() if prefer == "harbor" else NATRunner()
    if harbor_count > nat_count:
        return HarborRunner()
    return NATRunner()


def get_runner(name: str) -> Runner:
    """Return a Runner by name (``harbor`` or ``nat``)."""
    if name == "harbor":
        return HarborRunner()
    if name == "nat":
        return NATRunner()
    raise ValueError(f"Unknown runner: {name!r}. Expected 'harbor' or 'nat'.")
