# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Core utilities for the NeMo CLI."""

from __future__ import annotations

import json
import sys
from typing import Any

import typer

from nemo_platform_ext.cli.core.errors import InvalidSearchPatternError


def build_kwargs(**kwargs: Any) -> dict[str, Any]:
    """
    Build kwargs dictionary filtering out None values.

    This respects the SDK's Omit pattern - only parameters that are
    explicitly provided will be passed to the SDK, allowing server-side
    defaults to be used.

    Args:
        **kwargs: Keyword arguments to filter

    Returns:
        Dictionary with None values removed
    """
    return {k: v for k, v in kwargs.items() if v is not None}


def build_dict(**kwargs: Any) -> dict[str, Any] | None:
    """
    Build a dictionary from keyword arguments, filtering out None values.

    Returns None if all values are None (empty dict), otherwise returns
    the filtered dictionary. Useful for building filter/search dicts
    from individual CLI options.

    Args:
        **kwargs: Keyword arguments to filter

    Returns:
        Dictionary with None values removed, or None if empty

    Example:
        >>> build_dict(namespace="default", status=None)
        {"namespace": "default"}
        >>> build_dict(namespace=None, status=None)
        None
    """
    result = build_kwargs(**kwargs)
    return result or None


def merge_filter_dict(json_str: str | None, **kwargs: Any) -> dict[str, Any] | None:
    """
    Merge a JSON string with individual field values.

    Individual field values (kwargs) take precedence over JSON values.
    This allows users to use --filter '{"complex": {...}}' for complex fields
    while also using --filter.namespace for simple fields.

    Args:
        json_str: Optional JSON string to parse as base dict
        **kwargs: Individual field values to merge (override JSON)

    Returns:
        Merged dictionary, or None if empty

    Example:
        >>> merge_filter_dict('{"created_at": {"start": "2024-01-01"}}', namespace="default")
        {"created_at": {"start": "2024-01-01"}, "namespace": "default"}
        >>> merge_filter_dict(None, namespace="default")
        {"namespace": "default"}
    """
    result: dict[str, Any] = {}

    # Parse JSON if provided
    if json_str:
        stripped = json_str.strip()
        if not stripped:
            raise InvalidSearchPatternError(json_str)
        try:
            parsed = json.loads(json_str)
            if isinstance(parsed, dict):
                result = parsed
            else:
                typer.echo(f"Error: Expected JSON object, got {type(parsed).__name__}", err=True)
                raise typer.Exit(code=2)
        except json.JSONDecodeError as e:
            if not (stripped.startswith("{") or stripped.startswith("[")):
                raise InvalidSearchPatternError(json_str)
            raise InvalidSearchPatternError(json_str, parse_error=str(e))

    # Merge individual fields (override JSON values)
    for k, v in kwargs.items():
        if v is not None:
            result[k] = v

    return result or None


def parse_resource_id(
    resource_id: str | None,
    namespace_option: str | None,
    name_option: str | None,
    resource_type: str = "resource",
) -> tuple[str, str]:
    """
    Parse resource identifier from either namespace/name format or separate options.

    Supports three formats:
    1. namespace/name (e.g., "default/my-model")
    2. --namespace X --name Y
    3. name with --namespace X (e.g., "my-model --namespace default")

    Args:
        resource_id: Resource identifier (namespace/name or just name)
        namespace_option: Namespace from --namespace option
        name_option: Name from --name option
        resource_type: Type of resource for error messages (e.g., "model", "dataset")

    Returns:
        Tuple of (name, namespace)

    Raises:
        typer.Exit: If the arguments are invalid
    """
    if resource_id and "/" in resource_id:
        # Format: namespace/name
        parts = resource_id.split("/", 1)
        namespace = parts[0]
        name = parts[1]
    elif namespace_option and name_option:
        # Format: --namespace X --name Y
        namespace = namespace_option
        name = name_option
    elif resource_id:
        # Just name provided, require namespace option
        if not namespace_option:
            typer.echo(
                f"Error: When providing just the {resource_type} name, you must also specify --namespace",
                err=True,
            )
            raise typer.Exit(code=1)
        name = resource_id
        namespace = namespace_option
    else:
        typer.echo(f"Error: Provide either 'namespace/{resource_type}-name' or both --namespace and --name", err=True)
        raise typer.Exit(code=1)

    return (name, namespace)


def is_tty() -> bool:
    """Check if stdout is a TTY (terminal)."""
    return sys.stdout.isatty()
