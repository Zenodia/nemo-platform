# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Tests for export functionality."""

import json
import tempfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


class TestExportsAPI:
    """Tests for exports API endpoints."""

    @pytest.fixture(autouse=True)
    def create_test_data(self, client: TestClient):
        """Create test data for export tests."""
        # Create entries with different contexts
        for i in range(5):
            client.post(
                "/apis/intake/v2/workspaces/default/entries",
                json={
                    "external_id": f"export-entry-{i}",
                    "workspace": "default",
                    "data": {
                        "request": {"model": "gpt-4", "messages": [{"role": "user", "content": f"Question {i}"}]},
                        "response": {"choices": [{"message": {"role": "assistant", "content": f"Answer {i}"}}]},
                    },
                    "context": {
                        "app": "default/test-app",
                        "task": "chat",
                        "thread_id": f"thread_{i % 2}",  # 2 threads
                    },
                },
            )

    def test_preview_export_entries_mode(self, client: TestClient):
        """Test previewing export in entries mode."""
        response = client.post(
            "/apis/intake/v2/workspaces/default/export/preview",
            json={"config": {"filters": {"workspace": "default"}, "limit": 10}},
        )
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "count" in data
        assert data["count"] == 5  # All 5 entries

    def test_preview_export_path_workspace_overrides_config_filter(self, client: TestClient):
        """Test that preview exports use the workspace from the route."""
        response = client.post(
            "/apis/intake/v2/workspaces/default/export/preview",
            json={"config": {"filters": {"workspace": "other"}, "limit": 10}},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 5
        for entry in data["data"]:
            assert entry["workspace"] == "default"

    def test_preview_export_with_limit(self, client: TestClient):
        """Test previewing export with limit."""
        # Test that limit parameter works correctly
        response = client.post(
            "/apis/intake/v2/workspaces/default/export/preview",
            json={"config": {"filters": {"workspace": "default"}, "limit": 3}},
        )
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert data["count"] == 3  # Limited to 3 entries

    def test_export_to_local_file(self, client: TestClient):
        """Test exporting entries to local file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = Path(tmpdir) / "export.jsonl"

            response = client.post(
                "/apis/intake/v2/workspaces/default/export/jobs",
                json={
                    "output_file_url": f"file://{output_file}",
                    "config": {"filters": {"workspace": "default"}, "limit": 10},
                },
            )
            assert response.status_code == 200
            job_data = response.json()
            assert job_data["status"] == "completed"
            assert job_data["status_details"]["entries_count"] == 5

            # Verify file was created and has correct content
            assert output_file.exists()
            with output_file.open() as f:
                lines = f.readlines()
            assert len(lines) == 5

            # Verify messages array was added
            first_entry = json.loads(lines[0])
            assert "messages" in first_entry
            assert len(first_entry["messages"]) == 2  # user + assistant

    def test_get_export_job_status(self, client: TestClient):
        """Test getting export job status."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = Path(tmpdir) / "export.jsonl"

            # Create export job
            response = client.post(
                "/apis/intake/v2/workspaces/default/export/jobs",
                json={
                    "output_file_url": f"file://{output_file}",
                    "config": {"filters": {"workspace": "default"}},
                },
            )
            assert response.status_code == 200
            job_data = response.json()
            job_name = job_data["name"]

            # Get job status
            status_response = client.get(f"/apis/intake/v2/workspaces/default/export/jobs/{job_name}")
            assert status_response.status_code == 200
            status_data = status_response.json()
            assert status_data["name"] == job_name
            assert status_data["status"] == "completed"

    def test_export_with_filters(self, client: TestClient):
        """Test exporting with specific filters (using external_id)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = Path(tmpdir) / "export.jsonl"

            # Export only a specific entry by external_id
            response = client.post(
                "/apis/intake/v2/workspaces/default/export/jobs",
                json={
                    "output_file_url": f"file://{output_file}",
                    "config": {"filters": {"workspace": "default", "external_id": "export-entry-0"}},
                },
            )
            assert response.status_code == 200
            job_data = response.json()
            # Should export 1 entry with the matching external_id
            assert job_data["status_details"]["entries_count"] == 1

    def test_export_invalid_uri(self, client: TestClient):
        """Test that invalid URLs are rejected."""
        response = client.post(
            "/apis/intake/v2/workspaces/default/export/jobs",
            json={"output_file_url": "invalid://bad/uri", "config": {"filters": {"workspace": "default"}}},
        )
        assert response.status_code == 400

    def test_list_export_jobs(self, client: TestClient):
        """Test listing export jobs with pagination."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create multiple export jobs
            job_names = []
            for i in range(3):
                output_file = Path(tmpdir) / f"export_{i}.jsonl"
                response = client.post(
                    "/apis/intake/v2/workspaces/default/export/jobs",
                    json={
                        "output_file_url": f"file://{output_file}",
                        "config": {"filters": {"workspace": "default"}, "limit": 1},
                    },
                )
                assert response.status_code == 200
                job_names.append(response.json()["name"])

            # List export jobs
            response = client.get("/apis/intake/v2/workspaces/default/export/jobs?page=1&page_size=10")
            assert response.status_code == 200
            data = response.json()
            assert "data" in data
            assert "pagination" in data
            assert len(data["data"]) == 3
            assert data["pagination"]["total_results"] == 3

    def test_list_export_jobs_path_workspace_overrides_filter(self, client: TestClient):
        """Test that listing export jobs uses the workspace from the route."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = Path(tmpdir) / "export.jsonl"
            create_response = client.post(
                "/apis/intake/v2/workspaces/default/export/jobs",
                json={
                    "output_file_url": f"file://{output_file}",
                    "config": {"filters": {"workspace": "other"}, "limit": 1},
                },
            )
            assert create_response.status_code == 200
            job_name = create_response.json()["name"]

            response = client.get("/apis/intake/v2/workspaces/default/export/jobs?filter[workspace]=other")
            assert response.status_code == 200
            data = response.json()

            assert any(job["name"] == job_name for job in data["data"])
            for job in data["data"]:
                assert job["workspace"] == "default"

    def test_list_export_jobs_with_pagination(self, client: TestClient):
        """Test listing export jobs with pagination limits."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create 5 export jobs
            for i in range(5):
                output_file = Path(tmpdir) / f"export_{i}.jsonl"
                client.post(
                    "/apis/intake/v2/workspaces/default/export/jobs",
                    json={
                        "output_file_url": f"file://{output_file}",
                        "config": {"filters": {"workspace": "default"}, "limit": 1},
                    },
                )

            # List with page_size=2
            response = client.get("/apis/intake/v2/workspaces/default/export/jobs?page=1&page_size=2")
            assert response.status_code == 200
            data = response.json()
            assert len(data["data"]) == 2
            assert data["pagination"]["total_results"] == 5
            assert data["pagination"]["total_pages"] == 3

            # Get second page
            response = client.get("/apis/intake/v2/workspaces/default/export/jobs?page=2&page_size=2")
            assert response.status_code == 200
            data = response.json()
            assert len(data["data"]) == 2

    def test_list_export_jobs_filter_by_status(self, client: TestClient):
        """Test filtering export jobs by status."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create export jobs (all will be completed after running)
            for i in range(2):
                output_file = Path(tmpdir) / f"export_{i}.jsonl"
                client.post(
                    "/apis/intake/v2/workspaces/default/export/jobs",
                    json={
                        "output_file_url": f"file://{output_file}",
                        "config": {"filters": {"workspace": "default"}, "limit": 1},
                    },
                )

            # Filter by completed status
            response = client.get("/apis/intake/v2/workspaces/default/export/jobs?filter[status]=completed")
            assert response.status_code == 200
            data = response.json()
            # All jobs should be completed (synchronous execution)
            for job in data["data"]:
                assert job["status"] == "completed"

    def test_list_export_jobs_filter_by_name(self, client: TestClient):
        """Test filtering export jobs by name."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create an export job
            output_file = Path(tmpdir) / "export_filter_name.jsonl"
            response = client.post(
                "/apis/intake/v2/workspaces/default/export/jobs",
                json={
                    "output_file_url": f"file://{output_file}",
                    "config": {"filters": {"workspace": "default"}, "limit": 1},
                },
            )
            assert response.status_code == 200
            job_name = response.json()["name"]

            # Filter by exact name
            response = client.get(f"/apis/intake/v2/workspaces/default/export/jobs?filter[name]={job_name}")
            assert response.status_code == 200
            data = response.json()
            assert "data" in data
            assert "pagination" in data
            assert len(data["data"]) == 1
            assert data["data"][0]["name"] == job_name

    def test_list_export_jobs_with_sort(self, client: TestClient):
        """Test sorting export jobs."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create multiple export jobs
            for i in range(3):
                output_file = Path(tmpdir) / f"export_sort_{i}.jsonl"
                client.post(
                    "/apis/intake/v2/workspaces/default/export/jobs",
                    json={
                        "output_file_url": f"file://{output_file}",
                        "config": {"filters": {"workspace": "default"}, "limit": 1},
                    },
                )

            # Sort by created_at descending
            response = client.get("/apis/intake/v2/workspaces/default/export/jobs?sort=-created_at")
            assert response.status_code == 200
            data = response.json()
            assert data["sort"] == "-created_at"
            assert len(data["data"]) == 3
