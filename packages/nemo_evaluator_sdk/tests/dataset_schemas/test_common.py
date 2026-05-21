# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import pytest
from nemo_evaluator_sdk.dataset_schemas.common import (
    _MISSING,
    ARRAY_TOKEN,
    allowed_types,
    display_path,
    empty_object_schema,
    encode_type,
    get_schema_at_path,
    get_value_at_path,
    primitive_type_name,
    schema_kind,
    split_path,
    validate_json_schema,
    value_kind,
)


def test_validate_json_schema_rejects_invalid_schema():
    with pytest.raises(ValueError, match="invalid JSON Schema"):
        validate_json_schema({"type": "definitely-not-a-valid-json-schema-type"})


def test_empty_object_schema_uses_expected_shape():
    assert empty_object_schema() == {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "properties": {},
        "required": [],
    }


def test_split_path_expands_array_segments():
    assert split_path("messages[].content") == ["messages", ARRAY_TOKEN, "content"]


def test_split_path_preserves_nested_array_segments():
    assert split_path("messages[][].content") == ["messages", ARRAY_TOKEN, ARRAY_TOKEN, "content"]


def test_get_value_at_path_returns_missing_for_array_segments():
    assert get_value_at_path({"messages": [{"content": "hi"}]}, "messages[].content") is _MISSING


def test_get_schema_at_path_tracks_nested_required_state():
    schema, is_required = get_schema_at_path(
        {
            "type": "object",
            "properties": {
                "payload": {
                    "type": "object",
                    "properties": {"prompt": {"type": "string"}},
                    "required": ["prompt"],
                }
            },
            "required": ["payload"],
        },
        "payload.prompt",
    )

    assert schema == {"type": "string"}
    assert is_required is True


def test_schema_helpers_classify_common_types():
    assert encode_type(["string"]) == "string"
    assert encode_type(["null", "string"]) == ["null", "string"]
    assert primitive_type_name(True) == "boolean"
    assert primitive_type_name(3) == "integer"
    assert primitive_type_name(3.5) == "number"
    assert primitive_type_name(None) == "null"
    assert value_kind({"a": 1}) == "object"
    assert value_kind([1, 2]) == "array"
    assert allowed_types({"type": ["string", "null"]}) == {"string", "null"}
    assert schema_kind({"properties": {}}) == "object"
    assert schema_kind({"type": "null"}) == "primitive"
    assert schema_kind({"type": ["object", "null"]}) == "object"
    assert schema_kind({"type": ["array", "null"]}) == "array"
    assert display_path("") == "<root>"
