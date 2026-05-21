# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

from typing import Annotated, get_args

from fastapi import Depends, HTTPException, Query, Request, status
from nemo_evaluator_sdk.values.results import (
    AggregateFieldName,
    DefaultAggregateFieldName,
)
from pydantic import RootModel, model_validator


def validate_list_query_params(request: Request, additional_params: set | None = None) -> None:
    """Reject unsupported top-level query params for list endpoints."""
    allowed_top_level = {"page", "page_size", "sort", "filter"}
    unsupported: list[str] = []

    if additional_params:
        allowed_top_level.update(additional_params)

    for key in request.query_params.keys():
        if key in allowed_top_level:
            continue
        if key.startswith("filter["):
            continue
        unsupported.append(key)

    if unsupported:
        unsupported_sorted = sorted(set(unsupported))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Unsupported query parameter(s): {', '.join(unsupported_sorted)}. "
                f"Allowed parameters: {', '.join(allowed_top_level)}"
            ),
        )


# =============================================================================
# Query parameters for results
# /v2/workspaces/{workspace}/metric-evaluate
# /v2/workspaces/{workspace}/metric-job-results
# =============================================================================


def _parse_aggregate_fields(value: str | list[str] | dict | None) -> list[AggregateFieldName]:
    """Parse comma-separated or repeated query params into a list of AggregateFieldName."""
    if value is None:
        return []
    # FastAPI passes dict with query param name as key
    if isinstance(value, dict):
        value = value.get("aggregate_fields", value.get("root", []))
    if isinstance(value, str):
        return [v.strip() for v in value.split(",") if v.strip()]
    if not value:
        return []
    # Handle list that may contain comma-separated strings
    result: list[AggregateFieldName] = []
    for item in value:
        result.extend(v.strip() for v in item.split(",") if v.strip())
    return result


class AggregateFieldNameList(RootModel[list[AggregateFieldName]]):
    """Query parameter type that accepts comma-separated values or repeated params.

    Used for testing. For the actual endpoint, we use AggregateFieldsQuery.
    """

    root: list[AggregateFieldName] = []

    @model_validator(mode="before")
    @classmethod
    def parse_comma_separated(cls, value: str | list[str] | dict | None) -> list[str]:
        return _parse_aggregate_fields(value)


def _aggregate_fields_dependency(
    aggregate_fields: list[str] = Query(
        default=[],
        description=(
            "Aggregate score fields to include in the response (comma-separated or repeated). "
            f"Default: {get_args(DefaultAggregateFieldName)!r}. "
            f"Available: {get_args(AggregateFieldName)!r}."
        ),
        # Add enum to OpenAPI schema - we use list[str] for parsing but want the enum documented
        json_schema_extra={"items": {"enum": list(get_args(AggregateFieldName)), "type": "string"}},
    ),
) -> list[AggregateFieldName]:
    """FastAPI dependency that parses and validates aggregate_fields query parameter.

    Handles both comma-separated values (e.g., ?aggregate_fields=std_dev,variance)
    and repeated params (e.g., ?aggregate_fields=std_dev&aggregate_fields=variance).

    Note: We use list[str] for the Query type because FastAPI's query param handling
    bypasses Pydantic's BeforeValidator. Validation happens after parsing.
    """
    valid_fields = set(get_args(AggregateFieldName))
    result: list[AggregateFieldName] = []
    for item in aggregate_fields:
        for v in item.split(","):
            v = v.strip()
            if v:
                if v not in valid_fields:
                    raise HTTPException(
                        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                        detail=f"Invalid aggregate field: '{v}'. Valid fields: {sorted(valid_fields)}",
                    )
                result.append(v)
    return result


# Type alias for use with Depends() - provides type hint for endpoint parameters
AggregateFieldsQuery = Annotated[list[AggregateFieldName], Depends(_aggregate_fields_dependency)]
