# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import sys
from pathlib import Path
from typing import Generator

# When pytest is invoked from the repo root, site-packages order can resolve `nmp`
# to sdk/python/nemo-platform/src/nmp before services/evaluator/src/nmp. Evaluator
# tests must use the service tree (source of truth for app.values, APIs, etc.).
_EVALUATOR_SRC = Path(__file__).resolve().parents[1] / "src"
if str(_EVALUATOR_SRC) not in sys.path:
    sys.path.insert(0, str(_EVALUATOR_SRC))

from nemo_platform.types.jobs import PlatformJobResponse  # noqa: E402

# Add tests directory to sys.path so cross-test-file imports work
# when running from the service directory (e.g., `cd services/evaluator && pytest`)
_TESTS_DIR = Path(__file__).parent
if str(_TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(_TESTS_DIR))

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from nmp.common.entities.client import EntityClient  # noqa: E402
from nmp.evaluator.api.v2.benchmarks.manager import BenchmarksManager  # noqa: E402
from nmp.evaluator.service import EvaluatorService  # noqa: E402
from nmp.testing import create_test_client  # noqa: E402
from pydantic import BaseModel  # noqa: E402

# ============================================================================
# Pytest Hooks
# ============================================================================


def pytest_collection_modifyitems(config, items):
    """
    Modify test items during collection.

    Auto-marks tests based on their location:
    - Tests in e2e/ directories get the 'e2e' marker
    - Tests in integration/ directories get the 'integration' marker
    - Tests without category markers get the 'unit' marker
    """
    # Category markers that determine test type
    category_markers = {"unit", "e2e", "integration", "regression", "canary", "slow", "skip_in_ci"}

    for item in items:
        # Get current marker names
        marker_names = {marker.name for marker in item.iter_markers()}

        # Auto-mark tests in e2e directories
        if "/e2e/" in str(item.fspath):
            if "e2e" not in marker_names:
                item.add_marker(pytest.mark.e2e)
                marker_names.add("e2e")

        # Auto-mark tests in integration directories
        elif "/integration/" in str(item.fspath):
            if "integration" not in marker_names:
                item.add_marker(pytest.mark.integration)
                marker_names.add("integration")

        # Auto-mark tests without category markers as unit tests
        if not marker_names.intersection(category_markers):
            item.add_marker(pytest.mark.unit)


@pytest.fixture
def client(load_incluster_config):
    """Fixture for initializing a test client with in-memory entities."""
    # Include projects used in tests (new, proj-big, proj-llm)
    projects = ["default/test-project", "default/new", "default/proj-big", "default/proj-llm"]
    with create_test_client(
        EvaluatorService,
        client_type=TestClient,
        projects=projects,
    ) as tc:
        yield tc


@pytest.fixture
def mock_sdk():
    """Mock SDK instance for tests.

    Provides a consistent mock SDK with secrets.access and secrets.retrieve configured
    for use across all evaluator test modules. This fixture eliminates duplication
    and ensures consistent behavior.
    """
    from unittest import mock
    from unittest.mock import MagicMock

    sdk = mock.AsyncMock()
    # Mock secrets.access and secrets.retrieve to return a mock secret
    mock_secret = MagicMock()
    mock_secret.value = "mock-api-key"
    sdk.secrets.access = mock.AsyncMock(return_value=mock_secret)
    sdk.secrets.retrieve = mock.AsyncMock(return_value=mock_secret)

    def mock_sdk_jobs_create(**kwargs):
        """Return a job response with preserved job spec and mock values"""
        spec = kwargs.get("spec")
        assert isinstance(spec, BaseModel)
        kwargs.update(
            {
                "id": "mock-id",
                "attempt_id": "mock-attempt-id",
                "fileset": "default/mock-id",
                "name": kwargs.get("name", "mock-name"),
                "status": "pending",
                "spec": spec.model_dump(mode="json", exclude_none=True),
            }
        )
        return PlatformJobResponse.model_validate(kwargs)

    sdk.jobs.create.side_effect = mock_sdk_jobs_create

    return sdk


@pytest.fixture
def mock_entity_client() -> Generator[EntityClient, None, None]:
    """Real EntityClient backed by in-memory storage for integration-style testing."""
    workspaces = ["default", "system", "production"]
    with create_test_client(client_type=EntityClient, workspaces=workspaces) as client:
        yield client


@pytest.fixture
def benchmarks_manager(mock_entity_client) -> BenchmarksManager:
    """BenchmarksManager instance with mocked EntityClient."""
    return BenchmarksManager(mock_entity_client)
