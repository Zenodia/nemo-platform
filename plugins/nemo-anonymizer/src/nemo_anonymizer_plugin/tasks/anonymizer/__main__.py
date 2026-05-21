# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import logging
import signal
import sys
from types import FrameType

from nemo_anonymizer_plugin.tasks.anonymizer.run import run

logger = logging.getLogger(__name__)


def _configure_shutdown_handling() -> None:
    signal.signal(signal.SIGTERM, _shutdown_handler)


def _shutdown_handler(signum: int, frame: FrameType | None) -> None:
    logger.warning(f"Received shutdown signal ({signum}). Shutting down gracefully.")
    sys.exit(128 + signum)


if __name__ == "__main__":
    _configure_shutdown_handling()
    sys.exit(run())
