# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

from types import SimpleNamespace
from typing import Literal
from unittest import mock
from unittest.mock import AsyncMock

import nmp.evaluator.app.values as app
import nmp.evaluator.entities as entities
import pytest
from nmp.evaluator.api.v2.benchmarks.checks import (
    benchmark_creation_schema_check,
    benchmark_job_schema_check,
)
from nmp.evaluator.api.v2.benchmarks.schemas.jobs import BenchmarkOfflineJob, BenchmarkOnlineJob
from nmp.evaluator.api.v2.metrics.checks import metric_dataset_schema_check
from nmp.evaluator.api.v2.metrics.schemas.jobs import MetricOfflineJob, MetricOnlineJob
from nmp.evaluator.app.dataset_schemas import TemplateSchemaInferenceError
from nmp.evaluator.app.values import BenchmarkRef, FilesetRef, MetricRef, Model

INPUT_REQUIRED_SCHEMA = {
    "type": "object",
    "properties": {"input": {"type": "string"}},
    "required": ["input"],
}
INPUT_WITH_EXTRA_SCHEMA = {
    "type": "object",
    "properties": {"input": {"type": "string"}, "extra": {"type": "string"}},
    "required": ["input"],
}
REFERENCE_REQUIRED_SCHEMA = {
    "type": "object",
    "properties": {"reference": {"type": "string"}},
    "required": ["reference"],
}
SCHEMAS = {
    "input": INPUT_REQUIRED_SCHEMA,
    "input_extra": INPUT_WITH_EXTRA_SCHEMA,
    "reference": REFERENCE_REQUIRED_SCHEMA,
}
SCHEMA_REF_KEYS = {
    "input": "input_required",
    "input_extra": "input_with_extra",
    "reference": "reference_required",
}
SCHEMA_DEFS = {
    SCHEMA_REF_KEYS["input"]: INPUT_REQUIRED_SCHEMA,
    SCHEMA_REF_KEYS["input_extra"]: INPUT_WITH_EXTRA_SCHEMA,
    SCHEMA_REF_KEYS["reference"]: REFERENCE_REQUIRED_SCHEMA,
}


def _files_response(*paths: str) -> SimpleNamespace:
    return SimpleNamespace(data=[SimpleNamespace(path=path) for path in paths])


def _build_dataset_metadata(
    metadata_variant: Literal["schema_refs", "inline"],
    *,
    default_schema_kind: Literal["input", "reference"],
    path_schema_kinds: dict[str, str],
) -> SimpleNamespace:
    if metadata_variant == "schema_refs":
        return SimpleNamespace(
            metadata=SimpleNamespace(
                dataset=SimpleNamespace(
                    schema_=SCHEMA_REF_KEYS[default_schema_kind],
                    schemas_by_path={
                        path: SCHEMA_REF_KEYS[schema_kind] for path, schema_kind in path_schema_kinds.items()
                    },
                    schema_defs=SCHEMA_DEFS,
                )
            )
        )
    if metadata_variant == "inline":
        return SimpleNamespace(
            metadata=SimpleNamespace(
                dataset=SimpleNamespace(
                    schema_=SCHEMAS[default_schema_kind],
                    schemas_by_path={path: SCHEMAS[schema_kind] for path, schema_kind in path_schema_kinds.items()},
                    schema_defs={},
                )
            )
        )
    raise ValueError(f"unsupported metadata variant: {metadata_variant}")


def _mock_metric_with_required_schema(schema: dict) -> mock.Mock:
    metric = mock.Mock()
    metric.workspace = "default"
    metric.name = "metric"
    metric.supported_job_types = [app.SupportedJobTypes.OFFLINE, app.SupportedJobTypes.ONLINE]
    metric.input_schema.return_value = SimpleNamespace(schema_=schema)
    return metric


def _metric_job(dataset_root: str, *, optional_fields: list[str] | None = None) -> MetricOnlineJob:
    return MetricOnlineJob(
        metric=MetricRef(root="default/metric"),
        model=Model(url="http://model.test/v1", name="model"),
        dataset=FilesetRef(root=dataset_root),
        prompt_template="{{input}}",
        optional_fields=optional_fields or [],
    )


def _benchmark_online_job(*, optional_fields: list[str] | None = None) -> BenchmarkOnlineJob:
    return BenchmarkOnlineJob(
        benchmark=BenchmarkRef(root="default/bench"),
        model=Model(url="http://model.test/v1", name="model"),
        prompt_template="{{input}}",
        optional_fields=optional_fields or [],
    )


def _metric_offline_job(dataset_root: str) -> MetricOfflineJob:
    return MetricOfflineJob(
        metric=MetricRef(root="default/metric"),
        dataset=FilesetRef(root=dataset_root),
    )


def _benchmark_offline_job() -> BenchmarkOfflineJob:
    return BenchmarkOfflineJob(benchmark=BenchmarkRef(root="default/bench"))


def _benchmark_entity(dataset_root: str) -> entities.Benchmark:
    return entities.Benchmark(
        workspace="default",
        name="bench",
        description="Test benchmark",
        dataset=FilesetRef(root=dataset_root),
        metrics=[entities.BLEUMetric(workspace="default", name="bleu", references=[])],
    )


def _benchmark_entity_with_input_metric(dataset_root: str) -> entities.Benchmark:
    return entities.Benchmark(
        workspace="default",
        name="bench",
        description="Test benchmark",
        dataset=FilesetRef(root=dataset_root),
        metrics=[
            entities.ExactMatchMetric(
                workspace="default",
                name="exact-match",
                reference="{{input}}",
            )
        ],
    )


