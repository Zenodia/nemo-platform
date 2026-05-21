# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import os
from unittest.mock import patch

import pytest
from huggingface_hub import HfApi
from nmp.evaluator.app.datasets.nmp_datasets.hf import download_dataset
from nmp.evaluator.config import settings


@pytest.mark.asyncio
@patch.object(HfApi, "hf_hub_download")
@patch.dict(os.environ, {"DATA_STORE_URL": "http://data-store.test", "HF_TOKEN": "test-token"})
async def test_download_dataset_success_file(mock_hf_hub_download):
    mock_hf_hub_download.return_value = f"{settings.jobs.dataset_dir}/owner/repo/path/to/file.json"
    dataset_path, relative_repo_path = await download_dataset(
        hf_path="hf://datasets/owner/repo/path/to/file.json", local_dir=settings.jobs.dataset_dir
    )

    # Verify the result
    assert dataset_path == f"{settings.jobs.dataset_dir}/owner/repo"
    assert relative_repo_path == "path/to/file.json"


@pytest.mark.asyncio
@patch.object(HfApi, "snapshot_download")
@patch.dict(os.environ, {"DATA_STORE_URL": "http://data-store.test", "HF_TOKEN": "test-token"})
async def test_download_dataset_success_repo(mock_snapshot_download):
    mock_snapshot_download.return_value = f"{settings.jobs.dataset_dir}/owner/repo"
    dataset_path, relative_repo_path = await download_dataset(
        hf_path="hf://datasets/owner/repo", local_dir=settings.jobs.dataset_dir
    )

    # Verify the result
    assert dataset_path == f"{settings.jobs.dataset_dir}/owner/repo"
    assert relative_repo_path is None


@pytest.mark.asyncio
@patch.object(HfApi, "snapshot_download")
@patch.dict(os.environ, {"DATA_STORE_URL": "http://data-store.test", "HF_TOKEN": "test-token"})
async def test_download_dataset_success_repo_subdir(mock_snapshot_download):
    mock_snapshot_download.return_value = f"{settings.jobs.dataset_dir}/owner/repo"
    dataset_path, relative_repo_path = await download_dataset(
        hf_path="hf://datasets/owner/repo/sub/dir", local_dir=settings.jobs.dataset_dir
    )

    # Verify the result
    assert dataset_path == f"{settings.jobs.dataset_dir}/owner/repo"
    assert relative_repo_path == "sub/dir"


@pytest.mark.asyncio
async def test_download_dataset_invalid_path():
    # Test with invalid path format
    with pytest.raises(ValueError, match="Invalid dataset path: invalid/path. Must start with 'hf://datasets/'"):
        await download_dataset(hf_path="invalid/path", local_dir=settings.jobs.dataset_dir)


@pytest.mark.asyncio
@patch.object(HfApi, "hf_hub_download")
@patch.dict(os.environ, {"HF_TOKEN": "test-token"})
async def test_download_dataset_custom_endpoint(mock_hf_hub_download):
    # Call the function with custom endpoint
    mock_hf_hub_download.return_value = f"{settings.jobs.dataset_dir}/owner/repo/path/to/file.json"
    dataset_path, relative_repo_path = await download_dataset(
        hf_path="hf://datasets/owner/repo/path/to/file.json",
        local_dir=settings.jobs.dataset_dir,
        hf_endpoint="https://custom-hf-endpoint.com",
    )

    # Verify the result
    assert dataset_path == f"{settings.jobs.dataset_dir}/owner/repo"
    assert relative_repo_path == "path/to/file.json"


@pytest.mark.asyncio
@patch.object(HfApi, "hf_hub_download")
@patch.dict(os.environ, {"DATA_STORE_URL": "http://data-store.test", "HF_TOKEN": "test-token"})
async def test_download_dataset_error_handling(mock_hf_hub_download):
    mock_hf_hub_download.side_effect = Exception("Download failed")
    with pytest.raises(Exception, match="Download failed"):
        await download_dataset(
            hf_path="hf://datasets/owner/repo/path/to/file.json", local_dir=settings.jobs.dataset_dir
        )
