# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Span domain and API schema tests."""

import json
from datetime import datetime, timezone

import pytest
from nmp.intake.spans.api.spans_schemas import Span
from nmp.intake.spans.domain import IntakeSpan, SpanKind, SpanStatus
from nmp.intake.spans.storage import json_dumps_preserve
from pydantic import ValidationError


def test_intake_span_rejects_empty_external_span_id():
    with pytest.raises(ValidationError, match="external_span_id must not be empty"):
        IntakeSpan(
            workspace="workspace-a",
            session_id="session-a",
            trace_id="trace-a",
            source_format="test",
            external_span_id="",
            start_time=datetime(2026, 1, 1, tzinfo=timezone.utc),
            event_ts=datetime(2026, 1, 1, tzinfo=timezone.utc),
        )


def test_span_response_raw_attributes_merges_atif_raw_with_unknown_attributes():
    now = datetime(2026, 1, 1, tzinfo=timezone.utc)
    span = IntakeSpan(
        workspace="workspace-a",
        session_id="session-a",
        trace_id="trace-a",
        source_format="atif",
        external_span_id="span-a",
        kind=SpanKind.LLM,
        status=SpanStatus.SUCCESS,
        start_time=now,
        event_ts=now,
        attributes_string={
            "atif.raw": json_dumps_preserve(
                {"source_session_id": "session-a", "evaluation.metadata": {"source": "atif.raw"}}
            ),
            "custom.string": "value-a",
            "evaluation.metadata": json.dumps({"source": "attribute.bag"}),
            "gen_ai.request.model": "model-a",
        },
        attributes_number={"custom.number": 1.25, "llm.token_count.prompt": 42},
        attributes_bool={"custom.bool": True},
    )

    response = Span.from_domain(span)

    assert response.raw_attributes is not None
    assert json.loads(response.raw_attributes) == {
        "source_session_id": "session-a",
        "custom.string": "value-a",
        "custom.number": 1.25,
        "custom.bool": True,
    }