@pytest.mark.asyncio
@pytest.mark.parametrize("metadata_variant", ["schema_refs", "inline"])
async def test_metric_schema_check_wildcard_no_matches_returns_error(
    metadata_variant: Literal["schema_refs", "inline"],
):
    sdk = AsyncMock()
    sdk.files.filesets.retrieve.return_value = _build_dataset_metadata(
        metadata_variant,
        default_schema_kind="input",
        path_schema_kinds={},
    )
    # Fileset contains files, but none inside selector path.
    sdk.files.list.return_value = _files_response("train/c.jsonl")

    result = await metric_dataset_schema_check(
        _metric_job("default/my-fileset#validation/*.jsonl"),
        _mock_metric_with_required_schema(INPUT_REQUIRED_SCHEMA),
        sdk,
    )

    assert result.status is False
    assert any("no matching files found in fileset" in error for error in result.errors)


@pytest.mark.asyncio
@pytest.mark.parametrize("metadata_variant", ["schema_refs", "inline"])
async def test_metric_schema_check_wildcard_ignores_unmatched_incompatible_files(
    metadata_variant: Literal["schema_refs", "inline"],
):
    sdk = AsyncMock()
    sdk.files.filesets.retrieve.return_value = _build_dataset_metadata(
        metadata_variant,
        default_schema_kind="input",
        path_schema_kinds={
            "validation/a.jsonl": "input",
            "validation/b.jsonl": "input",
            # Outside selector and intentionally incompatible.
            "train/c.jsonl": "reference",
        },
    )
    sdk.files.list.return_value = _files_response(
        "validation/a.jsonl",
        "validation/b.jsonl",
        "train/c.jsonl",
    )

    result = await metric_dataset_schema_check(
        _metric_job("default/my-fileset#validation/*.jsonl"),
        _mock_metric_with_required_schema(INPUT_REQUIRED_SCHEMA),
        sdk,
    )

    assert result.status is True
    assert result.errors == []


@pytest.mark.asyncio
@pytest.mark.parametrize("metadata_variant", ["schema_refs", "inline"])
async def test_metric_schema_check_wildcard_does_not_validate_right_anchored_matches(
    metadata_variant: Literal["schema_refs", "inline"],
):
    sdk = AsyncMock()
    sdk.files.filesets.retrieve.return_value = _build_dataset_metadata(
        metadata_variant,
        default_schema_kind="input",
        path_schema_kinds={
            "validation/a.jsonl": "input",
            # Would match under right-anchored path matching, but root-anchored
            # fileset selector semantics should not select it.
            "nested/validation/b.jsonl": "reference",
        },
    )
    sdk.files.list.return_value = _files_response(
        "validation/a.jsonl",
        "nested/validation/b.jsonl",
    )

    result = await metric_dataset_schema_check(
        _metric_job("default/my-fileset#validation/*.jsonl"),
        _mock_metric_with_required_schema(INPUT_REQUIRED_SCHEMA),
        sdk,
    )

    assert result.status is True
    assert result.errors == []


@pytest.mark.asyncio
@pytest.mark.parametrize("metadata_variant", ["schema_refs", "inline"])
async def test_metric_schema_check_wildcard_default_fallback_applies_to_unmapped_matched_path(
    metadata_variant: Literal["schema_refs", "inline"],
):
    sdk = AsyncMock()
    sdk.files.filesets.retrieve.return_value = _build_dataset_metadata(
        metadata_variant,
        default_schema_kind="reference",
        path_schema_kinds={
            "validation/a.jsonl": "input",
            # Outside selector and should be ignored.
            "train/c.jsonl": "input",
        },
    )
    sdk.files.list.return_value = _files_response(
        "validation/a.jsonl",
        "validation/b.jsonl",
        "train/c.jsonl",
    )

    result = await metric_dataset_schema_check(
        _metric_job("default/my-fileset#validation/*.jsonl"),
        _mock_metric_with_required_schema(INPUT_REQUIRED_SCHEMA),
        sdk,
    )

    assert result.status is False
    assert any("[validation/b.jsonl]" in error for error in result.errors)
    assert all("[train/c.jsonl]" not in error for error in result.errors)


@pytest.mark.asyncio
@pytest.mark.parametrize("metadata_variant", ["schema_refs", "inline"])
async def test_metric_schema_check_exact_fragment_selects_only_exact_file(
    metadata_variant: Literal["schema_refs", "inline"],
):
    sdk = AsyncMock()
    sdk.files.filesets.retrieve.return_value = _build_dataset_metadata(
        metadata_variant,
        default_schema_kind="reference",
        path_schema_kinds={
            "validation/a.jsonl": "input",
            "validation/b.jsonl": "reference",
            "train/c.jsonl": "reference",
        },
    )
    sdk.files.list.return_value = _files_response(
        "validation/a.jsonl",
        "validation/b.jsonl",
        "train/c.jsonl",
    )

    result = await metric_dataset_schema_check(
        _metric_job("default/my-fileset#validation/a.jsonl"),
        _mock_metric_with_required_schema(INPUT_REQUIRED_SCHEMA),
        sdk,
    )

    assert result.status is True
    assert result.errors == []
    sdk.files.list.assert_not_awaited()


