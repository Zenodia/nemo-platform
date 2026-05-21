# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Mapper for converting between metric request DTOs and entity types."""

from typing import Type, TypeVar

import nmp.evaluator.entities as entities
from nemo_evaluator_sdk.values import MetricBase
from nmp.common.entities import EntityBase
from nmp.evaluator.api.v2.common.model_resolution import ResolvableModels, resolve_model
from nmp.evaluator.api.v2.metrics.schemas.metrics import Metric
from pydantic import TypeAdapter

# TypeAdapter for the discriminated Metric union - Pydantic automatically
# selects the correct type based on the 'type' field discriminator
_MetricEntityAdapter: TypeAdapter[entities.Metric] = TypeAdapter(entities.Metric)

SchemaT = TypeVar("SchemaT", bound=EntityBase)


class MetricMapper:
    """Maps between metric request DTOs and entity types."""

    @staticmethod
    async def request_to_entity(request: Metric | MetricBase, name: str, workspace: str) -> entities.Metric:
        """Convert a metric request DTO to an entity.

        Handles model resolution (ModelRef -> Model) via the ResolvableModels
        protocol and uses Pydantic's TypeAdapter to construct the appropriate
        entity type based on the discriminated union.

        Args:
            request: The metric request DTO
            name: Metric name (from path parameter)
            workspace: Workspace (from path parameter)

        Returns:
            The constructed metric entity
        """
        # Build the entity data from request, adding name/workspace
        data = request.model_dump(exclude_none=True)
        data["name"] = name
        data["workspace"] = workspace

        # Resolve ModelRef fields to Model using the protocol
        if isinstance(request, ResolvableModels):
            resolved = await request.resolve_models(resolve_model)
            data.update({k: v.model_dump(exclude_none=True) for k, v in resolved.items()})

        # Pydantic automatically selects the correct entity type based on 'type' discriminator
        return _MetricEntityAdapter.validate_python(data)

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

        resp = schema_cls.model_validate(data)
        resp._id = entity._id
        resp._created_at = entity._created_at
        resp._created_by = entity._created_by
        resp._updated_at = entity._updated_at
        resp._updated_by = entity._updated_by
        resp._parent = entity._parent
        return resp

    @staticmethod
    def entity_to_schema_via_adapter(entity: EntityBase, adapter: TypeAdapter[SchemaT]) -> SchemaT:
        """Validate an entity into a schema using a TypeAdapter, preserving base private attributes.

        Constructs the schema from the entity's model dump, then copies the private
        attributes managed by the entity store (_id, timestamps, _parent) from the
        source entity to the resulting schema.

        Args:
            entity: Source entity to serialize.
            adapter: TypeAdapter whose target type is bound to EntityBase.

        Returns:
            Schema instance with private attributes populated.
        """
        data = entity.model_dump(exclude_none=True)
        resp = adapter.validate_python(data)
        resp._id = entity._id
        resp._created_at = entity._created_at
        resp._created_by = entity._created_by
        resp._updated_at = entity._updated_at
        resp._updated_by = entity._updated_by
        resp._parent = entity._parent
        return resp
