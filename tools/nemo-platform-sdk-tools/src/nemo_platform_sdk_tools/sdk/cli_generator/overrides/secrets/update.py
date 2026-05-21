# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from typing import Annotated, Any, cast

import typer
from nemo_platform_ext.cli.core.code_generator import handle_code_generation
from nemo_platform_ext.cli.core.context import CLIContext
from nemo_platform_ext.cli.core.errors import handle_errors
from nemo_platform_ext.cli.core.formatters import format_output
from nemo_platform_ext.cli.core.help_formatter import collect_warnings
from nemo_platform_ext.cli.core.stdin_utils import resolve_secret_value
from nemo_platform_ext.cli.core.types import EntityOutputFormatOption

app = cast(Any, None)  # override-skip: provided by generated file


@app.command("update")
@collect_warnings
@handle_errors
def update_secrets(
    ctx: typer.Context,
    name: Annotated[str, typer.Argument()],
    workspace: Annotated[str | None, typer.Option("--workspace")] = None,
    from_file: Annotated[
        str | None,
        typer.Option("--from-file", help="Path to file containing the secret value. Use '-' to read from stdin."),
    ] = None,
    value: Annotated[
        str | None,
        typer.Option("--value", help="Secret value directly. Use --from-file for large or sensitive input."),
    ] = None,
    description: Annotated[
        str | None, typer.Option("--description", help="An optional description of the secret")
    ] = None,
    output_format: EntityOutputFormatOption = None,
) -> None:
    """Update a secret's metadata and/or value.

    [green]Examples:[/]
    [dim]# Update secret value directly[/]
    nemo secrets update my-secret --value "new-value"
    [dim]# Read secret from a file[/]
    nemo secrets update my-secret --from-file ./secret.txt --description "Updated!"
    [dim]# Read secret from stdin[/]
    cat secret.txt | nemo secrets update my-secret --from-file -
    [dim]# Read secret from environment variable[/]
    echo "$API_KEY" | nemo secrets update my-secret --from-file -
    """
    input_payload = {}

    if workspace is not None:
        input_payload["workspace"] = workspace
    if description is not None:
        input_payload["description"] = description

    all_kwargs = {"name": name, **input_payload}
    secret_data = resolve_secret_value(from_file, value, required=False)
    if secret_data is not None:
        all_kwargs["value"] = "***"

    state: CLIContext = ctx.obj
    output_format = state.get_output_format(output_format)
    if handle_code_generation(["secrets"], "update", all_kwargs, output_format, state):
        return

    if secret_data is not None:
        all_kwargs["value"] = secret_data
    client = state.get_client()
    result = client.secrets.update(**all_kwargs)

    format_output(
        result,
        is_list=False,
        output_format=output_format,
        no_truncate=state.get_no_truncate(),
        timestamp_format=state.get_timestamp_format(),
    )
