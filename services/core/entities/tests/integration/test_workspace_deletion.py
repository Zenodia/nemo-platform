# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Integration tests for workspace deletion behavior in entity API."""

from unittest.mock import AsyncMock, MagicMock

import pytest
from httpx import AsyncClient
from nmp.common.auth import get_auth_client
from nmp.common.auth.client import AuthClient
from nmp.common.auth.models import Principal
from nmp.core.entities.api.server import app
from nmp.core.entities.app.repository import WorkspaceRepositoryInterface
from nmp.core.entities.entities import WorkspaceDeletionStage


def _create_service_principal_auth_client() -> AuthClient:
    """Create a mock AuthClient for service principal testing."""
    principal = Principal(
        id="service:entities",
        email=None,
        groups=[],
        on_behalf_of=None,
    )
    auth_client = MagicMock(spec=AuthClient)
    auth_client.principal = principal
    auth_client.auth_enabled = False
    auth_client.wait_role = AsyncMock(return_value=True)
    auth_client.has_permissions = AsyncMock(return_value=True)
    auth_client.on_behalf_of_has_permissions = AsyncMock(return_value=True)
    return auth_client


@pytest.mark.integration
@pytest.mark.asyncio
class TestWorkspaceDeletionBehavior:
    """Test entity API behavior when workspaces are being deleted."""

    async def test_user_cannot_create_entity_in_deleting_workspace(self, client: AsyncClient, ctx, repos):
        """Test that users get 404 when creating entities in a workspace being deleted."""
        workspace_name = "test-deleting-ws"

        # Create a workspace
        response = await client.post(
            "/apis/entities/v2/workspaces",
            json={"name": workspace_name, "description": "Test workspace"},
        )
        assert response.status_code == 201

        # Mark workspace for deletion
        workspace_repo: WorkspaceRepositoryInterface = repos["workspace"]
        await workspace_repo.mark_workspace_for_deletion(
            name=workspace_name,
            deletion_stage=WorkspaceDeletionStage.PENDING,
        )

        # Try to create an entity - should get 404
        response = await client.post(
            f"/apis/entities/v2/workspaces/{workspace_name}/entities/customization_config",
            json={"name": "test-config", "data": {"target_id": "llama-2-7b"}},
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    async def test_user_cannot_get_entity_in_deleting_workspace(self, client: AsyncClient, ctx, repos):
        """Test that users get 404 when getting entities from a workspace being deleted."""
        workspace_name = "test-deleting-ws2"

        # Create a workspace and an entity
        response = await client.post(
            "/apis/entities/v2/workspaces",
            json={"name": workspace_name, "description": "Test workspace"},
        )
        assert response.status_code == 201

        response = await client.post(
            f"/apis/entities/v2/workspaces/{workspace_name}/entities/customization_config",
            json={"name": "test-config", "data": {"target_id": "llama-2-7b"}},
        )
        assert response.status_code == 201

        # Mark workspace for deletion
        workspace_repo: WorkspaceRepositoryInterface = repos["workspace"]
        await workspace_repo.mark_workspace_for_deletion(
            name=workspace_name,
            deletion_stage=WorkspaceDeletionStage.DELETING,
        )

        # Try to get the entity - should get 404
        response = await client.get(
            f"/apis/entities/v2/workspaces/{workspace_name}/entities/customization_config/test-config"
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    async def test_user_cannot_update_entity_in_deleting_workspace(self, client: AsyncClient, ctx, repos):
        """Test that users get 404 when updating entities in a workspace being deleted."""
        workspace_name = "test-deleting-ws3"

        # Create a workspace and an entity
        response = await client.post(
            "/apis/entities/v2/workspaces",
            json={"name": workspace_name, "description": "Test workspace"},
        )
        assert response.status_code == 201

        response = await client.post(
            f"/apis/entities/v2/workspaces/{workspace_name}/entities/customization_config",
            json={"name": "test-config", "data": {"target_id": "llama-2-7b"}},
        )
        assert response.status_code == 201

        # Mark workspace for deletion
        workspace_repo: WorkspaceRepositoryInterface = repos["workspace"]
        await workspace_repo.mark_workspace_for_deletion(
            name=workspace_name,
            deletion_stage=WorkspaceDeletionStage.FAILED,
        )

        # Try to update the entity - should get 404
        response = await client.put(
            f"/apis/entities/v2/workspaces/{workspace_name}/entities/customization_config/test-config",
            json={"data": {"target_id": "llama-3-8b"}},
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    async def test_user_cannot_delete_entity_in_deleting_workspace(self, client: AsyncClient, ctx, repos):
        """Test that users get 404 when deleting entities from a workspace being deleted."""
        workspace_name = "test-deleting-ws4"

        # Create a workspace and an entity
        response = await client.post(
            "/apis/entities/v2/workspaces",
            json={"name": workspace_name, "description": "Test workspace"},
        )
        assert response.status_code == 201

        response = await client.post(
            f"/apis/entities/v2/workspaces/{workspace_name}/entities/customization_config",
            json={"name": "test-config", "data": {"target_id": "llama-2-7b"}},
        )
        assert response.status_code == 201

        # Mark workspace for deletion
        workspace_repo: WorkspaceRepositoryInterface = repos["workspace"]
        await workspace_repo.mark_workspace_for_deletion(
            name=workspace_name,
            deletion_stage=WorkspaceDeletionStage.PENDING,
        )

        # Try to delete the entity - should get 404
        response = await client.delete(
            f"/apis/entities/v2/workspaces/{workspace_name}/entities/customization_config/test-config"
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    async def test_user_cannot_list_entities_in_deleting_workspace(self, client: AsyncClient, ctx, repos):
        """Test that users get 404 when listing entities in a workspace being deleted."""
        workspace_name = "test-deleting-ws5"

        # Create a workspace and an entity
        response = await client.post(
            "/apis/entities/v2/workspaces",
            json={"name": workspace_name, "description": "Test workspace"},
        )
        assert response.status_code == 201

        response = await client.post(
            f"/apis/entities/v2/workspaces/{workspace_name}/entities/customization_config",
            json={"name": "test-config", "data": {"target_id": "llama-2-7b"}},
        )
        assert response.status_code == 201

        # Mark workspace for deletion
        workspace_repo: WorkspaceRepositoryInterface = repos["workspace"]
        await workspace_repo.mark_workspace_for_deletion(
            name=workspace_name,
            deletion_stage=WorkspaceDeletionStage.DELETING,
        )

        # Try to list entities - should get 404
        response = await client.get(f"/apis/entities/v2/workspaces/{workspace_name}/entities/customization_config")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    async def test_service_principal_can_access_deleting_workspace(self, client: AsyncClient, ctx, repos):
        """Test that service principals can access entities in workspaces being deleted."""
        workspace_name = "test-deleting-ws6"

        # Create a workspace and an entity
        response = await client.post(
            "/apis/entities/v2/workspaces",
            json={"name": workspace_name, "description": "Test workspace"},
        )
        assert response.status_code == 201

        response = await client.post(
            f"/apis/entities/v2/workspaces/{workspace_name}/entities/customization_config",
            json={"name": "test-config", "data": {"target_id": "llama-2-7b"}},
        )
        assert response.status_code == 201

        # Mark workspace for deletion
        workspace_repo: WorkspaceRepositoryInterface = repos["workspace"]
        await workspace_repo.mark_workspace_for_deletion(
            name=workspace_name,
            deletion_stage=WorkspaceDeletionStage.DELETING,
        )

        # Override auth client with service principal
        app.dependency_overrides[get_auth_client] = _create_service_principal_auth_client

        try:
            # Service principal should be able to list entities
            response = await client.get(f"/apis/entities/v2/workspaces/{workspace_name}/entities/customization_config")
            assert response.status_code == 200
            entities = response.json()
            assert entities["pagination"]["total_results"] == 1

            # Service principal should be able to get entity
            response = await client.get(
                f"/apis/entities/v2/workspaces/{workspace_name}/entities/customization_config/test-config"
            )
            assert response.status_code == 200
            assert response.json()["name"] == "test-config"

            # Service principal should be able to update entity
            response = await client.put(
                f"/apis/entities/v2/workspaces/{workspace_name}/entities/customization_config/test-config",
                json={"data": {"target_id": "llama-3-8b"}},
            )
            assert response.status_code == 200
            assert response.json()["data"]["target_id"] == "llama-3-8b"

            # Service principal should be able to delete entity
            response = await client.delete(
                f"/apis/entities/v2/workspaces/{workspace_name}/entities/customization_config/test-config"
            )
            assert response.status_code == 200

            # Service principal should be able to create entity
            response = await client.post(
                f"/apis/entities/v2/workspaces/{workspace_name}/entities/customization_config",
                json={"name": "new-config", "data": {"target_id": "llama-2-7b"}},
            )
            assert response.status_code == 201
        finally:
            # Clean up override
            app.dependency_overrides.clear()
