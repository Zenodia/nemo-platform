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
from nemo_platform_ext.cli.core.stdin_utils import read_data_input_with_flags, read_payload, validate_required_fields
from nemo_platform_ext.cli.core.types import (
    EntityOutputFormatOption,
    ListOutputFormatOption,
    NoTruncateOption,
    OutputColumnsOption,
)

app = create_typer_app(name="jobs", help="Manage jobs")


@app.command("create")
@collect_warnings
@handle_errors
def create_jobs(
    ctx: typer.Context,
    workspace: Annotated[str | None, typer.Option("--workspace")] = None,
    config: Annotated[
        str | None,
        typer.Option(
            "--config",
            help="Input schema for export configuration.Defines what entries to export and how to format them. (JSON string) (required)",
        ),
    ] = None,
    output_file_url: Annotated[
        str | None,
        typer.Option(
            "--output-file-url",
            help="The place where the exported file should be written (file://, hf://, nds://, etc.) (required)",
        ),
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
    """Export entries to an external file.

    Use the `longest_per_thread` filter to export only the longest entry per thread,
    which is useful for thread-based exports.

    Supported output file URLs:

    - NeMo Datastore: nds://workspace/dataset_name
    - HuggingFace Dataset: hf://datasets/org/name/path/to/file
    - Local filesystem: file:///path/to/export (for development)

        [bold red]Required fields:[/] config, output_file_url

        [green]Examples:[/]
        nemo intake exports jobs create --input-file config.json
        nemo intake exports jobs create --input-data '{"config": {}, "output_file_url": "value"}'
        echo '{"json": "data"}' | nemo intake exports jobs create --input-file -
        nemo intake exports jobs create --<option> "value"
    """
    # Read base input (optional if all fields provided via flags)
    if input_file or input_data:
        input_payload = read_data_input_with_flags(input_file=input_file, input_data=input_data)
    else:
        input_payload = {}

    # Apply CLI flag overrides (flags take precedence)
    if workspace is not None:
        input_payload["workspace"] = workspace
    if config is not None:
        input_payload["config"] = read_payload("config", config)
    if output_file_url is not None:
        input_payload["output_file_url"] = output_file_url
    # Validate required fields are present after merging
    validate_required_fields(
        input_payload,
        ["config", "output_file_url"],
        "intake exports jobs create",
        {
            "config": "Input schema for export configuration.Defines what entries to export and how to format them. (JSON string) (required)",
            "output_file_url": "The place where the exported file should be written (file://, hf://, nds://, etc.) (required)",
        },
    )

    all_kwargs = input_payload
    state: CLIContext = ctx.obj
    output_format = state.get_output_format(output_format)

    if handle_code_generation(["intake", "exports", "jobs"], "create", all_kwargs, output_format, state):
        return

    client = state.get_client()
    result = client.intake.exports.jobs.create(**all_kwargs)

    format_output(
        result,
        is_list=False,
        output_format=output_format,
        no_truncate=state.get_no_truncate(),
        timestamp_format=state.get_timestamp_format(),
    )


@app.command("list")
@collect_warnings
@handle_errors
def list_jobs(
    ctx: typer.Context,
    workspace: Annotated[str | None, typer.Option("--workspace")] = None,
    filter: Annotated[
        str | None,
        typer.Option(
            "--filter",
            metavar="FILTER_JSON",
            help="Use --filter with JSON for complex/nested queries, or --filter.FIELD options for simple fields. Both can be combined, with field options taking precedence.\nJSON-only fields:\n  created_at: {gte: str, lte: str}\n  updated_at: {gte: str, lte: str}\n\nFilter export jobs by name, status, output_file_url, created_at, and updated_at.",
            rich_help_panel="Filter Options",
        ),
    ] = None,
    filter_id: Annotated[str | None, typer.Option("--filter.id", rich_help_panel="Filter Options")] = None,
    filter_name: Annotated[str | None, typer.Option("--filter.name", rich_help_panel="Filter Options")] = None,
    filter_output_file_url: Annotated[
        str | None, typer.Option("--filter.output-file-url", rich_help_panel="Filter Options")
    ] = None,
    filter_status: Annotated[str | None, typer.Option("--filter.status", rich_help_panel="Filter Options")] = None,
    filter_workspace: Annotated[
        str | None, typer.Option("--filter.workspace", rich_help_panel="Filter Options")
    ] = None,
    page: Annotated[int | None, typer.Option("--page", help="Page number.")] = None,
    page_size: Annotated[int | None, typer.Option("--page-size", help="Page size.")] = None,
    sort: Annotated[
        Literal["created_at", "-created_at", "updated_at", "-updated_at", "status", "-status"] | None,
        typer.Option(
            "--sort", help="The field to sort by. To sort in decreasing order, use `-` in front of the field name."
        ),
    ] = None,
    output_format: ListOutputFormatOption = None,
    no_truncate: NoTruncateOption = None,
    columns: OutputColumnsOption = None,
    all_pages: Annotated[bool, typer.Option("--all-pages", help="Fetch all pages")] = False,
) -> None:
    """List all export jobs with filtering capabilities.

    Use `workspace=-` for cross-workspace listing."""
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
            id=filter_id,
            name=filter_name,
            output_file_url=filter_output_file_url,
            status=filter_status,
            workspace=filter_workspace,
        ),
        page=page,
        page_size=page_size,
        sort=sort,
    )

    if handle_code_generation(["intake", "exports", "jobs"], "list", kwargs, output_format, state):
        return

    client = state.get_client()
    path_args = ()
    pagination_type = PaginationType.PAGE_NUMBER
    if all_pages:
        items = fetch_all_pages(
            client.intake.exports.jobs.list,
            path_args=path_args,
            body_args=kwargs,
            pagination_type=pagination_type,
        )
    else:
        items = client.intake.exports.jobs.list(*path_args, **kwargs)

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


@app.command("get")
@collect_warnings
@handle_errors
def retrieve_jobs(
    ctx: typer.Context,
    name: Annotated[str, typer.Argument()],
    workspace: Annotated[str | None, typer.Option("--workspace")] = None,
    output_format: EntityOutputFormatOption = None,
) -> None:
    """Check the status of an export job."""
    state: CLIContext = ctx.obj
    output_format = state.get_output_format(output_format)

    kwargs = build_kwargs(
        workspace=workspace,
    )
    if handle_code_generation(["intake", "exports", "jobs"], "retrieve", kwargs, output_format, state):
        return

    client = state.get_client()
    result = client.intake.exports.jobs.retrieve(name, **kwargs)

    format_output(
        result,
        is_list=False,
        output_format=output_format,
        no_truncate=state.get_no_truncate(),
        timestamp_format=state.get_timestamp_format(),
    )
