# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Skills-optimization strategy — modifies agent skills under a configurable path."""

from __future__ import annotations

from pathlib import Path

from nemo_agents_plugin.improvement.models import Hypothesis


class SkillsOptimizerStrategy:
    """The v0 strategy: improve agent skills based on eval failures.

    The strategy is allowed to write only under ``agent_root / skills_path``.
    Anything else is reverted by the loop's post-edit guard.
    """

    name = "skills"

    def __init__(self, skills_path: str = ".agents/skills") -> None:
        self.skills_path = skills_path.strip("/")

    def writable_paths(self, agent_root: Path) -> list[Path]:
        return [agent_root / self.skills_path]

    def render_prompt(self, hypothesis: Hypothesis, agent_root: Path) -> str:
        return (
            f"You are improving agent skills to fix eval failures.\n\n"
            f"## Cluster: {hypothesis.cluster_id}\n"
            f"## Affected Evals: {', '.join(hypothesis.eval_names)}\n"
            f"## Root Cause: {hypothesis.root_cause}\n"
            f"## Category: {hypothesis.category.value}\n"
            f"## Proposed Fix: {hypothesis.proposed_fix}\n\n"
            f"Modify ONLY files under {self.skills_path}. Be minimal and targeted.\n"
        )
