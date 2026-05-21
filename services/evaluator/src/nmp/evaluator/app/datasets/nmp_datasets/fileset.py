# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import json
import logging
import os
import uuid
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncIterator

import fsspec.asyn
from nemo_platform import AsyncNeMoPlatform, NeMoPlatform
from nemo_platform.filesets import FilesetFileSystem
from nemo_platform.types.files.fileset import Fileset as NMPFileset
from nmp.evaluator.app.datasets.fileset_selectors import (
    fileset_glob_prefix_dir,
    is_fileset_glob_pattern,
    matches_fileset_glob,
)
from nmp.evaluator.app.values import BuiltInDataset, Dataset, DatasetRows, Fileset, FilesetRef, PipelineDataset

logger = logging.getLogger(__name__)

DEFAULT_WORKSPACE_ID = "default"


def normalize_fileset_path(path: str) -> str:
    """Normalize a fileset path for local filesystem usage.

    For `FilesetRef.root`, we support fragments via `#` to select a file or a glob.
    For local path construction, we:
    - keep the base fileset path (`workspace/fileset`)
    - append a non-glob fragment (specific file / subpath)
    - drop the glob portion (and keep only the stable directory prefix, if any)

    Examples:
        "workspace/fileset#train.jsonl" -> "workspace/fileset/train.jsonl"
        "workspace/fileset#data/train.jsonl" -> "workspace/fileset/data/train.jsonl"
        "workspace/fileset#*.jsonl" -> "workspace/fileset"
        "workspace/fileset#data/*.jsonl" -> "workspace/fileset/data"
    """
    if "#" not in path:
        return path

    base, fragment = path.split("#", 1)
    fragment = fragment.lstrip("/")
    if not fragment:
        return base

    if is_fileset_glob_pattern(fragment):
        # Keep only the directory prefix before the first wildcard.
        dir_prefix = fileset_glob_prefix_dir(fragment)
        return f"{base}/{dir_prefix}" if dir_prefix else base

    return f"{base}/{fragment}"


def get_local_dataset_path(
    dataset: FilesetRef | Fileset | DatasetRows,
    output_dir: str | None,
    inline_filename: str = "dataset.json",
) -> str:
    """Get the local filesystem path where a dataset will be stored.

    This function constructs the local path for different dataset types:
    - FilesetRef: Normalizes # separator and joins with output_dir
    - Fileset: Joins output_dir with the fileset path
    - DatasetRows: Returns output_dir/inline_filename

    Args:
        dataset: The dataset object (FilesetRef, Fileset, or DatasetRows).
        output_dir: Base directory where datasets are stored.
        inline_filename: Filename for inline datasets. Defaults to "dataset.json".

    Returns:
        Full local path where the dataset will be stored.

    """
    if not output_dir:
        raise ValueError("output_dir is required for dataset path resolution")

    if isinstance(dataset, DatasetRows):
        return os.path.join(output_dir, inline_filename)

    if isinstance(dataset, FilesetRef):
        local_path = normalize_fileset_path(dataset.root)
        return os.path.join(output_dir, local_path)

    if isinstance(dataset, Fileset):
        if not dataset.path:
            return output_dir
        return os.path.join(output_dir, dataset.path)

    raise ValueError(f"Unsupported dataset type: {type(dataset)}")


def _generate_fileset_name() -> str:
    return f"fileset-{uuid.uuid4().hex[:8]}"


@asynccontextmanager
async def create_fileset(
    sdk: AsyncNeMoPlatform,
    name: str | None = None,
    workspace: str = DEFAULT_WORKSPACE_ID,
    **kwargs,
) -> AsyncIterator[NMPFileset]:
    if name is None:
        name = _generate_fileset_name()

    fileset = await sdk.files.filesets.create(
        workspace=workspace,
        name=name,
        description="Test fileset",
        **kwargs,
    )
    try:
        yield fileset
    finally:
        try:
            await sdk.files.filesets.delete(name, workspace=workspace)
        except Exception as e:
            logger.warning(f"Fileset cleanup failed: {e}")


