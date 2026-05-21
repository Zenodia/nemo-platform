# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Service-local dataset schema helpers for evaluator validation and fileset metadata."""

from __future__ import annotations

from nemo_evaluator_sdk.dataset_schemas.common import (
    SchemaCompatibilityError,
    TemplateSchemaInferenceError,
    validate_json_schema,
)
from nemo_evaluator_sdk.dataset_schemas.compatibility import (
    apply_column_mapping_to_row,
    check_dataset_schema_compatibility,
    merge_metric_required_schemas,
    project_dataset_schema_for_column_mapping,
    prune_schema_properties,
    validate_dataset_schema_requirement,
    validate_prompt_template_against_dataset_schema,
)
from nemo_evaluator_sdk.dataset_schemas.templates import infer_required_schema_from_template
from nemo_evaluator_sdk.values.dataset_schemas import FieldMapping, InputSchema
from nmp.evaluator.app.dataset_schemas.filesets import (
    parse_fileset_ref_path,
    resolve_schema_entry,
    select_schema_for_path,
)
from nmp.evaluator.app.dataset_schemas.resolution import (
    group_schema_resolution_targets,
    resolve_dataset_schema,
    resolve_dataset_schema_targets,
    runtime_available_evaluator_fields,
)

__all__ = [
    "FieldMapping",
    "InputSchema",
    "SchemaCompatibilityError",
    "TemplateSchemaInferenceError",
    "apply_column_mapping_to_row",
    "check_dataset_schema_compatibility",
    "group_schema_resolution_targets",
    "infer_required_schema_from_template",
    "merge_metric_required_schemas",
    "parse_fileset_ref_path",
    "project_dataset_schema_for_column_mapping",
    "prune_schema_properties",
    "resolve_dataset_schema",
    "resolve_dataset_schema_targets",
    "resolve_schema_entry",
    "runtime_available_evaluator_fields",
    "select_schema_for_path",
    "validate_dataset_schema_requirement",
    "validate_json_schema",
    "validate_prompt_template_against_dataset_schema",
]
