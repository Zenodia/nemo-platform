# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Cursor agent installer."""

from pathlib import Path

from nemo_platform_ext.cli.commands.skills.base import Scope
from nemo_platform_ext.cli.commands.skills.installer import BaseAgentInstaller


class CursorInstaller(BaseAgentInstaller):
    name = "cursor"
    display_name = "Cursor"
    supported_scopes = [Scope.PROJECT]

    def get_install_path(self, scope: Scope, project_root: Path, skill_name: str) -> Path:
        return project_root / ".cursor" / "rules" / f"nemo-{skill_name}" / "SKILL.md"
