# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Fileset selector helpers shared by dataset loading and schema prechecks.

Fileset fragments such as ``workspace/fileset#validation/*.jsonl`` are used in
two places: runtime dataset loading and create-time schema validation. Keeping
the selector logic here gives both paths the same definition of which files are
selected, so prechecks validate the files that execution will actually load.

Patterns are matched from the fileset root. For example,
``validation/*.jsonl`` matches ``validation/a.jsonl`` but not
``nested/validation/a.jsonl``.
"""

from __future__ import annotations

from fnmatch import fnmatchcase

from nemo_platform import AsyncNeMoPlatform

_GLOB_CHARS = {"*", "?", "["}


def is_fileset_glob_pattern(pattern: str) -> bool:
    """Return True when a fileset fragment contains glob wildcards."""
    return any(char in pattern for char in _GLOB_CHARS)


def _match_path_parts(path_parts: tuple[str, ...], pattern_parts: tuple[str, ...]) -> bool:
    if not pattern_parts:
        return not path_parts

    pattern_part = pattern_parts[0]
    remaining_pattern = pattern_parts[1:]
    if pattern_part == "**":
        return _match_path_parts(path_parts, remaining_pattern) or (
            bool(path_parts) and _match_path_parts(path_parts[1:], pattern_parts)
        )

    if not path_parts:
        return False
    return fnmatchcase(path_parts[0], pattern_part) and _match_path_parts(path_parts[1:], remaining_pattern)


def matches_fileset_glob(filepath: str, pattern: str) -> bool:
    """Return True when a fileset-relative path matches a root-anchored glob pattern.

    Slash-containing patterns are evaluated from the fileset root so
    validation does not consider files that runtime loading will not select.
    """
    normalized_path = filepath.strip("/")
    normalized_pattern = pattern.strip("/")
    if not normalized_path or not normalized_pattern:
        return False
    return _match_path_parts(tuple(normalized_path.split("/")), tuple(normalized_pattern.split("/")))


def fileset_glob_prefix_dir(pattern: str) -> str:
    """Return the stable directory prefix before the first glob wildcard."""
    pattern = pattern.lstrip("/")
    if not pattern or not is_fileset_glob_pattern(pattern):
        return pattern

    first_wildcard = min(index for index, char in enumerate(pattern) if char in _GLOB_CHARS)
    prefix = pattern[:first_wildcard]
    if "/" not in prefix:
        return ""
    return prefix.rsplit("/", 1)[0]


async def list_matching_fileset_paths(
    sdk: AsyncNeMoPlatform,
    *,
    workspace: str,
    fileset_name: str,
    fragment_pattern: str,
    max_validation_targets: int | None = None,
) -> list[str]:
    """List fileset paths matching a root-anchored glob fragment.

    Schema prechecks use this to expand wildcard dataset refs before validating
    path-specific schema metadata. Runtime loading uses the same matcher when
    filtering files to download, so this helper keeps create-time validation
    aligned with execution.

    The optional max_validation_targets cap is applied after the files service
    returns the stable-prefix listing. It limits how many matched files evaluator
    prechecks validate, but it is not an upstream files-service pagination limit.
    """
    pattern = fragment_pattern.lstrip("/")
    has_glob = is_fileset_glob_pattern(pattern)
    list_path = fileset_glob_prefix_dir(pattern) if has_glob else pattern
    if has_glob and list_path:
        list_path = list_path.rstrip("/") + "/"
    list_response = await sdk.files.list(fileset=fileset_name, workspace=workspace, remote_path=list_path)
    entries = getattr(list_response, "data", None) or []

    matches: list[str] = []
    for entry in entries:
        path = getattr(entry, "path", None)
        if not isinstance(path, str):
            continue
        normalized = path.lstrip("/")
        if has_glob and matches_fileset_glob(normalized, pattern):
            matches.append(normalized)
        if not has_glob and normalized == pattern:
            matches.append(normalized)
        if max_validation_targets is not None and len(matches) > max_validation_targets:
            raise ValueError(
                f"fileset pattern '{pattern}' matched more than {max_validation_targets} validation targets; "
                "narrow the selector before running create-time schema validation"
            )
    return sorted(matches)
