# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""OTLP ingest helper tests."""

from collections.abc import AsyncIterator
from datetime import datetime, timezone
from typing import Any, cast

import pytest
from fastapi import HTTPException, Request
from nmp.intake.spans.ingest.otlp import _read_limited_body, _span_to_domain

DEFAULT_TRACE_ID = bytes.fromhex("0" * 31 + "1")
DEFAULT_SPAN_ID = bytes.fromhex("0000000000000001")


class StreamingRequest:
    def __init__(self, chunks: list[bytes]) -> None:
        self._chunks = chunks

    async def stream(self) -> AsyncIterator[bytes]:
        for chunk in self._chunks:
            yield chunk


@pytest.mark.asyncio
async def test_read_limited_body_accepts_stream_under_limit():
    body = await _read_limited_body(cast(Request, StreamingRequest([b"abc", b"def"])), max_bytes=6)

    assert body == b"abcdef"


@pytest.mark.asyncio
async def test_read_limited_body_rejects_stream_over_limit():
    with pytest.raises(HTTPException) as exc_info:
        await _read_limited_body(cast(Request, StreamingRequest([b"abc", b"def"])), max_bytes=5)

    assert exc_info.value.status_code == 413


@pytest.mark.parametrize(
    ("trace_id", "span_id", "parent_span_id", "match"),
    [
        (bytes(16), bytes.fromhex("0000000000000001"), b"", "trace_id is required"),
        (bytes.fromhex("0" * 31 + "1"), bytes(8), b"", "span_id is required"),
        (bytes.fromhex("0" * 31 + "1"), bytes.fromhex("0000000000000001"), bytes(8), "parent_span_id"),
    ],
)
def test_span_to_domain_rejects_empty_or_zero_otlp_ids(
    trace_id: bytes, span_id: bytes, parent_span_id: bytes, match: str
):
    span = _make_span(trace_id=trace_id, span_id=span_id, parent_span_id=parent_span_id)

    with pytest.raises(ValueError, match=match):
        _span_to_domain(
            workspace="default",
            span=span,
            resource_attributes={},
            scope_data={},
            ingested_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        )


def test_span_to_domain_filters_resource_raw_attributes():
    span = _make_span()
    raw_resource_attributes = {
        "service.name": "intake-span-test",
        "session.id": "resource-session",
        "gen_ai.project": "project-a",
        "user.id": "user-a",
    }

    domain_span = _span_to_domain(
        workspace="default",
        span=span,
        resource_attributes=raw_resource_attributes,
        scope_data={},
        ingested_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
    )

    assert domain_span.attributes_string["service.name"] == "intake-span-test"
    assert domain_span.attributes_string["project.name"] == "project-a"
    assert domain_span.attributes_string["user.id"] == "user-a"


def test_span_to_domain_skips_empty_scope_data():
    span = _make_span()

    domain_span = _span_to_domain(
        workspace="default",
        span=span,
        resource_attributes={},
        scope_data={"name": None, "version": None},
        ingested_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
    )

    assert "otel.scope" not in domain_span.attributes_string


def test_span_to_domain_does_not_duplicate_model_aliases():
    span = _make_span()
    request_model = span.attributes.add()
    request_model.key = "gen_ai.request.model"
    request_model.value.string_value = "request-model"
    response_model = span.attributes.add()
    response_model.key = "gen_ai.response.model"
    response_model.value.string_value = "response-model"

    domain_span = _span_to_domain(
        workspace="default",
        span=span,
        resource_attributes={},
        scope_data={},
        ingested_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
    )

    assert domain_span.attributes_string["gen_ai.request.model"] == "request-model"
    assert "gen_ai.response.model" not in domain_span.attributes_string


def _make_span(
    *,
    trace_id: bytes = DEFAULT_TRACE_ID,
    span_id: bytes = DEFAULT_SPAN_ID,
    parent_span_id: bytes = b"",
) -> Any:
    from opentelemetry.proto.trace.v1 import trace_pb2

    span = trace_pb2.Span()
    span.trace_id = trace_id
    span.span_id = span_id
    span.parent_span_id = parent_span_id
    span.name = "test-span"
    span.start_time_unix_nano = 1_700_000_000_000_000_000
    span.end_time_unix_nano = 1_700_000_000_001_000_000
    return span
