# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

from datetime import datetime
from typing import Any, ClassVar

from pydantic import TypeAdapter, model_validator


class EmbeddedEntityMixin:
    """Mixin for entities that contain embedded EntityBase instances.

    This mixin overrides serialization and deserialization behavior to preserve
    computed fields (id, created_at, updated_at) on nested EntityBase instances.

    Without this mixin, nested entities lose their IDs and timestamps when stored
    because EntityBase uses computed fields backed by PrivateAttr, and the default
    _get_data_fields() uses exclude_computed_fields=True which strips these from
    ALL nested models.

    Usage:
        class MyEntity(EmbeddedEntityMixin, EntityBase):
            __embedded_entity_fields__: ClassVar[dict[str, type]] = {
                'items': ItemType,  # field_name -> union type or entity type
            }
            items: list[ItemType]
    """

    # Subclasses must define this mapping of field_name -> type for embedded entities
    __embedded_entity_fields__: ClassVar[dict[str, type]] = {}

    def _get_data_fields(self) -> dict[str, Any]:
        """Override to preserve nested entity computed fields during serialization.

        Uses exclude_computed_fields=False but explicitly excludes top-level computed
        fields by name, so nested entity IDs/timestamps are preserved.
        """
        model_dump = getattr(self, "model_dump", None)
        if not callable(model_dump):
            return {}

        base_fields = getattr(self, "__base_fields__", set())
        private_attributes = getattr(self, "__private_attributes__", {})
        base_private_attrs = getattr(self, "__base_private_attrs__", set())

        # Exclude top-level computed fields by name instead of using exclude_computed_fields=True
        exclude_set = set(base_fields) | {"id", "created_at", "updated_at", "entity_id", "parent"}
        data = {k: v for k, v in model_dump(exclude=exclude_set, exclude_computed_fields=False, mode="json").items()}
        # Include non-base PrivateAttr fields
        for field_name in private_attributes:
            if field_name not in base_private_attrs:
                data[field_name] = getattr(self, field_name)
        return data

    @model_validator(mode="before")
    @classmethod
    def _restore_embedded_entity_ids(cls, data: dict[str, Any]) -> dict[str, Any]:
        """Restore IDs and timestamps to embedded entities during deserialization.

        When data comes back from the entity store, nested entities are dicts with
        id/created_at/updated_at fields. This validator extracts those fields,
        validates the entity, then sets the private attrs so the computed fields work.
        """
        if not isinstance(data, dict):
            return data

        embedded_fields = getattr(cls, "__embedded_entity_fields__", {})
        if not embedded_fields:
            return data

        for field_name, field_type in embedded_fields.items():
            if field_name not in data:
                continue

            field_value = data[field_name]
            if not isinstance(field_value, list):
                continue

            restored_items = []
            for item in field_value:
                if isinstance(item, dict):
                    # Extract entity fields before validation
                    entity_id = item.pop("id", None)
                    created_at = item.pop("created_at", None)
                    updated_at = item.pop("updated_at", None)

                    # Validate the entity using TypeAdapter (works with Annotated unions)
                    adapter = TypeAdapter(field_type)
                    entity = adapter.validate_python(item)

                    # Restore the entity fields to private attrs
                    if entity_id:
                        entity._id = entity_id
                    if created_at:
                        entity._created_at = (
                            datetime.fromisoformat(created_at) if isinstance(created_at, str) else created_at
                        )
                    if updated_at:
                        entity._updated_at = (
                            datetime.fromisoformat(updated_at) if isinstance(updated_at, str) else updated_at
                        )

                    restored_items.append(entity)
                else:
                    # Already an entity instance, pass through
                    restored_items.append(item)

            data[field_name] = restored_items

        return data
