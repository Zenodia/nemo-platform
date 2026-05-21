# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Filesystem helpers for evaluator plugin SDK local result artifacts."""

from __future__ import annotations

from pathlib import Path
from typing import Literal, Self
from urllib.parse import unquote, urlparse

from nemo_evaluator.jobs.evaluate import DEFAULT_FILE_NAME
from nemo_platform_plugin.job_results import ResultRef
from pydantic import BaseModel, ConfigDict, model_validator


class EvaluatorLocalRunResult(BaseModel):
    """Validated payload returned by local evaluator plugin job execution."""

    model_config = ConfigDict(extra="allow")

    status: Literal["completed", "error"]
    artifact: ResultRef | None = None

    @model_validator(mode="after")
    def require_completed_artifact(self) -> Self:
        """Require completed local runs to include a saved result artifact."""
        if self.status == "completed" and self.artifact is None:
            raise ValueError("completed local evaluator jobs must include an artifact")
        return self


def local_result_path(payload: EvaluatorLocalRunResult) -> Path:
    """Return the JSON result file path for a completed local evaluator run."""
    if payload.status != "completed":
        raise RuntimeError(f"local evaluator job finished with status {payload.status!r}")
    if payload.artifact is None:
        raise TypeError("local evaluator job response must include an artifact object")
    artifact_path = local_artifact_path(payload.artifact)
    return artifact_path / DEFAULT_FILE_NAME if artifact_path.is_dir() else artifact_path


def local_artifact_path(artifact: ResultRef) -> Path:
    """Resolve a local evaluator job artifact reference to a filesystem path."""
    artifact_ref = artifact.artifact_url

    parsed = urlparse(artifact_ref)
    if parsed.scheme == "file":
        if parsed.netloc and parsed.netloc != "localhost":
            raise ValueError(f"local evaluator job artifact URL must point to this host: {artifact_ref!r}")
        return Path(unquote(parsed.path))
    if parsed.scheme:
        raise ValueError(f"local evaluator job artifact URL must use file:// for local execution: {artifact_ref!r}")
    return Path(artifact_ref)
