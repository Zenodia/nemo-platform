# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Shared evaluation context model for span ingest endpoints."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator


class EvaluationContext(BaseModel):
    evaluation_id: str | None = None
    evaluation_sha: str | None = None
    evaluation_run_id: str | None = None
    dataset_id: str | None = None
    dataset_name: str | None = None
    dataset_version: str | None = None
    test_case_id: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="after")
    def require_run_id_when_context_is_set(self) -> EvaluationContext:
        if self.evaluation_run_id is None and self._has_values():
            raise ValueError("evaluation_context.evaluation_run_id is required when evaluation_context fields are set")
        return self

    def _has_values(self) -> bool:
        return any(
            (
                self.evaluation_id,
                self.evaluation_sha,
                self.dataset_id,
                self.dataset_name,
                self.dataset_version,
                self.test_case_id,
                self.metadata,
            )
        )
