# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

# NOTE: This file is auto-generated
from __future__ import annotations

from nemo_platform.cli.commands.api.safe_synthesizer import jobs
from nemo_platform.cli.core.help_formatter import create_typer_app

app = create_typer_app(name="safe_synthesizer", help="Safe Synthesizer operations")

app.add_typer(jobs.app, name="jobs")
