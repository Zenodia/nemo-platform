# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
# property and proprietary rights in and to this material, related
# documentation and any modifications thereto. Any use, reproduction,
# disclosure or distribution of this material and related documentation
# without an express license agreement from NVIDIA CORPORATION or
# its affiliates is strictly prohibited.

"""Dataset loader module for evaluator tasks.

This module provides service-specific dataset reference adapters for downloaded
filesets while delegating core file loading/parsing to the SDK.

Supported dataset reference formats:
    - workspace/fileset: Load all parsable files in the fileset
    - workspace/fileset#path/to/file.json: Load a specific file
    - workspace/fileset#*.json: Load files matching a glob pattern
    - workspace/fileset#**/*.parquet: Recursive glob pattern

Note: Currently, the dataset-download job step downloads ALL files from a fileset,
and filtering happens at load time. A future optimization could parse the fragment
pattern during download to only fetch matching files.
"""

from pathlib import Path

import pyarrow as pa
from nemo_evaluator_sdk.datasets.loader import (
    DatasetLoadError,
    discover_files,
    is_glob_pattern,
    load_dataset,
    load_dataset_as_dicts,
    load_file,
)

# Backward-compatible aliases for previous private helper names.
_discover_files = discover_files
_is_glob_pattern = is_glob_pattern
_load_file = load_file


def _parse_dataset_ref(ref: str) -> tuple[str, str, str | None]:
    """Parse a dataset reference into components.

    Args:
        ref: Dataset reference string in format 'workspace/fileset[#pattern]'

    Returns:
        Tuple of (workspace, fileset, pattern) where pattern is None if not specified.

    Raises:
        ValueError: If the reference format is invalid.

    Examples:
        >>> _parse_dataset_ref("my-workspace/my-fileset")
        ("my-workspace", "my-fileset", None)
        >>> _parse_dataset_ref("workspace/fileset#train.jsonl")
        ("workspace", "fileset", "train.jsonl")
        >>> _parse_dataset_ref("workspace/fileset#**/*.json")
        ("workspace", "fileset", "**/*.json")
    """
    if not ref:
        raise ValueError("Dataset reference cannot be empty")

    # Split on first # to separate fileset path from pattern
    if "#" in ref:
        fileset_part, pattern = ref.split("#", 1)
        pattern = pattern.lstrip("/") if pattern else None
    else:
        fileset_part = ref
        pattern = None

    # Parse workspace/fileset
    if "/" not in fileset_part:
        raise ValueError(f"Dataset reference must include workspace: '{ref}' (expected 'workspace/fileset')")

    # Split on last / to handle potential edge cases
    parts = fileset_part.split("/")
    if len(parts) < 2:
        raise ValueError(f"Dataset reference must include workspace: '{ref}'")

    workspace = parts[0]
    fileset = "/".join(parts[1:])
    if not workspace or not fileset:
        raise ValueError(f"Invalid dataset reference: '{ref}'")

    return workspace, fileset, pattern


def load_dataset_from_ref(
    ref: str,
    base_dir: Path | str,
    pattern: str | None = None,
) -> pa.Table:
    """Load a dataset from a FilesetRef-style reference.

    This function is designed to work with downloaded filesets where the
    directory structure is: {base_dir}/{workspace}/{fileset}/

    The reference can include a fragment for file selection:
        - workspace/fileset: Uses the pattern parameter
        - workspace/fileset#file.json: Loads specific file (overrides pattern)
        - workspace/fileset#*.json: Uses glob pattern (overrides pattern)

    Args:
        ref: Dataset reference in format 'workspace/fileset[#pattern]'.
        base_dir: Base directory where filesets are downloaded.
        pattern: Default pattern to use if not specified in ref.

    Returns:
        PyArrow Table containing the dataset.

    Raises:
        DatasetLoadError: If the dataset cannot be loaded.
    """
    base_dir = Path(base_dir)
    workspace, fileset, ref_pattern = _parse_dataset_ref(ref)

    # Pattern from ref takes precedence
    effective_pattern = ref_pattern if ref_pattern is not None else pattern

    # Build the full path to the fileset directory
    fileset_path = base_dir / workspace / fileset

    if not fileset_path.exists():
        raise DatasetLoadError(f"Fileset directory not found: {fileset_path}")
    return load_dataset(fileset_path, effective_pattern)


def load_dataset_from_ref_as_dicts(
    ref: str,
    base_dir: Path | str,
    pattern: str | None = None,
) -> list[dict]:
    """Load a dataset from a FilesetRef and convert to list of dicts.

    Convenience function combining load_dataset_from_ref and to_pylist.

    Args:
        ref: Dataset reference in format 'workspace/fileset[#pattern]'.
        base_dir: Base directory where filesets are downloaded.
        pattern: Default pattern to use if not specified in ref.

    Returns:
        List of dictionaries, one per row.
    """
    base_dir = Path(base_dir)
    workspace, fileset, ref_pattern = _parse_dataset_ref(ref)
    effective_pattern = ref_pattern if ref_pattern is not None else pattern
    fileset_path = base_dir / workspace / fileset
    return load_dataset_as_dicts(fileset_path, effective_pattern)