@pytest.mark.asyncio
@pytest.mark.parametrize("metadata_variant", ["schema_refs", "inline"])
async def test_metric_schema_check_exact_fragment_uses_default_schema_without_listing(
    metadata_variant: Literal["schema_refs", "inline"],
):
    sdk = AsyncMock()
    sdk.files.filesets.retrieve.return_value = _build_dataset_metadata(
        metadata_variant,
        default_schema_kind="input",
        path_schema_kinds={},
    )
    sdk.files.list.return_value = _files_response("validation/b.jsonl", "train/c.jsonl")

    result = await metric_dataset_schema_check(
        _metric_job("default/my-fileset#validation/a.jsonl"),
        _mock_metric_with_required_schema(INPUT_REQUIRED_SCHEMA),
        sdk,
    )

    assert result.status is True
    assert result.errors == []
    sdk.files.list.assert_not_awaited()


@pytest.mark.asyncio
async def test_metric_schema_check_invalid_fileset_ref_format_returns_validation_error():
    sdk = AsyncMock()

    result = await metric_dataset_schema_check(
        _metric_job("my-fileset-without-workspace"),
        _mock_metric_with_required_schema(INPUT_REQUIRED_SCHEMA),
        sdk,
    )

    assert result.status is False
    assert any("Invalid dataset schema metadata" in error for error in result.errors)
    assert any("workspace/fileset-name" in error for error in result.errors)
    sdk.files.filesets.retrieve.assert_not_awaited()
    sdk.files.list.assert_not_awaited()


@pytest.mark.asyncio
@pytest.mark.parametrize("metadata_variant", ["schema_refs", "inline"])
async def test_metric_schema_check_prompt_validation_receives_optional_fields_and_ignored_roots(
    metadata_variant: Literal["schema_refs", "inline"],
):
    sdk = AsyncMock()
    sdk.files.filesets.retrieve.return_value = _build_dataset_metadata(
        metadata_variant,
        default_schema_kind="input",
        path_schema_kinds={
            "validation/a.jsonl": "input",
            "validation/b.jsonl": "input",
            "train/c.jsonl": "reference",
        },
    )
    sdk.files.list.return_value = _files_response(
        "validation/a.jsonl",
        "validation/b.jsonl",
        "train/c.jsonl",
    )
    job = _metric_job(
        "default/my-fileset#validation/*.jsonl",
        optional_fields=["reference", "sample.output_text"],
    )

    with mock.patch(
        "nmp.evaluator.api.v2.metrics.checks.validate_prompt_template_against_dataset_schema",
        return_value=[],
    ) as mock_prompt_check:
        result = await metric_dataset_schema_check(
            job,
            _mock_metric_with_required_schema(INPUT_REQUIRED_SCHEMA),
            sdk,
        )

    assert result.status is True
    assert mock_prompt_check.call_count == 1
    for call in mock_prompt_check.call_args_list:
        assert call.kwargs["ignored_roots"] == {"output", "output_text", "response"}
        assert call.kwargs["optional_fields"] == {"reference", "sample.output_text"}


@pytest.mark.asyncio
@pytest.mark.parametrize("metadata_variant", ["schema_refs", "inline"])
async def test_metric_schema_check_wildcard_prompt_error_has_matched_path_context_only(
    metadata_variant: Literal["schema_refs", "inline"],
):
    sdk = AsyncMock()
    sdk.files.filesets.retrieve.return_value = _build_dataset_metadata(
        metadata_variant,
        default_schema_kind="input",
        path_schema_kinds={
            "validation/a.jsonl": "input",
            "validation/b.jsonl": "input_extra",
            "train/c.jsonl": "reference",
        },
    )
    sdk.files.list.return_value = _files_response(
        "validation/a.jsonl",
        "validation/b.jsonl",
        "train/c.jsonl",
    )

    with mock.patch(
        "nmp.evaluator.api.v2.metrics.checks.validate_prompt_template_against_dataset_schema",
        side_effect=[[], ["dataset schema missing required field 'input'"]],
    ):
        result = await metric_dataset_schema_check(
            _metric_job("default/my-fileset#validation/*.jsonl"),
            _mock_metric_with_required_schema(INPUT_REQUIRED_SCHEMA),
            sdk,
        )

    assert result.status is False
    assert any("[validation/b.jsonl]" in error for error in result.errors)
    assert all("[train/c.jsonl]" not in error for error in result.errors)


@pytest.mark.asyncio
@pytest.mark.parametrize("metadata_variant", ["schema_refs", "inline"])
async def test_metric_schema_check_offline_job_skips_prompt_validation(
    metadata_variant: Literal["schema_refs", "inline"],
):
    sdk = AsyncMock()
    sdk.files.filesets.retrieve.return_value = _build_dataset_metadata(
        metadata_variant,
        default_schema_kind="input",
        path_schema_kinds={
            "validation/a.jsonl": "input",
            "validation/b.jsonl": "input",
        },
    )
    sdk.files.list.return_value = _files_response("validation/a.jsonl", "validation/b.jsonl")

    with mock.patch(
        "nmp.evaluator.api.v2.metrics.checks.validate_prompt_template_against_dataset_schema",
        return_value=[],
    ) as mock_prompt_check:
        result = await metric_dataset_schema_check(
            _metric_offline_job("default/my-fileset#validation/*.jsonl"),
            _mock_metric_with_required_schema(INPUT_REQUIRED_SCHEMA),
            sdk,
        )

    assert result.status is True
    mock_prompt_check.assert_not_called()


@pytest.mark.asyncio
@pytest.mark.parametrize("metadata_variant", ["schema_refs", "inline"])
async def test_metric_schema_check_without_fragment_uses_default_schema(
    metadata_variant: Literal["schema_refs", "inline"],
):
    sdk = AsyncMock()
    sdk.files.filesets.retrieve.return_value = _build_dataset_metadata(
        metadata_variant,
        default_schema_kind="input",
        path_schema_kinds={"validation/a.jsonl": "reference"},
    )
    sdk.files.list.return_value = _files_response("validation/a.jsonl")

    result = await metric_dataset_schema_check(
        _metric_job("default/my-fileset"),
        _mock_metric_with_required_schema(INPUT_REQUIRED_SCHEMA),
        sdk,
    )

    assert result.status is True
    assert result.errors == []
    sdk.files.list.assert_not_awaited()


