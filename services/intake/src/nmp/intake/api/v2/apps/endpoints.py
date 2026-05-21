# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""API endpoints for Apps using EntityClient pattern."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from nmp.common.api.common import Page
from nmp.common.api.parsed_filter import ParsedFilter, make_filter_dep
from nmp.common.api.utils import generate_openapi_extra_params
from nmp.common.entities import (
    EntityClient,
    EntityConflictError,
    EntityNotFoundError,
)
from nmp.common.service.dependencies import get_entity_client
from nmp.intake.entities import App as AppEntity

from .schemas import App, AppFilter, AppInput, AppSortField, AppUpdate

router = APIRouter()

API_TAG = "Apps"


@router.get(
    "/v2/workspaces/{workspace}/apps",
    response_model=Page[App],
    tags=[API_TAG],
    response_model_exclude_none=True,
    openapi_extra=generate_openapi_extra_params(
        filter_schema=AppFilter,
        filter_description="Filter apps by name, description, project, created_at, and updated_at.",
    ),
)
async def list_apps(
    workspace: str,
    entities_client: EntityClient = Depends(get_entity_client),
    page: int = Query(default=1, description="Page number."),
    page_size: int = Query(default=10, description="Page size."),
    sort: AppSortField = Query(
        default="created_at",
        description="""The field to sort by. To sort in decreasing order, use `-` in front of the field name.""",
    ),
    parsed: ParsedFilter = Depends(make_filter_dep(AppFilter)),
) -> Page[App]:
    """List all apps with filtering capabilities."""
    res = await entities_client.list(
        AppEntity,
        page=page,
        page_size=page_size,
        sort=sort,
        workspace=workspace,
        filter_operation=parsed.operation,
    )

    data_dicts = [item.model_dump(by_alias=True, mode="json") for item in res.data]

    return Page[App](
        data=data_dicts,
        pagination=res.pagination.model_dump(),
        sort=sort,
        filter=None,
    )


@router.post(
    "/v2/workspaces/{workspace}/apps",
    responses={
        200: {"description": "Successful Response"},
        409: {"description": "App already exists"},
        422: {"description": "Validation Error"},
    },
    response_model=App,
    tags=[API_TAG],
    status_code=status.HTTP_201_CREATED,
)
async def create_app(
    workspace: str,
    app_input: AppInput,
    entities_client: EntityClient = Depends(get_entity_client),
) -> App:
    """Create a new app."""
    # Convert input to entity
    app_entity = AppEntity(
        name=app_input.name,
        workspace=workspace,
        description=app_input.description,
        locked=app_input.locked if hasattr(app_input, "locked") else False,
    )

    try:
        created = await entities_client.create(app_entity)
    except EntityConflictError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"App {app_entity.workspace}/{app_entity.name} already exists",
        )

    return App(**created.model_dump(by_alias=True, mode="json"))


@router.get(
    "/v2/workspaces/{workspace}/apps/{name}",
    response_model=App,
    tags=[API_TAG],
)
async def get_app(
    workspace: str,
    name: str,
    entities_client: EntityClient = Depends(get_entity_client),
) -> App:
    """Get a specific app by workspace and name."""
    try:
        app_entity = await entities_client.get(AppEntity, name=name, workspace=workspace)
    except EntityNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"App {workspace}/{name} not found",
        )

    return App(**app_entity.model_dump(by_alias=True, mode="json"))


@router.patch(
    "/v2/workspaces/{workspace}/apps/{name}",
    response_model=App,
    tags=[API_TAG],
)
async def update_app(
    workspace: str,
    name: str,
    app_update: AppUpdate,
    entities_client: EntityClient = Depends(get_entity_client),
) -> App:
    """Update an existing app."""
    try:
        app_entity = await entities_client.get(AppEntity, name=name, workspace=workspace)
    except EntityNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"App {workspace}/{name} not found",
        )

    # Apply updates (only update fields that were provided)
    update_data = app_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(app_entity, field, value)

    # Save updated entity
    updated = await entities_client.update(app_entity)

    return App(**updated.model_dump(by_alias=True, mode="json"))


@router.delete(
    "/v2/workspaces/{workspace}/apps/{name}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=[API_TAG],
)
async def delete_app(
    workspace: str,
    name: str,
    entities_client: EntityClient = Depends(get_entity_client),
) -> None:
    """Delete an app."""
    try:
        await entities_client.get(AppEntity, name=name, workspace=workspace)
    except EntityNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"App {workspace}/{name} not found",
        )

    await entities_client.delete(AppEntity, name, workspace=workspace)
