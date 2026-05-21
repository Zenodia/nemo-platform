# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import logging
import signal
import threading
from types import FrameType

log = logging.getLogger(__name__)


def _handle_termination_signal(signum: int, _frame: FrameType | None) -> None:
    signal_name = signal.Signals(signum).name
    log.info("Received %s. Exiting task gracefully.", signal_name)
    raise KeyboardInterrupt


def register_task_signal_handlers() -> None:
    """Register SIGTERM/SIGINT handlers for task entrypoints.

    In task-harness tests, task `run()` may execute on a background thread.
    Python only permits signal registration on the main thread, so this
    function is a no-op outside the main thread.
    """
    if threading.current_thread() is not threading.main_thread():
        log.debug("Skipping signal handler registration outside main thread")
        return

    signal.signal(signal.SIGTERM, _handle_termination_signal)
    signal.signal(signal.SIGINT, _handle_termination_signal)
