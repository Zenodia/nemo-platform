# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Convention frames for NDJSON-streaming :class:`NemoFunction`s.

Plugin authors may use these directly or define their own frame
shapes — the route adapter doesn't enforce a particular schema on
user-yielded frames. The one exception is :class:`Heartbeat`: the
adapter emits a heartbeat frame on idle so proxies don't time the
connection out and so callers can tell "server is still working" apart
from "connection died".

The discriminator field name is ``kind``. The canonical values agreed
in `plan-functions.md` are ``"log" | "progress" | "data" | "error" |
"done" | "heartbeat"``. This module ships the three structural ones
(:class:`Heartbeat`, :class:`Done`, :class:`Error`); domain frames
(``log`` / ``progress`` / ``data``) are typically plugin-specific so
plugin authors define them themselves.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel


class Heartbeat(BaseModel):
    """Idle-tick frame emitted by the route adapter every ~5 s of silence.

    The route adapter inserts these unconditionally on streams that go
    quiet — they are not produced by user code. Plugins relying on
    strict frame typing on the receiving side should ignore unknown
    ``kind`` values or include :class:`Heartbeat` in their own
    discriminated union.
    """

    kind: Literal["heartbeat"] = "heartbeat"


class Done(BaseModel):
    """Terminator frame for a successful stream.

    Convention only — yield this as the *last* frame in a stream. The
    route adapter does not synthesise it; if your stream just ends
    without a ``Done``, callers see a clean EOF instead of an explicit
    success marker. The marker is useful when the same stream may end
    with :class:`Error` instead.
    """

    kind: Literal["done"] = "done"


class Error(BaseModel):
    """Terminator frame for an unsuccessful stream.

    Convention only — yield this when an error occurs mid-stream and
    you want to surface a structured failure rather than letting the
    underlying exception propagate (which would close the connection
    abruptly). Pair with raising the underlying exception for
    server-side observability.
    """

    kind: Literal["error"] = "error"
    message: str
    details: dict[str, Any] | None = None


__all__ = ["Done", "Error", "Heartbeat"]
