# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Coding-agent protocol — wraps a CLI that takes a prompt and edits files.

v0 ships ``ClaudeCodingAgent``. Codex is the named v1 deliverable; it will
implement this same protocol.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol, runtime_checkable


@dataclass
class InvocationResult:
    """Result of invoking the coding agent against a prompt."""

    changed_files: list[str] = field(default_factory=list)
    explanation: str = ""
    returncode: int = 0


@runtime_checkable
class CodingAgent(Protocol):
    """Protocol every coding-agent integration implements."""

    name: str

    def preflight(self) -> None:
        """Verify the agent CLI is available + authenticated. Raise on failure."""
        ...

    async def invoke(self, prompt: str, worktree: Path, *, timeout: float = 600.0) -> InvocationResult:
        """Run the coding agent against *prompt* in *worktree*."""
        ...