@pytest.mark.asyncio
@pytest.mark.parametrize("metadata_variant", ["schema_refs", "inline"])
async def test_metric_schema_check_without_fragment_error_has_no_path_prefix(
    metadata_variant: Literal["schema_refs", "inline"],
):
    sdk = AsyncMock()
    sdk.files.filesets.retrieve.return_value = _build_dataset_metadata(
        metadata_variant,
        default_schema_kind="reference",
        path_schema_kinds={},
    )
    sdk.files.list.return_value = _files_response("validation/a.jsonl")

    result = await metric_dataset_schema_check(
        _metric_job("default/my-fileset"),
        _mock_metric_with_required_schema(INPUT_REQUIRED_SCHEMA),
        sdk,
    )

    assert result.status is False
    assert any("dataset schema missing required field 'input'" in error for error in result.errors)
    assert all("[" not in error for error in result.errors)
    sdk.files.list.assert_not_awaited()


@pytest.mark.asyncio
async def test_metric_schema_check_returns_true_when_fileset_has_no_dataset_metadata():
    sdk = AsyncMock()
    sdk.files.filesets.retrieve.return_value = SimpleNamespace(metadata=SimpleNamespace(dataset=None))

    result = await metric_dataset_schema_check(
        _metric_job("default/my-fileset#validation/*.jsonl"),
        _mock_metric_with_required_schema(INPUT_REQUIRED_SCHEMA),
        sdk,
    )

    assert result.status is True
    assert result.errors == []
    sdk.files.list.assert_not_awaited()


@pytest.mark.asyncio
async def test_metric_schema_check_unknown_schema_ref_returns_invalid_metadata_error():
    sdk = AsyncMock()
    sdk.files.filesets.retrieve.return_value = SimpleNamespace(
        metadata=SimpleNamespace(
            dataset=SimpleNamespace(
                schema_="input_required",
                schemas_by_path={"validation/a.jsonl": "missing_schema"},
                schema_defs=SCHEMA_DEFS,
            )
        )
    )
    sdk.files.list.return_value = _files_response("validation/a.jsonl", "train/c.jsonl")

    result = await metric_dataset_schema_check(
        _metric_job("default/my-fileset#validation/*.jsonl"),
        _mock_metric_with_required_schema(INPUT_REQUIRED_SCHEMA),
        sdk,
    )

    assert result.status is False
    assert any("Invalid dataset schema metadata" in error for error in result.errors)
    assert any("unknown dataset schema reference" in error for error in result.errors)


@pytest.mark.asyncio
@pytest.mark.parametrize("metadata_variant", ["schema_refs", "inline"])
async def test_metric_schema_check_wraps_template_schema_inference_error_from_input_schema(
    metadata_variant: Literal["schema_refs", "inline"],
):
    sdk = AsyncMock()
    sdk.files.filesets.retrieve.return_value = _build_dataset_metadata(
        metadata_variant,
        default_schema_kind="input",
        path_schema_kinds={"validation/a.jsonl": "input"},
    )
    sdk.files.list.return_value = _files_response("validation/a.jsonl")
    metric = _mock_metric_with_required_schema(INPUT_REQUIRED_SCHEMA)
    metric.input_schema.side_effect = TemplateSchemaInferenceError("unsupported metric template expression")

    result = await metric_dataset_schema_check(
        _metric_job("default/my-fileset#validation/*.jsonl"),
        metric,
        sdk,
    )

    assert result.status is False
    assert any("Unsupported metric prompt template for schema inference" in error for error in result.errors)
    assert any("unsupported metric template expression" in error for error in result.errors)


@pytest.mark.asyncio
@pytest.mark.parametrize("metadata_variant", ["schema_refs", "inline"])
async def test_metric_schema_check_wraps_generic_prompt_validation_exception(
    metadata_variant: Literal["schema_refs", "inline"],
):
    sdk = AsyncMock()
    sdk.files.filesets.retrieve.return_value = _build_dataset_metadata(
        metadata_variant,
        default_schema_kind="input",
        path_schema_kinds={"validation/a.jsonl": "input"},
    )
    sdk.files.list.return_value = _files_response("validation/a.jsonl")

    with mock.patch(
        "nmp.evaluator.api.v2.metrics.checks.validate_prompt_template_against_dataset_schema",
        side_effect=RuntimeError("prompt validation blew up"),
    ):
        result = await metric_dataset_schema_check(
            _metric_job("default/my-fileset#validation/*.jsonl"),
            _mock_metric_with_required_schema(INPUT_REQUIRED_SCHEMA),
            sdk,
        )

    assert result.status is False
    assert any("Invalid dataset schema metadata" in error for error in result.errors)
    assert any("prompt validation blew up" in error for error in result.errors)


@pytest.mark.asyncio
@pytest.mark.parametrize("metadata_variant", ["schema_refs", "inline"])
async def test_benchmark_creation_schema_check_wildcard_ignores_unmatched_incompatible_files(
    metadata_variant: Literal["schema_refs", "inline"],
):
    sdk = AsyncMock()
    sdk.files.filesets.retrieve.return_value = _build_dataset_metadata(
        metadata_variant,
        default_schema_kind="input",
        path_schema_kinds={
            "validation/a.jsonl": "input",
            "validation/b.jsonl": "input",
            "train/c.jsonl": "reference",
        },
    )
    sdk.files.list.return_value = _files_response(
        "validation/a.jsonl",
        "validation/b.jsonl",
        "train/c.jsonl",
    )

    result = await benchmark_creation_schema_check(
        FilesetRef(root="default/my-fileset#validation/*.jsonl"),
        [_mock_metric_with_required_schema(INPUT_REQUIRED_SCHEMA)],
        None,
        sdk,
    )

    assert result.status is True
    assert result.errors == []


