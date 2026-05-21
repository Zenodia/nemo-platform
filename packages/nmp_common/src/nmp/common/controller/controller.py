# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Controller framework for background processes."""

import contextvars
import threading
import time
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from logging import getLogger
from typing import Callable

from nmp.common.observability.context import AppContext, initialize_app_ctx

logger = getLogger(__name__)


class Controller(ABC):
    """Step represents a function intended to be run in a loop."""

    @abstractmethod
    def step(self): ...

    @property
    def is_healthy(self) -> bool:
        """Check if the controller is healthy.

        Returns:
            True if the controller is healthy, False otherwise.
        """
        return True


class LoopWaiter(ABC):
    """
    Loop waiter waits in increments of sleep_secs.
    When wait is called, if it has been < sleep_secs since the last call, it will sleep the remaining time.
    If it has been >= sleep_secs since last call, it will return immediately.
    """

    @abstractmethod
    def wait(self): ...


class ProvidesLastExecutionTime(ABC):
    """ProvidesLastExecutionTime is an interface for objects providing a time of
    last successful execution.
    """

    @abstractmethod
    def last_execution_time(self) -> datetime: ...


class TrackLastExecutionTime(Controller, ProvidesLastExecutionTime):
    """TrackLastExecutionTime"""

    def __init__(self, controller: Controller):
        self._last_runtime = datetime.now(timezone.utc)
        self._internal = controller

    def last_execution_time(self) -> datetime:
        return self._last_runtime

    def step(self):
        self._last_runtime = datetime.now(timezone.utc)
        self._internal.step()

    @property
    def is_healthy(self) -> bool:
        """Delegate health check to the wrapped controller."""
        return self._internal.is_healthy


class TimedLoopWaiter(LoopWaiter):
    def __init__(self, sleep_secs: float, stop_signal: threading.Event | None = None):
        self._sleep_secs = sleep_secs
        self._next_step = 0.0
        self._stop_signal = stop_signal

    @property
    def sleep_secs(self) -> float:
        return self._sleep_secs

    def wait(self):
        now = time.time()
        if self._next_step > now:
            sleep_duration = self._next_step - now
            if self._stop_signal is not None:
                # Use Event.wait() which returns immediately if stop signal is set
                self._stop_signal.wait(timeout=sleep_duration)
            else:
                time.sleep(sleep_duration)
            self._next_step = self._next_step + self._sleep_secs
        else:
            self._next_step = now + self._sleep_secs


class Loop(threading.Thread):
    """
    Loop is a loop that runs in a separate Thread. The contents of the 'step' function are called every
    iteration.
    """

    def __init__(
        self,
        waiter: LoopWaiter,
        controller: Controller,
        shutdown_func: Callable | None = None,
        stop_signal: threading.Event | None = None,
    ):
        threading.Thread.__init__(self)
        self._waiter = waiter
        self._internal = controller
        self._stop_signal = stop_signal if stop_signal is not None else threading.Event()
        self._shutdown_func = shutdown_func

        # Capture the current context so it can be used in the thread
        self._context = contextvars.copy_context()

    def run(self):
        self._context.run(self._run_loop)

    def _run_loop(self):
        initialize_app_ctx(AppContext(service_name=self.name))
        try:
            while not self._stop_signal.is_set():
                self._waiter.wait()
                if self._stop_signal.is_set():
                    break

                try:
                    self._internal.step()
                except Exception as e:
                    logger.exception(f"Error: Control loop caught an exception: {e}")
        finally:
            if self._shutdown_func:
                try:
                    self._shutdown_func()
                except Exception as e:
                    logger.exception(f"Error during loop shutdown: {e}")

    def stop(self):
        self._stop_signal.set()

    @property
    def is_healthy(self) -> bool:
        """Check if the internal controller is healthy.

        Returns:
            True if the thread is active AND last execution is recent (or controller is healthy), False otherwise.
        """
        # Thread must be alive
        if not self.is_alive():
            logger.debug(f"Controller thread {self.name} is not alive")
            return False

        # Check if last execution time is within acceptable window
        if isinstance(self._internal, ProvidesLastExecutionTime) and isinstance(self._waiter, TimedLoopWaiter):
            last_execution = self._internal.last_execution_time()
            sleep_secs = self._waiter.sleep_secs
            now = datetime.now(timezone.utc)
            max_delay = sleep_secs * 3  # Allow 3 sleep windows before marking unhealthy
            time_since_last = (now - last_execution).total_seconds()
            if time_since_last > max_delay:
                logger.debug(
                    f"Controller thread {self.name} has not executed in {time_since_last:.2f}s "
                    f"(max allowed: {max_delay:.2f}s)"
                )
                return False

        if not self._internal.is_healthy:
            logger.debug(f"Controller thread {self.name} internal controller is unhealthy")
            return False

        return True
