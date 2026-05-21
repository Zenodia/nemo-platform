# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Logging configuration for the safe-synthesizer task.

This module provides JSON-formatted logging configuration for the safe-synthesizer service.
"""

import json
import logging
import os
import sys
from pathlib import Path


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter that properly escapes message content."""

    def format(self, record: logging.LogRecord) -> str:
        """Format the log record as valid JSON."""
        log_entry = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        return json.dumps(log_entry, ensure_ascii=False)


def configure_logging(log_level: str = "INFO") -> None:
    """Configure logging to write to stderr and optionally to a log file using Python primitives."""
    # Create formatters
    structured_formatter = JSONFormatter(datefmt="%Y-%m-%dT%H:%M:%S")

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))

    # Clear any existing handlers
    root_logger.handlers.clear()

    # Create stderr handler (always enabled)
    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setLevel(getattr(logging, log_level.upper()))
    stderr_handler.setFormatter(structured_formatter)
    root_logger.addHandler(stderr_handler)

    # Create file handler only if NEMO_JOB_LOG_PATH is set
    log_path = os.environ.get("NEMO_JOB_LOG_PATH")
    if log_path:
        log_dir = Path(log_path)
        log_file = log_dir / "application.log"

        # Ensure log directory exists
        log_dir.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(getattr(logging, log_level.upper()))
        file_handler.setFormatter(structured_formatter)
        root_logger.addHandler(file_handler)

    # Configure specific loggers
    for logger_name in ["safe_synthesizer", "nemo_safe_synthesizer"]:
        inner_logger = logging.getLogger(logger_name)
        inner_logger.setLevel(getattr(logging, log_level.upper()))
