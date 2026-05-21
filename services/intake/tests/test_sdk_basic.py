# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Simple test using sdk_client fixture with the actual Nemo SDK.

TODO(v2): These tests require the nemo_platform SDK client fixture.
See services/core/jobs/tests/conftest.py for the pattern:
1. Create an AsyncClient with ASGITransport pointing to the test app
2. Create AsyncNeMoPlatform with that client
3. Use the SDK methods to interact with the service

Currently skipped until nemo_platform is added as a test dependency
and the sdk_client fixture is implemented in conftest.py.
"""

import pytest


# TODO(v2): Implement sdk_client fixture following jobs service pattern
# See services/core/jobs/tests/conftest.py for reference
@pytest.mark.skip(
    reason="SDK client fixture not yet implemented - see services/core/jobs/tests/conftest.py for pattern"
)
def test_create_app_with_sdk_client(sdk_client):
    """Test creating an app using the actual Nemo SDK."""
    # Create app using SDK
    sdk_client.intake.apps.create(name="test-app", workspace="default", description="Test app")

    # Retrieve using SDK
    app = sdk_client.intake.apps.retrieve(workspace="default", app_name="test-app")

    assert app.name == "test-app"
    assert app.workspace == "default"
    assert app.description == "Test app"


# TODO(v2): Implement sdk_client fixture following jobs service pattern
@pytest.mark.skip(
    reason="SDK client fixture not yet implemented - see services/core/jobs/tests/conftest.py for pattern"
)
def test_complete_workflow_with_tasks_and_entries(sdk_client):
    """Test complete workflow: create app, tasks, entries, and filtering."""

    # Create app
    sdk_client.intake.apps.create(name="workflow-app", workspace="default", description="Workflow test app")

    # Create two tasks
    sdk_client.intake.apps.tasks.create(
        workspace="default", app_name="workflow-app", name="chat-task", description="Chat task for testing"
    )

    sdk_client.intake.apps.tasks.create(
        workspace="default", app_name="workflow-app", name="completion-task", description="Completion task for testing"
    )

    # Create 3 entries for first task (chat-task)
    for i in range(3):
        sdk_client.intake.entries.create(
            external_id=f"chat-entry-{i}",
            workspace="default",
            data={
                "request": {"model": "test-model", "messages": [{"role": "user", "content": f"Chat question {i}"}]},
                "response": {"choices": [{"message": {"role": "assistant", "content": f"Chat answer {i}"}}]},
            },
            context={"app": "default/workflow-app", "task": "chat-task"},
        )

    # Create 3 entries for second task (completion-task)
    for i in range(3):
        sdk_client.intake.entries.create(
            external_id=f"completion-entry-{i}",
            workspace="default",
            data={
                "request": {"model": "test-model", "messages": [{"role": "user", "content": f"Completion prompt {i}"}]},
                "response": {"choices": [{"message": {"role": "assistant", "content": f"Completion result {i}"}}]},
            },
            context={"app": "default/workflow-app", "task": "completion-task"},
        )

    # List all entries
    all_entries = sdk_client.intake.entries.list(page=1, page_size=20)
    assert len(all_entries.data) >= 6  # At least our 6 entries

    # Filter entries by workspace
    default_entries = sdk_client.intake.entries.list(page=1, page_size=20, filter={"workspace": "default"})
    assert len(default_entries.data) >= 6  # At least our 6 entries in default workspace

    # Verify we can access entry details
    for entry in default_entries.data[:3]:  # Check first 3
        assert entry.workspace == "default"
        assert entry.context.app == "default/workflow-app"
        assert entry.context.task in ["chat-task", "completion-task"]
        assert "entry" in entry.external_id
