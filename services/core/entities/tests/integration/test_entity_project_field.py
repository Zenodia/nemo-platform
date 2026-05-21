# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Integration tests for entity project field."""

import pytest
from httpx import AsyncClient


@pytest.mark.integration
@pytest.mark.asyncio
class TestEntityProjectField:
    """Test project field on entities."""

    async def _create_project(self, client: AsyncClient, name: str) -> None:
        """Helper to create a project in the default workspace."""
        response = await client.post(
            "/apis/entities/v2/workspaces/default/projects",
            json={"name": name, "description": f"Test project {name}"},
        )
        assert response.status_code == 201, f"Failed to create project: {response.text}"

    async def test_create_entity_with_project(self, client: AsyncClient, ctx):
        """Test creating an entity with a project field."""
        # First create the project
        await self._create_project(client, "ml-project")

        response = await client.post(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            json={
                "name": "test-config",
                "project": "ml-project",
                "data": {
                    "target_id": "llama-2-7b",
                },
            },
        )

        assert response.status_code == 201
        result = response.json()
        assert result["project"] == "ml-project"

    async def test_create_entity_without_project(self, client: AsyncClient, ctx):
        """Test creating an entity without a project field (should be None)."""
        response = await client.post(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            json={
                "name": "test-config-no-project",
                "data": {
                    "target_id": "llama-2-7b",
                },
            },
        )

        assert response.status_code == 201
        result = response.json()
        assert result["project"] is None

    async def test_create_entity_with_nonexistent_project_fails(self, client: AsyncClient, ctx):
        """Test that creating an entity with a non-existent project fails."""
        response = await client.post(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            json={
                "name": "test-config-bad-project",
                "project": "nonexistent-project",
                "data": {
                    "target_id": "llama-2-7b",
                },
            },
        )

        assert response.status_code == 422
        result = response.json()
        assert "nonexistent-project" in result["detail"]
        assert "does not exist" in result["detail"]

    async def test_update_entity_with_project(self, client: AsyncClient, ctx):
        """Test updating an entity's project field."""
        # First create the project
        await self._create_project(client, "new-project")

        await client.post(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            json={
                "name": "update-project-test",
                "data": {"target_id": "llama-2-7b"},
            },
        )

        response = await client.put(
            "/apis/entities/v2/workspaces/default/entities/customization_config/update-project-test",
            json={
                "project": "new-project",
                "data": {"target_id": "llama-2-7b"},
            },
        )

        assert response.status_code == 200
        result = response.json()
        assert result["project"] == "new-project"

    async def test_update_entity_with_nonexistent_project_fails(self, client: AsyncClient, ctx):
        """Test that updating an entity with a non-existent project fails."""
        await client.post(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            json={
                "name": "update-bad-project-test",
                "data": {"target_id": "llama-2-7b"},
            },
        )

        response = await client.put(
            "/apis/entities/v2/workspaces/default/entities/customization_config/update-bad-project-test",
            json={
                "project": "nonexistent-project",
                "data": {"target_id": "llama-2-7b"},
            },
        )

        assert response.status_code == 422
        result = response.json()
        assert "nonexistent-project" in result["detail"]
        assert "does not exist" in result["detail"]

    async def test_get_entity_returns_project(self, client: AsyncClient, ctx):
        """Test that getting an entity returns the project field."""
        # First create the project
        await self._create_project(client, "test-project")

        await client.post(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            json={
                "name": "get-project-test",
                "project": "test-project",
                "data": {"target_id": "llama-2-7b"},
            },
        )

        response = await client.get(
            "/apis/entities/v2/workspaces/default/entities/customization_config/get-project-test"
        )

        assert response.status_code == 200
        result = response.json()
        assert result["project"] == "test-project"

    async def test_list_entities_returns_project(self, client: AsyncClient, ctx):
        """Test that listing entities includes the project field."""
        # First create the project
        await self._create_project(client, "listed-project")

        await client.post(
            "/apis/entities/v2/workspaces/default/entities/customization_config",
            json={
                "name": "list-project-test",
                "project": "listed-project",
                "data": {"target_id": "llama-2-7b"},
            },
        )

        response = await client.get("/apis/entities/v2/workspaces/default/entities/customization_config")

        assert response.status_code == 200
        result = response.json()
        assert len(result["data"]) >= 1
        entity = next(e for e in result["data"] if e["name"] == "list-project-test")
        assert entity["project"] == "listed-project"
