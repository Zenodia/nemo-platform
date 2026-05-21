# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""API endpoints for Entries using EntityClient pattern."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from nemo_platform_plugin.filter_ops import FilterOperation
from nmp.common.api.common import Page, PaginationData
from nmp.common.api.parsed_filter import ParsedFilter, make_filter_dep
from nmp.common.api.utils import generate_openapi_extra_params
from nmp.common.entities import EntityClient, EntityConflictError, EntityNotFoundError
from nmp.common.service.dependencies import get_entity_client
from nmp.intake.entities import App as AppEntity
from nmp.intake.entities import Entry as EntryEntity
from nmp.intake.entities import Task as TaskEntity
from nmp.intake.entities import Usage, UserRating

from .schemas import Entry, EntryFilter, EntryInput, EntrySortField, EntryUpdate, EventsCreateRequest

router = APIRouter()

API_TAG = "Entries"

# Core entities `GET .../entities/{entity_type}` caps `page_size` at 1000 (Query le=1000).
_ENTITIES_LIST_MAX_PAGE_SIZE = 1000


# ---------------------------------------------------------------------------
# Helper Functions
# ---------------------------------------------------------------------------


async def _fetch_all_entry_entities(
    entities_client: EntityClient,
    *,
    workspace: str,
    sort: EntrySortField,
    filter_operation: FilterOperation | None,
) -> list:
    """Load all matching intake entries by paging entity-store list calls.

    ``longest_per_thread`` needs every row in the workspace filter to group by
    ``thread_id``, but the entities API rejects ``page_size`` > 1000 with HTTP 422.
    """
    page_size = _ENTITIES_LIST_MAX_PAGE_SIZE
    first = await entities_client.list(
        EntryEntity,
        page=1,
        page_size=page_size,
        sort=sort,
        workspace=workspace,
        filter_operation=filter_operation,
    )
    all_rows = list(first.data)
    total_pages = first.pagination.total_pages
    for page_num in range(2, total_pages + 1):
        page_res = await entities_client.list(
            EntryEntity,
            page=page_num,
            page_size=page_size,
            sort=sort,
            workspace=workspace,
            filter_operation=filter_operation,
        )
        all_rows.extend(page_res.data)
    return all_rows


def _parse_entry_id(entry_id: str) -> tuple[str, bool]:
    """Parse entry_id to check if it's an external_id reference.

    Returns:
        tuple: (actual_id, is_external) where is_external is True if using external: prefix
    """
    if entry_id.startswith("external:"):
        return entry_id[9:], True  # Remove "external:" prefix
    return entry_id, False


async def _get_entry_by_id_or_external(
    entities_client: EntityClient,
    entry_id: str,
    workspace: str,
) -> Optional[EntryEntity]:
    """Get entry by ID or external_id depending on prefix."""
    actual_id, is_external = _parse_entry_id(entry_id)

    try:
        if is_external:
            # Search by external_id
            return await entities_client.get_by_field(EntryEntity, workspace=workspace, external_id=actual_id)
        else:
            # Get by primary key (entity ID)
            return await entities_client.get_by_id(EntryEntity, actual_id)
    except EntityNotFoundError:
        return None


# ---------------------------------------------------------------------------
# Entry Endpoints
# ---------------------------------------------------------------------------


