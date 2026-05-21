# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

# NOTE: This file is auto-generated
from __future__ import annotations

from nemo_platform.cli.commands.api.iam import role_bindings
from nemo_platform.cli.core.help_formatter import create_typer_app

app = create_typer_app(name="iam", help="Iam operations")

app.add_typer(role_bindings.app, name="role-bindings")
