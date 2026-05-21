# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Abstract base class for HTTP endpoints."""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fastapi import FastAPI


class Endpoint(ABC):
    """
    Abstract base class for composable HTTP endpoint modules.

    Each endpoint module encapsulates a set of HTTP routes (e.g., OpenAI chat,
    Anthropic messages, health checks) and registers them onto a FastAPI app.

    Endpoint modules are composed into a list and registered via
    :func:`build_switchyard_app`.
    """

    @abstractmethod
    def register(self, app: "FastAPI") -> None:
        """Register this endpoint's routes onto the FastAPI application.

        Args:
            app: The FastAPI application instance to register routes on.
        """
        pass

    @property
    def name(self) -> str:
        """Human-readable name for logging and introspection."""
        return type(self).__name__
