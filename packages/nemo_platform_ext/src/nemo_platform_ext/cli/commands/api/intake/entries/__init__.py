# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

# NOTE: This file is auto-generated
from __future__ import annotations

from typing import Annotated, Literal

import typer

from nemo_platform_ext.cli.commands.api.intake.entries import events
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

app = create_typer_app(name="entries", help="Manage entries")

app.add_typer(events.app, name="events")


@app.command("create")
@collect_warnings
@handle_errors
def create_entries(
    ctx: typer.Context,
    workspace: Annotated[str | None, typer.Option("--workspace")] = None,
    context: Annotated[
        str | None,
        typer.Option(
            "--context",
            help="Contextual metadata attached to every entry record.Keeping these grouped in a dedicated object avoids polluting the top-level entity schema and makes it trivial to extend without breaking compatibility. (JSON string) (required)",
        ),
    ] = None,
    data: Annotated[
        str | None,
        typer.Option(
            "--data",
            help="Entry data containing the request and response for an LLM interaction. (JSON string) (required)",
        ),
    ] = None,
    custom_fields: Annotated[
        str | None,
        typer.Option(
            "--custom-fields",
            help="Free-form metadata bag for client-defined fields (e.g., external experiment metadata). (JSON string)",
        ),
    ] = None,
    events: Annotated[
        str | None, typer.Option("--events", help="Events associated with this entry (JSON string)")
    ] = None,
    external_id: Annotated[
        str | None,
        typer.Option(
            "--external-id", help="Optional client-provided identifier (e.g., completion_id from an LLM provider)"
        ),
    ] = None,
    project: Annotated[
        str | None, typer.Option("--project", help="The name of the project associated with this entry")
    ] = None,
    usage: Annotated[
        str | None,
        typer.Option(
            "--usage",
            help="Structured usage metrics captured at log time.Every field is optional so producers can populate whatever they have without schema breakage. Stored as the entry-level `usage` field so filters can reach it via `data.usage.<field>` entity-store paths. (JSON string)",
        ),
    ] = None,
    user_rating: Annotated[
        str | None,
        typer.Option(
            "--user-rating",
            help="User's rating/evaluation of an AI response.This captures various forms of end-user feedback about a model's response, including binary thumbs up/down ratings, numeric scores, free-text opinions, suggested rewrites, and structured category ratings.Either `thumb` or `rating` should be provided (they are mutually exclusive), but all fields are optional to accommodate different feedback collection patterns. (JSON string)",
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
    """Create a new entry.

    Apps and tasks referenced in the entry context will be auto-created if they
    don't exist.

        [bold red]Required fields:[/] context, data

        [green]Examples:[/]
        nemo intake entries create --input-file config.json
        nemo intake entries create --input-data '{"context": {}, "data": {}}'
        echo '{"json": "data"}' | nemo intake entries create --input-file -
        nemo intake entries create --<option> "value"
    """
    # Read base input (optional if all fields provided via flags)
    if input_file or input_data:
        input_payload = read_data_input_with_flags(input_file=input_file, input_data=input_data)
    else:
        input_payload = {}

    # Apply CLI flag overrides (flags take precedence)
    if workspace is not None:
        input_payload["workspace"] = workspace
    if context is not None:
        input_payload["context"] = read_payload("context", context)
    if data is not None:
        input_payload["data"] = read_payload("data", data)
    if custom_fields is not None:
        input_payload["custom_fields"] = read_payload("custom_fields", custom_fields)
    if events is not None:
        input_payload["events"] = read_payload("events", events)
    if external_id is not None:
        input_payload["external_id"] = external_id
    if project is not None:
        input_payload["project"] = project
    if usage is not None:
        input_payload["usage"] = read_payload("usage", usage)
    if user_rating is not None:
        input_payload["user_rating"] = read_payload("user_rating", user_rating)
    # Validate required fields are present after merging
    validate_required_fields(
        input_payload,
        ["context", "data"],
        "intake entries create",
        {
            "context": "Contextual metadata attached to every entry record.Keeping these grouped in a dedicated object avoids polluting the top-level entity schema and makes it trivial to extend without breaking compatibility. (JSON string) (required)",
            "data": "Entry data containing the request and response for an LLM interaction. (JSON string) (required)",
        },
    )

    all_kwargs = input_payload
    state: CLIContext = ctx.obj
    output_format = state.get_output_format(output_format)

    if handle_code_generation(["intake", "entries"], "create", all_kwargs, output_format, state):
        return

    client = state.get_client()
    result = client.intake.entries.create(**all_kwargs)

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
def delete_entries(
    ctx: typer.Context,
    name: Annotated[str, typer.Argument()],
    workspace: Annotated[str | None, typer.Option("--workspace")] = None,
) -> None:
    """Delete an entry by ID or external_id.

    Use `external:{external_id}` to delete by external_id. Example:
    `/v2/workspaces/{workspace}/entries/external:chatcmpl-abc123`"""
    state: CLIContext = ctx.obj
    client = state.get_client()

    kwargs = build_kwargs(
        workspace=workspace,
    )
    client.intake.entries.delete(name, **kwargs)

    typer.echo("✓ Deleted successfully")


@app.command("list")
@collect_warnings
@handle_errors
def list_entries(
    ctx: typer.Context,
    workspace: Annotated[str | None, typer.Option("--workspace")] = None,
    filter: Annotated[
        str | None,
        typer.Option(
            "--filter",
            metavar="FILTER_JSON",
            help="Use --filter with JSON for complex/nested queries, or --filter.FIELD options for simple fields. Both can be combined, with field options taking precedence.\nJSON-only fields:\n  context: {app: str, session_id: str, task: str, thread_id: str, user_id: str}\n  created_at: {gte: str, lte: str}\n  updated_at: {gte: str, lte: str}\n  user_rating: {thumb: 'up' | 'down'}\n\nFilter entries by id, project, external_id, created_at, updated_at, usage fields (model), context fields, and user_rating fields.",
            rich_help_panel="Filter Options",
        ),
    ] = None,
    filter_id: Annotated[list[str] | None, typer.Option("--filter.id", rich_help_panel="Filter Options")] = None,
    filter_external_id: Annotated[
        list[str] | None, typer.Option("--filter.external-id", rich_help_panel="Filter Options")
    ] = None,
    filter_has_events: Annotated[
        bool | None, typer.Option("--filter.has-events", rich_help_panel="Filter Options")
    ] = None,
    filter_has_opinion: Annotated[
        bool | None, typer.Option("--filter.has-opinion", rich_help_panel="Filter Options")
    ] = None,
    filter_has_rating: Annotated[
        bool | None, typer.Option("--filter.has-rating", rich_help_panel="Filter Options")
    ] = None,
    filter_has_rewrite: Annotated[
        bool | None, typer.Option("--filter.has-rewrite", rich_help_panel="Filter Options")
    ] = None,
    filter_has_thumb: Annotated[
        bool | None, typer.Option("--filter.has-thumb", rich_help_panel="Filter Options")
    ] = None,
    filter_longest_per_thread: Annotated[
        bool | None, typer.Option("--filter.longest-per-thread", rich_help_panel="Filter Options")
    ] = None,
    filter_model: Annotated[str | None, typer.Option("--filter.model", rich_help_panel="Filter Options")] = None,
    filter_project: Annotated[str | None, typer.Option("--filter.project", rich_help_panel="Filter Options")] = None,
    filter_workspace: Annotated[
        str | None, typer.Option("--filter.workspace", rich_help_panel="Filter Options")
    ] = None,
    page: Annotated[int | None, typer.Option("--page", help="Page number.")] = None,
    page_size: Annotated[int | None, typer.Option("--page-size", help="Page size.")] = None,
    sort: Annotated[
        Literal["created_at", "-created_at", "updated_at", "-updated_at"] | None,
        typer.Option(
            "--sort", help="The field to sort by. To sort in decreasing order, use `-` in front of the field name."
        ),
    ] = None,
    output_format: ListOutputFormatOption = None,
    no_truncate: NoTruncateOption = None,
    columns: OutputColumnsOption = None,
    all_pages: Annotated[bool, typer.Option("--all-pages", help="Fetch all pages")] = False,
) -> None:
    """List all entries with filtering capabilities.

    When longest_per_thread=true is set in filters, returns only the longest entry
    (by message count) for each unique thread_id."""
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
            external_id=filter_external_id,
            has_events=filter_has_events,
            has_opinion=filter_has_opinion,
            has_rating=filter_has_rating,
            has_rewrite=filter_has_rewrite,
            has_thumb=filter_has_thumb,
            longest_per_thread=filter_longest_per_thread,
            model=filter_model,
            project=filter_project,
            workspace=filter_workspace,
        ),
        page=page,
        page_size=page_size,
        sort=sort,
    )

    if handle_code_generation(["intake", "entries"], "list", kwargs, output_format, state):
        return

    client = state.get_client()
    path_args = ()
    pagination_type = PaginationType.PAGE_NUMBER
    if all_pages:
        items = fetch_all_pages(
            client.intake.entries.list,
            path_args=path_args,
            body_args=kwargs,
            pagination_type=pagination_type,
        )
    else:
        items = client.intake.entries.list(*path_args, **kwargs)

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
def patch_entries(
    ctx: typer.Context,
    name: Annotated[str, typer.Argument()],
    workspace: Annotated[str | None, typer.Option("--workspace")] = None,
    context: Annotated[
        str | None,
        typer.Option(
            "--context",
            help="Contextual metadata attached to every entry record.Keeping these grouped in a dedicated object avoids polluting the top-level entity schema and makes it trivial to extend without breaking compatibility. (JSON string)",
        ),
    ] = None,
    custom_fields: Annotated[
        str | None,
        typer.Option(
            "--custom-fields",
            help="Free-form metadata bag for client-defined fields (replaces existing value when provided). (JSON string)",
        ),
    ] = None,
    data: Annotated[
        str | None,
        typer.Option(
            "--data", help="Entry data containing the request and response for an LLM interaction. (JSON string)"
        ),
    ] = None,
    events: Annotated[
        str | None, typer.Option("--events", help="Events associated with this entry (JSON string)")
    ] = None,
    usage: Annotated[
        str | None,
        typer.Option(
            "--usage",
            help="Structured usage metrics captured at log time.Every field is optional so producers can populate whatever they have without schema breakage. Stored as the entry-level `usage` field so filters can reach it via `data.usage.<field>` entity-store paths. (JSON string)",
        ),
    ] = None,
    user_rating: Annotated[
        str | None,
        typer.Option(
            "--user-rating",
            help="User's rating/evaluation of an AI response.This captures various forms of end-user feedback about a model's response, including binary thumbs up/down ratings, numeric scores, free-text opinions, suggested rewrites, and structured category ratings.Either `thumb` or `rating` should be provided (they are mutually exclusive), but all fields are optional to accommodate different feedback collection patterns. (JSON string)",
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
    """Update an existing entry by ID or external_id.

    Use `external:{external_id}` to update by external_id. Example:
    `/v2/workspaces/{workspace}/entries/external:chatcmpl-abc123`

        [green]Examples:[/]
        nemo intake entries patch <name> --input-file config.json
        nemo intake entries patch <name> --input-data '{"field": "value"}'
        echo '{"json": "data"}' | nemo intake entries patch <name> --input-file -
        nemo intake entries patch <name> --<option> "value"
    """
    # Read base input (optional if all fields provided via flags)
    if input_file or input_data:
        input_payload = read_data_input_with_flags(input_file=input_file, input_data=input_data)
    else:
        input_payload = {}

    # Apply CLI flag overrides (flags take precedence)
    if workspace is not None:
        input_payload["workspace"] = workspace
    if context is not None:
        input_payload["context"] = read_payload("context", context)
    if custom_fields is not None:
        input_payload["custom_fields"] = read_payload("custom_fields", custom_fields)
    if data is not None:
        input_payload["data"] = read_payload("data", data)
    if events is not None:
        input_payload["events"] = read_payload("events", events)
    if usage is not None:
        input_payload["usage"] = read_payload("usage", usage)
    if user_rating is not None:
        input_payload["user_rating"] = read_payload("user_rating", user_rating)

    all_kwargs = {"name": name, **input_payload}

    state: CLIContext = ctx.obj
    output_format = state.get_output_format(output_format)

    if handle_code_generation(["intake", "entries"], "patch", all_kwargs, output_format, state):
        return

    client = state.get_client()
    result = client.intake.entries.patch(**all_kwargs)

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
def retrieve_entries(
    ctx: typer.Context,
    name: Annotated[str, typer.Argument()],
    workspace: Annotated[str | None, typer.Option("--workspace")] = None,
    output_format: EntityOutputFormatOption = None,
) -> None:
    """Get a specific entry by ID or external_id.

    Use `external:{external_id}` to get by external_id. Example:
    `/v2/workspaces/{workspace}/entries/external:chatcmpl-abc123`"""
    state: CLIContext = ctx.obj
    output_format = state.get_output_format(output_format)

    kwargs = build_kwargs(
        workspace=workspace,
    )
    if handle_code_generation(["intake", "entries"], "retrieve", kwargs, output_format, state):
        return

    client = state.get_client()
    result = client.intake.entries.retrieve(name, **kwargs)

    format_output(
        result,
        is_list=False,
        output_format=output_format,
        no_truncate=state.get_no_truncate(),
        timestamp_format=state.get_timestamp_format(),
    )
