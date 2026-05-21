# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Fileset metadata helpers for resolving dataset schemas by path or schema reference."""

from __future__ import annotations


def resolve_schema_entry(schema_entry: dict | str | None, schema_defs: dict[str, dict] | None = None) -> dict | None:
    """Resolve an inline schema or schema-def reference to a concrete JSON Schema."""
    if schema_entry is None:
        return None
    if isinstance(schema_entry, dict):
        return schema_entry
    if isinstance(schema_entry, str):
        resolved = (schema_defs or {}).get(schema_entry)
        if resolved is None:
            raise ValueError(f"unknown dataset schema reference '{schema_entry}'")
        return resolved
    raise TypeError(f"unsupported dataset schema entry type: {type(schema_entry).__name__}")


def select_schema_for_path(
    default_schema: dict | str | None,
    schemas_by_path: dict[str, dict | str],
    path: str | None,
    *,
    schema_defs: dict[str, dict] | None = None,
) -> dict | None:
    """Select a path-specific schema when an exact file path is available."""
    if path:
        normalized = path.lstrip("/")
        if normalized and normalized in schemas_by_path:
            return resolve_schema_entry(schemas_by_path[normalized], schema_defs)
    return resolve_schema_entry(default_schema, schema_defs)


def parse_fileset_ref_path(ref: str) -> tuple[str, str | None]:
    """Split a fileset ref into its base ref and exact fragment path, if any.

    Fragment paths are preserved verbatim (after leading slash normalization).
    """
    if "#" not in ref:
        return ref, None

    base, fragment = ref.split("#", 1)
    fragment = fragment.lstrip("/")
    if not fragment:
        return base, None
    return base, fragment