async def dataset_exists(
    sdk: AsyncNeMoPlatform,
    dataset: PipelineDataset,
    workspace: str = DEFAULT_WORKSPACE_ID,
) -> bool:
    """
    Check if a dataset exists.

    Handles different dataset types:
    - DatasetRows: Always returns True (inline data is always available).
    - FilesetRef: Checks if the reference path exists, supporting fragments (#) and glob patterns.
    - Fileset: Creates a temporary fileset and checks if the path exists.

    For FilesetRef with fragments:
    - `workspace/fileset` - checks if fileset exists and has files
    - `workspace/fileset#file.json` - checks if specific file exists
    - `workspace/fileset#*.json` - checks if any files match the glob pattern

    Args:
        sdk: AsyncNeMoPlatform SDK instance.
        dataset: Dataset object (DatasetRows, FilesetRef, or Fileset).
        workspace: Workspace ID for the fileset (used for Fileset).

    Returns:
        True if the dataset exists, False otherwise.
    """
    # DatasetRows and BuiltInDataset - inline data is always available, BEIR/RAGAS downloaded at runtime
    if isinstance(dataset, DatasetRows) or isinstance(dataset, BuiltInDataset):
        return True

    # FilesetRef - check if the reference path exists, handling fragments and globs
    if isinstance(dataset, FilesetRef):
        fs = FilesetFileSystem(sdk=sdk)
        ref = dataset.root

        # Check if there's a fragment pattern
        if "#" in ref:
            base_path, pattern = ref.split("#", 1)
            pattern = pattern.lstrip("/")

            # First check if the base fileset exists
            if not await fs._exists(base_path):
                return False

            # For glob fragments, only verify that the base fileset and stable
            # prefix dir exist. Schema prechecks do exact wildcard expansion
            # when they need per-file validation.
            if is_fileset_glob_pattern(pattern):
                prefix_dir = fileset_glob_prefix_dir(pattern)
                if prefix_dir:
                    return await fs._exists(f"{base_path}/{prefix_dir}")
                return True
            else:
                # Specific file path - check if it exists
                full_path = f"{base_path}/{pattern}"
                return await fs._exists(full_path)

        # No fragment - just check if the fileset exists
        return await fs._exists(ref)

    # Fileset - create temporary fileset and check
    storage_config = dataset.storage.model_dump()

    async with create_fileset(sdk, workspace=workspace, storage=storage_config) as fileset:
        if dataset.path is None:
            # No specific path - check if fileset has any files
            files_response = await sdk.files.list(
                fileset=fileset.name,
                workspace=fileset.workspace,
            )
            return len(files_response.data) > 0
        else:
            # Specific path - use FilesetFileSystem._exists
            fs = FilesetFileSystem(sdk=sdk)
            fileset_path = f"{fileset.workspace}/{fileset.name}/{dataset.path}"
            return await fs._exists(fileset_path)


def _download_inline_dataset(
    dataset: DatasetRows,
    destination: str,
    filename: str = "dataset.json",
) -> Path:
    """
    Write inline dataset rows to a JSON file in the destination directory.

    Handles two formats:
    - Row-based: List of dicts [{col: val}, ...] - written as-is
    - Columnar (RAGAS/HF): Single dict with list values {col: [val, ...]} wrapped in a list
      - Unwrapped to write just the dict for HuggingFace Dataset.from_dict() compatibility

    Args:
        dataset: DatasetRows object containing row data.
        destination: Local destination directory path.
        filename: Name of the output file. Defaults to "dataset.json".

    Returns:
        Path to the created file.
    """
    output_file = Path(get_local_dataset_path(dataset, destination, inline_filename=filename))
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # Detect columnar format: single-element list containing a dict with list values
    # This is the format expected by RAGAS/HuggingFace datasets
    data_to_write = dataset.rows
    if (
        isinstance(dataset.rows, list)
        and len(dataset.rows) == 1
        and isinstance(dataset.rows[0], dict)
        and all(isinstance(v, list) for v in dataset.rows[0].values())
    ):
        # Unwrap the columnar dict for Dataset.from_dict() compatibility
        data_to_write = dataset.rows[0]

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data_to_write, f, indent=2)

    return output_file


