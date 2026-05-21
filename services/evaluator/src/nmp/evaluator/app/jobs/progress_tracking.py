# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import asyncio
import logging
import os
import threading
from typing import Optional

import requests
import requests.exceptions
from nemo_evaluator_sdk.enums import TaskStatus
from nmp.evaluator.app.values import EvaluationStatusDetails
from nmp.evaluator.constants import DEFAULT_PROGRESS_TRACKING_INTERVAL
from requests.adapters import HTTPAdapter
from urllib3.exceptions import MaxRetryError
from urllib3.util.retry import Retry

log = logging.getLogger(__name__)

retry_strategy = Retry(total=5, backoff_factor=0.25, status_forcelist=[409, 429], allowed_methods=["PATCH"])


def get_progress_tracking_url() -> str:
    """
    Returns a URL string which includes job ID and workspace env variables that are expanded at runtime.
    Use the NMP_JOBS_URL set by Jobs MS for each step instead nmp.common.config.Configuration
    which is local to the API server.
    """
    return "${NMP_JOBS_URL}/apis/jobs/v2/workspaces/${NEMO_JOB_WORKSPACE}/jobs/${NEMO_JOB_ID}/status-details"


def get_progress_tracking_interval(num_samples: Optional[int], interval: Optional[int] = None) -> int:
    interval = interval or DEFAULT_PROGRESS_TRACKING_INTERVAL
    if num_samples and num_samples < interval:
        interval = num_samples
        # Set interval to a fraction of samples for more frequent updates.
        if num_samples >= 4:
            interval = num_samples // 4
    return interval


class ProgressTracking:
    def __init__(
        self,
        progress_tracking_url: str,
        progress_tracking_interval: Optional[int] = None,
        progress_tracking_interval_seconds: Optional[float] = None,
        request_method: str = "PATCH",
        total_samples: Optional[int] = None,
        total_work: Optional[int] = None,
        logger: logging.Logger | None = None,
    ):
        self._progress_tracking_url = os.path.expandvars(progress_tracking_url)
        self._request_method = request_method

        # total_samples tracks the inference requests and is updated to job.status_details
        # job.progress is derived from samples_processed and _total_samples.
        self._total_samples = total_samples

        # _completed and _total_work tracks any work and only updates job.progress.
        self._total_work = total_work
        self._completed = 0

        self._progress_tracking_interval = get_progress_tracking_interval(
            total_samples, progress_tracking_interval or 50
        )
        self._last_updated_status_details = EvaluationStatusDetails(samples_processed=0, progress=0.0)
        self._status_details = EvaluationStatusDetails(samples_processed=0, progress=0.0)
        self._lock = threading.Lock()
        self.log = logger or log

        self._update_on_timer_task = None
        if progress_tracking_interval_seconds:
            self._update_on_timer_task = asyncio.create_task(self._update_on_timer(progress_tracking_interval_seconds))

    @property
    def interval(self) -> int:
        """The getter method for 'total_samples'."""
        return self._progress_tracking_interval

    @property
    def total_samples(self) -> int:
        """The getter method for 'total_samples'."""
        assert self._total_samples is not None
        return self._total_samples

    @total_samples.setter
    def total_samples(self, num_samples: int):
        """The setter method for 'total_samples'."""
        if num_samples < 0:
            raise ValueError("num_samples cannot be negative.")
        self._total_samples = num_samples
        self._progress_tracking_interval = get_progress_tracking_interval(num_samples, self._progress_tracking_interval)

    @property
    def total_work(self) -> int | None:
        """The getter method for 'total_work'."""
        with self._lock:
            return self._total_work

    @total_work.setter
    def total_work(self, total_work: int):
        """The setter method for 'total_work'."""
        if total_work < 0:
            raise ValueError("total_work cannot be negative.")
        with self._lock:
            self._total_work = total_work

    async def _update_on_timer(self, interval_seconds: float):
        assert interval_seconds > 0
        while True:
            await asyncio.sleep(interval_seconds)
            self.update_progress()

    def stop(self):
        if self._update_on_timer_task:
            self._update_on_timer_task.cancel()

    def update_task_status(
        self, task_name: str, status: str | TaskStatus, message: Optional[str] = None
    ) -> requests.Response | None:
        task_status = status if isinstance(status, TaskStatus) else TaskStatus(status)
        status_detail = EvaluationStatusDetails(task_status={task_name: task_status}, message=message)
        return self._send_progress(status_detail)

    def increment_work(self, increment: int = 1) -> requests.Response | None:
        with self._lock:
            self._completed += increment
            completed = self._completed
            if not self._total_work:
                return
            self._status_details.progress = (self._completed / self._total_work) * 100

        if (completed % self._progress_tracking_interval) == 0:
            return self.update_progress()

    def increment_samples_processed(self, increment: int = 1) -> requests.Response | None:
        assert increment > 0
        status_details = EvaluationStatusDetails()
        with self._lock:
            self._status_details.samples_processed = (self._status_details.samples_processed or 0) + increment
            status_details.samples_processed = self._status_details.samples_processed

            if self._total_samples is not None:
                # If total samples are set, also update progress %
                progress = (self._status_details.samples_processed / self._total_samples) * 100
                self._status_details.progress = progress
                status_details.progress = progress

        if (status_details.samples_processed % self._progress_tracking_interval) == 0:
            return self._send_progress(status_details)

    def update_progress(self, progress: Optional[float] = None) -> requests.Response | None:
        with self._lock:
            status_detail = EvaluationStatusDetails(progress=progress or self._status_details.progress)
            if self._status_details.samples_processed:
                status_detail.samples_processed = self._status_details.samples_processed
            if self._last_updated_status_details == status_detail:
                # update_progress is called on a timer. Skip if there has been no change since last update.
                return
        return self._send_progress(status_detail)

    def _send_progress(self, status_details: EvaluationStatusDetails) -> requests.Response | None:
        self.log.debug(f"Sending request to {self._progress_tracking_url}: {status_details}")
        try:
            adapter = HTTPAdapter(max_retries=retry_strategy)
            with requests.Session() as session:
                session.mount("https://", adapter)
                session.mount("http://", adapter)
                resp = session.request(
                    self._request_method,
                    self._progress_tracking_url,
                    json=status_details.model_dump(mode="json", exclude_unset=True),
                )
            if resp.status_code > 299 or resp.status_code < 200:
                self.log.warning(
                    f"Failed to update job progress to {self._progress_tracking_url} {status_details}: {resp.status_code} {resp.text}"
                )
        except (requests.exceptions.RequestException, requests.exceptions.RetryError, MaxRetryError):
            self.log.exception("Failed to communicate with progress tracking server")
        else:
            with self._lock:
                if status_details.samples_processed:
                    self._last_updated_status_details = status_details
            return resp
