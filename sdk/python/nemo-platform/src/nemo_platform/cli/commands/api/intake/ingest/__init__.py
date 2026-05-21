# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

# NOTE: This file is auto-generated
from __future__ import annotations

from nemo_platform.cli.commands.api.intake.ingest import atif, chat_completions, otlp
from nemo_platform.cli.core.help_formatter import create_typer_app

app = create_typer_app(name="ingest", help="Ingest operations")

app.add_typer(atif.app, name="atif")
app.add_typer(chat_completions.app, name="chat-completions")
app.add_typer(otlp.app, name="otlp")
