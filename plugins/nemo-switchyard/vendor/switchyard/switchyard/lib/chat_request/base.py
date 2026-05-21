# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""ChatRequest type enum and abstract base class."""

from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum


class ChatRequestType(Enum):
    """Identifies the wire format of a ChatRequest subclass."""

    OPENAI_CHAT = "openai_chat"
    OPENAI_RESPONSES = "openai_responses"
    ANTHROPIC = "anthropic"


class ChatRequest(ABC):
    """Abstract base for all request formats flowing through the chain.

    Intentionally minimal — no format-specific fields, no common field
    interface.  Each subclass wraps its SDK's native ``TypedDict`` and
    exposes a strongly typed ``body`` property with full autocomplete.

    Switchyard-internal state (routing decisions, retry counts, timing)
    belongs on ProxyContext / ChainContext, not here.  ``ChatRequest`` is
    the *client's request*; the context is the *chain's state*.
    """

    @property
    @abstractmethod
    def request_type(self) -> ChatRequestType:
        """Identifies this request's wire format.

        Useful for logging, serialization, ``match`` statements, and
        metrics labels.  For dispatch logic in strategies and translation
        engines, prefer ``isinstance`` checks — they're what the type
        system understands.
        """
        ...
