# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Tests for Tasks API endpoints."""

import pytest
from fastapi.testclient import TestClient


class TestTasksAPI:
    """Tests for Tasks API endpoints."""

    @pytest.fixture(autouse=True)
    def create_test_app(self, client: TestClient):
        """Create a test app before each test."""
        client.post(
            "/apis/intake/v2/workspaces/default/apps",
            json={"name": "test-app", "description": "Test application"},
        )

    def test_create_task(self, client: TestClient):
        """Test creating a task under an app."""
        response = client.post(
            "/apis/intake/v2/workspaces/default/apps/test-app/tasks",
            json={"name": "chat", "description": "Chat task"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "chat"
        assert data["workspace"] == "default"
        assert data["app"] == "default/test-app"
        assert data["description"] == "Chat task"

    def test_get_task(self, client: TestClient):
        """Test getting a task by name."""
        # Create task
        client.post(
            "/apis/intake/v2/workspaces/default/apps/test-app/tasks",
            json={"name": "chat", "description": "Chat task"},
        )

        # Get task
        response = client.get("/apis/intake/v2/workspaces/default/apps/test-app/tasks/chat")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "chat"
        assert data["app"] == "default/test-app"

    def test_list_tasks(self, client: TestClient):
        """Test listing tasks for an app."""
        # Create multiple tasks
        for i in range(3):
            client.post(
                "/apis/intake/v2/workspaces/default/apps/test-app/tasks",
                json={"name": f"task-{i}", "description": f"Task {i}"},
            )

        # List tasks
        response = client.get("/apis/intake/v2/workspaces/default/apps/test-app/tasks")
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 3

    def test_update_task(self, client: TestClient):
        """Test updating a task."""
        # Create task
        client.post(
            "/apis/intake/v2/workspaces/default/apps/test-app/tasks",
            json={"name": "chat", "description": "Original description"},
        )

        # Update task
        response = client.patch(
            "/apis/intake/v2/workspaces/default/apps/test-app/tasks/chat",
            json={"description": "Updated description"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["description"] == "Updated description"

    def test_delete_task(self, client: TestClient):
        """Test deleting a task."""
        # Create task
        client.post(
            "/apis/intake/v2/workspaces/default/apps/test-app/tasks",
            json={"name": "chat", "description": "Chat task"},
        )

        # Delete task
        response = client.delete("/apis/intake/v2/workspaces/default/apps/test-app/tasks/chat")
        assert response.status_code == 204

        # Verify it's deleted
        response = client.get("/apis/intake/v2/workspaces/default/apps/test-app/tasks/chat")
        assert response.status_code == 404