async def _download_fileset_ref(
    sdk: AsyncNeMoPlatform,
    dataset: FilesetRef,
    destination: str,
    recursive: bool = True,
) -> Path:
    """
    Download files from a Fileset reference using FilesetFileSystem.

    Supports three reference formats:
    - 'workspace/fileset-name': Downloads all files
    - 'workspace/fileset-name#file.json': Downloads a specific file
    - 'workspace/fileset-name#*.json': Downloads files matching the glob pattern

    Args:
        sdk: AsyncNeMoPlatform SDK instance.
        dataset: FilesetRef object containing the reference path.
        destination: Local destination directory path.
        recursive: Whether to download recursively. Defaults to True.

    Returns:
        Path to the downloaded directory (destination/workspace/fileset-name).
    """
    fs = FilesetFileSystem(sdk=sdk)
    ref = dataset.root

    # Parse the fragment if present
    if "#" in ref:
        base_path, pattern = ref.split("#", 1)
        pattern = pattern.lstrip("/")

        if not pattern:
            return await _download_fileset_ref(
                sdk,
                FilesetRef(root=base_path),
                destination,
                recursive=recursive,
            )

        # Determine base destination path
        base_dest = Path(destination) / base_path
        base_dest.mkdir(parents=True, exist_ok=True)

        if is_fileset_glob_pattern(pattern):
            # Glob pattern - list files and download matching ones
            # _find returns paths in format "workspace/fileset#relative_path"
            all_files = await fs._find(base_path)
            for file_path in all_files:
                # Extract relative path: _find returns "workspace/fileset#path"
                if "#" in file_path:
                    relative_path = file_path.split("#", 1)[1]
                else:
                    relative_path = file_path.replace(base_path + "/", "", 1)
                if matches_fileset_glob(relative_path, pattern):
                    file_dest = base_dest / relative_path
                    file_dest.parent.mkdir(parents=True, exist_ok=True)
                    await fs._get_file(file_path, str(file_dest))
            return base_dest
        else:
            # Specific file path
            full_remote_path = f"{base_path}/{pattern}"
            file_dest = base_dest / pattern
            file_dest.parent.mkdir(parents=True, exist_ok=True)
            await fs._get_file(full_remote_path, str(file_dest))
            return file_dest

    # No fragment - download all files
    dest = Path(get_local_dataset_path(dataset, destination))
    # Directory download - use trailing slash on source to copy contents directly
    # into dest, rather than creating an extra subdirectory
    # (fs._get without trailing slash would create dest/fileset-name/files)
    source = ref.rstrip("/") + "/"
    await fs._get(source, str(dest), recursive=recursive)
    return dest


def _download_fileset_ref_sync(
    sdk: NeMoPlatform,
    dataset: FilesetRef,
    destination: str,
    recursive: bool = True,
) -> Path:
    """Sync bridge over `_download_fileset_ref`.

    Builds a sync-mode `FilesetFileSystem` from the sync SDK and schedules the
    async download on its fsspec daemon loop (`fs.loop`) via
    `fsspec.asyn.sync` — the same bridge pattern used by `FilesetFileManager`
    in `nemo-platform-plugin`. Closes the per-call async client in `finally` to avoid
    leaking the `httpx.AsyncClient` created by `FilesetFileSystem`. Test
    transports (e.g. ASGI) are preserved by the FilesetFileSystem converter.

    Args:
        sdk: NeMoPlatform SDK instance (sync).
        dataset: FilesetRef object containing the reference path.
        destination: Local destination directory path.
        recursive: Whether to download recursively for the no-fragment case. Defaults to True.

    Returns:
        Path to the downloaded file or directory (mirrors `_download_fileset_ref`).
    """
    fs = FilesetFileSystem(sdk=sdk)

    async def _impl() -> Path:
        try:
            return await _download_fileset_ref(fs._sdk, dataset, destination, recursive=recursive)
        finally:
            await fs._sdk.close()

    return fsspec.asyn.sync(fs.loop, _impl)


