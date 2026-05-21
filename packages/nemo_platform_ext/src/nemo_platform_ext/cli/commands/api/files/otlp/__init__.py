# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

# NOTE: This file is auto-generated
from __future__ import annotations

from nemo_platform_ext.cli.commands.api.files.otlp import logs
from nemo_platform_ext.cli.core.help_formatter import create_typer_app

app = create_typer_app(name="otlp", help="Otlp operations")

app.add_typer(logs.app, name="logs")
