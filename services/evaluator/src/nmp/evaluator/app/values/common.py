# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Common value types used throughout the evaluator service."""

from __future__ import annotations

from typing import Annotated, Any

from nmp.common.files.metadata import FilesetMetadata
from nmp.common.files.storage_config import (
    HuggingfaceStorageConfig,
    NGCStorageConfig,
)
from pydantic import BaseModel, ConfigDict, Field, RootModel


class MetricRef(RootModel):
    """Reference to a metric in the Metrics API.

    A reference is a string with format 'workspace/metric-name' that points to a
    persisted metric entity. See [Entity references](docs/get-started/concepts/entity-references.md) for the
    general entity reference pattern used across the platform.
    """

    root: str = Field(
        description="Reference to a metric (format: workspace/metric-name).",
        pattern=r"^[a-z0-9_-]+/[a-z0-9_-]+$",
        examples=[
            "workspace/metric-name",
        ],
    )


class BenchmarkRef(RootModel):
    """Reference to a benchmark in the Benchmarks API.

    A reference is a string with format 'workspace/benchmark-name' that points to a
    persisted benchmark entity. See [Entity references](docs/get-started/concepts/entity-references.md) for the
    general entity reference pattern used across the platform.
    """

    root: str = Field(
        description="Reference to a benchmark (format: workspace/benchmark-name).",
        pattern=r"^[a-z0-9_-]+/[a-z0-9_-]+$",
        examples=[
            "workspace/benchmark-name",
        ],
    )


class ModelRef(RootModel):
    """Reference to a Model in the Models API.

    See [Entity references](docs/get-started/concepts/entity-references.md) for the general entity reference
    pattern used across the platform.
    """

    root: str = Field(
        description="Reference to a model (format: workspace/name).",
        pattern=r"^[a-z0-9_-]+/[a-z0-9_-]+$",
        examples=[
            "workspace/model_name",
        ],
    )


StorageConfig = NGCStorageConfig | HuggingfaceStorageConfig

StorageConfigField = Annotated[StorageConfig, Field(discriminator="type")]


class Fileset(BaseModel):
    """Fileset definition for use without persisting to the Files API."""

    model_config = ConfigDict(extra="forbid")

    path: str | None = Field(
        default=None, min_length=1, description="The relative path to file/directory in the storage."
    )
    storage: StorageConfig = Field(description="The storage configuration for the fileset.")
    metadata: FilesetMetadata = Field(
        default_factory=FilesetMetadata,
        description="Purpose-specific metadata for the fileset.",
    )
    custom_fields: dict[str, Any] = Field(default_factory=dict, description="Custom fields for the fileset.")


class FilesetRef(RootModel):
    """Reference to a Fileset in the Files API.

    A reference is a string with format 'workspace/fileset-name' that points to a
    persisted fileset entity. When used as a dataset source, all files within the
    fileset will be downloaded to the job container.

    See [Entity references](docs/get-started/concepts/entity-references.md) for the general entity reference
    pattern used across the platform.
    """

    root: str = Field(description="Reference to a Fileset (format: workspace/fileset-name).")

    def with_fragment(self, fragment: str) -> FilesetRef:
        """Return a new fileset reference with a file path fragment appended."""
        normalized_fragment = fragment.lstrip("/")
        if not normalized_fragment:
            raise ValueError("FilesetRef fragment cannot be empty.")
        if "#" in normalized_fragment:
            raise ValueError("FilesetRef fragment cannot contain '#'.")
        if "#" in self.root:
            raise ValueError("FilesetRef already includes a fragment.")
        return FilesetRef(root=f"{self.root}#{normalized_fragment}")
