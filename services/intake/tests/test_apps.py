# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Tests for Apps API endpoints."""

import pytest
from fastapi.testclient import TestClient


class TestAppsAPI:
    """Tests for Apps API endpoints."""

    def test_create_app(self, client: TestClient):
        """Test creating a new app."""
        response = client.post(
            "/apis/intake/v2/workspaces/default/apps",
            json={"name": "test-app", "description": "Test application"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "test-app"
        assert data["workspace"] == "default"
        assert data["description"] == "Test application"
        assert "created_at" in data
        assert "updated_at" in data

    def test_get_app(self, client: TestClient):
        """Test getting an app by workspace_id and app_id."""
        # Create app first
        client.post(
            "/apis/intake/v2/workspaces/default/apps",
            json={"name": "test-app", "description": "Test application"},
        )

        # Get the app - workspace_id is "default", app_id is "test-app"
        response = client.get("/apis/intake/v2/workspaces/default/apps/test-app")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "test-app"
        assert data["workspace"] == "default"

    def test_list_apps(self, client: TestClient):
        """Test listing apps with pagination."""
        # Create multiple apps
        for i in range(3):
            client.post(
                "/apis/intake/v2/workspaces/default/apps",
                json={"name": f"app-{i}", "description": f"App {i}"},
            )

        # List apps
        response = client.get("/apis/intake/v2/workspaces/default/apps?page=1&page_size=10")
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "pagination" in data
        assert len(data["data"]) == 3
        assert data["pagination"]["total_results"] == 3

    def test_update_app(self, client: TestClient):
        """Test updating an app."""
        # Create app
        client.post(
            "/apis/intake/v2/workspaces/default/apps",
            json={"name": "test-app", "description": "Original description"},
        )

        # Update app
        response = client.patch(
            "/apis/intake/v2/workspaces/default/apps/test-app", json={"description": "Updated description"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["description"] == "Updated description"

    def test_delete_app(self, client: TestClient):
        """Test deleting an app."""
        # Create app
        client.post(
            "/apis/intake/v2/workspaces/default/apps",
            json={"name": "test-app", "description": "Test application"},
        )

        # Delete app
        response = client.delete("/apis/intake/v2/workspaces/default/apps/test-app")
        assert response.status_code == 204

        # Verify it's deleted
        response = client.get("/apis/intake/v2/workspaces/default/apps/test-app")
        assert response.status_code == 404

    # TODO(v2): Reactivate when Entities Service supports unique constraints
    @pytest.mark.skip(reason="Entities Service does not yet enforce unique constraints")
    def test_create_duplicate_app(self, client: TestClient):
        """Test that creating duplicate app fails."""
        # Create app
        client.post(
            "/apis/intake/v2/workspaces/default/apps",
            json={"name": "test-app", "description": "Test application"},
        )

        # Try to create duplicate
        response = client.post(
            "/apis/intake/v2/workspaces/default/apps",
            json={"name": "test-app", "description": "Duplicate"},
        )
        assert response.status_code == 409
