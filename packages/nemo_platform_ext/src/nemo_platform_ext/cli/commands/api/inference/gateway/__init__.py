# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

# NOTE: This file is auto-generated
from __future__ import annotations

from nemo_platform_ext.cli.commands.api.inference.gateway import model, openai, provider
from nemo_platform_ext.cli.core.help_formatter import create_typer_app

app = create_typer_app(name="gateway", help="Gateway operations")

app.add_typer(model.app, name="model")
app.add_typer(openai.app, name="openai")
app.add_typer(provider.app, name="provider")