@pytest.mark.asyncio
@pytest.mark.parametrize("metadata_variant", ["schema_refs", "inline"])
async def test_benchmark_creation_schema_check_wildcard_no_matches_returns_error(
    metadata_variant: Literal["schema_refs", "inline"],
):
    sdk = AsyncMock()
    sdk.files.filesets.retrieve.return_value = _build_dataset_metadata(
        metadata_variant,
        default_schema_kind="input",
        path_schema_kinds={},
    )
    sdk.files.list.return_value = _files_response("train/c.jsonl")

    result = await benchmark_creation_schema_check(
        FilesetRef(root="default/my-fileset#validation/*.jsonl"),
        [_mock_metric_with_required_schema(INPUT_REQUIRED_SCHEMA)],
        None,
        sdk,
    )

    assert result.status is False
    assert any("no matching files found in fileset" in error for error in result.errors)


@pytest.mark.asyncio
@pytest.mark.parametrize("metadata_variant", ["schema_refs", "inline"])
async def test_benchmark_creation_schema_check_wildcard_default_fallback_applies_to_unmapped_matched_path(
    metadata_variant: Literal["schema_refs", "inline"],
):
    sdk = AsyncMock()
    sdk.files.filesets.retrieve.return_value = _build_dataset_metadata(
        metadata_variant,
        default_schema_kind="reference",
        path_schema_kinds={
            "validation/a.jsonl": "input",
            # Outside selector and should be ignored.
            "train/c.jsonl": "input",
        },
    )
    sdk.files.list.return_value = _files_response(
        "validation/a.jsonl",
        "validation/b.jsonl",
        "train/c.jsonl",
    )

    result = await benchmark_creation_schema_check(
        FilesetRef(root="default/my-fileset#validation/*.jsonl"),
        [_mock_metric_with_required_schema(INPUT_REQUIRED_SCHEMA)],
        None,
        sdk,
    )

    assert result.status is False
    assert any("[validation/b.jsonl]" in error for error in result.errors)
    assert all("[train/c.jsonl]" not in error for error in result.errors)


@pytest.mark.asyncio
@pytest.mark.parametrize("metadata_variant", ["schema_refs", "inline"])
async def test_benchmark_creation_schema_check_exact_fragment_selects_only_exact_file(
    metadata_variant: Literal["schema_refs", "inline"],
):
    sdk = AsyncMock()
    sdk.files.filesets.retrieve.return_value = _build_dataset_metadata(
        metadata_variant,
        default_schema_kind="reference",
        path_schema_kinds={
            "validation/a.jsonl": "input",
            "validation/b.jsonl": "reference",
            "train/c.jsonl": "reference",
        },
    )
    sdk.files.list.return_value = _files_response(
        "validation/a.jsonl",
        "validation/b.jsonl",
        "train/c.jsonl",
    )

    result = await benchmark_creation_schema_check(
        FilesetRef(root="default/my-fileset#validation/a.jsonl"),
        [_mock_metric_with_required_schema(INPUT_REQUIRED_SCHEMA)],
        None,
        sdk,
    )

    assert result.status is True
    assert result.errors == []
    sdk.files.list.assert_not_awaited()


@pytest.mark.asyncio
async def test_benchmark_creation_schema_check_invalid_fileset_ref_format_returns_validation_error():
    sdk = AsyncMock()

    result = await benchmark_creation_schema_check(
        FilesetRef(root="my-fileset-without-workspace"),
        [_mock_metric_with_required_schema(INPUT_REQUIRED_SCHEMA)],
        None,
        sdk,
    )

    assert result.status is False
    assert any("Invalid dataset schema metadata" in error for error in result.errors)
    assert any("workspace/fileset-name" in error for error in result.errors)
    sdk.files.filesets.retrieve.assert_not_awaited()
    sdk.files.list.assert_not_awaited()


@pytest.mark.asyncio
async def test_benchmark_creation_schema_check_unknown_schema_ref_returns_invalid_metadata_error():
    sdk = AsyncMock()
    sdk.files.filesets.retrieve.return_value = SimpleNamespace(
        metadata=SimpleNamespace(
            dataset=SimpleNamespace(
                schema_="input_required",
                schemas_by_path={"validation/a.jsonl": "missing_schema"},
                schema_defs=SCHEMA_DEFS,
            )
        )
    )
    sdk.files.list.return_value = _files_response("validation/a.jsonl", "train/c.jsonl")

    result = await benchmark_creation_schema_check(
        FilesetRef(root="default/my-fileset#validation/*.jsonl"),
        [_mock_metric_with_required_schema(INPUT_REQUIRED_SCHEMA)],
        None,
        sdk,
    )

    assert result.status is False
    assert any("Invalid dataset schema metadata" in error for error in result.errors)
    assert any("unknown dataset schema reference" in error for error in result.errors)


