# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

# NOTE: This file is auto-generated
from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from nemo_platform.cli.core.api import build_kwargs
from nemo_platform.cli.core.code_generator import handle_code_generation
from nemo_platform.cli.core.context import CLIContext
from nemo_platform.cli.core.errors import handle_errors
from nemo_platform.cli.core.formatters import Column, check_output_columns_with_format, format_output
from nemo_platform.cli.core.help_formatter import collect_warnings, create_typer_app
from nemo_platform.cli.core.types import (
    EntityOutputFormatOption,
    ListOutputFormatOption,
    NoTruncateOption,
    OutputColumnsOption,
)

app = create_typer_app(name="results", help="Manage results")


@app.command("download")
@handle_errors
def download_results(
    ctx: typer.Context,
    name: Annotated[str, typer.Argument()],
    workspace: Annotated[str | None, typer.Option("--workspace")] = None,
    job: Annotated[str, typer.Option("--job")] = ...,
    output_file: Annotated[Path, typer.Option("--output-file", "-o", help="Output file path")] = ...,
) -> None:
    """Download Job Result"""
    state: CLIContext = ctx.obj
    client = state.get_client()

    kwargs = build_kwargs(
        workspace=workspace,
        job=job,
    )
    result = client.safe_synthesizer.jobs.results.download(name, **kwargs)

    result.write_to_file(output_file)
    typer.echo(f"✓ Downloaded to {output_file!r}")


@app.command("download-adapter")
@handle_errors
def download_adapter_results(
    ctx: typer.Context,
    job: Annotated[str, typer.Argument()],
    workspace: Annotated[str | None, typer.Option("--workspace")] = None,
    output_file: Annotated[Path, typer.Option("--output-file", "-o", help="Output file path")] = ...,
) -> None:
    """Download Job Result Adapter"""
    state: CLIContext = ctx.obj
    client = state.get_client()

    kwargs = build_kwargs(
        workspace=workspace,
    )
    result = client.safe_synthesizer.jobs.results.download_adapter(job, **kwargs)

    result.write_to_file(output_file)
    typer.echo(f"✓ Downloaded to {output_file!r}")


@app.command("download-evaluation-report")
@handle_errors
def download_evaluation_report_results(
    ctx: typer.Context,
    job: Annotated[str, typer.Argument()],
    workspace: Annotated[str | None, typer.Option("--workspace")] = None,
    output_file: Annotated[Path, typer.Option("--output-file", "-o", help="Output file path")] = ...,
) -> None:
    """Download Job Result Evaluation-Report"""
    state: CLIContext = ctx.obj
    client = state.get_client()

    kwargs = build_kwargs(
        workspace=workspace,
    )
    result = client.safe_synthesizer.jobs.results.download_evaluation_report(job, **kwargs)

    result.write_to_file(output_file)
    typer.echo(f"✓ Downloaded to {output_file!r}")


@app.command("download-summary")
@handle_errors
def download_summary_results(
    ctx: typer.Context,
    job: Annotated[str, typer.Argument()],
    workspace: Annotated[str | None, typer.Option("--workspace")] = None,
    output_file: Annotated[Path, typer.Option("--output-file", "-o", help="Output file path")] = ...,
) -> None:
    """Download Job Result Summary"""
    state: CLIContext = ctx.obj
    client = state.get_client()

    kwargs = build_kwargs(
        workspace=workspace,
    )
    result = client.safe_synthesizer.jobs.results.download_summary(job, **kwargs)

    result.write_to_file(output_file)
    typer.echo(f"✓ Downloaded to {output_file!r}")


@app.command("download-synthetic-data")
@handle_errors
def download_synthetic_data_results(
    ctx: typer.Context,
    job: Annotated[str, typer.Argument()],
    workspace: Annotated[str | None, typer.Option("--workspace")] = None,
    output_file: Annotated[Path, typer.Option("--output-file", "-o", help="Output file path")] = ...,
) -> None:
    """Download Job Result Synthetic-Data"""
    state: CLIContext = ctx.obj
    client = state.get_client()

    kwargs = build_kwargs(
        workspace=workspace,
    )
    result = client.safe_synthesizer.jobs.results.download_synthetic_data(job, **kwargs)

    result.write_to_file(output_file)
    typer.echo(f"✓ Downloaded to {output_file!r}")


@app.command("list")
@collect_warnings
@handle_errors
def list_results(
    ctx: typer.Context,
    name: Annotated[str, typer.Argument()],
    workspace: Annotated[str | None, typer.Option("--workspace")] = None,
    output_format: ListOutputFormatOption = None,
    no_truncate: NoTruncateOption = None,
    columns: OutputColumnsOption = None,
) -> None:
    """List Job Results"""
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
    )

    if handle_code_generation(["safe_synthesizer", "jobs", "results"], "list", kwargs, output_format, state):
        return

    client = state.get_client()
    path_args = (name,)
    items = client.safe_synthesizer.jobs.results.list(*path_args, **kwargs)

    format_output(
        items,
        is_list=True,
        output_format=output_format,
        output_columns=columns,
        no_truncate=state.get_no_truncate(no_truncate),
        timestamp_format=state.get_timestamp_format(),
    )


@app.command("get")
@collect_warnings
@handle_errors
def retrieve_results(
    ctx: typer.Context,
    name: Annotated[str, typer.Argument()],
    workspace: Annotated[str | None, typer.Option("--workspace")] = None,
    job: Annotated[str, typer.Option("--job")] = ...,
    output_format: EntityOutputFormatOption = None,
) -> None:
    """Get Job Result"""
    state: CLIContext = ctx.obj
    output_format = state.get_output_format(output_format)

    kwargs = build_kwargs(
        workspace=workspace,
        job=job,
    )
    if handle_code_generation(["safe_synthesizer", "jobs", "results"], "retrieve", kwargs, output_format, state):
        return

    client = state.get_client()
    result = client.safe_synthesizer.jobs.results.retrieve(name, **kwargs)

    format_output(
        result,
        is_list=False,
        output_format=output_format,
        no_truncate=state.get_no_truncate(),
        timestamp_format=state.get_timestamp_format(),
    )