@router.get(
    "/v2/workspaces/{workspace}/entries",
    response_model=Page[Entry],
    tags=[API_TAG],
    openapi_extra=generate_openapi_extra_params(
        filter_schema=EntryFilter,
        filter_description=(
            "Filter entries by id, project, external_id, created_at, updated_at, "
            "usage fields (model), context fields, and user_rating fields."
        ),
    ),
)
async def list_entries(
    workspace: str,
    entities_client: EntityClient = Depends(get_entity_client),
    page: int = Query(default=1, description="Page number."),
    page_size: int = Query(default=10, description="Page size."),
    sort: EntrySortField = Query(
        default="created_at",
        description="""The field to sort by. To sort in decreasing order, use `-` in front of the field name.""",
    ),
    parsed: ParsedFilter = Depends(make_filter_dep(EntryFilter)),
) -> Page[Entry]:
    """List all entries with filtering capabilities.

    When longest_per_thread=true is set in filters, returns only the longest entry
    (by message count) for each unique thread_id.
    """
    # Extract longest_per_thread before forwarding to entity store
    longest_per_thread_val = parsed.remove("longest_per_thread")
    longest_per_thread = longest_per_thread_val in (True, "true")

    # Workspace from the path takes precedence over any filter value.
    parsed.remove("workspace")

    if longest_per_thread:
        # Need full filtered corpus to pick longest-per-thread; entities API max page_size is 1000.
        entry_rows = await _fetch_all_entry_entities(
            entities_client,
            workspace=workspace,
            sort=sort,
            filter_operation=parsed.operation,
        )

        # Group entries by thread_id and keep only the longest per thread
        from collections import defaultdict

        threads = defaultdict(list)

        for entry in entry_rows:
            if entry.context and entry.context.thread_id:
                threads[entry.context.thread_id].append(entry)

        # For each thread, keep only the entry with most messages
        filtered_entries = []
        for thread_entries in threads.values():

            def get_message_count(entry):
                """Count messages in an entry."""
                try:
                    if entry.data and hasattr(entry.data, "request") and hasattr(entry.data.request, "messages"):
                        return len(entry.data.request.messages)
                    elif entry.data and isinstance(entry.data, dict):
                        request = entry.data.get("request", {})
                        if isinstance(request, dict):
                            messages = request.get("messages", [])
                            return len(messages) if isinstance(messages, list) else 0
                except Exception:
                    pass
                return 0

            # Get the entry with the most messages
            longest_entry = max(thread_entries, key=get_message_count, default=None)
            if longest_entry:
                filtered_entries.append(longest_entry)

        # Apply pagination to filtered results
        total_results = len(filtered_entries)
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_entries = filtered_entries[start_idx:end_idx]

        data_dicts = [entry.model_dump(by_alias=True, mode="json") for entry in paginated_entries]

        return Page[Entry](
            data=data_dicts,
            pagination=PaginationData(
                page=page,
                page_size=page_size,
                current_page_size=len(paginated_entries),
                total_results=total_results,
                total_pages=(total_results + page_size - 1) // page_size,
            ),
            sort=sort,
            filter=None,
        )
    else:
        # Normal listing without longest_per_thread
        res = await entities_client.list(
            EntryEntity,
            page=page,
            page_size=page_size,
            sort=sort,
            workspace=workspace,
            filter_operation=parsed.operation,
        )

        data_dicts = [entry.model_dump(by_alias=True, mode="json") for entry in res.data]

        return Page[Entry](
            data=data_dicts,
            pagination=res.pagination.model_dump(),
            sort=sort,
            filter=None,
        )


def _auto_register_app_and_task_async(
    entities_client: EntityClient,
    app_ref: str,
    task_name: Optional[str],
    workspace: str,
) -> None:
    """Auto-register app and task if they don't exist - fire and forget."""
    import asyncio

    # Parse app reference (format: "workspace/app_name")
    if "/" in app_ref:
        app_workspace, app_name = app_ref.split("/", 1)
    else:
        app_workspace = workspace
        app_name = app_ref

    # Build full app reference for task association
    full_app_ref = f"{app_workspace}/{app_name}"

    # Fire off inserts without waiting
    async def try_insert_app():
        try:
            app = AppEntity(
                name=app_name,
                workspace=app_workspace,
                description="Auto-registered from entry",
            )
            await entities_client.create(app)
        except EntityConflictError:
            pass  # Already exists

    async def try_insert_task():
        if task_name:
            try:
                task = TaskEntity(
                    name=task_name,
                    workspace=workspace,
                    app=full_app_ref,
                    description="Auto-registered from entry",
                )
                await entities_client.create(task)
            except EntityConflictError:
                pass  # Already exists

    # Launch background tasks without waiting
    asyncio.create_task(try_insert_app())
    if task_name:
        asyncio.create_task(try_insert_task())


@router.post(
    "/v2/workspaces/{workspace}/entries",
    response_model=Entry,
    tags=[API_TAG],
    status_code=status.HTTP_201_CREATED,
)
async def create_entry(
    workspace: str,
    entry_input: EntryInput,
    entities_client: EntityClient = Depends(get_entity_client),
) -> Entry:
    """Create a new entry.

    Apps and tasks referenced in the entry context will be auto-created if they don't exist.
    """
    # Generate a unique name for the entry
    from nmp.core.entities.utils.identifiers import generate_random_suffix

    entry_name = f"entry-{generate_random_suffix()}"

    entry_entity = EntryEntity(
        name=entry_name,
        workspace=workspace,
        external_id=entry_input.external_id if hasattr(entry_input, "external_id") else None,
        data=entry_input.data,
        usage=entry_input.usage,
        context=entry_input.context,
        user_rating=entry_input.user_rating if hasattr(entry_input, "user_rating") else None,
        events=entry_input.events if hasattr(entry_input, "events") else [],
        custom_fields=entry_input.custom_fields if hasattr(entry_input, "custom_fields") else None,
    )

    # Auto-register app and task from context (fire-and-forget, don't await)
    if entry_entity.context and entry_entity.context.app:
        _auto_register_app_and_task_async(
            entities_client,
            entry_entity.context.app,
            entry_entity.context.task,
            entry_entity.workspace,
        )

    try:
        created = await entities_client.create(entry_entity)
    except EntityConflictError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Entry with external_id={entry_entity.external_id} already exists",
        )

    return Entry.model_validate(created.model_dump(by_alias=True, mode="json"))


@router.get(
    "/v2/workspaces/{workspace}/entries/{name}",
    response_model=Entry,
    tags=[API_TAG],
)
async def get_entry(
    workspace: str,
    name: str,
    entities_client: EntityClient = Depends(get_entity_client),
) -> Entry:
    """Get a specific entry by ID or external_id.

    Use `external:{external_id}` to get by external_id.
    Example: `/v2/workspaces/{workspace}/entries/external:chatcmpl-abc123`
    """
    entry_entity = await _get_entry_by_id_or_external(entities_client, name, workspace)

    if entry_entity is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Entry {name} not found",
        )

    return Entry.model_validate(entry_entity.model_dump(by_alias=True, mode="json"))


