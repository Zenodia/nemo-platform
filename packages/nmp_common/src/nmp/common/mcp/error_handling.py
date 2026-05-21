# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Error handling utilities for MCP tools."""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


def format_error_response(error: Exception) -> dict[str, Any]:
    """
    Format an exception into a standard error response for MCP tools.

    Provides consistent error structure across all MCP tools with logging.

    Args:
        error: The exception to format

    Returns:
        Dictionary with success=False, error message, and error type

    Example:
        >>> try:
        ...     result = await some_operation()
        ... except Exception as e:
        ...     return format_error_response(e)
    """
    logger.error(f"Error in MCP tool: {error}", exc_info=True)
    return {
        "success": False,
        "error": str(error),
        "error_type": type(error).__name__,
    }
