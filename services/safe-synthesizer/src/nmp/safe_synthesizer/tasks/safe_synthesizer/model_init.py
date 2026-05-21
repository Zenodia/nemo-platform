# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Model initialization module for downloading models from Files API.

This module downloads model weights from the Files API and places them
in the HuggingFace cache directory structure so that `from_pretrained()`
calls can find them without network access.
"""

import asyncio
import hashlib
import logging
import os
from dataclasses import dataclass
from pathlib import Path

import httpx
from nmp.common.config import Configuration

logger = logging.getLogger(__name__)

# Default HuggingFace cache directory
DEFAULT_HF_HOME = "/app/.cache/huggingface"


@dataclass
class ModelFileset:
    """Configuration for a model fileset to download."""

    workspace: str
    name: str
    # The HuggingFace model ID that from_pretrained() will use
    # e.g., "gretelai/gretel-gliner-bi-large-v1.0"
    hf_model_id: str

    @property
    def fileset_ref(self) -> str:
        return f"{self.workspace}/{self.name}"


# Default model filesets for Safe Synthesizer
# These correspond to the filesets created by setup_model_filesets.py
DEFAULT_MODEL_FILESETS = [
    ModelFileset(
        workspace="default",
        name="smollm3-3b",
        hf_model_id="HuggingFaceTB/SmolLM3-3B",
    ),
    ModelFileset(
        workspace="default",
        name="gliner-gretel-bi-large",
        hf_model_id="gretelai/gretel-gliner-bi-large-v1.0",
    ),
    ModelFileset(
        workspace="default",
        name="bge-base-en",
        hf_model_id="BAAI/bge-base-en-v1.5",
    ),
    ModelFileset(
        workspace="default",
        name="sentence-transformer-distiluse",
        hf_model_id="sentence-transformers/distiluse-base-multilingual-cased-v2",
    ),
]


def get_hf_cache_dir(hf_home: str | None = None) -> Path:
    """Get the HuggingFace hub cache directory."""
    hf_home = hf_home or os.environ.get("HF_HOME", DEFAULT_HF_HOME)
    return Path(hf_home) / "hub"


def get_model_cache_path(model_id: str, hf_home: str | None = None) -> Path:
    """Get the cache path for a specific model.

    HuggingFace uses the format: hub/models--{org}--{model}/
    where slashes in model_id are replaced with double dashes.
    """
    cache_dir = get_hf_cache_dir(hf_home)
    # Replace / with -- for the directory name
    model_dir_name = f"models--{model_id.replace('/', '--')}"
    return cache_dir / model_dir_name


def generate_snapshot_hash(fileset_name: str) -> str:
    """Generate a consistent snapshot hash for a fileset.

    We use a hash of the fileset name to create a stable "commit" identifier.
    This allows HuggingFace's cache to recognize the files.
    """
    return hashlib.sha1(fileset_name.encode()).hexdigest()[:40]


def is_model_cached(model_id: str, hf_home: str | None = None) -> bool:
    """Check if a model is already cached locally."""
    model_path = get_model_cache_path(model_id, hf_home)
    snapshots_dir = model_path / "snapshots"

    if not snapshots_dir.exists():
        return False

    # Check if there's at least one snapshot with files
    for snapshot in snapshots_dir.iterdir():
        if snapshot.is_dir() and any(snapshot.iterdir()):
            return True

    return False


async def download_file(
    client: httpx.AsyncClient,
    files_api_url: str,
    workspace: str,
    fileset_name: str,
    file_path: str,
    dest_path: Path,
) -> None:
    """Download a single file from the Files API."""
    url = f"{files_api_url}/v2/workspaces/{workspace}/filesets/{fileset_name}/-/{file_path}"

    dest_path.parent.mkdir(parents=True, exist_ok=True)

    async with client.stream("GET", url) as response:
        response.raise_for_status()
        with open(dest_path, "wb") as f:
            async for chunk in response.aiter_bytes(chunk_size=64 * 1024):
                f.write(chunk)

    logger.debug(f"Downloaded: {file_path} -> {dest_path}")


async def list_fileset_files(
    client: httpx.AsyncClient,
    files_api_url: str,
    workspace: str,
    fileset_name: str,
) -> list[dict]:
    """List all files in a fileset."""
    url = f"{files_api_url}/v2/workspaces/{workspace}/filesets/{fileset_name}/files"
    response = await client.get(url)
    response.raise_for_status()
    return response.json().get("files", [])


async def download_model_fileset(
    client: httpx.AsyncClient,
    files_api_url: str,
    fileset: ModelFileset,
    hf_home: str | None = None,
    force: bool = False,
) -> bool:
    """Download a model fileset to the HuggingFace cache.

    Args:
        client: HTTP client for making requests
        files_api_url: Base URL of the Files API
        fileset: Model fileset configuration
        hf_home: HuggingFace home directory
        force: Force re-download even if cached

    Returns:
        True if download was successful or model was already cached
    """
    model_id = fileset.hf_model_id

    # Check if already cached
    if not force and is_model_cached(model_id, hf_home):
        logger.info(f"Model already cached: {model_id}")
        return True

    logger.info(f"Downloading model: {model_id} from fileset {fileset.fileset_ref}")

    try:
        # List files in the fileset
        files = await list_fileset_files(client, files_api_url, fileset.workspace, fileset.name)

        if not files:
            logger.warning(f"No files found in fileset: {fileset.fileset_ref}")
            return False

        # Set up cache directories
        model_cache_path = get_model_cache_path(model_id, hf_home)
        snapshot_hash = generate_snapshot_hash(fileset.name)
        snapshot_path = model_cache_path / "snapshots" / snapshot_hash

        # Download all files
        download_tasks = []
        for file_info in files:
            file_path = file_info["path"]
            dest_path = snapshot_path / file_path
            download_tasks.append(
                download_file(
                    client,
                    files_api_url,
                    fileset.workspace,
                    fileset.name,
                    file_path,
                    dest_path,
                )
            )

        await asyncio.gather(*download_tasks)

        # Create refs/main to point to this snapshot
        refs_dir = model_cache_path / "refs"
        refs_dir.mkdir(parents=True, exist_ok=True)
        (refs_dir / "main").write_text(snapshot_hash)

        logger.info(f"Successfully downloaded model: {model_id} ({len(files)} files)")
        return True

    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error downloading {model_id}: {e.response.status_code}")
        return False
    except Exception as e:
        logger.error(f"Error downloading {model_id}: {e}")
        return False


async def init_models(
    files_api_url: str,
    filesets: list[ModelFileset] | None = None,
    hf_home: str | None = None,
    force: bool = False,
    timeout: float = 600.0,
) -> dict[str, bool]:
    """Initialize all model weights by downloading from Files API.

    Args:
        files_api_url: Base URL of the Files API
        filesets: List of model filesets to download (defaults to all Safe Synthesizer models)
        hf_home: HuggingFace home directory
        force: Force re-download even if cached
        timeout: HTTP timeout in seconds

    Returns:
        Dict mapping model IDs to success status
    """
    filesets = filesets or DEFAULT_MODEL_FILESETS
    results = {}

    async with httpx.AsyncClient(timeout=timeout) as client:
        for fileset in filesets:
            success = await download_model_fileset(client, files_api_url, fileset, hf_home, force)
            results[fileset.hf_model_id] = success

    return results


def init_models_sync(
    files_api_url: str | None = None,
    filesets: list[ModelFileset] | None = None,
    hf_home: str | None = None,
    force: bool = False,
) -> dict[str, bool]:
    """Synchronous wrapper for init_models.

    Uses environment variables if files_api_url is not provided:
    - NMP_FILES_URL
    """
    if files_api_url is None:
        files_api_url = Configuration.get_platform_config().get_service_url("files")

    if not files_api_url:
        logger.warning(
            "Files API URL not configured. Set NMP_FILES_URL or pass files_api_url parameter. Skipping model download."
        )
        return {}

    logger.info(f"Initializing models from Files API: {files_api_url}")

    return asyncio.run(
        init_models(
            files_api_url=files_api_url,
            filesets=filesets,
            hf_home=hf_home,
            force=force,
        )
    )


if __name__ == "__main__":
    import sys

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Allow running standalone for testing
    files_url = sys.argv[1] if len(sys.argv) > 1 else None
    results = init_models_sync(files_api_url=files_url)

    if results:
        print("\nModel initialization results:")
        for model_id, success in results.items():
            status = "OK" if success else "FAILED"
            print(f"  {model_id}: {status}")

        failed = [m for m, s in results.items() if not s]
        if failed:
            print(f"\n{len(failed)} model(s) failed to download")
            sys.exit(1)
    else:
        print("No models were initialized (Files API URL not configured)")
