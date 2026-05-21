# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Tests for Entries API endpoints."""

import time
from datetime import datetime

import pytest
from fastapi.testclient import TestClient


def wait_for_status(
    client: TestClient, url: str, expected_status: int = 200, max_attempts: int = 20, delay: float = 0.05
):
    """Poll a URL until it returns the expected status code.

    Used for endpoints that depend on fire-and-forget background tasks completing.
    """
    response = client.get(url)
    for _ in range(max_attempts):
        if response.status_code == expected_status:
            return response
        time.sleep(delay)
        response = client.get(url)
    return response  # Return last response for assertion error messages


class TestEntriesAPI:
    """Tests for Entries API endpoints."""

    @pytest.fixture(autouse=True)
    def create_test_app_and_task(self, client: TestClient):
        """Create test app and task before each test."""
        client.post(
            "/apis/intake/v2/workspaces/default/apps",
            json={"name": "test-app", "description": "Test application"},
        )
        client.post(
            "/apis/intake/v2/workspaces/default/apps/test-app/tasks",
            json={"name": "chat", "description": "Chat task"},
        )

    def test_create_entry(self, client: TestClient):
        """Test creating an entry."""
        response = client.post(
            "/apis/intake/v2/workspaces/default/entries",
            json={
                "external_id": "chatcmpl-test123",
                "data": {
                    "request": {"model": "gpt-4", "messages": [{"role": "user", "content": "What is 2+2?"}]},
                    "response": {"choices": [{"message": {"role": "assistant", "content": "4"}}]},
                },
                "context": {"app": "default/test-app", "task": "chat", "thread_id": "thread_123"},
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["id"] is not None
        assert data["external_id"] == "chatcmpl-test123"
        assert data["workspace"] == "default"
        assert data["data"]["request"]["model"] == "gpt-4"
        assert data["context"]["app"] == "default/test-app"
        assert data["context"]["task"] == "chat"

    def test_create_entry_without_external_id(self, client: TestClient):
        """Test creating an entry without external_id - should still return an id."""
        response = client.post(
            "/apis/intake/v2/workspaces/default/entries",
            json={
                "data": {
                    "request": {"model": "gpt-4", "messages": [{"role": "user", "content": "What is 2+2?"}]},
                    "response": {"choices": [{"message": {"role": "assistant", "content": "4"}}]},
                },
                "context": {"app": "default/test-app", "task": "chat", "thread_id": "thread_123"},
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["id"] is not None
        assert data["id"].startswith("intake-entry-")  # ID format: {entity_type}-{uuid}
        assert data["external_id"] is None  # external_id should be None but still present
        assert data["workspace"] == "default"

        # Verify we can retrieve it by the generated ID
        entry_id = data["id"]
        get_response = client.get(f"/apis/intake/v2/workspaces/default/entries/{entry_id}")
        assert get_response.status_code == 200
        get_data = get_response.json()
        assert get_data["id"] == entry_id

    def test_get_entry_by_external_id(self, client: TestClient):
        """Test getting entry using external: prefix."""
        # Create entry
        client.post(
            "/apis/intake/v2/workspaces/default/entries",
            json={
                "external_id": "chatcmpl-test456",
                "data": {"request": {"model": "gpt-4", "messages": []}, "response": {"choices": []}},
                "context": {"app": "default/test-app", "task": "chat", "thread_id": "thread_123"},
            },
        )

        # Get by external_id using external: prefix
        response = client.get("/apis/intake/v2/workspaces/default/entries/external:chatcmpl-test456")
        assert response.status_code == 200
        data = response.json()
        assert data["external_id"] == "chatcmpl-test456"

    def test_list_entries(self, client: TestClient):
        """Test listing entries with pagination."""
        # Create multiple entries
        for i in range(3):
            client.post(
                "/apis/intake/v2/workspaces/default/entries",
                json={
                    "external_id": f"chatcmpl-{i}",
                    "data": {"request": {"model": "gpt-4", "messages": []}, "response": {"choices": []}},
                    "context": {"app": "default/test-app", "task": "chat", "thread_id": f"thread_{i}"},
                },
            )

        # List entries
        response = client.get("/apis/intake/v2/workspaces/default/entries?page=1&page_size=10")
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 3
        assert data["pagination"]["total_results"] == 3

        # Verify each entry has id and external_id fields (even if external_id is None)
        for entry in data["data"]:
            assert "id" in entry
            assert entry["id"] is not None
            assert "external_id" in entry  # Should be present even if None

    def test_update_entry_by_external_id(self, client: TestClient):
        """Test updating entry using external: prefix."""
        # Create entry
        client.post(
            "/apis/intake/v2/workspaces/default/entries",
            json={
                "external_id": "chatcmpl-update",
                "data": {"request": {"model": "gpt-4", "messages": []}, "response": {"choices": []}},
                "context": {"app": "default/test-app", "task": "chat", "thread_id": "thread_123"},
            },
        )

        # Update using external_id
        response = client.patch(
            "/apis/intake/v2/workspaces/default/entries/external:chatcmpl-update", json={"user_rating": {"thumb": "up"}}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["user_rating"]["thumb"] == "up"

    def test_delete_entry(self, client: TestClient):
        """Test deleting an entry."""
        # Create entry
        response = client.post(
            "/apis/intake/v2/workspaces/default/entries",
            json={
                "external_id": "chatcmpl-delete",
                "data": {"request": {"model": "gpt-4", "messages": []}, "response": {"choices": []}},
                "context": {"app": "default/test-app", "task": "chat", "thread_id": "thread_123"},
            },
        )

        # Delete entry using external_id
        response = client.delete("/apis/intake/v2/workspaces/default/entries/external:chatcmpl-delete")
        assert response.status_code == 204

        # Verify it's deleted
        response = client.get("/apis/intake/v2/workspaces/default/entries/external:chatcmpl-delete")
        assert response.status_code == 404

    def test_add_events_to_entry(self, client: TestClient):
        """Test adding events to an entry."""
        # Create entry
        client.post(
            "/apis/intake/v2/workspaces/default/entries",
            json={
                "external_id": "chatcmpl-events",
                "data": {"request": {"model": "gpt-4", "messages": []}, "response": {"choices": []}},
                "context": {"app": "default/test-app", "task": "chat", "thread_id": "thread_123"},
            },
        )

        # Add events
        response = client.post(
            "/apis/intake/v2/workspaces/default/entries/external:chatcmpl-events/events",
            json={"events": [{"event_type": "user_feedback", "thumb": "up"}]},
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["events"]) == 1
        assert data["events"][0]["event_type"] == "user_feedback"

    def test_filter_entries_by_workspace(self, client: TestClient):
        """Test filtering entries by workspace using workspace-scoped endpoint."""
        # Create entry with full data structure like other tests
        create_response = client.post(
            "/apis/intake/v2/workspaces/default/entries",
            json={
                "external_id": "chatcmpl-ns1",
                "data": {"request": {"model": "gpt-4", "messages": []}, "response": {"choices": []}},
                "context": {"app": "default/test-app", "task": "chat", "thread_id": "thread_1"},
            },
        )
        assert create_response.status_code == 201, f"Failed to create entry: {create_response.json()}"

        # List all entries first
        list_response = client.get("/apis/intake/v2/workspaces/default/entries")
        assert list_response.status_code == 200
        all_data = list_response.json()

        # Filter by workspace via workspace-scoped endpoint
        # The workspace in URL path acts as workspace filter
        response = client.get("/apis/intake/v2/workspaces/default/entries")
        assert response.status_code == 200
        data = response.json()
        # Should have at least the entry we just created
        assert len(data["data"]) >= 1, (
            f"Expected at least 1 entry, got {len(data['data'])}. All entries: {len(all_data['data'])}"
        )
        for entry in data["data"]:
            assert entry["workspace"] == "default"

    def test_path_workspace_overrides_workspace_filter(self, client: TestClient):
        """Test that the route workspace is authoritative over query filters."""
        create_response = client.post(
            "/apis/intake/v2/workspaces/default/entries",
            json={
                "external_id": "chatcmpl-path-workspace",
                "data": {"request": {"model": "gpt-4", "messages": []}, "response": {"choices": []}},
                "context": {"app": "default/test-app", "task": "chat", "thread_id": "thread_path_workspace"},
            },
        )
        assert create_response.status_code == 201
        entry_id = create_response.json()["id"]

        response = client.get("/apis/intake/v2/workspaces/default/entries?filter[workspace]=other")
        assert response.status_code == 200
        data = response.json()

        assert any(entry["id"] == entry_id for entry in data["data"])
        for entry in data["data"]:
            assert entry["workspace"] == "default"

    def test_filter_entries_by_id(self, client: TestClient):
        """Test filtering entries by a single ID."""
        # Create entry
        create_response = client.post(
            "/apis/intake/v2/workspaces/default/entries",
            json={
                "external_id": "chatcmpl-id-filter",
                "data": {"request": {"model": "gpt-4", "messages": []}, "response": {"choices": []}},
                "context": {"app": "default/test-app", "task": "chat", "thread_id": "thread_id_filter"},
            },
        )
        assert create_response.status_code == 201
        entry_id = create_response.json()["id"]

        # Filter by ID
        response = client.get(f"/apis/intake/v2/workspaces/default/entries?filter[id]={entry_id}")
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 1
        assert data["data"][0]["id"] == entry_id

    # TODO(v2): Investigate 'in' operator filter conversion for EntityClient
    @pytest.mark.skip(reason="Complex filter operators need EntityClient filter conversion support")
    def test_filter_entries_by_multiple_ids(self, client: TestClient):
        """Test filtering entries by multiple IDs using the 'in' operator."""
        # Create multiple entries
        entry_ids = []
        for i in range(3):
            create_response = client.post(
                "/apis/intake/v2/workspaces/default/entries",
                json={
                    "external_id": f"chatcmpl-multi-{i}",
                    "data": {"request": {"model": "gpt-4", "messages": []}, "response": {"choices": []}},
                    "context": {"app": "default/test-app", "task": "chat", "thread_id": f"thread_multi_{i}"},
                },
            )
            assert create_response.status_code == 201
            entry_ids.append(create_response.json()["id"])

        # Filter by first two IDs using 'in' operator with proper JSON syntax
        import json

        ids_json = json.dumps([entry_ids[0], entry_ids[1]])
        response = client.get(f"/apis/intake/v2/workspaces/default/entries?filter[id][in]={ids_json}")
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 2
        returned_ids = [entry["id"] for entry in data["data"]]
        assert entry_ids[0] in returned_ids
        assert entry_ids[1] in returned_ids
        assert entry_ids[2] not in returned_ids

    def test_filter_entries_by_id_with_invalid_json(self, client: TestClient):
        """Test that invalid JSON in filter gives helpful error message."""
        # Try to filter with invalid JSON syntax (missing quotes)
        response = client.get("/apis/intake/v2/workspaces/default/entries?filter[id][in]=[entry-ABC,entry-XYZ]")
        assert response.status_code == 400
        error_data = response.json()
        assert "Invalid filter value" in error_data["detail"]
        assert "valid JSON with proper quoting" in error_data["detail"]
        assert '["item1","item2"]' in error_data["detail"]

    def test_filter_entries_by_external_id(self, client: TestClient):
        """Test filtering entries by a single external_id."""
        # Create entry
        create_response = client.post(
            "/apis/intake/v2/workspaces/default/entries",
            json={
                "external_id": "chatcmpl-ext-filter",
                "data": {"request": {"model": "gpt-4", "messages": []}, "response": {"choices": []}},
                "context": {"app": "default/test-app", "task": "chat", "thread_id": "thread_ext_filter"},
            },
        )
        assert create_response.status_code == 201
        external_id = create_response.json()["external_id"]

        # Filter by external_id
        response = client.get(f"/apis/intake/v2/workspaces/default/entries?filter[external_id]={external_id}")
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 1
        assert data["data"][0]["external_id"] == external_id

    # TODO(v2): Investigate 'in' operator filter conversion for EntityClient
    @pytest.mark.skip(reason="Complex filter operators need EntityClient filter conversion support")
    def test_filter_entries_by_multiple_external_ids(self, client: TestClient):
        """Test filtering entries by multiple external_ids using the 'in' operator."""
        # Create multiple entries with external_ids
        external_ids = []
        for i in range(3):
            create_response = client.post(
                "/apis/intake/v2/workspaces/default/entries",
                json={
                    "external_id": f"chatcmpl-ext-multi-{i}",
                    "data": {"request": {"model": "gpt-4", "messages": []}, "response": {"choices": []}},
                    "context": {"app": "default/test-app", "task": "chat", "thread_id": f"thread_ext_multi_{i}"},
                },
            )
            assert create_response.status_code == 201
            external_ids.append(create_response.json()["external_id"])

        # Filter by first two external_ids using 'in' operator with proper JSON syntax
        import json

        ext_ids_json = json.dumps([external_ids[0], external_ids[1]])
        response = client.get(f"/apis/intake/v2/workspaces/default/entries?filter[external_id][in]={ext_ids_json}")
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 2
        returned_ext_ids = [entry["external_id"] for entry in data["data"]]
        assert external_ids[0] in returned_ext_ids
        assert external_ids[1] in returned_ext_ids
        assert external_ids[2] not in returned_ext_ids

    def test_filter_entries_by_external_id_with_invalid_json(self, client: TestClient):
        """Test that invalid JSON in external_id filter gives helpful error message."""
        # Try to filter with invalid JSON syntax (missing quotes) - the actual issue from the user
        response = client.get(
            "/apis/intake/v2/workspaces/default/entries?filter[external_id][in]=[entry-CTXhK1QzYR7E62mwoxqGp9]"
        )
        assert response.status_code == 400
        error_data = response.json()
        assert "Invalid filter value" in error_data["detail"]
        assert "valid JSON with proper quoting" in error_data["detail"]

    def test_auto_registration_of_app_and_task(self, client: TestClient):
        """Test that apps and tasks are auto-created when entry is created."""
        # Create entry without pre-creating app and task
        response = client.post(
            "/apis/intake/v2/workspaces/default/entries",
            json={
                "external_id": "chatcmpl-autoreg",
                "data": {"request": {"model": "gpt-4", "messages": []}, "response": {"choices": []}},
                "context": {"app": "default/auto-app", "task": "auto-task", "thread_id": "thread_auto"},
            },
        )
        assert response.status_code == 201

        # Verify app was auto-created (poll because auto-registration is fire-and-forget)
        app_response = wait_for_status(client, "/apis/intake/v2/workspaces/default/apps/auto-app")
        assert app_response.status_code == 200
        app_data = app_response.json()
        assert app_data["name"] == "auto-app"
        assert "Auto-registered" in app_data["description"]

        # Verify task was auto-created
        task_response = wait_for_status(client, "/apis/intake/v2/workspaces/default/apps/auto-app/tasks/auto-task")
        assert task_response.status_code == 200
        task_data = task_response.json()
        assert task_data["name"] == "auto-task"
        assert "Auto-registered" in task_data["description"]

    def test_auto_registration_without_workspace_prefix(self, client: TestClient):
        """Test that apps and tasks auto-created without workspace prefix can be updated."""
        # Create entry with app name WITHOUT workspace prefix (just "my-app" not "default/my-app")
        response = client.post(
            "/apis/intake/v2/workspaces/default/entries",
            json={
                "external_id": "chatcmpl-no-ns",
                "data": {"request": {"model": "gpt-4", "messages": []}, "response": {"choices": []}},
                "context": {"app": "no-ns-app", "task": "no-ns-task", "thread_id": "thread_no_ns"},
            },
        )
        assert response.status_code == 201

        # Verify app was auto-created (poll because auto-registration is fire-and-forget)
        app_response = wait_for_status(client, "/apis/intake/v2/workspaces/default/apps/no-ns-app")
        assert app_response.status_code == 200

        # Verify task was auto-created and can be retrieved
        task_response = wait_for_status(client, "/apis/intake/v2/workspaces/default/apps/no-ns-app/tasks/no-ns-task")
        assert task_response.status_code == 200

        # Verify task can be updated (this was the bug)
        update_response = client.patch(
            "/apis/intake/v2/workspaces/default/apps/no-ns-app/tasks/no-ns-task",
            json={"description": "This task was updated successfully"},
        )
        assert update_response.status_code == 200
        updated_task = update_response.json()
        assert updated_task["description"] == "This task was updated successfully"

    # TODO(v2): Investigate longest_per_thread filter aggregation with EntityClient
    @pytest.mark.skip(reason="Thread aggregation filter needs EntityClient support investigation")
    def test_longest_per_thread_filter(self, client: TestClient):
        """Test filtering to get only longest entry per thread."""
        # Create multiple entries in the same thread with different message counts
        for i in range(3):
            messages = [{"role": "user", "content": f"msg{j}"} for j in range(i + 1)]
            client.post(
                "/apis/intake/v2/workspaces/default/entries",
                json={
                    "external_id": f"chatcmpl-thread-{i}",
                    "data": {"request": {"model": "gpt-4", "messages": messages}, "response": {"choices": []}},
                    "context": {"app": "default/test-app", "task": "chat", "thread_id": "thread_longest"},
                },
            )

        # Get all entries first (should have 3 from this thread)
        all_response = client.get("/apis/intake/v2/workspaces/default/entries")
        assert all_response.status_code == 200
        all_response.json()

        # Get longest per thread
        filtered_response = client.get("/apis/intake/v2/workspaces/default/entries?filter[longest_per_thread]=true")
        assert filtered_response.status_code == 200
        filtered_data = filtered_response.json()

        # Should have only 1 entry from this thread (the longest)
        # Count entries with thread_longest
        longest_entries = [
            e for e in filtered_data["data"] if e.get("context", {}).get("thread_id") == "thread_longest"
        ]
        assert len(longest_entries) == 1
        # Should be the one with 3 messages (i=2)
        longest_entry = longest_entries[0]
        assert longest_entry["external_id"] == "chatcmpl-thread-2"

    def test_create_entry_with_user_id(self, client: TestClient):
        """Test creating an entry with user_id."""
        response = client.post(
            "/apis/intake/v2/workspaces/default/entries",
            json={
                "external_id": "chatcmpl-user-test",
                "data": {
                    "request": {"model": "gpt-4", "messages": [{"role": "user", "content": "Hello"}]},
                    "response": {"choices": [{"message": {"role": "assistant", "content": "Hi there"}}]},
                },
                "context": {
                    "app": "default/test-app",
                    "task": "chat",
                    "thread_id": "thread_user_1",
                    "user_id": "user_12345",
                },
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["context"]["user_id"] == "user_12345"

    @pytest.mark.skip(
        reason="Nested JSON filtering requires PostgreSQL JSONB support; SQLite tests use JSON which lacks this functionality"
    )
    def test_filter_entries_by_user_id(self, client: TestClient):
        """Test filtering entries by user_id."""
        # Create entries for different users
        for user_num in [1, 2]:
            client.post(
                "/apis/intake/v2/workspaces/default/entries",
                json={
                    "external_id": f"chatcmpl-user-{user_num}",
                    "data": {"request": {"model": "gpt-4", "messages": []}, "response": {"choices": []}},
                    "context": {
                        "app": "default/test-app",
                        "task": "chat",
                        "thread_id": f"thread_{user_num}",
                        "user_id": f"user_{user_num}",
                    },
                },
            )

        # Filter by user_id
        response = client.get("/apis/intake/v2/workspaces/default/entries?filter[context][user_id]=user_1")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1

        # Verify all returned entries have the correct user_id
        for entry in data["items"]:
            assert entry["context"]["user_id"] == "user_1"

    @pytest.mark.skip(
        reason="Nested JSON filtering requires PostgreSQL JSONB support; SQLite tests use JSON which lacks this functionality"
    )
    def test_filter_entries_by_nonexistent_user_id(self, client: TestClient):
        """Test filtering entries by non-existent user_id returns empty results."""
        # Create an entry with a user_id
        client.post(
            "/apis/intake/v2/workspaces/default/entries",
            json={
                "external_id": "chatcmpl-existing-user",
                "data": {"request": {"model": "gpt-4", "messages": []}, "response": {"choices": []}},
                "context": {
                    "app": "default/test-app",
                    "task": "chat",
                    "thread_id": "thread_1",
                    "user_id": "existing_user",
                },
            },
        )

        # Filter by non-existent user_id should return 200 with empty results
        response = client.get(
            "/apis/intake/v2/workspaces/default/entries?filter[context][user_id]=nonexistent_user_999"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert len(data["items"]) == 0

    def test_create_entry_with_custom_fields(self, client: TestClient):
        """Custom fields round-trip through POST and GET."""
        custom = {"experiment": {"id": "job-abc", "model": "gpt-4", "num_attempts": 3}}
        response = client.post(
            "/apis/intake/v2/workspaces/default/entries",
            json={
                "external_id": "chatcmpl-cf",
                "data": {"request": {"model": "gpt-4", "messages": []}, "response": {"choices": []}},
                "context": {"app": "default/test-app", "task": "chat"},
                "custom_fields": custom,
            },
        )
        assert response.status_code == 201
        assert response.json()["custom_fields"] == custom

        get_response = client.get("/apis/intake/v2/workspaces/default/entries/external:chatcmpl-cf")
        assert get_response.status_code == 200
        assert get_response.json()["custom_fields"] == custom

    def test_update_entry_custom_fields(self, client: TestClient):
        """PATCH replaces custom_fields with the provided value."""
        client.post(
            "/apis/intake/v2/workspaces/default/entries",
            json={
                "external_id": "chatcmpl-cf-patch",
                "data": {"request": {"model": "gpt-4", "messages": []}, "response": {"choices": []}},
                "context": {"app": "default/test-app", "task": "chat"},
                "custom_fields": {"experiment": {"id": "job-1"}},
            },
        )

        new_custom = {"experiment": {"id": "job-1", "num_errors": 0, "num_trials": 5}}
        patch_response = client.patch(
            "/apis/intake/v2/workspaces/default/entries/external:chatcmpl-cf-patch",
            json={"custom_fields": new_custom},
        )
        assert patch_response.status_code == 200
        assert patch_response.json()["custom_fields"] == new_custom

    def test_create_entry_with_session_id(self, client: TestClient):
        """Entries accept and round-trip context.session_id."""
        response = client.post(
            "/apis/intake/v2/workspaces/default/entries",
            json={
                "external_id": "chatcmpl-session",
                "data": {"request": {"model": "gpt-4", "messages": []}, "response": {"choices": []}},
                "context": {
                    "app": "default/test-app",
                    "task": "chat",
                    "session_id": "harbor-session-xyz",
                },
            },
        )
        assert response.status_code == 201
        assert response.json()["context"]["session_id"] == "harbor-session-xyz"

    @pytest.mark.skip(
        reason="Nested JSON filtering requires PostgreSQL JSONB support; SQLite tests use JSON which lacks this functionality"
    )
    def test_filter_entries_by_session_id(self, client: TestClient):
        """Filter entries by session_id (matches the Harbor exporter lookup pattern)."""
        for i in range(2):
            client.post(
                "/apis/intake/v2/workspaces/default/entries",
                json={
                    "external_id": f"chatcmpl-session-filter-{i}",
                    "data": {"request": {"model": "gpt-4", "messages": []}, "response": {"choices": []}},
                    "context": {
                        "app": "default/test-app",
                        "task": "chat",
                        "session_id": "harbor-session-A",
                    },
                },
            )

        response = client.get("/apis/intake/v2/workspaces/default/entries?filter[context][session_id]=harbor-session-A")
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) >= 2
        for entry in data["data"]:
            assert entry["context"]["session_id"] == "harbor-session-A"

    def test_add_evaluator_result_event_to_entry(self, client: TestClient):
        """Evaluator-result events are accepted, stored, and not synced into user_rating."""
        client.post(
            "/apis/intake/v2/workspaces/default/entries",
            json={
                "external_id": "chatcmpl-eval",
                "data": {"request": {"model": "gpt-4", "messages": []}, "response": {"choices": []}},
                "context": {"app": "default/test-app", "task": "chat"},
            },
        )

        response = client.post(
            "/apis/intake/v2/workspaces/default/entries/external:chatcmpl-eval/events",
            json={
                "events": [
                    {
                        "event_type": "evaluator_result",
                        "name": "harbor.verifier",
                        "score": 0.875,
                        "metadata": {"trial_name": "trial-1"},
                    }
                ]
            },
        )
        assert response.status_code == 200
        data = response.json()
        eval_events = [e for e in data["events"] if e["event_type"] == "evaluator_result"]
        assert len(eval_events) == 1
        assert eval_events[0]["name"] == "harbor.verifier"
        assert eval_events[0]["score"] == 0.875
        assert eval_events[0]["metadata"] == {"trial_name": "trial-1"}
        # Evaluator results must not bleed into user_rating (that's user_feedback's job).
        assert data.get("user_rating") in (None, {}) or all(
            data["user_rating"].get(k) is None for k in ("thumb", "rating", "opinion")
        )

    def test_add_evaluator_result_event_with_string_score(self, client: TestClient):
        """Evaluator-result score accepts a string label (e.g., 'pass'/'fail')."""
        client.post(
            "/apis/intake/v2/workspaces/default/entries",
            json={
                "external_id": "chatcmpl-eval-str",
                "data": {"request": {"model": "gpt-4", "messages": []}, "response": {"choices": []}},
                "context": {"app": "default/test-app", "task": "chat"},
            },
        )

        response = client.post(
            "/apis/intake/v2/workspaces/default/entries/external:chatcmpl-eval-str/events",
            json={
                "events": [
                    {
                        "event_type": "evaluator_result",
                        "name": "auditor.pii_probe",
                        "score": "pass",
                    }
                ]
            },
        )
        assert response.status_code == 200
        eval_events = [e for e in response.json()["events"] if e["event_type"] == "evaluator_result"]
        assert eval_events[0]["score"] == "pass"

    def test_create_entry_with_full_usage(self, client: TestClient):
        """POST with a fully-populated usage block round-trips through GET."""
        usage_in = {
            "model": "gpt-4o",
            "started_at": "2026-04-30T15:00:00Z",
            "ended_at": "2026-04-30T15:00:01.840000Z",
            "latency_ms": 1840,
            "cost_usd": 0.0034,
            "cost_input_usd": 0.0023,
            "cost_output_usd": 0.0011,
            "input_tokens": 120,
            "output_tokens": 35,
            "cached_tokens": 64,
        }
        response = client.post(
            "/apis/intake/v2/workspaces/default/entries",
            json={
                "external_id": "chatcmpl-usage-full",
                "data": {
                    "request": {"model": "gpt-4o", "messages": [{"role": "user", "content": "hi"}]},
                    "response": {"choices": [{"message": {"role": "assistant", "content": "hello"}}]},
                },
                "usage": usage_in,
                "context": {"app": "default/test-app", "task": "chat"},
            },
        )
        assert response.status_code == 201, response.json()
        body = response.json()
        for key in (
            "model",
            "latency_ms",
            "cost_usd",
            "cost_input_usd",
            "cost_output_usd",
            "input_tokens",
            "output_tokens",
            "cached_tokens",
        ):
            assert body["usage"][key] == usage_in[key]
        # Datetimes round-trip as ISO strings — exact format may vary, so parse and compare.
        assert datetime.fromisoformat(body["usage"]["started_at"].replace("Z", "+00:00")) == datetime.fromisoformat(
            usage_in["started_at"].replace("Z", "+00:00")
        )
        assert datetime.fromisoformat(body["usage"]["ended_at"].replace("Z", "+00:00")) == datetime.fromisoformat(
            usage_in["ended_at"].replace("Z", "+00:00")
        )

        get_response = client.get("/apis/intake/v2/workspaces/default/entries/external:chatcmpl-usage-full")
        assert get_response.status_code == 200
        assert get_response.json()["usage"]["model"] == usage_in["model"]
        assert get_response.json()["usage"]["cost_usd"] == usage_in["cost_usd"]

    def test_create_entry_with_partial_usage(self, client: TestClient):
        """Usage fields are individually optional — partial blocks are accepted."""
        response = client.post(
            "/apis/intake/v2/workspaces/default/entries",
            json={
                "external_id": "chatcmpl-usage-partial",
                "data": {
                    "request": {"model": "gpt-4o", "messages": []},
                    "response": {"choices": []},
                },
                "usage": {"model": "gpt-4o", "cost_usd": 0.0012},
                "context": {"app": "default/test-app", "task": "chat"},
            },
        )
        assert response.status_code == 201, response.json()
        usage = response.json()["usage"]
        assert usage["model"] == "gpt-4o"
        assert usage["cost_usd"] == 0.0012
        assert usage["latency_ms"] is None
        assert usage["input_tokens"] is None

    def test_create_entry_without_usage(self, client: TestClient):
        """Usage is optional — entries without it serialize with usage == None."""
        response = client.post(
            "/apis/intake/v2/workspaces/default/entries",
            json={
                "external_id": "chatcmpl-usage-absent",
                "data": {
                    "request": {"model": "gpt-4o", "messages": []},
                    "response": {"choices": []},
                },
                "context": {"app": "default/test-app", "task": "chat"},
            },
        )
        assert response.status_code == 201, response.json()
        assert response.json()["usage"] is None

    def test_usage_rejects_negative_values(self, client: TestClient):
        """Latency/cost/token fields are constrained ≥ 0."""
        response = client.post(
            "/apis/intake/v2/workspaces/default/entries",
            json={
                "external_id": "chatcmpl-usage-bad",
                "data": {
                    "request": {"model": "gpt-4o", "messages": []},
                    "response": {"choices": []},
                },
                "usage": {"latency_ms": -1},
                "context": {"app": "default/test-app", "task": "chat"},
            },
        )
        assert response.status_code == 422

    def test_update_entry_usage(self, client: TestClient):
        """PATCH updates usage independently from data."""
        client.post(
            "/apis/intake/v2/workspaces/default/entries",
            json={
                "external_id": "chatcmpl-usage-patch",
                "data": {
                    "request": {"model": "gpt-4o", "messages": []},
                    "response": {"choices": []},
                },
                "usage": {"model": "gpt-4o", "cost_usd": 0.001},
                "context": {"app": "default/test-app", "task": "chat"},
            },
        )

        patch_response = client.patch(
            "/apis/intake/v2/workspaces/default/entries/external:chatcmpl-usage-patch",
            json={
                "usage": {"model": "gpt-4o", "cost_usd": 0.005, "input_tokens": 200},
            },
        )
        assert patch_response.status_code == 200, patch_response.json()
        usage = patch_response.json()["usage"]
        assert usage["cost_usd"] == 0.005
        assert usage["input_tokens"] == 200

    @pytest.mark.skip(
        reason="Nested JSON filtering requires PostgreSQL JSONB support; SQLite tests use JSON which lacks this functionality"
    )
    def test_filter_entries_by_usage_model(self, client: TestClient):
        """Filter entries by usage.model (production / Postgres only)."""
        for served in ("gpt-4o", "gpt-4o-mini"):
            client.post(
                "/apis/intake/v2/workspaces/default/entries",
                json={
                    "external_id": f"chatcmpl-tm-{served}",
                    "data": {
                        "request": {"model": "gpt-4o", "messages": []},
                        "response": {"choices": []},
                    },
                    "usage": {"model": served},
                    "context": {"app": "default/test-app", "task": "chat"},
                },
            )

        response = client.get("/apis/intake/v2/workspaces/default/entries?filter[model]=gpt-4o-mini")
        assert response.status_code == 200
        entries = response.json()["data"]
        assert len(entries) >= 1
        for entry in entries:
            assert entry["usage"]["model"] == "gpt-4o-mini"
