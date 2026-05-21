# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import asyncio
import os
from typing import Tuple

from huggingface_hub import HfApi

hf_dataset_prefix = "hf://datasets/"


async def download_dataset(
    hf_path: str, local_dir: str, hf_endpoint: str | None = None, hf_token: str | None = None
) -> Tuple[str, str | None]:
    """
    Download a file from HuggingFace Hub to a local directory.

    Args:
        hf_path: The HuggingFace path in format hf://datasets/owner/repo/path/to/file
        local_dir: The local directory where the file should be downloaded
        hf_endpoint: Optional HuggingFace endpoint URL
        hf_token: Optional HuggingFace token

    Returns:
        str: The directory path where the dataset downloaded to
        str | None: The relative path to the downloaded file or a subdirectory within the repo
    """
    if not hf_path.startswith(hf_dataset_prefix):
        raise ValueError(f"Invalid dataset path: {hf_path}. Must start with '{hf_dataset_prefix}'")

    # If no HF endpoint is provided, use default
    hf_endpoint = hf_endpoint or os.environ.get("DATA_STORE_URL")
    if not hf_endpoint:
        raise ValueError("DATA_STORE_URL is not defined and no HuggingFace endpoint provided for downloading dataset.")

    # For the token, we put a fake one when using Data Store
    hf_token = hf_token or os.environ.get("DATA_STORE_TOKEN")
    is_file = "." in hf_path.split("/")[-1]

    hf_api = HfApi(endpoint=hf_endpoint, token=hf_token)

    # Parse repo_id namespace/name and relative path to file or dataset subdirectory if included
    hf_dataset_uri = hf_path.removeprefix(hf_dataset_prefix)
    if hf_dataset_uri.count("/") == 1:
        repo_id = hf_dataset_uri
        relative_repo_path = None
    else:
        (
            repo_ns,
            repo_name,
            relative_repo_path,
        ) = hf_dataset_uri.split("/", maxsplit=2)
        repo_id = f"{repo_ns}/{repo_name}"

    if is_file:
        # Download only the specified file
        assert relative_repo_path is not None
        local_dir = os.path.join(local_dir, repo_id)
        await asyncio.to_thread(
            hf_api.hf_hub_download,
            repo_id=repo_id,
            filename=relative_repo_path,
            local_dir=local_dir,
            repo_type="dataset",
        )
    else:
        # Download the entire repo when the URI is namespace/name or includes a subdirectory of the repo
        # e.g. namespace/name/subdirectory_path
        local_dir = os.path.join(local_dir, repo_id)
        local_dir = await asyncio.to_thread(
            hf_api.snapshot_download, repo_id=repo_id, repo_type="dataset", local_dir=local_dir
        )

    return local_dir, relative_repo_path
