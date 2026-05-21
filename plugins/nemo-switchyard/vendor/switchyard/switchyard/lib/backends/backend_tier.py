# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Generic backend tier configuration.

A tier represents a single LLM backend endpoint with its connection parameters,
model name, and tuning config. Reusable across any backend pipeline:
- Passthrough (single tier)
- Random routing (two tiers)
- Multi-tier routing (N tiers)

Each tier specifies:
- Model name to route to
- Wire format (OpenAI, Anthropic, etc.)
- Connection parameters (api_key, base_url, timeout)
- Optional per-tier tuning parameters
"""

from __future__ import annotations

from enum import Enum
from typing import ClassVar

from pydantic import BaseModel, ConfigDict, Field

from switchyard.lib.backends.llm_backend_tuning import LLMBackendTuning


class BackendFormat(str, Enum):
    """Wire format of an LLM backend.

    Maps to exactly one :class:`LLMBackend` implementation:

    * :attr:`AUTO` → resolve at backend construction time.
    * :attr:`OPENAI` → :class:`OpenAILLMBackend` (POST /v1/chat/completions).
    * :attr:`ANTHROPIC` → :class:`AnthropicNativeLLMBackend` (POST /v1/messages).
    """

    AUTO = "auto"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"


class BackendTier(BaseModel):
    """Configuration for a single backend tier — model + wire format + connection.

    Pure configuration: model name, wire format, connection params, and
    per-tier tuning. Factories turn each tier into a concrete
    :class:`LLMBackend` on construction, dispatching on :attr:`backend_format`
    and forwarding :attr:`tuning` to the backend's constructor.

    ``protected_namespaces=()`` disables Pydantic v2's ``model_*`` check
    so the ``model: str`` field name (used in OpenAI / Anthropic SDKs)
    doesn't trigger a warning. ``arbitrary_types_allowed=True`` allows
    :class:`LLMBackendTuning` (a dataclass, not a Pydantic model).
    """

    model_config: ClassVar[ConfigDict] = ConfigDict(
        frozen=True,
        protected_namespaces=(),
        arbitrary_types_allowed=True,
    )

    model: str = ""
    backend_format: BackendFormat = BackendFormat.OPENAI
    api_key: str | None = None
    base_url: str | None = None
    timeout: float | None = None
    tuning: LLMBackendTuning = Field(default_factory=LLMBackendTuning)
