# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""FastAPI filter utilities for entity endpoints."""

from copy import deepcopy
from typing import Callable, Type, TypeVar

from fastapi import HTTPException
from nmp.common.api.utils import parse_deep_object
from pydantic import BaseModel
from starlette import status
from starlette.requests import Request

FilterType = TypeVar("FilterType")


def _extract_validated_fields(validated: BaseModel, raw: dict) -> dict:
    """Extract fields from validated model that correspond to raw input fields.

    This ensures we get type conversions from Pydantic validation (e.g., datetime strings
    to datetime objects) while only including fields that were actually provided in the
    query parameters, avoiding issues with default values.

    Args:
        validated: The validated Pydantic model instance with proper types
        raw: The original raw dict from query parameters

    Returns:
        Dict with the same structure as raw but with properly typed values
    """
    result = {}
    for key in raw.keys():
        if hasattr(validated, key):
            value = getattr(validated, key)
            if isinstance(raw[key], dict) and isinstance(value, BaseModel):
                # Use model_dump with by_alias=True and mode="json" to:
                # - Output aliased field names (e.g., $gte instead of gte for DatetimeFilter)
                # - Serialize datetime objects to ISO format strings
                result[key] = value.model_dump(exclude_none=True, by_alias=True, mode="json")
            elif isinstance(value, BaseModel):
                # Handle case where validator transformed a string into a BaseModel
                # (e.g., URN string -> NamedEntityFilter with namespace/name fields)
                result[key] = value.model_dump(exclude_none=True, by_alias=True, mode="json")
            else:
                result[key] = value
    return result


def make_filter_obj_dep(filter_model: Type[FilterType], param_name: str = "filter") -> Callable[[Request], FilterType]:
    """Create a FastAPI dependency for parsing deepObject-style filter query parameters.

    This function creates a dependency that parses filter[field][subfield]=value style
    query parameters into a validated Pydantic model.

    Args:
        filter_model: The Pydantic model class to validate the filter against
        param_name: The name of the query parameter prefix (default: "filter")

    Returns:
        A FastAPI dependency function that returns the parsed and validated filter

    Example:
        ```python
        class MyFilter(Filter):
            name: Optional[str] = None
            created_at: Optional[DatetimeFilter] = None

        @router.get("/items")
        async def list_items(filter: dict = Depends(make_filter_obj_dep(MyFilter))):
            # filter will contain validated values from query params like:
            # ?filter[name]=foo&filter[created_at][gte]=2024-01-01
            ...
        ```
    """

    async def _dep(request: Request) -> FilterType:
        try:
            raw = parse_deep_object(name=param_name, params=request.query_params) or {}
        except ValueError as e:
            # Return a proper 400 response
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

        # We add support for raw filters for advanced use cases not covered by the standard filtering schema
        # When raw mode is enabled, we don't validate the filter object
        if raw.get("*"):
            return raw
        else:
            # Validate and convert types (e.g., datetime strings to datetime objects)
            # Use deepcopy to avoid validators modifying the original raw dict
            validated = filter_model.model_validate(deepcopy(raw))
            # Return dict with only the fields that were in the raw input, but with converted types
            return _extract_validated_fields(validated, raw)

    return _dep
