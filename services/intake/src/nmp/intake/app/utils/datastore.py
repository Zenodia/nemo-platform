# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Client for interacting with the NeMo Datastore service.

DEPRECATED: This module is deprecated and will be removed in a future release.
Use the Files API instead for file storage and retrieval operations.
"""

from __future__ import annotations

import logging
import warnings
from pathlib import Path
from typing import BinaryIO

from huggingface_hub import HfApi
from huggingface_hub.errors import HfHubHTTPError

# TODO(v2): CONFIG
from nmp.intake.config import config

logger = logging.getLogger(__name__)

# Emit deprecation warning when module is imported
warnings.warn(
    "nmp.intake.app.utils.datastore is deprecated and will be removed in a future release. Use the Files API instead.",
    DeprecationWarning,
    stacklevel=2,
)


class DataStoreClient:
    """Client for interacting with the NeMo Datastore service.

    .. deprecated::
        This class is deprecated. Use the Files API instead for file storage
        and retrieval operations.
    """

    def __init__(self, base_url: str | None = None, token: str | None = None):
        """Initialize the client.

        Args:
            base_url: Optional base URL for the DataStore service. If not provided, uses the URL from config.
            token: Optional authentication token. If not provided, uses the token from config.
        """
        self.base_url = base_url or config.datastore_url
        # HF-compatible Files endpoints require service principal auth when platform auth is enabled.
        self.token = token or "service:intake"
        self.api = HfApi(endpoint=f"{self.base_url}/v1/hf", token=self.token)

    def dataset_exists(self, dataset_id: str) -> bool:
        """Check if a dataset exists.

        Args:
            dataset_id: The dataset ID in format `workspace/name`

        Returns:
            bool: True if the dataset exists, False otherwise

        Raises:
            HfHubHTTPError: If the API request fails for reasons other than 404
        """
        try:
            return self.api.repo_exists(repo_id=dataset_id, repo_type="dataset")
        except HfHubHTTPError as e:
            if e.response.status_code == 404:
                return False
            raise

    def create_dataset(self, dataset_id: str) -> None:
        """Create a new dataset.

        Args:
            dataset_id: The dataset ID in format 'workspace/name'

        Raises:
            HfHubHTTPError: If dataset creation fails
        """
        logger.debug("Creating dataset: %s", dataset_id)
        self.api.create_repo(repo_id=dataset_id, repo_type="dataset")

    def delete_dataset(self, dataset_id: str) -> None:
        """Delete a dataset.

        Args:
            dataset_id: The dataset ID in format 'workspace/name'

        Raises:
            HfHubHTTPError: If dataset deletion fails
        """
        logger.debug("Deleting dataset: %s", dataset_id)
        self.api.delete_repo(repo_id=dataset_id, repo_type="dataset", missing_ok=True)

    def upload_file(
        self, file_path: str | Path | BinaryIO, dataset_id: str, path_in_repo: str, commit_message: str | None = None
    ) -> None:
        """Upload a file to a dataset.

        Args:
            file_path: Path to the file to upload, or a file-like object
            dataset_id: The dataset ID in format `workspace/name`
            path_in_repo: Path where the file should be stored in the dataset
            commit_message: Optional commit message for the upload

        Raises:
            HfHubHTTPError: If file upload fails
        """
        logger.debug("Uploading file to dataset %s at path %s", dataset_id, path_in_repo)
        self.api.upload_file(
            path_or_fileobj=file_path,
            path_in_repo=path_in_repo,
            repo_id=dataset_id,
            repo_type="dataset",
            commit_message=commit_message,
        )
