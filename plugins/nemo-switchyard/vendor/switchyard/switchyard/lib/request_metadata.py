# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""request metadata helpers for HTTP endpoint context."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

CTX_REQUEST_METADATA = "_request_metadata"

# Existing Switchyard session header. Do not add aliases here unless a
# concrete client requires one; keeping one spelling avoids ambiguity.
PROXY_SESSION_ID_HEADER = "proxy_x_session_id"
INTAKE_ENABLED_HEADER = "x-switchyard-intake-enabled"
INTAKE_APP_HEADER = "x-switchyard-intake-app"
INTAKE_TASK_HEADER = "x-switchyard-intake-task"


@dataclass(frozen=True)
class IntakeRequestMetadata:
    """Intake-specific request metadata extracted from allowlisted headers."""

    enabled: bool | None = None
    app: str | None = None
    task: str | None = None


@dataclass(frozen=True)
class RequestMetadata:
    """Explicit metadata extracted by filters and processors.

    This is intentionally not a generic header passthrough. Add fields
    only for headers with an existing Switchyard meaning or a concrete
    processor consumer.
    """

    session_id: str | None = None
    intake: IntakeRequestMetadata = IntakeRequestMetadata()

    @classmethod
    def from_headers(cls, headers: Mapping[str, str]) -> RequestMetadata:
        normalized = {name.lower(): value for name, value in headers.items()}
        return cls(
            session_id=_header_value(normalized, PROXY_SESSION_ID_HEADER),
            intake=IntakeRequestMetadata(
                enabled=_parse_bool(_header_value(normalized, INTAKE_ENABLED_HEADER)),
                app=_header_value(normalized, INTAKE_APP_HEADER),
                task=_header_value(normalized, INTAKE_TASK_HEADER),
            ),
        )


def _header_value(headers: Mapping[str, str], name: str) -> str | None:
    value = headers.get(name)
    return value if isinstance(value, str) and value else None


def _parse_bool(raw: str | None) -> bool | None:
    if raw is None:
        return None
    normalized = raw.strip().lower()
    if normalized == "true":
        return True
    if normalized == "false":
        return False
    return None
