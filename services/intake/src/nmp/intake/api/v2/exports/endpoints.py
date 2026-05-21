# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""API endpoints for managing data exports using EntityClient pattern."""

import logging

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from nmp.common.api.common import Page
from nmp.common.api.parsed_filter import ParsedFilter, make_filter_dep
from nmp.common.api.utils import generate_openapi_extra_params
from nmp.common.entities.client import EntityClient, EntityNotFoundError
from nmp.common.service.dependencies import get_entity_client
from nmp.intake.app.exporter import DataExporter
from nmp.intake.app.utils.exports import extract_datastore_path, extract_nds_path, is_local_file_uri
from nmp.intake.app.utils.exports import is_datastore_uri as _is_datastore_uri
from nmp.intake.entities import ExportConfig, ExportStatusDetails, JobStatus
from nmp.intake.entities import ExportJob as ExportJobEntity

from .schemas import (
    ExportJobFilter,
    ExportJobInput,
    ExportJobSortField,
    ExportPreviewRequest,
    ExportPreviewResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter()

API_TAG = "Exports"


def _with_path_workspace(config: ExportConfig, workspace: str) -> ExportConfig:
    """Return an export config whose entry filter is scoped to the route workspace."""
    filters = dict(config.filters or {})
    filters["workspace"] = workspace
    return config.model_copy(update={"filters": filters})


@router.get(
    "/v2/workspaces/{workspace}/export/jobs",
    response_model=Page[ExportJobEntity],
    tags=[API_TAG],
    response_model_exclude_none=True,
    openapi_extra=generate_openapi_extra_params(
        filter_schema=ExportJobFilter,
        filter_description="Filter export jobs by name, status, output_file_url, created_at, and updated_at.",
    ),
)
async def list_export_jobs(
    workspace: str,
    entities_client: EntityClient = Depends(get_entity_client),
    page: int = Query(default=1, description="Page number."),
    page_size: int = Query(default=10, description="Page size."),
    sort: ExportJobSortField = Query(
        default="created_at",
        description="""The field to sort by. To sort in decreasing order, use `-` in front of the field name.""",
    ),
    parsed: ParsedFilter = Depends(make_filter_dep(ExportJobFilter)),
) -> Page[ExportJobEntity]:
    """List all export jobs with filtering capabilities.

    Use `workspace=-` for cross-workspace listing.
    """
    # Workspace from the path takes precedence over any filter value.
    parsed.remove("workspace")

    res = await entities_client.list(
        ExportJobEntity,
        page=page,
        page_size=page_size,
        sort=sort,
        workspace=workspace,
        filter_operation=parsed.operation,
    )

    data_dicts = [item.model_dump(by_alias=True, mode="json") for item in res.data]

    return Page[ExportJobEntity](
        data=data_dicts,
        pagination=res.pagination.model_dump(),
        sort=sort,
        filter=None,
    )


@router.post("/v2/workspaces/{workspace}/export/jobs", response_model=ExportJobEntity, tags=[API_TAG])
async def create_export_job(
    workspace: str,
    export_request: ExportJobInput,
    response: Response,
    entities_client: EntityClient = Depends(get_entity_client),
) -> ExportJobEntity:
    """Export entries to an external file.

    Use the `longest_per_thread` filter to export only the longest entry per thread,
    which is useful for thread-based exports.

    Supported output file URLs:

    - NeMo Datastore: nds://workspace/dataset_name
    - HuggingFace Dataset: hf://datasets/org/name/path/to/file
    - Local filesystem: file:///path/to/export (for development)
    """
    # Note: Currently runs synchronously. Async/Celery support to be added.
    # Convert AnyUrl to string for validation
    output_url_str = str(export_request.output_file_url)
    is_remote_url = _is_datastore_uri(output_url_str)
    is_local_url = is_local_file_uri(output_url_str)

    if not (is_local_url or is_remote_url):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only file://, hf://, and nds:// URLs are supported for output_file_url",
        )

    if is_remote_url:
        try:
            # Validate the URL format
            from urllib.parse import urlparse

            parsed = urlparse(output_url_str)
            if parsed.scheme == "hf":
                extract_datastore_path(output_url_str)
            elif parsed.scheme == "nds":
                extract_nds_path(output_url_str)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid output file URL: {str(e)}")

    try:
        # Convert input config to ExportConfig
        config_obj = _with_path_workspace(ExportConfig(**export_request.config.model_dump()), workspace)

        # Create job entity (name will be auto-generated by the entity API)
        job_entity = ExportJobEntity(
            workspace=workspace,
            status=JobStatus.PENDING,
            output_file_url=export_request.output_file_url,
            config=config_obj,
            status_details=ExportStatusDetails(entries_count=0),
        )
        job_entity = await entities_client.create(job_entity)

        logger.info(
            "Creating export job %s with output file URL %s",
            job_entity.id,
            export_request.output_file_url,
        )

        # Run export synchronously (TODO: Add async/Celery support)
        try:
            # Update job status
            job_entity.status = JobStatus.RUNNING
            job_entity = await entities_client.update(job_entity)

            # Perform export
            exporter = DataExporter(entities_client)
            export_data = await exporter.export_entries(config_obj)

            # Write to destination
            if is_local_url:
                from nmp.intake.app.utils.exports import extract_local_path

                file_path = extract_local_path(output_url_str)
                records_count = await exporter.write_to_file(export_data, str(file_path))
            else:
                # Handle remote exports (HuggingFace or NeMo Datastore)
                from urllib.parse import urlparse

                parsed = urlparse(output_url_str)
                if parsed.scheme == "hf":
                    records_count = await exporter.write_to_hf_dataset(export_data, output_url_str)
                elif parsed.scheme == "nds":
                    records_count = await exporter.write_to_nds_dataset(export_data, output_url_str)
                else:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Unsupported URI scheme: {parsed.scheme}",
                    )

            # Update job as completed
            job_entity.status = JobStatus.COMPLETED
            if job_entity.status_details:
                job_entity.status_details.entries_count = records_count
            else:
                job_entity.status_details = ExportStatusDetails(entries_count=records_count)
            job_entity = await entities_client.update(job_entity)

        except Exception as e:
            # Update job as failed
            job_entity.status = JobStatus.FAILED
            if job_entity.status_details:
                job_entity.status_details.error_message = str(e)
            else:
                job_entity.status_details = ExportStatusDetails(error_message=str(e))
            await entities_client.update(job_entity)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Export failed: {str(e)}")

        # Return job entity
        return job_entity

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to create export job: %s", str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/v2/workspaces/{workspace}/export/preview", response_model=ExportPreviewResponse, tags=[API_TAG])
async def preview_export(
    workspace: str,
    export_request: ExportPreviewRequest,
    entities_client: EntityClient = Depends(get_entity_client),
) -> ExportPreviewResponse:
    """Preview export data without writing to a file (max 100 records)."""
    try:
        # Convert input config to ExportConfig
        config_obj = _with_path_workspace(ExportConfig(**export_request.config.model_dump()), workspace)

        exporter = DataExporter(entities_client)
        preview_data = await exporter.preview_export(config_obj)

        return ExportPreviewResponse(data=preview_data, count=len(preview_data), config=export_request.config)
    except Exception as e:
        logger.exception("Failed to preview export: %s", str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/v2/workspaces/{workspace}/export/jobs/{name}", response_model=ExportJobEntity, tags=[API_TAG])
async def get_export_job_status(
    workspace: str,
    name: str,
    entities_client: EntityClient = Depends(get_entity_client),
) -> ExportJobEntity:
    """Check the status of an export job."""
    try:
        job_entity = await entities_client.get(ExportJobEntity, name, workspace=workspace)
    except EntityNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Export job not found")

    return job_entity
