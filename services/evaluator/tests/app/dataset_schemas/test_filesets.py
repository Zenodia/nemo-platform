# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import pytest
from nmp.evaluator.app.dataset_schemas.filesets import (
    parse_fileset_ref_path,
    resolve_schema_entry,
    select_schema_for_path,
)


def test_select_schema_for_path_resolves_schema_defs():
    selected = select_schema_for_path(
        "default_row",
        {"validation.jsonl": "validation_row"},
        "validation.jsonl",
        schema_defs={
            "default_row": {"type": "object", "properties": {"id": {"type": "string"}}},
            "validation_row": {"type": "object", "properties": {"name": {"type": "string"}}},
        },
    )

    assert selected == {"type": "object", "properties": {"name": {"type": "string"}}}


def test_select_schema_for_path_normalizes_leading_slash():
    selected = select_schema_for_path(
        {"type": "object", "properties": {"id": {"type": "string"}}},
        {"validation.jsonl": {"type": "object", "properties": {"input": {"type": "string"}}}},
        "/validation.jsonl",
    )

    assert selected == {"type": "object", "properties": {"input": {"type": "string"}}}


def test_parse_fileset_ref_path_preserves_glob_fragments():
    assert parse_fileset_ref_path("workspace/fileset#validation/*.jsonl") == (
        "workspace/fileset",
        "validation/*.jsonl",
    )


def test_parse_fileset_ref_path_without_fragment():
    assert parse_fileset_ref_path("workspace/fileset") == ("workspace/fileset", None)


def test_parse_fileset_ref_path_normalizes_empty_and_leading_slash_fragments():
    assert parse_fileset_ref_path("workspace/fileset#") == ("workspace/fileset", None)
    assert parse_fileset_ref_path("workspace/fileset#/") == ("workspace/fileset", None)
    assert parse_fileset_ref_path("workspace/fileset#/validation/a.jsonl") == (
        "workspace/fileset",
        "validation/a.jsonl",
    )


def test_resolve_schema_entry_rejects_unknown_schema_def_reference():
    with pytest.raises(ValueError, match="unknown dataset schema reference"):
        resolve_schema_entry("missing_schema", schema_defs={"other": {"type": "object"}})


def test_resolve_schema_entry_rejects_unsupported_type():
    with pytest.raises(TypeError, match="unsupported dataset schema entry type"):
        resolve_schema_entry(123, schema_defs={})