@pytest.mark.asyncio
@pytest.mark.parametrize("metadata_variant", ["schema_refs", "inline"])
async def test_benchmark_job_schema_check_wildcard_prompt_validation_runs_for_matched_only(
    metadata_variant: Literal["schema_refs", "inline"],
):
    sdk = AsyncMock()
    sdk.files.filesets.retrieve.return_value = _build_dataset_metadata(
        metadata_variant,
        default_schema_kind="input",
        path_schema_kinds={
            "validation/a.jsonl": "input",
            "validation/b.jsonl": "input",
            "train/c.jsonl": "reference",
        },
    )
    sdk.files.list.return_value = _files_response(
        "validation/a.jsonl",
        "validation/b.jsonl",
        "train/c.jsonl",
    )
    benchmark = _benchmark_entity_with_input_metric("default/my-fileset#validation/*.jsonl")
    job = _benchmark_online_job()

    with mock.patch(
        "nmp.evaluator.api.v2.benchmarks.checks.validate_prompt_template_against_dataset_schema",
        return_value=[],
    ) as mock_prompt_check:
        result = await benchmark_job_schema_check(job, benchmark, sdk)

    assert result.status is True
    assert mock_prompt_check.call_count == 1


@pytest.mark.asyncio
@pytest.mark.parametrize("metadata_variant", ["schema_refs", "inline"])
async def test_benchmark_job_schema_check_prompt_validation_receives_optional_fields_and_ignored_roots(
    metadata_variant: Literal["schema_refs", "inline"],
):
    sdk = AsyncMock()
    sdk.files.filesets.retrieve.return_value = _build_dataset_metadata(
        metadata_variant,
        default_schema_kind="input",
        path_schema_kinds={
            "validation/a.jsonl": "input",
            "validation/b.jsonl": "input",
            "train/c.jsonl": "reference",
        },
    )
    sdk.files.list.return_value = _files_response(
        "validation/a.jsonl",
        "validation/b.jsonl",
        "train/c.jsonl",
    )
    benchmark = _benchmark_entity_with_input_metric("default/my-fileset#validation/*.jsonl")
    job = _benchmark_online_job(optional_fields=["reference", "sample.output_text"])

    with mock.patch(
        "nmp.evaluator.api.v2.benchmarks.checks.validate_prompt_template_against_dataset_schema",
        return_value=[],
    ) as mock_prompt_check:
        result = await benchmark_job_schema_check(job, benchmark, sdk)

    assert result.status is True
    assert mock_prompt_check.call_count == 1
    for call in mock_prompt_check.call_args_list:
        assert call.kwargs["ignored_roots"] == {"output", "output_text", "response"}
        assert call.kwargs["optional_fields"] == {"reference", "sample.output_text"}


@pytest.mark.asyncio
@pytest.mark.parametrize("metadata_variant", ["schema_refs", "inline"])
async def test_benchmark_job_schema_check_offline_job_skips_prompt_validation(
    metadata_variant: Literal["schema_refs", "inline"],
):
    sdk = AsyncMock()
    sdk.files.filesets.retrieve.return_value = _build_dataset_metadata(
        metadata_variant,
        default_schema_kind="input",
        path_schema_kinds={
            "validation/a.jsonl": "input",
            "validation/b.jsonl": "input",
        },
    )
    sdk.files.list.return_value = _files_response("validation/a.jsonl", "validation/b.jsonl")
    benchmark = _benchmark_entity_with_input_metric("default/my-fileset#validation/*.jsonl")

    with mock.patch(
        "nmp.evaluator.api.v2.benchmarks.checks.validate_prompt_template_against_dataset_schema",
        return_value=[],
    ) as mock_prompt_check:
        result = await benchmark_job_schema_check(_benchmark_offline_job(), benchmark, sdk)

    assert result.status is True
    mock_prompt_check.assert_not_called()


@pytest.mark.asyncio
@pytest.mark.parametrize("metadata_variant", ["schema_refs", "inline"])
async def test_benchmark_creation_schema_check_without_fragment_uses_default_schema(
    metadata_variant: Literal["schema_refs", "inline"],
):
    sdk = AsyncMock()
    sdk.files.filesets.retrieve.return_value = _build_dataset_metadata(
        metadata_variant,
        default_schema_kind="input",
        path_schema_kinds={"validation/a.jsonl": "reference"},
    )
    sdk.files.list.return_value = _files_response("validation/a.jsonl")

    result = await benchmark_creation_schema_check(
        FilesetRef(root="default/my-fileset"),
        [_mock_metric_with_required_schema(INPUT_REQUIRED_SCHEMA)],
        None,
        sdk,
    )

    assert result.status is True
    assert result.errors == []
    sdk.files.list.assert_not_awaited()


@pytest.mark.asyncio
@pytest.mark.parametrize("metadata_variant", ["schema_refs", "inline"])
async def test_benchmark_creation_schema_check_without_fragment_error_has_no_path_prefix(
    metadata_variant: Literal["schema_refs", "inline"],
):
    sdk = AsyncMock()
    sdk.files.filesets.retrieve.return_value = _build_dataset_metadata(
        metadata_variant,
        default_schema_kind="reference",
        path_schema_kinds={},
    )
    sdk.files.list.return_value = _files_response("validation/a.jsonl")

    result = await benchmark_creation_schema_check(
        FilesetRef(root="default/my-fileset"),
        [_mock_metric_with_required_schema(INPUT_REQUIRED_SCHEMA)],
        None,
        sdk,
    )

    assert result.status is False
    assert any("dataset schema missing required field 'input'" in error for error in result.errors)
    assert all("[" not in error for error in result.errors)
    sdk.files.list.assert_not_awaited()


