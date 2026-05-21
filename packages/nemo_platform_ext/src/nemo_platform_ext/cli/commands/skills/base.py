# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Base types and protocol for agent skill installers."""

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Protocol


@dataclass
class Skill:
    name: str
    description: str
    version: str
    content: str
    raw: str
    source_dir: Path | None = None
    # Entry-point name under ``nemo.skills`` (e.g. ``"agents"``, ``"platform"``).
    # Useful for programmatic filtering; the human-friendly label is built from
    # ``source_dist`` instead.
    source_plugin: str | None = None
    # Distribution (PyPI / wheel) name that registered this skill's entry point
    # (e.g. ``"nemo-agents-plugin"``, ``"nemo-platform-ext"``,
    # ``"nemo-platform-sdk"``). This is what users see in ``pip list`` / what
    # they ``uv add``'d, and is what the ``Source`` column in
    # ``nemo skills list`` renders.
    source_dist: str | None = None


class Scope(str, Enum):
    PROJECT = "project"
    USER = "user"


class AgentInstaller(Protocol):
    """Protocol that all agent installers must implement."""

    @property
    def name(self) -> str: ...

    @property
    def display_name(self) -> str: ...

    @property
    def supported_scopes(self) -> list[Scope]: ...

    def get_install_path(self, scope: Scope, project_root: Path, skill_name: str) -> Path: ...

    def format_content(self, skill: Skill) -> str: ...

    def install(self, scope: Scope, project_root: Path, skills: dict[str, Skill]) -> list[Path]: ...
