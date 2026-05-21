# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Integration tests for the intake service.

These tests verify:
- Entry CRUD endpoints functionality
- App CRUD endpoints functionality
- Task CRUD endpoints functionality
- Events sub-resource functionality
- API routes are properly registered in OpenAPI

Uses the create_test_client pattern for fast in-memory testing.
"""

import time
import uuid
from typing import Generator

import pytest
from fastapi.testclient import TestClient
from nemo_platform import NeMoPlatform
from nmp.intake.service import IntakeService
from nmp.testing.client import create_test_client

# Default workspace for tests
DEFAULT_WORKSPACE = "default"


@pytest.fixture(scope="module")
def http_client() -> Generator[TestClient, None, None]:
    """TestClient with IntakeService."""
    with create_test_client(
        IntakeService,
        client_type=TestClient,
    ) as client:
        yield client


@pytest.fixture(scope="module")
def sdk(http_client: TestClient) -> NeMoPlatform:
    """SDK client backed by the test client."""
    return NeMoPlatform(base_url="http://testserver", http_client=http_client)


def generate_entry_data(app_name: str = "test-app", task_name: str = "test-task"):
    """Generate test entry data matching the EntryInput schema."""
    return {
        "data": {
            "request": {
                "messages": [{"role": "user", "content": "Hello, how are you?"}],
                "model": "test-model",
            },
            "response": {
                "choices": [
                    {
                        "message": {"role": "assistant", "content": "I'm doing well, thank you!"},
                        "finish_reason": "stop",
                    }
                ]
            },
        },
        "context": {
            "app": f"{DEFAULT_WORKSPACE}/{app_name}",
            "task": task_name,
            "thread_id": str(uuid.uuid4()),
            "user_id": "test-user",
        },
    }


class TestIntakeOpenAPI:
    """Tests for intake routes in OpenAPI spec."""

    def test_entries_routes_in_openapi(self, sdk: NeMoPlatform):
        """Test that entry endpoints are documented in OpenAPI spec."""
        response = sdk._client.get("/openapi.json")
        assert response.status_code == 200

        spec = response.json()
        paths = spec.get("paths", {})

        # Verify workspace-scoped entry endpoints are present
        assert "/apis/intake/v2/workspaces/{workspace}/entries" in paths
        assert "get" in paths["/apis/intake/v2/workspaces/{workspace}/entries"]
        assert "post" in paths["/apis/intake/v2/workspaces/{workspace}/entries"]

    def test_apps_routes_in_openapi(self, sdk: NeMoPlatform):
        """Test that app endpoints are documented in OpenAPI spec."""
        response = sdk._client.get("/openapi.json")
        assert response.status_code == 200

        spec = response.json()
        paths = spec.get("paths", {})

        # Verify workspace-scoped app endpoints are present
        assert "/apis/intake/v2/workspaces/{workspace}/apps" in paths
        assert "get" in paths["/apis/intake/v2/workspaces/{workspace}/apps"]
        assert "post" in paths["/apis/intake/v2/workspaces/{workspace}/apps"]

    def test_tasks_routes_in_openapi(self, sdk: NeMoPlatform):
        """Test that task endpoints are documented in OpenAPI spec."""
        response = sdk._client.get("/openapi.json")
        assert response.status_code == 200

        spec = response.json()
        paths = spec.get("paths", {})

        # Verify task endpoints are present (nested under apps, workspace-scoped)
        assert "/apis/intake/v2/workspaces/{workspace}/apps/{name}/tasks" in paths
        assert "post" in paths["/apis/intake/v2/workspaces/{workspace}/apps/{name}/tasks"]
        assert "get" in paths["/apis/intake/v2/workspaces/{workspace}/apps/{name}/tasks"]

    def test_trace_routes_in_openapi(self, sdk: NeMoPlatform):
        """Test that span trace endpoints are documented in OpenAPI spec."""
        response = sdk._client.get("/openapi.json")
        assert response.status_code == 200

        paths = response.json().get("paths", {})

        assert "/apis/intake/v2/workspaces/{workspace}/sessions" not in paths
        assert "/apis/intake/v2/workspaces/{workspace}/sessions/{session_id}/spans" not in paths
        assert "/apis/intake/v2/workspaces/{workspace}/spans" in paths
        assert "get" in paths["/apis/intake/v2/workspaces/{workspace}/spans"]
        assert "/apis/intake/v2/workspaces/{workspace}/ingest/otlp/v1/traces" in paths
        assert "post" in paths["/apis/intake/v2/workspaces/{workspace}/ingest/otlp/v1/traces"]


class TestIntakeEntries:
    """Tests for the intake entry endpoints."""

    def test_entry_crud_lifecycle(self, sdk: NeMoPlatform):
        """Test full CRUD lifecycle for entries."""
        entry_data = generate_entry_data(
            app_name=f"e2e-app-{uuid.uuid4().hex[:8]}",
            task_name=f"e2e-task-{uuid.uuid4().hex[:8]}",
        )

        # CREATE
        response = sdk._client.post(f"/apis/intake/v2/workspaces/{DEFAULT_WORKSPACE}/entries", json=entry_data)
        assert response.status_code == 201, f"Create failed: {response.text}"
        created = response.json()
        assert "id" in created
        entry_id = created["id"]

        # READ (single)
        response = sdk._client.get(f"/apis/intake/v2/workspaces/{DEFAULT_WORKSPACE}/entries/{entry_id}")
        assert response.status_code == 200, f"Get failed: {response.text}"
        fetched = response.json()
        assert fetched["id"] == entry_id
        assert fetched["context"]["thread_id"] == entry_data["context"]["thread_id"]

        # LIST (workspace-scoped)
        response = sdk._client.get(f"/apis/intake/v2/workspaces/{DEFAULT_WORKSPACE}/entries")
        assert response.status_code == 200, f"List failed: {response.text}"
        entries = response.json()
        assert "data" in entries
        assert any(e["id"] == entry_id for e in entries["data"])

        # UPDATE - update user_rating since context has required fields
        update_data = {"user_rating": {"opinion": "Updated via e2e test"}}
        response = sdk._client.patch(
            f"/apis/intake/v2/workspaces/{DEFAULT_WORKSPACE}/entries/{entry_id}", json=update_data
        )
        assert response.status_code == 200, f"Update failed: {response.text}"
        updated = response.json()
        assert updated["user_rating"]["opinion"] == "Updated via e2e test"

        # DELETE
        response = sdk._client.delete(f"/apis/intake/v2/workspaces/{DEFAULT_WORKSPACE}/entries/{entry_id}")
        assert response.status_code == 204, f"Delete failed: {response.text}"

        # Verify deleted
        response = sdk._client.get(f"/apis/intake/v2/workspaces/{DEFAULT_WORKSPACE}/entries/{entry_id}")
        assert response.status_code == 404

    def test_get_nonexistent_entry_returns_404(self, sdk: NeMoPlatform):
        """Test that getting a non-existent entry returns 404."""
        response = sdk._client.get(f"/apis/intake/v2/workspaces/{DEFAULT_WORKSPACE}/entries/nonexistent-entry-id")
        assert response.status_code == 404

    def test_entry_list_pagination(self, sdk: NeMoPlatform):
        """Test that entry listing supports pagination."""
        response = sdk._client.get(f"/apis/intake/v2/workspaces/{DEFAULT_WORKSPACE}/entries?page=1&page_size=5")
        assert response.status_code == 200

        data = response.json()
        assert "data" in data
        assert "pagination" in data
        assert data["pagination"]["page"] == 1
        assert data["pagination"]["page_size"] == 5


class TestIntakeEntryEvents:
    """Tests for the intake entry events sub-resource."""

    def test_add_events_to_entry(self, sdk: NeMoPlatform):
        """Test adding events (feedback) to an entry."""
        # Create an entry first
        entry_data = generate_entry_data(
            app_name=f"e2e-app-{uuid.uuid4().hex[:8]}",
            task_name=f"e2e-task-{uuid.uuid4().hex[:8]}",
        )
        response = sdk._client.post(f"/apis/intake/v2/workspaces/{DEFAULT_WORKSPACE}/entries", json=entry_data)
        assert response.status_code == 201
        entry_id = response.json()["id"]

        # Add thumbs up feedback event
        events_data = {"events": [{"event_type": "user_feedback", "thumb": "up"}]}

        response = sdk._client.post(
            f"/apis/intake/v2/workspaces/{DEFAULT_WORKSPACE}/entries/{entry_id}/events", json=events_data
        )
        assert response.status_code == 200, f"Add events failed: {response.text}"
        updated = response.json()
        assert len(updated.get("events", [])) >= 1
        # user_rating should be updated from the feedback event
        assert updated.get("user_rating", {}).get("thumb") == "up"

        # Cleanup
        sdk._client.delete(f"/apis/intake/v2/workspaces/{DEFAULT_WORKSPACE}/entries/{entry_id}")

    def test_add_rating_event_to_entry(self, sdk: NeMoPlatform):
        """Test adding a rating event to an entry."""
        # Create an entry first
        entry_data = generate_entry_data(
            app_name=f"e2e-app-{uuid.uuid4().hex[:8]}",
            task_name=f"e2e-task-{uuid.uuid4().hex[:8]}",
        )
        response = sdk._client.post(f"/apis/intake/v2/workspaces/{DEFAULT_WORKSPACE}/entries", json=entry_data)
        assert response.status_code == 201
        entry_id = response.json()["id"]

        # Add rating feedback event
        events_data = {
            "events": [
                {
                    "event_type": "user_feedback",
                    "rating": 5,
                    "opinion": "Great response!",
                }
            ]
        }

        response = sdk._client.post(
            f"/apis/intake/v2/workspaces/{DEFAULT_WORKSPACE}/entries/{entry_id}/events", json=events_data
        )
        assert response.status_code == 200, f"Add events failed: {response.text}"
        updated = response.json()
        assert updated.get("user_rating", {}).get("rating") == 5
        assert updated.get("user_rating", {}).get("opinion") == "Great response!"

        # Cleanup
        sdk._client.delete(f"/apis/intake/v2/workspaces/{DEFAULT_WORKSPACE}/entries/{entry_id}")


class TestIntakeApps:
    """Tests for the intake app entity endpoints."""

    def test_app_crud_lifecycle(self, sdk: NeMoPlatform):
        """Test full CRUD lifecycle for apps."""
        test_name = f"test-app-{uuid.uuid4().hex[:8]}"

        # CREATE - workspace comes from URL path, not body
        app_data = {
            "name": test_name,
            "description": "E2E test app",
        }
        response = sdk._client.post(f"/apis/intake/v2/workspaces/{DEFAULT_WORKSPACE}/apps", json=app_data)
        assert response.status_code == 201, f"Create failed: {response.text}"
        created = response.json()
        assert created["name"] == test_name
        assert created["workspace"] == DEFAULT_WORKSPACE

        # READ (single)
        response = sdk._client.get(f"/apis/intake/v2/workspaces/{DEFAULT_WORKSPACE}/apps/{test_name}")
        assert response.status_code == 200, f"Get failed: {response.text}"
        fetched = response.json()
        assert fetched["name"] == created["name"]
        assert fetched["description"] == "E2E test app"

        # LIST (workspace-scoped)
        response = sdk._client.get(f"/apis/intake/v2/workspaces/{DEFAULT_WORKSPACE}/apps?page_size=100")
        assert response.status_code == 200, f"List failed: {response.text}"
        apps = response.json()
        assert "data" in apps
        assert any(a["name"] == test_name for a in apps["data"])

        # UPDATE
        update_data = {"description": "Updated description"}
        response = sdk._client.patch(
            f"/apis/intake/v2/workspaces/{DEFAULT_WORKSPACE}/apps/{test_name}", json=update_data
        )
        assert response.status_code == 200, f"Update failed: {response.text}"
        updated = response.json()
        assert updated["description"] == "Updated description"

        # DELETE
        response = sdk._client.delete(f"/apis/intake/v2/workspaces/{DEFAULT_WORKSPACE}/apps/{test_name}")
        assert response.status_code == 204, f"Delete failed: {response.text}"

        # Verify deleted
        response = sdk._client.get(f"/apis/intake/v2/workspaces/{DEFAULT_WORKSPACE}/apps/{test_name}")
        assert response.status_code == 404

    @pytest.mark.skip(
        reason="TODO: Re-enable once entity store supports unique constraint on (workspace_id, entity_type, name)"
    )
    def test_create_duplicate_app_fails(self, sdk: NeMoPlatform):
        """Test that creating a duplicate app returns 409."""
        test_name = f"dup-app-{uuid.uuid4().hex[:8]}"

        app_data = {
            "name": test_name,
        }

        # Create first app
        response = sdk._client.post(f"/apis/intake/v2/workspaces/{DEFAULT_WORKSPACE}/apps", json=app_data)
        assert response.status_code == 201

        # Try to create duplicate
        response = sdk._client.post(f"/apis/intake/v2/workspaces/{DEFAULT_WORKSPACE}/apps", json=app_data)
        assert response.status_code == 409

        # Cleanup
        sdk._client.delete(f"/apis/intake/v2/workspaces/{DEFAULT_WORKSPACE}/apps/{test_name}")

    def test_get_nonexistent_app_returns_404(self, sdk: NeMoPlatform):
        """Test that getting a non-existent app returns 404."""
        response = sdk._client.get(f"/apis/intake/v2/workspaces/{DEFAULT_WORKSPACE}/apps/nonexistent-app")
        assert response.status_code == 404


class TestIntakeTasks:
    """Tests for the intake task entity endpoints."""

    def test_task_crud_lifecycle(self, sdk: NeMoPlatform):
        """Test full CRUD lifecycle for tasks."""
        # First create an app for the task
        app_name = f"test-app-{uuid.uuid4().hex[:8]}"
        app_data = {"name": app_name}
        response = sdk._client.post(f"/apis/intake/v2/workspaces/{DEFAULT_WORKSPACE}/apps", json=app_data)
        assert response.status_code == 201

        task_name = f"test-task-{uuid.uuid4().hex[:8]}"

        # CREATE
        task_data = {
            "name": task_name,
            "description": "E2E test task",
        }
        response = sdk._client.post(
            f"/apis/intake/v2/workspaces/{DEFAULT_WORKSPACE}/apps/{app_name}/tasks",
            json=task_data,
        )
        assert response.status_code == 201, f"Create failed: {response.text}"
        created = response.json()
        assert created["name"] == task_name
        assert created["workspace"] == DEFAULT_WORKSPACE

        # READ (single)
        response = sdk._client.get(f"/apis/intake/v2/workspaces/{DEFAULT_WORKSPACE}/apps/{app_name}/tasks/{task_name}")
        assert response.status_code == 200, f"Get failed: {response.text}"
        fetched = response.json()
        assert fetched["name"] == created["name"]
        assert fetched["description"] == "E2E test task"

        # LIST
        response = sdk._client.get(f"/apis/intake/v2/workspaces/{DEFAULT_WORKSPACE}/apps/{app_name}/tasks")
        assert response.status_code == 200, f"List failed: {response.text}"
        tasks = response.json()
        assert "data" in tasks
        assert any(t["name"] == task_name for t in tasks["data"])

        # UPDATE
        update_data = {"description": "Updated task description"}
        response = sdk._client.patch(
            f"/apis/intake/v2/workspaces/{DEFAULT_WORKSPACE}/apps/{app_name}/tasks/{task_name}",
            json=update_data,
        )
        assert response.status_code == 200, f"Update failed: {response.text}"
        updated = response.json()
        assert updated["description"] == "Updated task description"

        # DELETE task
        response = sdk._client.delete(
            f"/apis/intake/v2/workspaces/{DEFAULT_WORKSPACE}/apps/{app_name}/tasks/{task_name}"
        )
        assert response.status_code == 204, f"Delete task failed: {response.text}"

        # Verify task deleted
        response = sdk._client.get(f"/apis/intake/v2/workspaces/{DEFAULT_WORKSPACE}/apps/{app_name}/tasks/{task_name}")
        assert response.status_code == 404

        # Cleanup - delete the app
        sdk._client.delete(f"/apis/intake/v2/workspaces/{DEFAULT_WORKSPACE}/apps/{app_name}")

    @pytest.mark.skip(
        reason="TODO: Re-enable once entity store supports unique constraint on (workspace_id, entity_type, name)"
    )
    def test_create_duplicate_task_fails(self, sdk: NeMoPlatform):
        """Test that creating a duplicate task returns 409."""
        # First create an app
        app_name = f"test-app-{uuid.uuid4().hex[:8]}"
        app_data = {"name": app_name}
        response = sdk._client.post(f"/apis/intake/v2/workspaces/{DEFAULT_WORKSPACE}/apps", json=app_data)
        assert response.status_code == 201

        task_name = f"dup-task-{uuid.uuid4().hex[:8]}"
        task_data = {"name": task_name}

        # Create first task
        response = sdk._client.post(
            f"/apis/intake/v2/workspaces/{DEFAULT_WORKSPACE}/apps/{app_name}/tasks",
            json=task_data,
        )
        assert response.status_code == 201

        # Try to create duplicate
        response = sdk._client.post(
            f"/apis/intake/v2/workspaces/{DEFAULT_WORKSPACE}/apps/{app_name}/tasks",
            json=task_data,
        )
        assert response.status_code == 409

        # Cleanup
        sdk._client.delete(f"/apis/intake/v2/workspaces/{DEFAULT_WORKSPACE}/apps/{app_name}/tasks/{task_name}")
        sdk._client.delete(f"/apis/intake/v2/workspaces/{DEFAULT_WORKSPACE}/apps/{app_name}")

    def test_get_nonexistent_task_returns_404(self, sdk: NeMoPlatform):
        """Test that getting a non-existent task returns 404."""
        # First create an app
        app_name = f"test-app-{uuid.uuid4().hex[:8]}"
        app_data = {"name": app_name}
        response = sdk._client.post(f"/apis/intake/v2/workspaces/{DEFAULT_WORKSPACE}/apps", json=app_data)
        assert response.status_code == 201

        response = sdk._client.get(
            f"/apis/intake/v2/workspaces/{DEFAULT_WORKSPACE}/apps/{app_name}/tasks/nonexistent-task"
        )
        assert response.status_code == 404

        # Cleanup
        sdk._client.delete(f"/apis/intake/v2/workspaces/{DEFAULT_WORKSPACE}/apps/{app_name}")


class TestIntakeAutoCreation:
    """Tests for automatic app/task creation when creating entries."""

    def test_entry_auto_creates_app_and_task(self, sdk: NeMoPlatform):
        """Test that creating an entry auto-creates referenced app and task."""
        app_name = f"auto-app-{uuid.uuid4().hex[:8]}"
        task_name = f"auto-task-{uuid.uuid4().hex[:8]}"

        # Create entry with new app/task references
        entry_data = generate_entry_data(app_name=app_name, task_name=task_name)
        response = sdk._client.post(f"/apis/intake/v2/workspaces/{DEFAULT_WORKSPACE}/entries", json=entry_data)
        assert response.status_code == 201, f"Create entry failed: {response.text}"
        entry_id = response.json()["id"]

        # Wait a moment for async auto-creation to complete
        time.sleep(0.5)

        # Verify app was auto-created
        response = sdk._client.get(f"/apis/intake/v2/workspaces/{DEFAULT_WORKSPACE}/apps/{app_name}")
        assert response.status_code == 200, f"App was not auto-created: {response.text}"

        # Verify task was auto-created
        response = sdk._client.get(f"/apis/intake/v2/workspaces/{DEFAULT_WORKSPACE}/apps/{app_name}/tasks/{task_name}")
        assert response.status_code == 200, f"Task was not auto-created: {response.text}"

        # Cleanup
        sdk._client.delete(f"/apis/intake/v2/workspaces/{DEFAULT_WORKSPACE}/entries/{entry_id}")
        sdk._client.delete(f"/apis/intake/v2/workspaces/{DEFAULT_WORKSPACE}/apps/{app_name}/tasks/{task_name}")
        sdk._client.delete(f"/apis/intake/v2/workspaces/{DEFAULT_WORKSPACE}/apps/{app_name}")
