# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Tests for CustomizerService."""

import pytest
from nmp.customizer.service import CustomizerService


class TestCustomizerService:
    """Tests for CustomizerService class."""

    def test_service_name(self):
        """Test service has correct name."""
        service = CustomizerService()
        assert service.name == "customization"

    def test_service_module_name(self):
        """Test service has correct module name."""
        service = CustomizerService()
        assert service.module_name == "nmp.customizer"

    def test_service_title(self):
        """Test service title."""
        service = CustomizerService()
        assert service.title == "NeMo Customizer Microservice"

    def test_service_description(self):
        """Test service description."""
        service = CustomizerService()
        assert "fine-tuning" in service.description.lower()

    def test_get_routers(self):
        """Test get_routers returns routers."""
        service = CustomizerService()
        routers = service.get_routers()

        assert len(routers) == 1
        # Jobs router (prefix is relative to service mount; platform adds /apis/customizer)
        assert routers[0].tag == "Customizer"

    def test_app_creation(self):
        """Test app is created successfully."""
        service = CustomizerService()
        app = service.app

        assert app is not None
        assert app.title == "NeMo Customizer Microservice"


class TestCustomizerEndpoints:
    """Tests for customizer API endpoints."""

    @pytest.fixture
    def client(self):
        """Create test client for CustomizerService."""
        from fastapi.testclient import TestClient

        service = CustomizerService()
        return TestClient(service.app)

    def test_openapi_spec_available(self, client):
        """Test OpenAPI spec is available."""
        response = client.get("/openapi.json")

        assert response.status_code == 200
        spec = response.json()
        assert "paths" in spec
        assert "components" in spec

    def test_v2_customization_jobs_in_spec(self, client):
        """Test /v2/customization/jobs is in OpenAPI spec."""
        response = client.get("/openapi.json")
        assert response.status_code == 200

        spec = response.json()
        paths = spec.get("paths", {})

        assert "/v2/workspaces/{workspace}/jobs" in paths
        assert "post" in paths["/v2/workspaces/{workspace}/jobs"]
        assert "get" in paths["/v2/workspaces/{workspace}/jobs"]
