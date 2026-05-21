# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from nmp.evaluator.app.dataset_schemas.resolution import (
    SchemaResolutionTarget,
    group_schema_resolution_targets,
    resolve_dataset_schema_targets,
)
from nmp.evaluator.app.values import DatasetRows, Fileset, FilesetRef


def _mock_fileset_with_dataset_metadata(
    *,
    schema_: dict | str | None = None,
    schemas_by_path: dict[str, dict | str] | None = None,
    schema_defs: dict[str, dict] | None = None,
) -> SimpleNamespace:
    return SimpleNamespace(
        metadata=SimpleNamespace(
            dataset=SimpleNamespace(
                schema_=schema_,
                schemas_by_path=schemas_by_path or {},
                schema_defs=schema_defs or {},
            )
        )
    )


def test_group_schema_resolution_targets_collapses_identical_schemas_with_path_context():
    schema = {"type": "object", "properties": {"input": {"type": "string"}}}

    grouped = group_schema_resolution_targets(
        [
            SchemaResolutionTarget(paths=("validation/a.jsonl",), schema=schema),
            SchemaResolutionTarget(
                paths=("validation/b.jsonl",), schema={"properties": {"input": {"type": "string"}}, "type": "object"}
            ),
            SchemaResolutionTarget(paths=("validation/c.jsonl",), schema={"type": "object"}),
        ]
    )

    assert [(target.paths, target.schema) for target in grouped] == [
        (("validation/a.jsonl", "validation/b.jsonl"), schema),
        (("validation/c.jsonl",), {"type": "object"}),
    ]
    assert grouped[0].path_context() == "validation/a.jsonl (+1 more paths)"


@pytest.mark.asyncio
async def test_resolve_dataset_schema_targets_rejects_wildcard_with_no_matches():
    sdk = AsyncMock()
    sdk.files.filesets.retrieve.return_value = _mock_fileset_with_dataset_metadata(schema_={"type": "object"})
    sdk.files.list.return_value = SimpleNamespace(data=[])

    with pytest.raises(ValueError, match="no matching files found in fileset"):
        await resolve_dataset_schema_targets(FilesetRef(root="workspace/fileset#validation/*.jsonl"), sdk)


@pytest.mark.asyncio
async def test_resolve_dataset_schema_targets_rejects_wildcard_over_match_limit(monkeypatch: pytest.MonkeyPatch):
    sdk = AsyncMock()
    sdk.files.filesets.retrieve.return_value = _mock_fileset_with_dataset_metadata(schema_={"type": "object"})
    sdk.files.list.return_value = SimpleNamespace(
        data=[
            SimpleNamespace(path="validation/a.jsonl"),
            SimpleNamespace(path="validation/b.jsonl"),
            SimpleNamespace(path="validation/c.jsonl"),
        ]
    )
    monkeypatch.setattr("nmp.evaluator.app.dataset_schemas.resolution._MAX_WILDCARD_SCHEMA_VALIDATION_TARGETS", 2)

    with pytest.raises(ValueError, match="matched more than 2 validation targets"):
        await resolve_dataset_schema_targets(FilesetRef(root="workspace/fileset#validation/*.jsonl"), sdk)


@pytest.mark.asyncio
async def test_resolve_dataset_schema_targets_returns_empty_when_fileset_metadata_has_no_dataset():
    sdk = AsyncMock()
    sdk.files.filesets.retrieve.return_value = SimpleNamespace(metadata=SimpleNamespace(dataset=None))

    targets = await resolve_dataset_schema_targets(FilesetRef(root="workspace/fileset#validation/*.jsonl"), sdk)

    assert targets == []
    sdk.files.list.assert_not_awaited()


@pytest.mark.asyncio
async def test_resolve_dataset_schema_targets_returns_schema_per_matched_path():
    sdk = AsyncMock()
    sdk.files.filesets.retrieve.return_value = _mock_fileset_with_dataset_metadata(
        schema_="default_row",
        schemas_by_path={"validation/a.jsonl": "special_row"},
        schema_defs={
            "default_row": {"type": "object", "properties": {"id": {"type": "string"}}},
            "special_row": {"type": "object", "properties": {"name": {"type": "string"}}},
        },
    )
    sdk.files.list.return_value = SimpleNamespace(
        data=[
            SimpleNamespace(path="validation/a.jsonl"),
            SimpleNamespace(path="validation/b.jsonl"),
            SimpleNamespace(path="train/c.jsonl"),
        ]
    )

    targets = await resolve_dataset_schema_targets(FilesetRef(root="workspace/fileset#validation/*.jsonl"), sdk)

    assert [(target.paths, target.schema) for target in targets] == [
        (("validation/a.jsonl",), {"type": "object", "properties": {"name": {"type": "string"}}}),
        (("validation/b.jsonl",), {"type": "object", "properties": {"id": {"type": "string"}}}),
    ]


