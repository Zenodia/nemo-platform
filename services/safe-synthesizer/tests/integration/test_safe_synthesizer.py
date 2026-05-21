# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Integration tests for the safe-synthesizer service.

These tests verify:
- Health endpoint functionality
- Job API routes are properly registered in OpenAPI
- Job schemas (SafeSynthesizerJobConfig) are present in OpenAPI
- List jobs endpoint works
- Job creation and completion lifecycle

Uses the create_test_client pattern for fast in-memory testing.
"""

import time
from typing import Generator

import pytest
from fastapi.testclient import TestClient
from nemo_platform import NeMoPlatform
from nmp.safe_synthesizer.service import SafeSynthesizerService
from nmp.testing.client import create_test_client

# Default workspace for tests
DEFAULT_WORKSPACE = "default"

# Skip reason for job execution tests
JOBS_SKIP_REASON = "TODO: Need new pattern for configuring jobs SDK to use ASGI transport"


@pytest.fixture(scope="module")
def http_client() -> Generator[TestClient, None, None]:
    """TestClient with SafeSynthesizerService."""
    with create_test_client(
        SafeSynthesizerService,
        client_type=TestClient,
    ) as client:
        yield client


@pytest.fixture(scope="module")
def sdk(http_client: TestClient) -> NeMoPlatform:
    """SDK client backed by the test client."""
    return NeMoPlatform(base_url="http://testserver", http_client=http_client)


class TestSafeSynthesizerHealth:
    """Tests for safe-synthesizer health endpoints."""

    @pytest.mark.integration
    def test_health_endpoint(self, sdk: NeMoPlatform):
        """Test that health endpoint returns OK."""
        response = sdk._client.get("/health")
        assert response.status_code == 200


class TestSafeSynthesizerJobs:
    """Tests for the safe-synthesizer job endpoints."""

    @pytest.mark.integration
    def test_jobs_routes_in_openapi(self, sdk: NeMoPlatform):
        """Test that job endpoints are documented in OpenAPI spec."""
        response = sdk._client.get("/openapi.json")
        assert response.status_code == 200

        spec = response.json()
        paths = spec.get("paths", {})

        # Verify job endpoints are present
        assert "/v2/workspaces/{workspace}/safe-synthesizer/jobs" in paths
        assert "post" in paths["/v2/workspaces/{workspace}/safe-synthesizer/jobs"]
        assert "get" in paths["/v2/workspaces/{workspace}/safe-synthesizer/jobs"]

    @pytest.mark.integration
    def test_jobs_schema_in_openapi(self, sdk: NeMoPlatform):
        """Test that SafeSynthesizer job schemas are in OpenAPI spec."""
        response = sdk._client.get("/openapi.json")
        assert response.status_code == 200

        spec = response.json()
        schemas = spec.get("components", {}).get("schemas", {})

        # Verify SafeSynthesizer job-related schemas are present
        # job_route_factory creates {job_type}JobRequest, and job_type="SafeSynthesizer"
        assert "SafeSynthesizerJobRequest" in schemas

    @pytest.mark.skip(reason=JOBS_SKIP_REASON)
    @pytest.mark.integration
    def test_list_jobs(self, sdk: NeMoPlatform):
        """Test listing jobs."""
        response = sdk._client.get(f"/v2/workspaces/{DEFAULT_WORKSPACE}/safe-synthesizer/jobs")
        assert response.status_code == 200, f"List jobs failed: {response.text}"

        data = response.json()
        assert "data" in data  # Paginated response

    @pytest.mark.skip(reason=JOBS_SKIP_REASON)
    @pytest.mark.integration
    def test_create_job_and_wait_for_completion(self, sdk: NeMoPlatform):
        """Test that a safe-synthesizer job can be created and reaches completed status."""
        job_request = {
            "name": "e2e-safe-synthesizer-job",
            "spec": {
                "data_source": "test://e2e-test-data",
                "config": {
                    "enable_synthesis": True,
                    "enable_replace_pii": False,
                },
            },
        }

        # Create the job
        response = sdk._client.post(
            f"/v2/workspaces/{DEFAULT_WORKSPACE}/safe-synthesizer/jobs",
            json=job_request,
        )
        assert response.status_code == 201, f"Create job failed: {response.text}"
        job = response.json()

        assert job["id"] is not None
        assert job["status"] == "created"

        # Poll until job reaches terminal status
        timeout = 60
        start = time.time()
        terminal_statuses = {"completed", "error", "cancelled", "paused"}

        while time.time() - start < timeout:
            response = sdk._client.get(f"/v2/workspaces/{DEFAULT_WORKSPACE}/safe-synthesizer/jobs/{job['id']}")
            assert response.status_code == 200
            job = response.json()
            if job["status"] in terminal_statuses:
                break
            time.sleep(1)
        else:
            raise TimeoutError(f"Job {job['id']} did not reach terminal status within {timeout}s")

        assert job["status"] == "completed", f"Expected job to complete, got status: {job['status']}"
