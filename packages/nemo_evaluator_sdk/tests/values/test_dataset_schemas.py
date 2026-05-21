# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import pytest
from nemo_evaluator_sdk.values.dataset_schemas import (
    FieldMapping,
    InputSchema,
)


def test_column_mapping_rejects_unknown_fields():
    with pytest.raises(ValueError, match="Extra inputs are not permitted"):
        FieldMapping.model_validate({"input": "text", "unexpected": "value"})


def test_column_mapping_rejects_array_paths():
    with pytest.raises(ValueError):
        FieldMapping.model_validate({"messages": "conversations[].messages"})


def test_column_mapping_rejects_empty_paths():
    with pytest.raises(ValueError):
        FieldMapping.model_validate({"input": ""})

    with pytest.raises(ValueError):
        FieldMapping.model_validate({"custom": {"rubric": ""}})


def test_column_mapping_supports_trajectory_binding():
    mapping = FieldMapping.model_validate({"trajectory": "steps"})

    assert mapping.mapping()["trajectory"] == "steps"


def test_column_mapping_schema_rejects_bracket_paths():
    schema = FieldMapping.model_json_schema()
    expected_pattern = r"^[^\[\]]*$"

    for field_name in ("input", "output", "context", "reference", "trajectory", "messages", "tool_calls", "tools"):
        any_of = schema["properties"][field_name]["anyOf"]
        constrained_branch = next(branch for branch in any_of if branch.get("type") == "string")
        assert constrained_branch["minLength"] == 1
        assert constrained_branch["pattern"] == expected_pattern

    assert schema["properties"]["custom"]["additionalProperties"]["minLength"] == 1
    assert schema["properties"]["custom"]["additionalProperties"]["pattern"] == expected_pattern


def test_required_input_schema_rejects_invalid_json_schema():
    with pytest.raises(ValueError, match="invalid JSON Schema"):
        InputSchema.model_validate({"schema": {"type": "definitely-not-a-valid-json-schema-type"}})
