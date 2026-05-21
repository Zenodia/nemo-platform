# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Prechecks for metric job validation."""

import asyncio
import logging
from typing import Any

import nmp.evaluator.app.values as app
from nemo_platform import AsyncNeMoPlatform
from nmp.evaluator.api.v2.common.checks import (
    ValidationResult,
    collect_schema_target_errors,
    format_model_reachability_error,
    mapping_hint,
    prompt_hint,
    schema_error_message,
    validation_result_from_exception,
)
from nmp.evaluator.api.v2.metrics.schemas.jobs import MetricJob
from nmp.evaluator.app.dataset_schemas import (
    TemplateSchemaInferenceError,
    group_schema_resolution_targets,
    prune_schema_properties,
    resolve_dataset_schema_targets,
    runtime_available_evaluator_fields,
    validate_dataset_schema_requirement,
    validate_prompt_template_against_dataset_schema,
)
from nmp.evaluator.app.values import Dataset as DatasetValue

log = logging.getLogger(__name__)


async def job_fileset_exists_check(job: MetricJob, sdk: AsyncNeMoPlatform) -> ValidationResult:
    """Check if the fileset dataset exists using the fileset API.

    Args:
        job: The metric job input to validate.
        sdk: SDK instance with request-scoped user context. Required and must be obtained
             from Depends(get_sdk_client) in API endpoints to ensure proper user context.

    Returns:
        ValidationResult indicating if the fileset exists.
    """
    # Lazy imports to avoid slow startup (SDK imports kubernetes, etc.)
    from nmp.evaluator.app.datasets.nmp_datasets.fileset import dataset_exists as fileset_exists

    # Check if job has a dataset attribute
    dataset: DatasetValue | None = getattr(job, "dataset", None)
    if dataset is None:
        return ValidationResult(True)

    log.info(f"job_fileset_exists_check: dataset type={type(dataset).__name__}, value={dataset}")

    try:
        exists = await fileset_exists(sdk, dataset)
        if not exists:
            return ValidationResult(False, ["Dataset does not exist in fileset."])
    except Exception as e:
        return ValidationResult(False, [f"Error checking fileset existence: {e}"])

    return ValidationResult(True)


def _to_dict(value: Any) -> dict | None:
    """Convert a value to a dict (Pydantic model or dict)."""
    if value is None:
        return None

    if hasattr(value, "model_dump"):
        dumped = value.model_dump()
        return dumped if isinstance(dumped, dict) else None
    if isinstance(value, dict):
        return value

    return None


def _extract_model_dict(value: Any) -> dict | None:
    """Extract a model dictionary from a value (Pydantic model or dict)."""
    value_dict = _to_dict(value)
    if value_dict and isinstance(value_dict, dict) and "url" in value_dict and "name" in value_dict:
        return value_dict
    return None


def _extract_model_from_metric(job: MetricJob) -> dict | None:
    """Extract model dictionary from job.metric (for inline LLM Judge metrics and other metrics with models)."""
    metric = getattr(job, "metric", None)
    if metric is None:
        return None

    # Try to access model attribute directly (for Pydantic models like app.LLMJudgeMetric)
    metric_model = getattr(metric, "model", None)

    # If not found as attribute, try accessing from dict representation
    if metric_model is None:
        metric_dict = _to_dict(metric)
        if metric_dict:
            metric_model = metric_dict.get("model")

    # If still no model found, this metric doesn't have a model field
    if metric_model is None:
        return None

    # Extract model dict (handles both Model objects and dicts)
    model_dict = _extract_model_dict(metric_model)
    if model_dict:
        log.debug(
            f"_extract_model_from_metric: Found model in job.metric: {model_dict.get('name', 'unknown')} at {model_dict.get('url', 'unknown')}"
        )
    return model_dict


def _extract_judge_model_from_params(job: MetricJob) -> dict | None:
    """Extract judge model dictionary from job.metric_params."""
    metric_params = getattr(job, "metric_params", None)
    if not metric_params or not isinstance(metric_params, dict):
        return None

    judge = metric_params.get("judge")
    if not judge or not isinstance(judge, dict):
        return None

    judge_model = judge.get("model")
    return _extract_model_dict(judge_model)


