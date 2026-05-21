# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import logging

from nemo_anonymizer_plugin.sdk import logging as sdk_logging


def _managed_handlers(logger: logging.Logger) -> list[logging.Handler]:
    return [handler for handler in logger.handlers if getattr(handler, sdk_logging._HANDLER_MARKER, False)]


def _reset_sdk_logging_state() -> None:
    sdk_logging._active_handler_users = 0
    sdk_logging._managed_handler = None
    sdk_logging._saved_level = None
    sdk_logging._saved_propagate = None


def test_ensure_logging_handler_attaches_direct_handler_even_when_root_has_handler() -> None:
    plugin_logger = logging.getLogger(sdk_logging._LOGGER_NAME)
    root_logger = logging.getLogger()
    original_plugin_handlers = list(plugin_logger.handlers)
    original_plugin_level = plugin_logger.level
    original_plugin_propagate = plugin_logger.propagate
    original_root_handlers = list(root_logger.handlers)

    try:
        _reset_sdk_logging_state()
        plugin_logger.handlers = []
        plugin_logger.setLevel(logging.WARNING)
        plugin_logger.propagate = True
        root_logger.handlers = [logging.NullHandler()]

        with sdk_logging._ensure_logging_handler():
            assert len(_managed_handlers(plugin_logger)) == 1
            assert plugin_logger.level == logging.INFO
            assert plugin_logger.propagate is False

        assert _managed_handlers(plugin_logger) == []
        assert plugin_logger.level == logging.WARNING
        assert plugin_logger.propagate is True
    finally:
        plugin_logger.handlers = original_plugin_handlers
        plugin_logger.setLevel(original_plugin_level)
        plugin_logger.propagate = original_plugin_propagate
        root_logger.handlers = original_root_handlers
        _reset_sdk_logging_state()


def test_ensure_logging_handler_keeps_handler_until_outer_call_exits() -> None:
    plugin_logger = logging.getLogger(sdk_logging._LOGGER_NAME)
    original_handlers = list(plugin_logger.handlers)
    original_level = plugin_logger.level
    original_propagate = plugin_logger.propagate

    try:
        _reset_sdk_logging_state()
        plugin_logger.handlers = []

        with sdk_logging._ensure_logging_handler():
            outer_handler = _managed_handlers(plugin_logger)[0]
            with sdk_logging._ensure_logging_handler():
                assert _managed_handlers(plugin_logger) == [outer_handler]
            assert _managed_handlers(plugin_logger) == [outer_handler]

        assert _managed_handlers(plugin_logger) == []
    finally:
        plugin_logger.handlers = original_handlers
        plugin_logger.setLevel(original_level)
        plugin_logger.propagate = original_propagate
        _reset_sdk_logging_state()