async def _download_inline_fileset(
    sdk: AsyncNeMoPlatform,
    dataset: Fileset,
    destination: str,
    workspace: str = DEFAULT_WORKSPACE_ID,
    recursive: bool = True,
) -> Path:
    """
    Download files from an Fileset configuration.

    Creates a temporary fileset, downloads the files, then cleans up.

    Args:
        sdk: AsyncNeMoPlatform SDK instance.
        dataset: Fileset object containing storage config and optional path.
        destination: Local destination directory path.
        workspace: Workspace ID for the temporary fileset.
        recursive: Whether to download recursively. Defaults to True.
    """
    storage_config = dataset.storage.model_dump()

    async with create_fileset(sdk, workspace=workspace, storage=storage_config) as fileset:
        fs = FilesetFileSystem(sdk=sdk)
        remote_path = f"{fileset.workspace}/{fileset.name}/{dataset.path or ''}"
        dest = Path(get_local_dataset_path(dataset, destination))
        await fs._get(remote_path, str(dest), recursive=recursive)
    return dest


def _download_inline_fileset_sync(
    sdk: NeMoPlatform,
    dataset: Fileset,
    destination: str,
    workspace: str = DEFAULT_WORKSPACE_ID,
    recursive: bool = True,
) -> Path:
    """Sync bridge over `_download_inline_fileset`.

    Mirrors `_download_fileset_ref_sync`: builds a sync-mode
    `FilesetFileSystem` and schedules the async inline-fileset download on
    `fs.loop` via `fsspec.asyn.sync`, closing the per-call async client in
    `finally`. Lets sync local evaluator execution handle storage-backed
    Fileset configs without duplicating the async download algorithm.
    """
    fs = FilesetFileSystem(sdk=sdk)

    async def _impl() -> Path:
        try:
            return await _download_inline_fileset(
                fs._sdk,
                dataset,
                destination,
                workspace=workspace,
                recursive=recursive,
            )
        finally:
            await fs._sdk.close()

    return fsspec.asyn.sync(fs.loop, _impl)


async def download_dataset(
    sdk: AsyncNeMoPlatform,
    dataset: Dataset,
    destination: str,
    workspace: str = DEFAULT_WORKSPACE_ID,
    recursive: bool = True,
) -> Path:
    """
    Download a dataset to a local directory.

    Handles different dataset types:
    - DatasetRows: Creates destination directory and writes rows to a JSON file.
    - FilesetRef: Downloads all files from the fileset using FilesetFileSystem._get.
    - Fileset: Creates a temporary fileset, downloads, then cleans up.

    Args:
        sdk: AsyncNeMoPlatform SDK instance.
        dataset: Dataset object (DatasetRows, FilesetRef, or Fileset).
        destination: Local destination directory path.
        workspace: Workspace ID for the fileset (used for Fileset).
        recursive: Whether to download recursively. Defaults to True.

    Example:
        # DatasetRows
        inline = DatasetRows(rows=[{"a": 1}, {"a": 2}])
        await download_dataset(sdk, inline, "/local/destination/")

        # FilesetRef
        ref = FilesetRef(root="default/my-fileset")
        await download_dataset(sdk, ref, "/local/destination/")

        # Fileset
        fileset = Fileset(
            storage={"type": "huggingface", "repo_id": "my-org/my-repo", "repo_type": "dataset"},
            path="checkpoints/"
        )
        await download_dataset(sdk, fileset, "/local/destination/")
    """
    if isinstance(dataset, DatasetRows):
        return _download_inline_dataset(dataset, destination)
    elif isinstance(dataset, FilesetRef):
        return await _download_fileset_ref(sdk, dataset, destination, recursive=recursive)
    else:
        return await _download_inline_fileset(sdk, dataset, destination, workspace=workspace, recursive=recursive)


def download_dataset_sync(
    sdk: NeMoPlatform,
    dataset: Dataset,
    destination: str,
    workspace: str = DEFAULT_WORKSPACE_ID,
    recursive: bool = True,
) -> Path:
    """
    Download a dataset to a local directory using the sync SDK where supported.

    Sync local evaluator execution supports inline rows, persisted FilesetRef
    datasets, and inline Fileset storage configs through async bridges.
    """
    if isinstance(dataset, DatasetRows):
        return _download_inline_dataset(dataset, destination)
    if isinstance(dataset, FilesetRef):
        return _download_fileset_ref_sync(sdk, dataset, destination, recursive=recursive)
    return _download_inline_fileset_sync(sdk, dataset, destination, workspace=workspace, recursive=recursive)