@router.patch(
    "/v2/workspaces/{workspace}/entries/{name}",
    response_model=Entry,
    tags=[API_TAG],
)
async def update_entry(
    workspace: str,
    name: str,
    entry_update: EntryUpdate,
    entities_client: EntityClient = Depends(get_entity_client),
) -> Entry:
    """Update an existing entry by ID or external_id.

    Use `external:{external_id}` to update by external_id.
    Example: `/v2/workspaces/{workspace}/entries/external:chatcmpl-abc123`
    """
    entry_entity = await _get_entry_by_id_or_external(entities_client, name, workspace)

    if entry_entity is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Entry {name} not found",
        )

    # Apply updates, coercing nested models to proper types
    update_data = entry_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        # Coerce user_rating dict to UserRating to avoid Pydantic serialization warnings
        if field == "user_rating" and isinstance(value, dict):
            value = UserRating(**value)
        elif field == "usage" and isinstance(value, dict):
            value = Usage(**value)
        setattr(entry_entity, field, value)

    updated = await entities_client.update(entry_entity)

    return Entry.model_validate(updated.model_dump(by_alias=True, mode="json"))


@router.delete(
    "/v2/workspaces/{workspace}/entries/{name}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=[API_TAG],
)
async def delete_entry(
    workspace: str,
    name: str,
    entities_client: EntityClient = Depends(get_entity_client),
) -> None:
    """Delete an entry by ID or external_id.

    Use `external:{external_id}` to delete by external_id.
    Example: `/v2/workspaces/{workspace}/entries/external:chatcmpl-abc123`
    """
    entry_entity = await _get_entry_by_id_or_external(entities_client, name, workspace)

    if entry_entity is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Entry {name} not found",
        )

    await entities_client.delete(EntryEntity, entry_entity.name, workspace=entry_entity.workspace)


# ---------------------------------------------------------------------------
# Events Sub-resource
# ---------------------------------------------------------------------------


@router.post(
    "/v2/workspaces/{workspace}/entries/{name}/events",
    response_model=Entry,
    tags=[API_TAG],
)
async def add_events(
    workspace: str,
    name: str,
    request: EventsCreateRequest,
    entities_client: EntityClient = Depends(get_entity_client),
) -> Entry:
    """Add events to an entry by ID or external_id.

    Use `external:{external_id}` to add events by external_id.
    Example: `/v2/workspaces/{workspace}/entries/external:chatcmpl-abc123/events`
    """
    entry_entity = await _get_entry_by_id_or_external(entities_client, name, workspace)

    if entry_entity is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Entry {name} not found",
        )

    # Add new events
    entry_entity.events.extend(request.events)

    # Update user_rating if any UserFeedbackEvent is present
    for event in request.events:
        if hasattr(event, "event_type") and event.event_type == "user_feedback":
            # Update user_rating fields from the feedback event
            if not entry_entity.user_rating:
                entry_entity.user_rating = UserRating()

            if hasattr(event, "thumb") and event.thumb:
                entry_entity.user_rating.thumb = event.thumb
            if hasattr(event, "rating") and event.rating is not None:
                entry_entity.user_rating.rating = event.rating
            if hasattr(event, "opinion") and event.opinion:
                entry_entity.user_rating.opinion = event.opinion
            if hasattr(event, "rewrite") and event.rewrite:
                entry_entity.user_rating.rewrite = event.rewrite
            if hasattr(event, "chosen_index") and event.chosen_index is not None:
                entry_entity.user_rating.chosen_index = event.chosen_index
            if hasattr(event, "categories") and event.categories:
                entry_entity.user_rating.categories = event.categories

    updated = await entities_client.update(entry_entity)

    return Entry.model_validate(updated.model_dump(by_alias=True, mode="json"))


@router.delete(
    "/v2/workspaces/{workspace}/entries/{entry}/events/{name}",
    response_model=Entry,
    tags=[API_TAG],
)
async def delete_event(
    workspace: str,
    entry: str,
    name: str,
    entities_client: EntityClient = Depends(get_entity_client),
) -> Entry:
    """Delete a specific event from an entry.

    Entry can be referenced by ID or external_id using `external:{external_id}` prefix.
    """
    entry_entity = await _get_entry_by_id_or_external(entities_client, entry, workspace)

    if entry_entity is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Entry {entry} not found",
        )

    # Find and remove the event
    event_found = False
    for i, event in enumerate(entry_entity.events):
        if hasattr(event, "id") and event.id == name:
            entry_entity.events.pop(i)
            event_found = True
            break

    if not event_found:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Event {name} not found in entry {entry}",
        )

    updated = await entities_client.update(entry_entity)

    return Entry.model_validate(updated.model_dump(by_alias=True, mode="json"))
