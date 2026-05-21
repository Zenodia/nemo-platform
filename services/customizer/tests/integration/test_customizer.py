# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Integration tests for the customizer service.

These tests verify:
- Customizer service is properly registered in the platform
- Job endpoints are available in OpenAPI spec
- Jobs can be created (though training execution is stubbed)

Uses the create_test_client pattern for fast in-memory testing.
"""

from typing import Generator

import pytest
from fastapi.testclient import TestClient
from nemo_platform import NeMoPlatform
from nmp.customizer.service import CustomizerService
from nmp.testing.client import create_test_client

# Default workspace for tests
DEFAULT_WORKSPACE = "default"

# Skip reason for job execution tests
JOBS_SKIP_REASON = "TODO: Need new pattern for configuring jobs SDK to use ASGI transport"


@pytest.fixture(scope="module")
def http_client() -> Generator[TestClient, None, None]:
    """TestClient with CustomizerService."""
    with create_test_client(
        CustomizerService,
        client_type=TestClient,
    ) as client:
        yield client


@pytest.fixture(scope="module")
def sdk(http_client: TestClient) -> NeMoPlatform:
    """SDK client backed by the test client."""
    return NeMoPlatform(base_url="http://testserver", http_client=http_client)


class TestCustomizerInPlatform:
    """Tests for customizer service registration in platform."""

    def test_customizer_routes_in_openapi(self, sdk: NeMoPlatform):
        """Test that customizer routes are in OpenAPI spec."""
        response = sdk._client.get("/openapi.json")
        assert response.status_code == 200

        spec = response.json()
        paths = spec.get("paths", {})

        # Verify customizer job endpoints are present
        assert "/apis/customization/v2/workspaces/{workspace}/jobs" in paths
        assert "post" in paths["/apis/customization/v2/workspaces/{workspace}/jobs"]
        assert "get" in paths["/apis/customization/v2/workspaces/{workspace}/jobs"]


class TestCustomizerJobsOpenAPI:
    """Tests for customizer job endpoints in OpenAPI spec."""

    def test_jobs_endpoint_in_openapi(self, sdk: NeMoPlatform):
        """Test that /apis/customization/v2/workspaces/{workspace}/jobs is documented in OpenAPI spec."""
        response = sdk._client.get("/openapi.json")
        assert response.status_code == 200

        spec = response.json()
        paths = spec.get("paths", {})

        assert "/apis/customization/v2/workspaces/{workspace}/jobs" in paths
        jobs_path = paths["/apis/customization/v2/workspaces/{workspace}/jobs"]

        # Verify CRUD methods
        assert "post" in jobs_path, "POST method missing from jobs endpoint"
        assert "get" in jobs_path, "GET method missing from jobs endpoint"

    def test_single_job_endpoint_in_openapi(self, sdk: NeMoPlatform):
        """Test that single job endpoint is documented in OpenAPI spec."""
        response = sdk._client.get("/openapi.json")
        assert response.status_code == 200

        spec = response.json()
        paths = spec.get("paths", {})

        # Path uses {name} not {id}
        assert "/apis/customization/v2/workspaces/{workspace}/jobs/{name}" in paths
        job_path = paths["/apis/customization/v2/workspaces/{workspace}/jobs/{name}"]

        # Verify methods for single job
        assert "get" in job_path, "GET method missing from single job endpoint"
        assert "delete" in job_path, "DELETE method missing from single job endpoint"

    def test_jobs_schema_in_openapi(self, sdk: NeMoPlatform):
        """Test that job schemas are in OpenAPI spec."""
        response = sdk._client.get("/openapi.json")
        assert response.status_code == 200

        spec = response.json()
        schemas = spec.get("components", {}).get("schemas", {})

        # Verify job-related schemas are present
        # Request schema is CustomizationJobRequest, response schema is CustomizationJob
        assert "CustomizationJobRequest" in schemas
        assert "CustomizationJob" in schemas

    def test_job_request_schema_has_required_fields(self, sdk: NeMoPlatform):
        """Test that CustomizationJobRequest schema has expected fields."""
        response = sdk._client.get("/openapi.json")
        assert response.status_code == 200

        spec = response.json()
        schemas = spec.get("components", {}).get("schemas", {})
        job_request = schemas.get("CustomizationJobRequest", {})
        properties = job_request.get("properties", {})

        # Should have spec property (contains the CustomizationJobInput)
        assert "spec" in properties, "spec field missing from CustomizationJobRequest"


class TestCustomizerJobsCreateValidation:
    """Tests for job creation validation (e.g. unsupported training types)."""

    def test_create_job_with_dpo_and_peft_returns_422(self, http_client: TestClient):
        """POST with DPO + PEFT returns 422 because PEFT is not yet supported with DPO."""
        url = f"/apis/customization/v2/workspaces/{DEFAULT_WORKSPACE}/jobs"
        payload = {
            "spec": {
                "model": "default/some-model",
                "training": {
                    "type": "dpo",
                    "peft": {"type": "lora"},
                },
                "dataset": "fileset://default/some-dataset",
            }
        }
        response = http_client.post(url, json=payload)
        assert response.status_code == 422
        detail_str = str(response.json().get("detail", [])).lower()
        assert "not yet supported with dpo" in detail_str
