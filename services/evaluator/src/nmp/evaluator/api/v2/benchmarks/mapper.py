# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

from typing import Type, TypeVar

import nmp.evaluator.entities as entities
from nmp.common.entities.client import EntityBase
from nmp.evaluator.api.v2.benchmarks.schemas.benchmarks import (
    Benchmark,
    BenchmarkRequest,
)
from nmp.evaluator.app.values import MetricRef

SchemaT = TypeVar("SchemaT", bound=EntityBase)


class BenchmarkMapper:
    @staticmethod
    def request_to_entity(
        benchmark: BenchmarkRequest, workspace: str, metrics: list[entities.Metric]
    ) -> entities.Benchmark:
        # Metrics are already validated EntityBase instances with IDs - use them directly
        return entities.Benchmark(
            name=benchmark.name,
            workspace=workspace,
            description=benchmark.description,
            metrics=metrics,
            dataset=benchmark.dataset,
            field_mapping=benchmark.field_mapping,
            labels=benchmark.labels,
        )

    @staticmethod
    def entity_to_schema(entity: EntityBase, schema_cls: Type[SchemaT]) -> SchemaT:
        """Validate an entity into a schema class, preserving base private attributes.

        Constructs the schema from the entity's model dump, then copies the private
        attributes managed by the entity store (_id, timestamps, _parent) from the
        source entity to the resulting schema.

        Args:
            entity: Source entity to serialize.
            schema_cls: Target schema class to validate into.

        Returns:
            Schema instance with private attributes populated.
        """
        data = entity.model_dump(exclude_none=True)

        if isinstance(entity, entities.Benchmark) and issubclass(schema_cls, Benchmark):
            # Special handling for Benchmark which maps metric to metric references
            metrics = [MetricRef(root=f"{metric.workspace}/{metric.name}") for metric in entity.metrics]
            data.update({"metrics": metrics})

        resp = schema_cls.model_validate(data)
        resp._id = entity._id
        resp._created_at = entity._created_at
        resp._created_by = entity._created_by
        resp._updated_at = entity._updated_at
        resp._updated_by = entity._updated_by
        resp._parent = entity._parent
        return resp
