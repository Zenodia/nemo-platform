# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

# NOTE: This file is auto-generated
from __future__ import annotations

from typing import Annotated, Literal

import typer

from nemo_platform_ext.cli.core.api import build_kwargs, merge_filter_dict
from nemo_platform_ext.cli.core.code_generator import handle_code_generation
from nemo_platform_ext.cli.core.context import CLIContext
from nemo_platform_ext.cli.core.errors import handle_errors
from nemo_platform_ext.cli.core.formatters import Column, check_output_columns_with_format, format_output
from nemo_platform_ext.cli.core.help_formatter import collect_warnings, create_typer_app
from nemo_platform_ext.cli.core.pagination import PaginationType, fetch_all_pages, warn_if_more_pages
from nemo_platform_ext.cli.core.stdin_utils import read_data_input_with_flags, validate_required_fields
from nemo_platform_ext.cli.core.types import (
    EntityOutputFormatOption,
    ListOutputFormatOption,
    NoTruncateOption,
    OutputColumnsOption,
)

app = create_typer_app(name="tasks", help="Manage tasks")


@app.command("create")
@collect_warnings
@handle_errors
def create_tasks(
    ctx: typer.Context,
    path_name: Annotated[str, typer.Argument()],
    workspace: Annotated[str | None, typer.Option("--workspace")] = None,
    body_name: Annotated[str | None, typer.Option("--body-name", help="Task name (required)")] = None,
    description: Annotated[str | None, typer.Option("--description", help="Task description")] = None,
    locked: Annotated[
        bool | None,
        typer.Option(
            "--locked", help="If true, this record cannot be automatically updated when entries are ingested."
        ),
    ] = None,
    project: Annotated[
        str | None, typer.Option("--project", help="The name of the project associated with this task")
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
    """Create a new task.

    [bold red]Required fields:[/] body_name

    [green]Examples:[/]
    nemo intake apps tasks create <path_name> --input-file config.json
    nemo intake apps tasks create <path_name> --input-data '{"body_name": "value"}'
    echo '{"json": "data"}' | nemo intake apps tasks create <path_name> --input-file -
    nemo intake apps tasks create <path_name> --<option> "value"
    """
    # Read base input (optional if all fields provided via flags)
    if input_file or input_data:
        input_payload = read_data_input_with_flags(input_file=input_file, input_data=input_data)
    else:
        input_payload = {}

    # Apply CLI flag overrides (flags take precedence)
    if workspace is not None:
        input_payload["workspace"] = workspace
    if body_name is not None:
        input_payload["body_name"] = body_name
    if description is not None:
        input_payload["description"] = description
    if locked is not None:
        input_payload["locked"] = locked
    if project is not None:
        input_payload["project"] = project
    # Validate required fields are present after merging
    validate_required_fields(
        input_payload,
        ["body_name"],
        "intake apps tasks create",
        {
            "body_name": "Task name (required)",
        },
    )

    all_kwargs = {"path_name": path_name, **input_payload}
    state: CLIContext = ctx.obj
    output_format = state.get_output_format(output_format)

    if handle_code_generation(["intake", "apps", "tasks"], "create", all_kwargs, output_format, state):
        return

    client = state.get_client()
    result = client.intake.apps.tasks.create(**all_kwargs)

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
def delete_tasks(
    ctx: typer.Context,
    name: Annotated[str, typer.Argument()],
    workspace: Annotated[str | None, typer.Option("--workspace")] = None,
    app: Annotated[str, typer.Option("--app")] = ...,
) -> None:
    """Delete a task."""
    state: CLIContext = ctx.obj
    client = state.get_client()

    kwargs = build_kwargs(
        workspace=workspace,
        app=app,
    )
    client.intake.apps.tasks.delete(name, **kwargs)

    typer.echo("✓ Deleted successfully")


@app.command("list")
@collect_warnings
@handle_errors
def list_tasks(
    ctx: typer.Context,
    name: Annotated[str, typer.Argument()],
    workspace: Annotated[str | None, typer.Option("--workspace")] = None,
    filter: Annotated[
        str | None,
        typer.Option(
            "--filter",
            metavar="FILTER_JSON",
            help="Use --filter with JSON for complex/nested queries, or --filter.FIELD options for simple fields. Both can be combined, with field options taking precedence.\nJSON-only fields:\n  created_at: {gte: str, lte: str}\n  updated_at: {gte: str, lte: str}\n\nFilter tasks by name, app, description, project, created_at, and updated_at.",
            rich_help_panel="Filter Options",
        ),
    ] = None,
    filter_app: Annotated[str | None, typer.Option("--filter.app", rich_help_panel="Filter Options")] = None,
    filter_description: Annotated[
        str | None, typer.Option("--filter.description", rich_help_panel="Filter Options")
    ] = None,
    filter_name: Annotated[str | None, typer.Option("--filter.name", rich_help_panel="Filter Options")] = None,
    filter_project: Annotated[str | None, typer.Option("--filter.project", rich_help_panel="Filter Options")] = None,
    filter_workspace: Annotated[
        str | None, typer.Option("--filter.workspace", rich_help_panel="Filter Options")
    ] = None,
    page: Annotated[int | None, typer.Option("--page", help="Page number.")] = None,
    page_size: Annotated[int | None, typer.Option("--page-size", help="Page size.")] = None,
    sort: Annotated[
        Literal["created_at", "-created_at", "name", "-name", "updated_at", "-updated_at"] | None,
        typer.Option(
            "--sort", help="The field to sort by. To sort in decreasing order, use `-` in front of the field name."
        ),
    ] = None,
    output_format: ListOutputFormatOption = None,
    no_truncate: NoTruncateOption = None,
    columns: OutputColumnsOption = None,
    all_pages: Annotated[bool, typer.Option("--all-pages", help="Fetch all pages")] = False,
) -> None:
    """List all tasks for a specific app."""
    state: CLIContext = ctx.obj
    output_format = state.get_output_format(output_format)

    check_output_columns_with_format(columns, output_format)

    default_columns = [
        Column("name", None),
        Column("workspace", None),
        Column("created_at", None),
    ]
    if columns is None or str(columns).strip() == "default":
        columns = default_columns

    kwargs = build_kwargs(
        workspace=workspace,
        filter=merge_filter_dict(
            filter,
            app=filter_app,
            description=filter_description,
            name=filter_name,
            project=filter_project,
            workspace=filter_workspace,
        ),
        page=page,
        page_size=page_size,
        sort=sort,
    )

    if handle_code_generation(["intake", "apps", "tasks"], "list", kwargs, output_format, state):
        return

    client = state.get_client()
    path_args = (name,)
    pagination_type = PaginationType.PAGE_NUMBER
    if all_pages:
        items = fetch_all_pages(
            client.intake.apps.tasks.list,
            path_args=path_args,
            body_args=kwargs,
            pagination_type=pagination_type,
        )
    else:
        items = client.intake.apps.tasks.list(*path_args, **kwargs)

    format_output(
        items,
        is_list=True,
        output_format=output_format,
        output_columns=columns,
        no_truncate=state.get_no_truncate(no_truncate),
        timestamp_format=state.get_timestamp_format(),
    )
    if not all_pages:
        warn_if_more_pages(items, pagination_type)


@app.command("patch")
@collect_warnings
@handle_errors
def patch_tasks(
    ctx: typer.Context,
    name: Annotated[str, typer.Argument()],
    workspace: Annotated[str | None, typer.Option("--workspace")] = None,
    app: Annotated[str | None, typer.Option("--app", help="(required)")] = None,
    description: Annotated[str | None, typer.Option("--description", help="Task description")] = None,
    locked: Annotated[bool | None, typer.Option("--locked", help="Lock status")] = None,
    project: Annotated[
        str | None, typer.Option("--project", help="The name of the project associated with this task")
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
    """Update an existing task.

    [bold red]Required fields:[/] app

    [green]Examples:[/]
    nemo intake apps tasks patch <name> --input-file config.json
    nemo intake apps tasks patch <name> --input-data '{"app": "value"}'
    echo '{"json": "data"}' | nemo intake apps tasks patch <name> --input-file -
    nemo intake apps tasks patch <name> --<option> "value"
    """
    # Read base input (optional if all fields provided via flags)
    if input_file or input_data:
        input_payload = read_data_input_with_flags(input_file=input_file, input_data=input_data)
    else:
        input_payload = {}

    # Apply CLI flag overrides (flags take precedence)
    if workspace is not None:
        input_payload["workspace"] = workspace
    if app is not None:
        input_payload["app"] = app
    if description is not None:
        input_payload["description"] = description
    if locked is not None:
        input_payload["locked"] = locked
    if project is not None:
        input_payload["project"] = project
    # Validate required fields are present after merging
    validate_required_fields(
        input_payload,
        ["app"],
        "intake apps tasks patch",
        {
            "app": "(required)",
        },
    )

    all_kwargs = {"name": name, **input_payload}

    state: CLIContext = ctx.obj
    output_format = state.get_output_format(output_format)

    if handle_code_generation(["intake", "apps", "tasks"], "patch", all_kwargs, output_format, state):
        return

    client = state.get_client()
    result = client.intake.apps.tasks.patch(**all_kwargs)

    format_output(
        result,
        is_list=False,
        output_format=output_format,
        no_truncate=state.get_no_truncate(),
        timestamp_format=state.get_timestamp_format(),
    )


@app.command("get")
@collect_warnings
@handle_errors
def retrieve_tasks(
    ctx: typer.Context,
    name: Annotated[str, typer.Argument()],
    workspace: Annotated[str | None, typer.Option("--workspace")] = None,
    app: Annotated[str, typer.Option("--app")] = ...,
    output_format: EntityOutputFormatOption = None,
) -> None:
    """Get a specific task."""
    state: CLIContext = ctx.obj
    output_format = state.get_output_format(output_format)

    kwargs = build_kwargs(
        workspace=workspace,
        app=app,
    )
    if handle_code_generation(["intake", "apps", "tasks"], "retrieve", kwargs, output_format, state):
        return

    client = state.get_client()
    result = client.intake.apps.tasks.retrieve(name, **kwargs)

    format_output(
        result,
        is_list=False,
        output_format=output_format,
        no_truncate=state.get_no_truncate(),
        timestamp_format=state.get_timestamp_format(),
    )
