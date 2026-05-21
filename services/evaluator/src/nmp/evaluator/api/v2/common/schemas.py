# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

from typing import Literal

from pydantic import BaseModel, Field

ErrorCode = Literal[
    "METRIC_NOT_FOUND",
    "METRIC_ALREADY_EXISTS",
    "METRIC_NAME_INVALID",
    "METRIC_IMMUTABLE",
    "BENCHMARK_NOT_FOUND",
    "BENCHMARK_ALREADY_EXISTS",
    "BENCHMARK_IMMUTABLE",
]


class FieldError(BaseModel):
    field: str = Field(description="The field path that has an error.")
    message: str = Field(description="Error message for this field.")


class ErrorResponse(BaseModel):
    detail: str = Field(description="Human-readable error message describing what went wrong.")
    error_code: ErrorCode = Field(description="Machine-readable error code.")
    suggestions: list[str] = Field(description="Actionable suggestions on how to resolve the error.")
    field_errors: list[FieldError] = Field(description="Validation errors for specific fields.")
