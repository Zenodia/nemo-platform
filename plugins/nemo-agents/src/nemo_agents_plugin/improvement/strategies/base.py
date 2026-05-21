# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Strategy protocol — what is allowed to be modified, and how to ask the
coding agent to do it.

POC ships exactly one strategy: ``skills``. Future strategies (prompt tuning,
agent-config tuning, etc.) implement this protocol.
"""

from __future__ import annotations

from pathlib import Path
from typing import Protocol, runtime_checkable

from nemo_agents_plugin.improvement.models import Hypothesis


@runtime_checkable
class ImprovementStrategy(Protocol):
    """Protocol every improvement strategy implements."""

    name: str

    def writable_paths(self, agent_root: Path) -> list[Path]:
        """Paths inside *agent_root* the coding agent is allowed to modify.

        Computed once at construction; cannot vary per hypothesis.
        """
        ...

    def render_prompt(self, hypothesis: Hypothesis, agent_root: Path) -> str:
        """Build the coding-agent prompt for this hypothesis."""
        ...
