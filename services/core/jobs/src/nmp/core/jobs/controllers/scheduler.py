# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import logging
import threading
import traceback

import nemo_platform
from nemo_platform import NeMoPlatform
from nemo_platform.types.jobs import PlatformJobStepWithContext
from nmp.common.controller import Controller
from nmp.common.jobs.schemas import PlatformJobStatus
from nmp.common.observability import start_span_with_ctx
from nmp.core.jobs.app.ctx import JobBackendContext, JobContext
from nmp.core.jobs.controllers.backends import JobUpdate, extract_provider_profile
from nmp.core.jobs.controllers.backends.exceptions import ResourceAllocationError
from nmp.core.jobs.controllers.backends.registry import BackendRegistry
from opentelemetry import metrics, trace

tracer = trace.get_tracer(__name__)
meter = metrics.get_meter(__name__)
logger = logging.getLogger(__name__)

DEFAULT_PROFILE = "default"
DEFAULT_PROVIDER = "cpu"


class JobScheduler(Controller):
    def __init__(
        self,
        backend_registry: BackendRegistry,
        nmp_sdk: NeMoPlatform,
        stop_signal: threading.Event | None = None,
    ) -> None:
        self._backend_registry = backend_registry
        self._nmp_sdk = nmp_sdk
        self._stop_signal = stop_signal
        self._is_healthy = False

        self._step_scheduled_total = meter.create_counter(
            name="nmp.jobs.scheduler.step.scheduled.total",
            description="Total number of job scheduling attempts",
        )
        self._step_scheduling_errors = meter.create_counter(
            name="nmp.jobs.scheduler.step.scheduling.errors",
            description="Number of job scheduling errors",
        )

    @property
    def is_healthy(self) -> bool:
        return self._is_healthy

    def step(self):
        # Check stop signal before making any API calls
        if self._stop_signal and self._stop_signal.is_set():
            logger.debug("Stop signal received, skipping scheduling step")
            return

        steps = []
        with tracer.start_as_current_span("jobs_scheduler/fetch_steps_for_scheduling"):
            try:
                steps = self.get_steps_for_scheduling()
                self._is_healthy = True
            except nemo_platform.APIError:
                self._is_healthy = False
                logger.exception("Could not fetch job steps for scheduling", exc_info=True)
                return

        if len(steps) > 0:
            logger.info(f"Got {len(steps)} job steps to schedule")
        else:
            logger.debug("No job steps to schedule")
        for step in steps:
            with start_span_with_ctx(
                tracer, "jobs_scheduler/schedule_step", JobContext(id=step.job, step_name=step.name)
            ):
                try:
                    update = self.schedule_step(step)
                    logger.info("Scheduled job step")
                    self._nmp_sdk.jobs.steps.update_status(
                        step.name,
                        workspace=step.workspace,
                        job=step.job,
                        status=update.status,
                        status_details=update.status_details,  # type: ignore
                        error_details=update.error_details,  # type: ignore
                    )

                except ResourceAllocationError as e:
                    logger.info(
                        f"Could not schedule job '{step.job}' step '{step.name}' due to resource constraints: {e.message}. Marking step as error."
                    )
                    self._step_scheduling_errors.add(1, attributes={"error_type": "resource_allocation"})
                    self._nmp_sdk.jobs.steps.update_status(
                        step.name,
                        workspace=step.workspace,
                        job=step.job,
                        status=PlatformJobStatus.ERROR,
                        status_details={"message": e.message},  # type: ignore
                        error_details={"message": e.message},  # type: ignore
                    )
                except Exception as e:
                    logger.exception("Could not schedule job step", exc_info=True)
                    self._step_scheduling_errors.add(1, attributes={"error_type": "unknown"})
                    self._nmp_sdk.jobs.steps.update_status(
                        step.name,
                        workspace=step.workspace,
                        job=step.job,
                        status=PlatformJobStatus.ERROR,
                        status_details={"message": str(e)},  # type: ignore
                        error_details={"message": str(e), "error": traceback.format_exc()},
                    )

    def get_steps_for_scheduling(self) -> list[PlatformJobStepWithContext]:
        """
        Return the oldest set of steps to schedule. We using the
        set of pending steps as our queue for what to schedule next.
        """
        # Iterate through all pages to get all steps
        steps = []
        for step in self._nmp_sdk.jobs.steps.list(
            name="-",  # Use "-" to indicate all jobs
            workspace="-",  # Cross-workspace query
            filter={"status": [PlatformJobStatus.CREATED.value, PlatformJobStatus.RESUMING.value]},
            sort="-created_at",
        ):
            steps.append(step)
        return steps

    def schedule_step(self, step: PlatformJobStepWithContext) -> JobUpdate:
        provider, profile = extract_provider_profile(step)
        backend = self._backend_registry.get_backend(profile=profile, provider=provider)
        self._step_scheduled_total.add(1, attributes={"provider": provider, "profile": profile})
        with start_span_with_ctx(
            tracer,
            "job_scheduler/schedule_step_with_backend",
            JobBackendContext(provider=provider, profile=profile, name=str(backend)),
        ):
            return backend.schedule(step.step_spec.executor, step)
