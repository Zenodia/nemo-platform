# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import logging
from pathlib import Path
from urllib.parse import urlparse

# Configure logger with a specific name
logger = logging.getLogger("nmp.intake.app.utils.exports")

# Supported file extensions for exports
SUPPORTED_FILE_EXTENSIONS: list[str] = [".jsonl"]


def is_local_file_uri(uri: str) -> bool:
    """Check if URI is local filesystem (file://)."""
    parsed = urlparse(uri)
    logger.debug(f"Checking if {uri} is a local file URI. Scheme: {parsed.scheme}")
    return parsed.scheme == "file"


def is_datastore_uri(uri: str) -> bool:
    """Check if URI is HuggingFace dataset (hf://) or NeMo Datastore (nds://)."""
    parsed = urlparse(uri)
    logger.debug(f"Checking if {uri} is a datastore URI. Scheme: {parsed.scheme}")
    return parsed.scheme in ("hf", "nds")


def extract_local_path(uri: str) -> Path:
    """Extract filesystem path from file:// URI."""
    logger.debug(f"Extracting local path from URI: {uri}")
    parsed = urlparse(uri)
    if parsed.scheme != "file":
        logger.error(f"Invalid URI scheme: {parsed.scheme}. Expected 'file'")
        raise ValueError(f"Not a file:// URI: {uri}")

    path = Path(parsed.path)
    logger.debug(f"Extracted path: {path}")
    logger.debug(f"Absolute path: {path.absolute()}")
    return path


def extract_datastore_path(uri: str) -> tuple[str, str]:
    """Extract dataset ID and file path from hf:// URI.

    Args:
        uri: The HuggingFace URI in format hf://datasets/namespace/name/path/to/file

    Returns:
        tuple[str, str]: (dataset_id, path_in_repo)
    """
    logger.debug(f"Extracting datastore path from URI: {uri}")
    uri_components = urlparse(uri)
    if uri_components.scheme != "hf":
        logger.error(f"Invalid URI scheme: {uri_components.scheme}. Expected 'hf'")
        raise ValueError(f"Not a hf:// URI: {uri}")

    # Remove leading slash from path
    dataset_path = uri_components.path.lstrip("/")
    path_parts = dataset_path.split("/")
    logger.debug(f"Path parts: {path_parts}")

    # Ensure path contains at least two parts (namespace/name)
    if len(path_parts) < 2:
        logger.error(f"Invalid path format. Got {len(path_parts)} parts, expected at least 2")
        raise ValueError("Invalid URI format. Expected format: hf://datasets/namespace/dataset_name/file_name")

    dataset_id = f"{path_parts[0]}/{path_parts[1]}"
    logger.info(f"dataset_id: {dataset_id}")

    # Extract file path from remaining parts of URI
    path_in_repo = "/".join(path_parts[2:]) if len(path_parts) > 2 else ""
    logger.info(f"path_in_repo: {path_in_repo}")

    if not path_in_repo or not path_in_repo.endswith(tuple(SUPPORTED_FILE_EXTENSIONS)):
        logger.error(f"Invalid file path: {path_in_repo}. Supported extensions: {SUPPORTED_FILE_EXTENSIONS}")
        raise ValueError("Invalid file path. Supported file extensions: " + ", ".join(SUPPORTED_FILE_EXTENSIONS))

    return dataset_id, path_in_repo


def extract_nds_path(uri: str) -> tuple[str, str]:
    """Extract workspace and dataset name from nds:// URI.

    Args:
        uri: The NeMo Datastore URI in format nds://workspace/dataset_name

    Returns:
        tuple[str, str]: (workspace, dataset_name)
    """
    logger.debug(f"Extracting NDS path from URI: {uri}")
    uri_components = urlparse(uri)
    if uri_components.scheme != "nds":
        logger.error(f"Invalid URI scheme: {uri_components.scheme}. Expected 'nds'")
        raise ValueError(f"Not a nds:// URI: {uri}")

    # For nds://workspace/dataset_name:
    # - workspace is in netloc
    # - dataset_name is in path (without leading slash)
    workspace = uri_components.netloc
    dataset_name = uri_components.path.lstrip("/")

    logger.debug(f"Parsed workspace: {workspace}, dataset_name: {dataset_name}")

    # Validate that both parts exist
    if not workspace or not dataset_name:
        logger.error(f"Invalid URI format. workspace='{workspace}', dataset_name='{dataset_name}'")
        raise ValueError("Invalid URI format. Expected format: nds://workspace/dataset_name")

    logger.info(f"workspace: {workspace}")
    logger.info(f"dataset_name: {dataset_name}")

    return workspace, dataset_name
