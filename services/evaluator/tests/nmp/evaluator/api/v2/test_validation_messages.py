# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import nmp.evaluator.app.values as app
from nmp.evaluator.api.v2.common.checks import mapping_hint, schema_error_message


def test_metric_schema_error_message_deduplicates_missing_field_pairs():
    message = schema_error_message(
        "Dataset schema is incompatible with metric 'llm-judge'",
        [
            "dataset schema missing required field 'input'",
            "dataset schema missing field definition 'input'",
            "dataset schema missing required field 'output'",
            "dataset schema missing field definition 'output'",
        ],
        hint=mapping_hint(app.FieldMapping()),
    )

    assert "missing required field 'input'" in message
    assert "missing field definition 'input'" not in message
    assert "missing required field 'output'" in message
    assert "missing field definition 'output'" not in message
    assert "provide field_mapping" in message


def test_benchmark_schema_error_message_deduplicates_repeated_errors_and_adds_mapping_hint():
    message = schema_error_message(
        "Benchmark dataset schema is incompatible with benchmark metrics",
        [
            "dataset schema missing required field 'output'",
            "dataset schema missing field definition 'output'",
            "dataset schema missing required field 'output'",
        ],
        hint=mapping_hint(app.FieldMapping(output="answer")),
    )

    assert message.count("missing required field 'output'") == 1
    assert "missing field definition 'output'" not in message
    assert "Check field_mapping values against your dataset schema" in message
