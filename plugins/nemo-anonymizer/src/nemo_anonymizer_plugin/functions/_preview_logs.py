# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Bridge upstream Anonymizer/DD log records into the preview NDJSON stream."""

from __future__ import annotations

import logging
from collections.abc import Callable
from contextvars import ContextVar

from nemo_anonymizer_plugin.functions.preview import LogFrame, LogLevel
from pydantic import BaseModel

logger = logging.getLogger(__name__)

MessageCallback = Callable[[BaseModel], None]
request_callback_cvar = ContextVar[MessageCallback | None]("request_callback_cvar", default=None)


def attach_preview_handler() -> None:
    # Anonymizer logs under "anonymizer" and DD logs under "data_designer".
    # Attaching to both gives the user the full picture from a single stream.
    for logger_name in ("anonymizer", "data_designer"):
        lib_logger = logging.getLogger(logger_name)
        if not any(isinstance(handler, PreviewHandler) for handler in lib_logger.handlers):
            lib_logger.addHandler(PreviewHandler())


class PreviewHandler(logging.Handler):
    """Forward upstream library log records to the active preview stream."""

    def emit(self, record: logging.LogRecord) -> None:
        callback = request_callback_cvar.get()
        if callback:
            callback(LogFrame(message=record.getMessage(), level=_log_level(record)))


def _log_level(record: logging.LogRecord) -> LogLevel:
    if record.levelno >= logging.ERROR:
        return "error"
    if record.levelno >= logging.WARNING:
        return "warning"
    if record.levelno >= logging.INFO:
        return "info"
    return "debug"