async def job_model_check(job: MetricJob, workspace: str, sdk: AsyncNeMoPlatform) -> ValidationResult:
    """Check if models in a metric job are reachable.

    Args:
        job: The metric job input to validate.
        workspace: Workspace for resolving secrets.
        sdk: SDK instance with request-scoped user context. Required and must be obtained
             from Depends(get_sdk_client) in API endpoints to ensure proper user context.

    Returns:
        ValidationResult indicating if all models are reachable.
    """

    models_to_check: list[tuple[str, dict]] = []

    # Check job.model if present (for online/RAG jobs)
    model = getattr(job, "model", None)
    model_dict = _extract_model_dict(model)
    if model_dict:
        models_to_check.append(("job.model", model_dict))

    # Check job.metric.model if present (for inline LLM Judge metrics and other metrics with models)
    metric_model_dict = _extract_model_from_metric(job)
    if metric_model_dict:
        log.info(f"job_model_check: Found model in job.metric.model: {metric_model_dict.get('name', 'unknown')}")
        models_to_check.append(("job.metric.model", metric_model_dict))
    else:
        metric = getattr(job, "metric", None)
        if metric:
            log.debug(
                f"job_model_check: No model found in job.metric. Metric type: {type(metric).__name__}, metric: {metric}"
            )

    # Check metric_params.judge.model if present (for metrics requiring judge)
    judge_model_dict = _extract_judge_model_from_params(job)
    if judge_model_dict:
        models_to_check.append(("metric_params.judge.model", judge_model_dict))

    if not models_to_check:
        return ValidationResult(True)

    # Check all models in parallel, resolving secrets before checking reachability
    from nmp.evaluator.app.inference import verify_model_reachable

    results = await asyncio.gather(
        *[verify_model_reachable(model_dict, sdk=sdk, workspace=workspace) for _, model_dict in models_to_check],
        return_exceptions=True,
    )
    errors = []
    for (name, model_dict), result in zip(models_to_check, results, strict=True):
        # Only treat Exceptions as errors; successful responses are dicts
        if isinstance(result, Exception):
            errors.append(format_model_reachability_error(name, model_dict, result))

    if errors:
        return ValidationResult(False, errors)
    return ValidationResult(True)


async def metric_dataset_schema_check(
    job: MetricJob,
    metric: app.Metric,
    sdk: AsyncNeMoPlatform,
) -> ValidationResult:
    """Validate that the dataset schema is compatible with the metric requirements."""
    dataset = getattr(job, "dataset", None)
    if dataset is None:
        return ValidationResult(True)

    try:
        dataset_targets = await resolve_dataset_schema_targets(dataset, sdk)
    except Exception as e:
        return validation_result_from_exception("Invalid dataset schema metadata", e)
    if not dataset_targets:
        return ValidationResult(True)
    dataset_targets = group_schema_resolution_targets(dataset_targets)

    job_type = job.__job_type__
    field_mapping = getattr(job, "field_mapping", app.FieldMapping())
    metric_errors: list[str] = []
    prompt_errors: list[str] = []

    try:
        input_schema = metric.input_schema()
        required_schema = prune_schema_properties(
            input_schema.schema_,
            runtime_available_evaluator_fields(job_type),
        )
    except TemplateSchemaInferenceError as e:
        return validation_result_from_exception("Unsupported metric prompt template for schema inference", e)
    except Exception as e:
        return validation_result_from_exception("Invalid dataset schema metadata", e)

    def validate_metric_schema(dataset_schema: dict | None) -> ValidationResult:
        if dataset_schema is None:
            return ValidationResult(True)
        errors = validate_dataset_schema_requirement(dataset_schema, required_schema, field_mapping)
        return ValidationResult(not errors, errors)

    try:
        metric_errors.extend(collect_schema_target_errors(dataset_targets, validate_metric_schema))
    except Exception as e:
        return validation_result_from_exception("Invalid dataset schema metadata", e)

    prompt_template = getattr(job, "prompt_template", None)
    optional_fields = set(getattr(job, "optional_fields", None) or [])
    if prompt_template is not None:

        def validate_prompt_schema(dataset_schema: dict | None) -> ValidationResult:
            if dataset_schema is None:
                return ValidationResult(True)
            errors = validate_prompt_template_against_dataset_schema(
                dataset_schema,
                prompt_template,
                field_mapping,
                ignored_roots=runtime_available_evaluator_fields(job_type),
                optional_fields=optional_fields,
            )
            return ValidationResult(not errors, errors)

        try:
            prompt_errors.extend(collect_schema_target_errors(dataset_targets, validate_prompt_schema))
        except TemplateSchemaInferenceError as e:
            return validation_result_from_exception("Unsupported prompt template for schema inference", e)
        except Exception as e:
            return validation_result_from_exception("Invalid dataset schema metadata", e)

    if metric_errors or prompt_errors:
        metric_name = getattr(metric, "name", None) or getattr(metric, "type", "metric")
        errors: list[str] = []
        if metric_errors:
            errors.append(
                schema_error_message(
                    f"Dataset schema is incompatible with metric '{metric_name}'",
                    metric_errors,
                    hint=mapping_hint(field_mapping),
                )
            )
        if prompt_errors:
            errors.append(
                schema_error_message(
                    "Dataset schema is incompatible with the job prompt template",
                    prompt_errors,
                    hint=prompt_hint(field_mapping),
                )
            )
        return ValidationResult(
            False,
            errors,
        )
    return ValidationResult(True)
