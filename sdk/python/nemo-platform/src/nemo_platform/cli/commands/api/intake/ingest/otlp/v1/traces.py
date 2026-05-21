# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

# NOTE: This file is auto-generated
from __future__ import annotations

from typing import Annotated

import typer

from nemo_platform.cli.core.code_generator import handle_code_generation
from nemo_platform.cli.core.context import CLIContext
from nemo_platform.cli.core.errors import handle_errors
from nemo_platform.cli.core.formatters import format_output
from nemo_platform.cli.core.help_formatter import collect_warnings, create_typer_app
from nemo_platform.cli.core.stdin_utils import read_data_input_with_flags
from nemo_platform.cli.core.types import EntityOutputFormatOption

app = create_typer_app(name="traces", help="Manage traces")


@app.command("create")
@collect_warnings
@handle_errors
def create_traces(
    ctx: typer.Context,
    workspace: Annotated[str | None, typer.Option("--workspace")] = None,
    input_file: Annotated[
        str | None,
        typer.Option("--input-file", help="Path to JSON file (use '-' for stdin)", rich_help_panel="Input Options"),
    ] = None,
    input_data: Annotated[
        str | None,
        typer.Option("--input-data", help="Input data for the request (JSON or YAML)", rich_help_panel="Input Options"),
    ] = None,
    output_format: EntityOutputFormatOption = None,
) -> None:
    """Ingest Otlp Traces

    [green]Examples:[/]
    nemo intake ingest otlp v1 traces create --input-file config.json
    nemo intake ingest otlp v1 traces create --input-data '{"field": "value"}'
    echo '{"json": "data"}' | nemo intake ingest otlp v1 traces create --input-file -
    nemo intake ingest otlp v1 traces create --<option> "value"
    """
    # Read base input (optional if all fields provided via flags)
    if input_file or input_data:
        input_payload = read_data_input_with_flags(input_file=input_file, input_data=input_data)
    else:
        input_payload = {}

    # Apply CLI flag overrides (flags take precedence)
    if workspace is not None:
        input_payload["workspace"] = workspace

    all_kwargs = input_payload
    state: CLIContext = ctx.obj
    output_format = state.get_output_format(output_format)

    if handle_code_generation(["intake", "ingest", "otlp", "v1", "traces"], "create", all_kwargs, output_format, state):
        return

    client = state.get_client()
    result = client.intake.ingest.otlp.v1.traces.create(**all_kwargs)

    format_output(
        result,
        is_list=False,
        output_format=output_format,
        no_truncate=state.get_no_truncate(),
        timestamp_format=state.get_timestamp_format(),
    )
