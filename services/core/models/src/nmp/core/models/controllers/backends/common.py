# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Shared helpers for model deployment backends (Docker and K8s NIM Operator)."""

from datetime import datetime, timezone

from nemo_platform.types.inference.model_deployment import ModelDeployment

LOG_TAIL_LINES = 80
LOG_MAX_CHARS = 2048


def deployment_elapsed_seconds(deployment: ModelDeployment) -> float:
    """Seconds since the deployment entity was created.

    Uses the entity-store ``created_at`` timestamp so the value survives
    controller restarts.
    """
    created_at = deployment.created_at
    if created_at is None:
        return 0.0
    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)
    return (datetime.now(timezone.utc) - created_at).total_seconds()


def format_duration(seconds: float) -> str:
    """Human-readable duration string (e.g. '2h 5m 30s')."""
    h, rem = divmod(int(seconds), 3600)
    m, s = divmod(rem, 60)
    parts = []
    if h:
        parts.append(f"{h}h")
    if m:
        parts.append(f"{m}m")
    parts.append(f"{s}s")
    return " ".join(parts)
