# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

# NOTE: This file is auto-generated
from __future__ import annotations

from typing import Annotated

import typer

from nemo_platform.cli.commands.api.intake.exports import jobs
from nemo_platform.cli.core.api import build_kwargs, merge_filter_dict
from nemo_platform.cli.core.code_generator import handle_code_generation
from nemo_platform.cli.core.context import CLIContext
from nemo_platform.cli.core.errors import handle_errors
from nemo_platform.cli.core.formatters import format_output
from nemo_platform.cli.core.help_formatter import collect_warnings, create_typer_app
from nemo_platform.cli.core.types import EntityOutputFormatOption

app = create_typer_app(name="exports", help="Manage exports")

app.add_typer(jobs.app, name="jobs")


@app.command("preview")
@collect_warnings
@handle_errors
def preview_exports(
    ctx: typer.Context,
    workspace: Annotated[str | None, typer.Option("--workspace")] = None,
    config: Annotated[
        str | None,
        typer.Option(
            "--config",
            metavar="CONFIG_JSON",
            help="Use --config with JSON for complex/nested queries, or --config.FIELD options for simple fields. Both can be combined, with field options taking precedence.\nJSON-only fields:\n  filters: dict[str, object]\n  format_options: dict[str, object]\n  search: dict[str, object]\n\nInput schema for export configuration.Defines what entries to export and how to format them.",
            rich_help_panel="Config Options",
        ),
    ] = None,
    config_limit: Annotated[int | None, typer.Option("--config.limit", rich_help_panel="Config Options")] = None,
    output_format: EntityOutputFormatOption = None,
) -> None:
    """Preview export data without writing to a file (max 100 records)."""
    state: CLIContext = ctx.obj
    output_format = state.get_output_format(output_format)

    kwargs = build_kwargs(
        workspace=workspace,
        config=merge_filter_dict(config, limit=config_limit),
    )
    if handle_code_generation(["intake", "exports"], "preview", kwargs, output_format, state):
        return

    client = state.get_client()
    result = client.intake.exports.preview(**kwargs)

    format_output(
        result,
        is_list=False,
        output_format=output_format,
        no_truncate=state.get_no_truncate(),
        timestamp_format=state.get_timestamp_format(),
    )