@pytest.mark.asyncio
async def test_benchmark_creation_schema_check_returns_true_when_fileset_has_no_dataset_metadata():
    sdk = AsyncMock()
    sdk.files.filesets.retrieve.return_value = SimpleNamespace(metadata=SimpleNamespace(dataset=None))

    result = await benchmark_creation_schema_check(
        FilesetRef(root="default/my-fileset#validation/*.jsonl"),
        [_mock_metric_with_required_schema(INPUT_REQUIRED_SCHEMA)],
        None,
        sdk,
    )

    assert result.status is True
    assert result.errors == []
    sdk.files.list.assert_not_awaited()


@pytest.mark.asyncio
@pytest.mark.parametrize("metadata_variant", ["schema_refs", "inline"])
async def test_benchmark_job_schema_check_without_fragment_uses_default_schema(
    metadata_variant: Literal["schema_refs", "inline"],
):
    sdk = AsyncMock()
    sdk.files.filesets.retrieve.return_value = _build_dataset_metadata(
        metadata_variant,
        default_schema_kind="input",
        path_schema_kinds={"validation/a.jsonl": "reference"},
    )
    sdk.files.list.return_value = _files_response("validation/a.jsonl")
    benchmark = _benchmark_entity_with_input_metric("default/my-fileset")
    job = _benchmark_online_job()

    result = await benchmark_job_schema_check(job, benchmark, sdk)

    assert result.status is True
    assert result.errors == []
    sdk.files.list.assert_not_awaited()


@pytest.mark.asyncio
@pytest.mark.parametrize("metadata_variant", ["schema_refs", "inline"])
async def test_benchmark_job_schema_check_without_fragment_error_has_no_path_prefix(
    metadata_variant: Literal["schema_refs", "inline"],
):
    sdk = AsyncMock()
    sdk.files.filesets.retrieve.return_value = _build_dataset_metadata(
        metadata_variant,
        default_schema_kind="reference",
        path_schema_kinds={},
    )
    sdk.files.list.return_value = _files_response("validation/a.jsonl")
    benchmark = _benchmark_entity_with_input_metric("default/my-fileset")
    job = _benchmark_online_job()

    result = await benchmark_job_schema_check(job, benchmark, sdk)

    assert result.status is False
    assert any("dataset schema missing required field 'input'" in error for error in result.errors)
    assert all("[" not in error for error in result.errors)
    sdk.files.list.assert_not_awaited()


@pytest.mark.asyncio
async def test_benchmark_job_schema_check_returns_true_when_fileset_has_no_dataset_metadata():
    sdk = AsyncMock()
    sdk.files.filesets.retrieve.return_value = SimpleNamespace(metadata=SimpleNamespace(dataset=None))
    benchmark = _benchmark_entity_with_input_metric("default/my-fileset#validation/*.jsonl")
    job = _benchmark_online_job()

    result = await benchmark_job_schema_check(job, benchmark, sdk)

    assert result.status is True
    assert result.errors == []
    sdk.files.list.assert_not_awaited()


@pytest.mark.asyncio
async def test_benchmark_job_schema_check_validates_job_type_without_dataset_schema_metadata():
    sdk = AsyncMock()
    sdk.files.filesets.retrieve.return_value = SimpleNamespace(metadata=SimpleNamespace(dataset=None))
    benchmark = _benchmark_entity_with_input_metric("default/my-fileset#validation/*.jsonl")
    benchmark.metrics[0].supported_job_types = [app.SupportedJobTypes.OFFLINE]

    result = await benchmark_job_schema_check(_benchmark_online_job(), benchmark, sdk)

    assert result.status is False
    assert any("Benchmark does not support online jobs." in error for error in result.errors)
    sdk.files.filesets.retrieve.assert_not_awaited()
    sdk.files.list.assert_not_awaited()


@pytest.mark.asyncio
@pytest.mark.parametrize("metadata_variant", ["schema_refs", "inline"])
async def test_benchmark_job_schema_check_wildcard_prompt_error_has_matched_path_context_only(
    metadata_variant: Literal["schema_refs", "inline"],
):
    sdk = AsyncMock()
    sdk.files.filesets.retrieve.return_value = _build_dataset_metadata(
        metadata_variant,
        default_schema_kind="input",
        path_schema_kinds={
            "validation/a.jsonl": "input",
            "validation/b.jsonl": "input_extra",
            "train/c.jsonl": "reference",
        },
    )
    sdk.files.list.return_value = _files_response(
        "validation/a.jsonl",
        "validation/b.jsonl",
        "train/c.jsonl",
    )
    benchmark = _benchmark_entity_with_input_metric("default/my-fileset#validation/*.jsonl")
    job = _benchmark_online_job()

    with mock.patch(
        "nmp.evaluator.api.v2.benchmarks.checks.validate_prompt_template_against_dataset_schema",
        side_effect=[[], ["dataset schema missing required field 'input'"]],
    ):
        result = await benchmark_job_schema_check(job, benchmark, sdk)

    assert result.status is False
    assert any("[validation/b.jsonl]" in error for error in result.errors)
    assert all("[train/c.jsonl]" not in error for error in result.errors)


@pytest.mark.asyncio
@pytest.mark.parametrize("metadata_variant", ["schema_refs", "inline"])
async def test_benchmark_job_schema_check_exact_fragment_selects_only_exact_file(
    metadata_variant: Literal["schema_refs", "inline"],
):
    sdk = AsyncMock()
    sdk.files.filesets.retrieve.return_value = _build_dataset_metadata(
        metadata_variant,
        default_schema_kind="reference",
        path_schema_kinds={
            "validation/a.jsonl": "input",
            "validation/b.jsonl": "reference",
            "train/c.jsonl": "reference",
        },
    )
    sdk.files.list.return_value = _files_response(
        "validation/a.jsonl",
        "validation/b.jsonl",
        "train/c.jsonl",
    )
    benchmark = _benchmark_entity_with_input_metric("default/my-fileset#validation/a.jsonl")
    job = _benchmark_online_job()

    result = await benchmark_job_schema_check(job, benchmark, sdk)

    assert result.status is True
    assert result.errors == []
    sdk.files.list.assert_not_awaited()


