# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""API endpoints for Tasks using EntityClient pattern."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from nmp.common.api.common import Page
from nmp.common.api.filter import ComparisonOperation, FilterOperator, LogicalOperation
from nmp.common.api.parsed_filter import ParsedFilter, make_filter_dep
from nmp.common.api.utils import generate_openapi_extra_params
from nmp.common.entities.client import EntityClient, EntityConflictError, EntityNotFoundError
from nmp.common.service.dependencies import get_entity_client
from nmp.intake.entities import Task as TaskEntity

from .schemas import Task, TaskFilter, TaskInput, TaskSortField, TaskUpdate

router = APIRouter()

API_TAG = "Tasks"


@router.get(
    "/v2/workspaces/{workspace}/apps/{name}/tasks",
    response_model=Page[Task],
    tags=[API_TAG],
    response_model_exclude_none=True,
    openapi_extra=generate_openapi_extra_params(
        filter_schema=TaskFilter,
        filter_description="Filter tasks by name, app, description, project, created_at, and updated_at.",
    ),
)
async def list_tasks(
    workspace: str,
    name: str,
    entities_client: EntityClient = Depends(get_entity_client),
    page: int = Query(default=1, description="Page number."),
    page_size: int = Query(default=10, description="Page size."),
    sort: TaskSortField = Query(
        default="created_at",
        description="""The field to sort by. To sort in decreasing order, use `-` in front of the field name.""",
    ),
    parsed: ParsedFilter = Depends(make_filter_dep(TaskFilter)),
) -> Page[Task]:
    """List all tasks for a specific app."""
    # Inject app filter from URL path params
    app_ref = f"{workspace}/{name}"
    app_field = parsed._resolve_field("app")
    app_op = ComparisonOperation(field=app_field, operator=FilterOperator.EQ, value=app_ref)
    if parsed.operation is None:
        parsed.operation = app_op
    elif isinstance(parsed.operation, LogicalOperation) and parsed.operation.operator == FilterOperator.AND:
        parsed.operation.operations.append(app_op)
    else:
        parsed.operation = LogicalOperation(operator=FilterOperator.AND, operations=[parsed.operation, app_op])

    res = await entities_client.list(
        TaskEntity,
        workspace=workspace,
        page=page,
        page_size=page_size,
        sort=sort,
        filter_operation=parsed.operation,
    )

    data_dicts = [item.model_dump(by_alias=True, mode="json") for item in res.data]

    return Page[Task](
        data=data_dicts,
        pagination=res.pagination.model_dump(),
        sort=sort,
        filter=None,
    )


@router.post(
    "/v2/workspaces/{workspace}/apps/{name}/tasks",
    response_model=Task,
    tags=[API_TAG],
    status_code=status.HTTP_201_CREATED,
)
async def create_task(
    workspace: str,
    name: str,
    task_input: TaskInput,
    entities_client: EntityClient = Depends(get_entity_client),
) -> Task:
    """Create a new task."""
    # Build app reference (name is the app name from the URL path)
    app_ref = f"{workspace}/{name}"

    task_entity = TaskEntity(
        name=task_input.name,
        workspace=workspace,
        description=task_input.description,
        app=app_ref,
        locked=task_input.locked if hasattr(task_input, "locked") else False,
    )

    try:
        created = await entities_client.create(task_entity)
    except EntityConflictError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Task {workspace}/{name}/{task_entity.name} already exists",
        )

    return Task(**created.model_dump(by_alias=True, mode="json"))


@router.get(
    "/v2/workspaces/{workspace}/apps/{app}/tasks/{name}",
    response_model=Task,
    tags=[API_TAG],
)
async def get_task(
    workspace: str,
    app: str,
    name: str,
    entities_client: EntityClient = Depends(get_entity_client),
) -> Task:
    """Get a specific task."""
    app_ref = f"{workspace}/{app}"

    try:
        task_entity = await entities_client.get_by_field(TaskEntity, workspace=workspace, name=name, app=app_ref)
    except EntityNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {workspace}/{app}/{name} not found",
        )

    return Task(**task_entity.model_dump(by_alias=True, mode="json"))


@router.patch(
    "/v2/workspaces/{workspace}/apps/{app}/tasks/{name}",
    response_model=Task,
    tags=[API_TAG],
)
async def update_task(
    workspace: str,
    app: str,
    name: str,
    task_update: TaskUpdate,
    entities_client: EntityClient = Depends(get_entity_client),
) -> Task:
    """Update an existing task."""
    app_ref = f"{workspace}/{app}"

    try:
        task_entity = await entities_client.get_by_field(TaskEntity, workspace=workspace, name=name, app=app_ref)
    except EntityNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {workspace}/{app}/{name} not found",
        )

    # Apply updates
    update_data = task_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task_entity, field, value)

    updated = await entities_client.update(task_entity)

    return Task(**updated.model_dump(by_alias=True, mode="json"))


@router.delete(
    "/v2/workspaces/{workspace}/apps/{app}/tasks/{name}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=[API_TAG],
)
async def delete_task(
    workspace: str,
    app: str,
    name: str,
    entities_client: EntityClient = Depends(get_entity_client),
) -> None:
    """Delete a task."""
    app_ref = f"{workspace}/{app}"

    try:
        await entities_client.get_by_field(TaskEntity, workspace=workspace, name=name, app=app_ref)
    except EntityNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {workspace}/{app}/{name} not found",
        )

    await entities_client.delete(TaskEntity, name, workspace=workspace)
