# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

from unittest.mock import patch

from nmp.common.jobs.schemas import PlatformJobStatus
from nmp.core.jobs.api.v2.jobs.schemas import PlatformJobStepWithContext
from nmp.core.jobs.controllers.backends.exceptions import ResourceAllocationError
from nmp.core.jobs.controllers.backends.registry import BackendRegistry
from nmp.core.jobs.controllers.backends.test import MockDockerCPUJobBackend
from nmp.core.jobs.controllers.scheduler import JobScheduler
from pytest import fixture


@fixture
def job_scheduler(backend_registry: BackendRegistry, mock_nmp_client) -> JobScheduler:
    return JobScheduler(backend_registry, mock_nmp_client)


def test_does_schedule_job(
    job_scheduler: JobScheduler,
    backend_registry: BackendRegistry,
    mock_nmp_client,
    test_step_pending: PlatformJobStepWithContext,
):
    # Mock the jobs list response
    mock_nmp_client.jobs.steps.list.return_value = [test_step_pending]

    # Get the test backend from the registry
    backend = backend_registry.get_backend(provider="cpu", profile="default")
    assert isinstance(backend, MockDockerCPUJobBackend)
    test_backend = backend

    # Run scheduler step
    job_scheduler.step()

    # Verify the NeMo Platform client was called with the correct filter
    # Note: MARK_INTERNAL_REQUEST_HEADERS are now set at SDK initialization, not per-request
    mock_nmp_client.jobs.steps.list.assert_called_once_with(
        workspace="-",
        name="-",
        filter={"status": ["created", "resuming"]},
        sort="-created_at",
    )

    # Test backend should have received one schedule call for our test job
    assert len(test_backend.mock.schedule_calls) == 1
    assert test_backend.mock.schedule_calls[0]["step"].id == test_step_pending.id
    assert test_backend.mock.sync_calls == []


def test_resource_allocation_error_marks_step_as_error(
    job_scheduler: JobScheduler,
    mock_nmp_client,
    test_step_pending: PlatformJobStepWithContext,
):
    """When ResourceAllocationError is raised (e.g. no GPUs), scheduler marks step as error with error_details."""
    mock_nmp_client.jobs.steps.list.return_value = [test_step_pending]
    error_message = "No GPUs available on this system. GPU jobs require a system with NVIDIA GPUs."

    with patch.object(job_scheduler, "schedule_step", side_effect=ResourceAllocationError(error_message)):
        job_scheduler.step()

    mock_nmp_client.jobs.steps.update_status.assert_called_once_with(
        test_step_pending.name,
        workspace=test_step_pending.workspace,
        job=test_step_pending.job,
        status=PlatformJobStatus.ERROR,
        status_details={"message": error_message},
        error_details={"message": error_message},
    )
