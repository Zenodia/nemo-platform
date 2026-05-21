# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Configuration for the intake sink usage case."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict


class IntakeSinkConfig(BaseModel):
    """Configuration for posting completed turns to intake."""

    model_config = ConfigDict(frozen=True)

    intake_base_url: str | None = None
    workspace: str | None = None
    user_id: str = "switchyard"
    api_key: str | None = None
    max_queue_size: int = 1000
    request_timeout_s: float = 10.0
    max_retries: int = 2
    on_queue_full: Literal["drop", "block"] = "drop"
