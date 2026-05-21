# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

from pydantic import BaseModel


class PlatformSecretAdminRotationResponse(BaseModel):
    """Response schema for admin secret rotation routine."""

    rotated_secrets: int
    success: bool
