# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Tests for EmbeddedEntityMixin in entities/utils.py."""

from datetime import datetime
from typing import ClassVar

from nmp.common.entities.client import EntityBase
from nmp.evaluator.entities.utils import EmbeddedEntityMixin
from pydantic import Field


class ChildEntity(EntityBase):
    """Simple entity for testing embedding."""

    value: str


class ParentWithMixin(EmbeddedEntityMixin, EntityBase):
    """Parent entity using the mixin."""

    __embedded_entity_fields__: ClassVar[dict[str, type]] = {"children": ChildEntity}

    children: list[ChildEntity]


class ParentWithoutEmbeddedFields(EmbeddedEntityMixin, EntityBase):
    """Parent entity with mixin but no embedded fields defined."""

    name_field: str


class TestEmbeddedEntityMixinSerialization:
    """Tests for _get_data_fields serialization."""

    def test_preserves_nested_entity_ids_during_serialization(self):
        """Nested entity IDs should be included in serialized data."""
        child = ChildEntity(name="child-1", workspace="default", value="test")
        child._id = "child-id-123"
        child._created_at = datetime(2024, 1, 15, 10, 30)
        child._updated_at = datetime(2024, 1, 15, 10, 30)

        parent = ParentWithMixin(name="parent-1", workspace="default", children=[child])

        data = parent._get_data_fields()

        assert "children" in data
        assert len(data["children"]) == 1
        assert data["children"][0]["id"] == "child-id-123"
        assert data["children"][0]["created_at"] == "2024-01-15T10:30:00"

    def test_excludes_top_level_computed_fields(self):
        """Top-level id/created_at/updated_at should not be in serialized data."""
        child = ChildEntity(name="child-1", workspace="default", value="test")
        parent = ParentWithMixin(name="parent-1", workspace="default", children=[child])
        parent._id = "parent-id-456"
        parent._created_at = datetime(2024, 1, 20)

        data = parent._get_data_fields()

        assert "id" not in data
        assert "created_at" not in data
        assert "updated_at" not in data
        assert "entity_id" not in data


class TestEmbeddedEntityMixinDeserialization:
    """Tests for _restore_embedded_entity_ids deserialization."""

    def test_restores_nested_entity_ids_from_dict(self):
        """IDs and timestamps should be restored to nested entities from dict data."""
        data = {
            "name": "parent-1",
            "workspace": "default",
            "children": [
                {
                    "name": "child-1",
                    "workspace": "default",
                    "value": "test",
                    "id": "restored-id-123",
                    "created_at": "2024-01-15T10:30:00",
                    "updated_at": "2024-01-15T11:00:00",
                }
            ],
        }

        parent = ParentWithMixin.model_validate(data)

        assert parent.children[0].id == "restored-id-123"
        assert parent.children[0].created_at == datetime(2024, 1, 15, 10, 30)
        assert parent.children[0].updated_at == datetime(2024, 1, 15, 11, 0)

    def test_handles_datetime_objects_in_nested_data(self):
        """Datetime objects (not strings) should be handled correctly."""
        data = {
            "name": "parent-1",
            "workspace": "default",
            "children": [
                {
                    "name": "child-1",
                    "workspace": "default",
                    "value": "test",
                    "id": "id-123",
                    "created_at": datetime(2024, 1, 15, 10, 30),
                    "updated_at": datetime(2024, 1, 15, 11, 0),
                }
            ],
        }

        parent = ParentWithMixin.model_validate(data)

        assert parent.children[0].created_at == datetime(2024, 1, 15, 10, 30)
        assert parent.children[0].updated_at == datetime(2024, 1, 15, 11, 0)

    def test_handles_missing_id_fields(self):
        """Validation should work when nested entities have no IDs."""
        data = {
            "name": "parent-1",
            "workspace": "default",
            "children": [
                {
                    "name": "child-1",
                    "workspace": "default",
                    "value": "test",
                    # No id, created_at, updated_at
                }
            ],
        }

        parent = ParentWithMixin.model_validate(data)

        assert parent.children[0].id == ""  # Default empty string
        assert parent.children[0].created_at is None

    def test_passes_through_entity_instances(self):
        """Already-validated entity instances should pass through unchanged."""
        child = ChildEntity(name="child-1", workspace="default", value="test")
        child._id = "existing-id"
        child._created_at = datetime(2024, 1, 15)

        parent = ParentWithMixin(name="parent-1", workspace="default", children=[child])

        assert parent.children[0].id == "existing-id"
        assert parent.children[0].created_at == datetime(2024, 1, 15)

    def test_handles_non_dict_input(self):
        """Non-dict input should pass through (edge case for model_validator)."""
        # When Pydantic passes already-validated instances, it may not be a dict
        child = ChildEntity(name="child-1", workspace="default", value="test")
        parent = ParentWithMixin(name="parent-1", workspace="default", children=[child])

        # Round-trip through model_validate with an instance
        parent2 = ParentWithMixin.model_validate(parent)
        assert parent2.name == "parent-1"

    def test_handles_empty_embedded_fields_config(self):
        """Entity with mixin but no __embedded_entity_fields__ should work."""
        data = {"name": "test", "workspace": "default", "name_field": "value"}

        entity = ParentWithoutEmbeddedFields.model_validate(data)

        assert entity.name == "test"
        assert entity.name_field == "value"

    def test_handles_missing_embedded_field_in_data(self):
        """Validation should work when embedded field is not in input data."""

        # Create a variant that has an optional children field
        class OptionalChildrenParent(EmbeddedEntityMixin, EntityBase):
            __embedded_entity_fields__: ClassVar[dict[str, type]] = {"children": ChildEntity}
            children: list[ChildEntity] = Field(default_factory=list)

        data = {"name": "parent-1", "workspace": "default"}

        parent = OptionalChildrenParent.model_validate(data)

        assert parent.children == []


class TestEmbeddedEntityMixinRoundTrip:
    """Tests for full serialization/deserialization round-trip."""

    def test_full_round_trip_preserves_nested_ids(self):
        """IDs should survive serialize -> store -> deserialize cycle."""
        # Create entity with nested IDs
        child = ChildEntity(name="child-1", workspace="default", value="test")
        child._id = "child-id-abc"
        child._created_at = datetime(2024, 1, 15, 10, 30)
        child._updated_at = datetime(2024, 1, 15, 10, 30)

        parent = ParentWithMixin(name="parent-1", workspace="default", children=[child])

        # Simulate what EntityClient does: serialize
        data = parent._get_data_fields()

        # Simulate store response (store adds parent's own id/timestamps)
        store_response = {
            **data,
            "name": "parent-1",
            "workspace": "default",
            "id": "parent-id-xyz",
            "created_at": "2024-01-20T12:00:00",
            "updated_at": "2024-01-20T12:00:00",
        }

        # Deserialize
        reconstructed = ParentWithMixin.model_validate(store_response)

        # Verify nested IDs preserved
        assert reconstructed.children[0].id == "child-id-abc"
        assert reconstructed.children[0].created_at == datetime(2024, 1, 15, 10, 30)
        assert reconstructed.children[0].name == "child-1"
        assert reconstructed.children[0].value == "test"