@pytest.mark.asyncio
async def test_benchmark_job_schema_check_invalid_fileset_ref_format_returns_validation_error():
    sdk = AsyncMock()
    benchmark = _benchmark_entity_with_input_metric("my-fileset-without-workspace")
    job = _benchmark_online_job()

    result = await benchmark_job_schema_check(job, benchmark, sdk)

    assert result.status is False
    assert any("Invalid dataset schema metadata" in error for error in result.errors)
    assert any("workspace/fileset-name" in error for error in result.errors)
    sdk.files.filesets.retrieve.assert_not_awaited()
    sdk.files.list.assert_not_awaited()


@pytest.mark.asyncio
@pytest.mark.parametrize("metadata_variant", ["schema_refs", "inline"])
async def test_benchmark_job_schema_check_skips_prompt_validation_when_schema_fails(
    metadata_variant: Literal["schema_refs", "inline"],
):
    sdk = AsyncMock()
    sdk.files.filesets.retrieve.return_value = _build_dataset_metadata(
        metadata_variant,
        default_schema_kind="reference",
        path_schema_kinds={
            "validation/a.jsonl": "input",
            "validation/b.jsonl": "reference",
            "train/c.jsonl": "input",
        },
    )
    sdk.files.list.return_value = _files_response(
        "validation/a.jsonl",
        "validation/b.jsonl",
        "train/c.jsonl",
    )
    benchmark = _benchmark_entity_with_input_metric("default/my-fileset#validation/*.jsonl")
    job = _benchmark_online_job()

    with mock.patch(
        "nmp.evaluator.api.v2.benchmarks.checks.validate_prompt_template_against_dataset_schema",
        return_value=[],
    ) as mock_prompt_check:
        result = await benchmark_job_schema_check(job, benchmark, sdk)

    assert result.status is False
    assert any("[validation/b.jsonl]" in error for error in result.errors)
    assert all("[train/c.jsonl]" not in error for error in result.errors)
    mock_prompt_check.assert_not_called()


@pytest.mark.asyncio
async def test_benchmark_job_schema_check_unknown_schema_ref_returns_invalid_metadata_error():
    sdk = AsyncMock()
    sdk.files.filesets.retrieve.return_value = SimpleNamespace(
        metadata=SimpleNamespace(
            dataset=SimpleNamespace(
                schema_="input_required",
                schemas_by_path={"validation/a.jsonl": "missing_schema"},
                schema_defs=SCHEMA_DEFS,
            )
        )
    )
    sdk.files.list.return_value = _files_response("validation/a.jsonl", "train/c.jsonl")
    benchmark = _benchmark_entity("default/my-fileset#validation/*.jsonl")
    job = _benchmark_online_job()

    result = await benchmark_job_schema_check(job, benchmark, sdk)

    assert result.status is False
    assert any("Invalid dataset schema metadata" in error for error in result.errors)
    assert any("unknown dataset schema reference" in error for error in result.errors)


@pytest.mark.asyncio
@pytest.mark.parametrize("metadata_variant", ["schema_refs", "inline"])
async def test_benchmark_job_schema_check_wraps_template_schema_inference_error_from_prompt_validation(
    metadata_variant: Literal["schema_refs", "inline"],
):
    sdk = AsyncMock()
    sdk.files.filesets.retrieve.return_value = _build_dataset_metadata(
        metadata_variant,
        default_schema_kind="input",
        path_schema_kinds={"validation/a.jsonl": "input"},
    )
    sdk.files.list.return_value = _files_response("validation/a.jsonl")
    benchmark = _benchmark_entity_with_input_metric("default/my-fileset#validation/*.jsonl")
    job = _benchmark_online_job()

    with mock.patch(
        "nmp.evaluator.api.v2.benchmarks.checks.validate_prompt_template_against_dataset_schema",
        side_effect=TemplateSchemaInferenceError("unsupported benchmark prompt expression"),
    ):
        result = await benchmark_job_schema_check(job, benchmark, sdk)

    assert result.status is False
    assert any("Unsupported prompt template for schema inference" in error for error in result.errors)
    assert any("unsupported benchmark prompt expression" in error for error in result.errors)


@pytest.mark.asyncio
@pytest.mark.parametrize("metadata_variant", ["schema_refs", "inline"])
async def test_benchmark_job_schema_check_wraps_generic_prompt_validation_exception(
    metadata_variant: Literal["schema_refs", "inline"],
):
    sdk = AsyncMock()
    sdk.files.filesets.retrieve.return_value = _build_dataset_metadata(
        metadata_variant,
        default_schema_kind="input",
        path_schema_kinds={"validation/a.jsonl": "input"},
    )
    sdk.files.list.return_value = _files_response("validation/a.jsonl")
    benchmark = _benchmark_entity_with_input_metric("default/my-fileset#validation/*.jsonl")
    job = _benchmark_online_job()

    with mock.patch(
        "nmp.evaluator.api.v2.benchmarks.checks.validate_prompt_template_against_dataset_schema",
        side_effect=RuntimeError("benchmark prompt validation blew up"),
    ):
        result = await benchmark_job_schema_check(job, benchmark, sdk)

    assert result.status is False
    assert any("Invalid dataset schema metadata" in error for error in result.errors)
    assert any("benchmark prompt validation blew up" in error for error in result.errors)
