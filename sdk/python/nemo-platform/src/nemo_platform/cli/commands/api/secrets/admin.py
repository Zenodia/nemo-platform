# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

# NOTE: This file is auto-generated
from __future__ import annotations

import typer

from nemo_platform.cli.core.api import build_kwargs
from nemo_platform.cli.core.code_generator import handle_code_generation
from nemo_platform.cli.core.context import CLIContext
from nemo_platform.cli.core.errors import handle_errors
from nemo_platform.cli.core.formatters import format_output
from nemo_platform.cli.core.help_formatter import collect_warnings, create_typer_app
from nemo_platform.cli.core.types import EntityOutputFormatOption

app = create_typer_app(name="admin", help="Manage admin")


@app.command("rotate-encryption-keys")
@collect_warnings
@handle_errors
def rotate_encryption_keys_admin(
    ctx: typer.Context,
    output_format: EntityOutputFormatOption = None,
) -> None:
    """Rotate encryption keys for all platform secrets."""
    state: CLIContext = ctx.obj
    output_format = state.get_output_format(output_format)

    kwargs = build_kwargs()
    if handle_code_generation(["secrets", "admin"], "rotate_encryption_keys", kwargs, output_format, state):
        return

    client = state.get_client()
    result = client.secrets.admin.rotate_encryption_keys(**kwargs)

    format_output(
        result,
        is_list=False,
        output_format=output_format,
        no_truncate=state.get_no_truncate(),
        timestamp_format=state.get_timestamp_format(),
    )
