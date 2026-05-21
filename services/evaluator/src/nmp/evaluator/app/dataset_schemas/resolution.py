# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Dataset schema resolution helpers for evaluator validation paths."""

from __future__ import annotations

import json
from collections.abc import Iterable
from dataclasses import dataclass, replace

from nemo_evaluator_sdk.values.common import SupportedJobTypes
from nemo_platform import AsyncNeMoPlatform
from nmp.evaluator.app.dataset_schemas.filesets import (
    parse_fileset_ref_path,
    select_schema_for_path,
)
from nmp.evaluator.app.datasets.fileset_selectors import is_fileset_glob_pattern, list_matching_fileset_paths
from nmp.evaluator.app.values.common import Fileset, FilesetRef
from nmp.evaluator.app.values.datasets import Dataset, DatasetRows

_MAX_WILDCARD_SCHEMA_VALIDATION_TARGETS = 5000


@dataclass(frozen=True)
class SchemaResolutionTarget:
    """A dataset schema plus the fileset paths it represents.

    `paths` contains fileset-relative paths that resolved to this effective
    schema. Exact dataset refs and ungrouped wildcard matches have one path.
    Grouped targets can contain several paths that share the same schema.

    An empty `paths` tuple means there is no file-specific path context, such
    as when validating a fileset-level default schema without a fragment.
    """

    paths: tuple[str, ...]
    schema: dict | None

    def path_context(self) -> str | None:
        if not self.paths:
            return None
        if len(self.paths) == 1:
            return self.paths[0]
        return f"{self.paths[0]} (+{len(self.paths) - 1} more paths)"


def _validate_schema_supported_fileset_ref(ref: str) -> None:
    if "/" not in ref.split("#", 1)[0]:
        raise ValueError("FilesetRef must use 'workspace/fileset-name' format")


def _schema_cache_key(schema: dict | None) -> str:
    return json.dumps(schema, sort_keys=True, separators=(",", ":"), default=str)


def group_schema_resolution_targets(targets: Iterable[SchemaResolutionTarget]) -> list[SchemaResolutionTarget]:
    """Collapse targets with identical effective schemas while retaining path context."""
    grouped: dict[str, SchemaResolutionTarget] = {}
    paths_by_key: dict[str, list[str]] = {}

    for target in targets:
        key = _schema_cache_key(target.schema)
        if key not in grouped:
            grouped[key] = target
            paths_by_key[key] = list(target.paths)
            continue

        paths_by_key[key].extend(target.paths)

    return [replace(target, paths=tuple(paths_by_key[key])) for key, target in grouped.items()]


async def resolve_dataset_schema_targets(
    dataset: Dataset | Fileset | FilesetRef | DatasetRows,
    sdk: AsyncNeMoPlatform,
) -> list[SchemaResolutionTarget]:
    """Resolve dataset schema targets for prechecks.

    Returns one target for exact dataset refs and many targets for wildcard refs.
    """
    if isinstance(dataset, DatasetRows):
        return []

    if isinstance(dataset, Fileset):
        metadata = dataset.metadata.dataset
        if metadata is None:
            return []
        return [
            SchemaResolutionTarget(
                paths=(dataset.path,) if dataset.path else (),
                schema=select_schema_for_path(
                    metadata.schema_,
                    metadata.schemas_by_path,
                    dataset.path,
                    schema_defs=metadata.schema_defs,
                ),
            )
        ]

    if not isinstance(dataset, FilesetRef):
        return []

    _validate_schema_supported_fileset_ref(dataset.root)
    base_ref, fragment_path = parse_fileset_ref_path(dataset.root)
    workspace, name = base_ref.split("/", 1)
    fileset = await sdk.files.filesets.retrieve(name=name, workspace=workspace)
    metadata = getattr(fileset, "metadata", None)
    dataset_metadata = getattr(metadata, "dataset", None)
    if dataset_metadata is None:
        return []

    default_schema = getattr(dataset_metadata, "schema_", None)
    if default_schema is not None and not isinstance(default_schema, dict | str):
        return []
    schema_defs = getattr(dataset_metadata, "schema_defs", {}) or {}
    if not isinstance(schema_defs, dict):
        schema_defs = {}
    schemas_by_path = getattr(dataset_metadata, "schemas_by_path", {}) or {}
    if not isinstance(schemas_by_path, dict):
        schemas_by_path = {}

    if fragment_path and is_fileset_glob_pattern(fragment_path):
        # TODO: If FilesetFileSystem grows resolved per-file dataset schema
        # metadata, use it here instead of separately retrieving fileset metadata
        # and applying schemas_by_path in evaluator.
        matched_paths = await list_matching_fileset_paths(
            sdk,
            workspace=workspace,
            fileset_name=name,
            fragment_pattern=fragment_path,
            max_validation_targets=_MAX_WILDCARD_SCHEMA_VALIDATION_TARGETS,
        )
        if not matched_paths:
            raise ValueError(f"no matching files found in fileset for pattern '{fragment_path}'")
        return [
            SchemaResolutionTarget(
                paths=(matched_path,),
                schema=select_schema_for_path(default_schema, schemas_by_path, matched_path, schema_defs=schema_defs),
            )
            for matched_path in matched_paths
        ]

    return [
        SchemaResolutionTarget(
            paths=(fragment_path,) if fragment_path else (),
            schema=select_schema_for_path(default_schema, schemas_by_path, fragment_path, schema_defs=schema_defs),
        )
    ]


async def resolve_dataset_schema(
    dataset: Dataset | Fileset | FilesetRef | DatasetRows,
    sdk: AsyncNeMoPlatform,
) -> dict | None:
    """Resolve one dataset schema for legacy callers.

    Wildcard fileset references can resolve to several path-specific schemas. New
    precheck callers should use resolve_dataset_schema_targets() so every matched
    fileset path is considered.
    """
    targets = await resolve_dataset_schema_targets(dataset, sdk)
    if not targets:
        # Expected when no first-class schema metadata is available, such as
        # inline DatasetRows, filesets without dataset metadata, or unsupported
        # schema metadata shapes. Preserve legacy behavior by skipping
        # create-time schema validation; issues may still surface at runtime.
        return None
    # Single-schema compatibility helper for existing callers.
    return targets[0].schema


def runtime_available_evaluator_fields(job_type: SupportedJobTypes) -> set[str]:
    """Return canonical evaluator fields populated by runtime for the given job type."""
    if job_type == SupportedJobTypes.ONLINE:
        return {"output", "output_text", "response"}
    return set()
