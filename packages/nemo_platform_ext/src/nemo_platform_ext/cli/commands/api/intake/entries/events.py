# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

# NOTE: This file is auto-generated
from __future__ import annotations

from typing import Annotated

import typer

from nemo_platform_ext.cli.core.api import build_kwargs
from nemo_platform_ext.cli.core.code_generator import handle_code_generation
from nemo_platform_ext.cli.core.context import CLIContext
from nemo_platform_ext.cli.core.errors import handle_errors
from nemo_platform_ext.cli.core.formatters import format_output
from nemo_platform_ext.cli.core.help_formatter import collect_warnings, create_typer_app
from nemo_platform_ext.cli.core.stdin_utils import read_data_input_with_flags, read_payload, validate_required_fields
from nemo_platform_ext.cli.core.types import EntityOutputFormatOption

app = create_typer_app(name="events", help="Manage events")


@app.command("create")
@collect_warnings
@handle_errors
def create_events(
    ctx: typer.Context,
    name: Annotated[str, typer.Argument()],
    workspace: Annotated[str | None, typer.Option("--workspace")] = None,
    events: Annotated[
        str | None, typer.Option("--events", help="List of events to add to the entry. (JSON string) (required)")
    ] = None,
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
    """Add events to an entry by ID or external_id.

    Use `external:{external_id}` to add events by external_id. Example:
    `/v2/workspaces/{workspace}/entries/external:chatcmpl-abc123/events`

        [bold red]Required fields:[/] events

        [green]Examples:[/]
        nemo intake entries events create <name> --input-file config.json
        nemo intake entries events create <name> --input-data '{"events": {}}'
        echo '{"json": "data"}' | nemo intake entries events create <name> --input-file -
        nemo intake entries events create <name> --<option> "value"
    """
    # Read base input (optional if all fields provided via flags)
    if input_file or input_data:
        input_payload = read_data_input_with_flags(input_file=input_file, input_data=input_data)
    else:
        input_payload = {}

    # Apply CLI flag overrides (flags take precedence)
    if workspace is not None:
        input_payload["workspace"] = workspace
    if events is not None:
        input_payload["events"] = read_payload("events", events)
    # Validate required fields are present after merging
    validate_required_fields(
        input_payload,
        ["events"],
        "intake entries events create",
        {
            "events": "List of events to add to the entry. (JSON string) (required)",
        },
    )

    all_kwargs = {"name": name, **input_payload}
    state: CLIContext = ctx.obj
    output_format = state.get_output_format(output_format)

    if handle_code_generation(["intake", "entries", "events"], "create", all_kwargs, output_format, state):
        return

    client = state.get_client()
    result = client.intake.entries.events.create(**all_kwargs)

    format_output(
        result,
        is_list=False,
        output_format=output_format,
        no_truncate=state.get_no_truncate(),
        timestamp_format=state.get_timestamp_format(),
    )


@app.command("delete")
@collect_warnings
@handle_errors
def delete_events(
    ctx: typer.Context,
    name: Annotated[str, typer.Argument()],
    workspace: Annotated[str | None, typer.Option("--workspace")] = None,
    entry: Annotated[str, typer.Option("--entry")] = ...,
) -> None:
    """Delete a specific event from an entry.

    Entry can be referenced by ID or external_id using `external:{external_id}`
    prefix."""
    state: CLIContext = ctx.obj
    client = state.get_client()

    kwargs = build_kwargs(
        workspace=workspace,
        entry=entry,
    )
    client.intake.entries.events.delete(name, **kwargs)

    typer.echo("✓ Deleted successfully")
