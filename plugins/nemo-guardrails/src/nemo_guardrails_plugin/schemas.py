# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Request-time schemas for the Guardrails inference middleware plugin."""

from pydantic import BaseModel, ConfigDict, Field, StrictBool


class GuardrailsLogOptions(BaseModel):
    """Supported ``guardrails.options.log`` fields on VirtualModel inference requests."""

    model_config = ConfigDict(extra="forbid")

    activated_rails: StrictBool | None = Field(default=None)
    colang_history: StrictBool | None = Field(default=None)
    internal_events: StrictBool | None = Field(default=None)
    llm_calls: StrictBool | None = Field(default=None)
    stats: StrictBool | None = Field(default=None)


class GuardrailsOptions(BaseModel):
    """Supported ``guardrails.options`` fields on VirtualModel inference requests."""

    model_config = ConfigDict(extra="forbid")

    log: GuardrailsLogOptions | None = Field(default=None)


class GuardrailsRequest(BaseModel):
    """Supported fields on the ``guardrails`` object on VirtualModel inference requests."""

    model_config = ConfigDict(extra="forbid")

    options: GuardrailsOptions | None = Field(default=None)
    return_choice: StrictBool = Field(default=False)