@pytest.mark.asyncio
async def test_resolve_dataset_schema_targets_ignores_unsupported_default_schema_type():
    sdk = AsyncMock()
    sdk.files.filesets.retrieve.return_value = SimpleNamespace(
        metadata=SimpleNamespace(
            dataset=SimpleNamespace(
                schema_=123,
                schemas_by_path={},
                schema_defs={},
            )
        )
    )

    targets = await resolve_dataset_schema_targets(FilesetRef(root="workspace/fileset#validation/*.jsonl"), sdk)

    assert targets == []
    sdk.files.list.assert_not_awaited()


@pytest.mark.asyncio
async def test_resolve_dataset_schema_targets_coerces_invalid_schema_maps_to_defaults():
    default_schema = {"type": "object", "properties": {"id": {"type": "string"}}}
    sdk = AsyncMock()
    sdk.files.filesets.retrieve.return_value = SimpleNamespace(
        metadata=SimpleNamespace(
            dataset=SimpleNamespace(
                schema_=default_schema,
                schemas_by_path=["not-a-dict"],
                schema_defs=["not-a-dict"],
            )
        )
    )
    sdk.files.list.return_value = SimpleNamespace(data=[SimpleNamespace(path="validation/a.jsonl")])

    targets = await resolve_dataset_schema_targets(FilesetRef(root="workspace/fileset#validation/*.jsonl"), sdk)

    assert [(target.paths, target.schema) for target in targets] == [(("validation/a.jsonl",), default_schema)]


@pytest.mark.asyncio
async def test_resolve_dataset_schema_targets_returns_empty_for_inline_dataset_rows():
    sdk = AsyncMock()

    targets = await resolve_dataset_schema_targets(
        DatasetRows(rows=[{"input": "hello"}]),
        sdk,
    )

    assert targets == []
    sdk.files.filesets.retrieve.assert_not_awaited()
    sdk.files.list.assert_not_awaited()


@pytest.mark.asyncio
async def test_resolve_dataset_schema_targets_uses_fileset_embedded_metadata_without_sdk_lookup():
    sdk = AsyncMock()
    fileset = Fileset(
        path="validation/a.jsonl",
        storage={
            "type": "ngc",
            "org": "org",
            "team": "team",
            "target": "target",
            "api_key_secret": "test-api-key",
        },
        metadata={
            "dataset": {
                "schema": {"type": "object", "properties": {"id": {"type": "string"}}},
                "schemas_by_path": {
                    "validation/a.jsonl": {"type": "object", "properties": {"input": {"type": "string"}}}
                },
            }
        },
    )

    targets = await resolve_dataset_schema_targets(fileset, sdk)

    assert [(target.paths, target.schema) for target in targets] == [
        (("validation/a.jsonl",), {"type": "object", "properties": {"input": {"type": "string"}}})
    ]
    sdk.files.filesets.retrieve.assert_not_awaited()
    sdk.files.list.assert_not_awaited()


@pytest.mark.asyncio
async def test_resolve_dataset_schema_targets_returns_empty_for_fileset_without_dataset_metadata():
    sdk = AsyncMock()
    fileset = Fileset(
        path="validation/a.jsonl",
        storage={
            "type": "ngc",
            "org": "org",
            "team": "team",
            "target": "target",
            "api_key_secret": "test-api-key",
        },
    )

    targets = await resolve_dataset_schema_targets(fileset, sdk)

    assert targets == []
    sdk.files.filesets.retrieve.assert_not_awaited()
    sdk.files.list.assert_not_awaited()


@pytest.mark.asyncio
async def test_resolve_dataset_schema_targets_rejects_invalid_fileset_ref_format():
    sdk = AsyncMock()

    with pytest.raises(ValueError, match="workspace/fileset-name"):
        await resolve_dataset_schema_targets(FilesetRef(root="fileset-only"), sdk)

    sdk.files.filesets.retrieve.assert_not_awaited()
    sdk.files.list.assert_not_awaited()


@pytest.mark.asyncio
async def test_resolve_dataset_schema_targets_rejects_unknown_default_schema_reference():
    sdk = AsyncMock()
    sdk.files.filesets.retrieve.return_value = _mock_fileset_with_dataset_metadata(
        schema_="missing_default_schema",
        schemas_by_path={},
        schema_defs={},
    )
    sdk.files.list.return_value = SimpleNamespace(data=[SimpleNamespace(path="validation/a.jsonl")])

    with pytest.raises(ValueError, match="unknown dataset schema reference"):
        await resolve_dataset_schema_targets(FilesetRef(root="workspace/fileset#validation/*.jsonl"), sdk)


@pytest.mark.asyncio
async def test_resolve_dataset_schema_targets_without_fragment_uses_default_schema():
    default_schema = {"type": "object", "properties": {"input": {"type": "string"}}}
    sdk = AsyncMock()
    sdk.files.filesets.retrieve.return_value = _mock_fileset_with_dataset_metadata(
        schema_=default_schema,
        schemas_by_path={"validation/a.jsonl": {"type": "object", "properties": {"reference": {"type": "string"}}}},
    )

    targets = await resolve_dataset_schema_targets(FilesetRef(root="workspace/fileset"), sdk)

    assert [(target.paths, target.schema) for target in targets] == [((), default_schema)]
    sdk.files.list.assert_not_awaited()
