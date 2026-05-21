# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""ChatResponse type enum and abstract base class."""

from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum


class ChatResponseType(Enum):
    """Identifies the format and delivery mode of a ChatResponse subclass."""

    COMPLETION = "completion"
    STREAM = "stream"
    RESPONSES_API_COMPLETION = "responses_api_completion"
    RESPONSES_API_STREAM = "responses_api_stream"
    ANTHROPIC_COMPLETION = "anthropic_completion"
    ANTHROPIC_STREAM = "anthropic_stream"


class ChatResponse(ABC):
    """Abstract base for all response formats flowing through the chain.

    Six concrete subclasses cover the wire-format x delivery-mode
    matrix.  Response processors dispatch via ``isinstance`` to handle
    each variant.
    """

    @property
    @abstractmethod
    def response_type(self) -> ChatResponseType:
        """Identifies this response's format and delivery mode.

        Useful for logging, serialization, and ``match`` statements.
        For dispatch logic in response processors, prefer ``isinstance``
        checks.
        """
        ...
