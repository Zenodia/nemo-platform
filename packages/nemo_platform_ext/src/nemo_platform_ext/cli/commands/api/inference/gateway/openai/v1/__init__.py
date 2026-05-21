# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

# NOTE: This file is auto-generated
from __future__ import annotations

from nemo_platform_ext.cli.commands.api.inference.gateway.openai.v1 import models
from nemo_platform_ext.cli.core.help_formatter import create_typer_app

app = create_typer_app(name="v1", help="V1 operations")

app.add_typer(models.app, name="models")
