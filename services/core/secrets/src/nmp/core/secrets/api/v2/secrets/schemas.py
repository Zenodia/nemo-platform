# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Self

from nmp.common.entities import constants
from nmp.core.secrets.entities import PlatformSecret
from pydantic import BaseModel, Field, SecretStr, field_validator, model_validator

_NAME_RE: re.Pattern[str] = re.compile(constants.REGEX_WORD_CHARACTER_DOT_DASH)


class PlatformSecretResponse(BaseModel):
    """Response model for a platform secret."""

    name: str = Field(..., description="The name of the secret")
    workspace: str = Field(..., description="The workspace ID the secret belongs to")
    description: str | None = Field(None, description="An optional description of the secret")
    created_at: datetime | None = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime | None = Field(default_factory=lambda: datetime.now(timezone.utc))

    @classmethod
    def from_entity(cls, secret: PlatformSecret) -> PlatformSecretResponse:
        """Create a PlatformSecretResponse from a PlatformSecret entity."""
        return cls(
            name=secret.name,
            workspace=secret.workspace,
            description=secret.description,
            created_at=secret.created_at,
            updated_at=secret.updated_at,
        )


class PlatformSecretCreateRequest(BaseModel):
    """Request body for creating a new platform secret."""

    name: str = Field(
        ...,
        description=f"The name of the secret to create. {constants.REGEX_WORD_CHARACTER_DOT_DASH_DESCRIPTION}",
        examples=["hf-token", "wandb-api-key"],
    )
    description: str | None = Field(None, description="An optional description of the secret")
    value: SecretStr = Field(..., description="The payload of the secret")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not _NAME_RE.match(v):
            raise ValueError(
                f"Invalid secret name '{v}'. {constants.REGEX_WORD_CHARACTER_DOT_DASH_DESCRIPTION} Example: my-api-key"
            )
        return v

    @model_validator(mode="after")
    def validate_self(self) -> Self:
        if not self.value.get_secret_value():
            raise ValueError("Secret value cannot be empty")
        return self


class PlatformSecretUpdateRequest(BaseModel):
    """Request body for updating a platform secret's metadata."""

    description: str | None = Field(None, description="An optional description of the secret")
    value: SecretStr | None = Field(None, description="The new secret value")

    @model_validator(mode="after")
    def validate_self(self) -> Self:
        if self.value is not None and not self.value.get_secret_value():
            raise ValueError("Secret value cannot be empty")
        return self


class PlatformSecretAccessResponse(BaseModel):
    """Response model for accessing a platform secret's value."""

    name: str = Field(..., description="The name of the secret")
    workspace: str = Field(..., description="The workspace ID the secret belongs to")
    value: str = Field(..., description="The payload of the secret")
