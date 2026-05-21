# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Compatibility re-exports for metric value types.

Metric value models now live in ``nemo_evaluator_sdk.values.metrics``.
This module is kept for backward compatibility with existing service imports.
"""

from typing import Annotated, Literal

from nemo_evaluator_sdk.enums import MetricType
from nemo_evaluator_sdk.metrics.types import MetricVariants
from nemo_evaluator_sdk.values import MetricBase, SupportedJobTypes
from pydantic import BaseModel, ConfigDict, Field, TypeAdapter


class Parameter(BaseModel):
    # This allows validation using both 'schema_' and 'schema'
    model_config = ConfigDict(populate_by_name=True)

    name: str = Field(description="Name of the parameter.")
    type: Literal["boolean", "string", "number", "integer", "object", "secret"] = Field(
        description="The value type of the parameter."
    )
    description: str | None = Field(default=None, description="Description of the parameter.")
    default: bool | str | float | int | None = Field(default=None, description="The default value of the parameter.")
    # Use schema_ internally, but 'schema' externally to avoid shadowing BaseModel.schema()
    schema_: dict | None = Field(
        default=None, alias="schema", description="The JSON schema for parameters with object type."
    )


class SystemMetric(MetricBase):
    """Metric entity for system metric that have pre-defined dataset."""

    type: Literal[MetricType.SYSTEM, MetricType.SYSTEM_RETRIEVER] = MetricType.SYSTEM
    name: str = Field("Metric name")
    required_params: list[Parameter] = Field(
        default_factory=list, description="List of required parameters for running an evaluation with the metric."
    )
    optional_params: list[Parameter] = Field(
        default_factory=list, description="List of optional parameters for running an evaluation with the metric."
    )
    supported_job_types: list[
        Literal[SupportedJobTypes.ONLINE, SupportedJobTypes.OFFLINE, SupportedJobTypes.RETRIEVER]
    ] = Field(
        default=[SupportedJobTypes.ONLINE],
        description="A metric can evaluate model outputs for online evaluations or pre-generated outputs for offline evaluations.",
    )


Metric = Annotated[
    MetricVariants | SystemMetric,
    Field(discriminator="type"),
]

MetricAdapter = TypeAdapter(Metric)
