# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Integration tests for the secrets service.

These tests verify:
- Secret CRUD operations (create, retrieve, list, update, delete)
- Secret access (value retrieval)
- Validation (empty data rejection)

Uses the create_test_client pattern for fast in-memory testing.
"""

import uuid

from fastapi import status
from nemo_platform import APIStatusError, NeMoPlatform
from nmp.common.entities import DEFAULT_WORKSPACE


def short_secret_name(prefix: str) -> str:
    """Generate a short secret name (max 32 chars total)."""
    suffix = uuid.uuid4().hex[:8]
    return f"{prefix[:22]}-{suffix}"


def test_create_secret(sdk: NeMoPlatform):
    secret_name = short_secret_name("testsecret")
    secret_value = "supersecret"
    secret = sdk.secrets.create(workspace=DEFAULT_WORKSPACE, name=secret_name, value=secret_value)
    assert secret.name == secret_name
    # Retrieve the secret
    secret_retrieved = sdk.secrets.retrieve(secret_name, workspace=DEFAULT_WORKSPACE)
    assert secret_retrieved.name == secret.name
    # Access the secret value
    secret_access_resp = sdk.secrets.access(secret_name, workspace=DEFAULT_WORKSPACE)
    assert secret_access_resp.value == secret_value


def test_create_and_list_secrets(sdk: NeMoPlatform):
    secret_name_1 = short_secret_name("secret1")
    secret_name_2 = short_secret_name("secret2")
    secret_data = "somedata"
    sdk.secrets.create(workspace=DEFAULT_WORKSPACE, name=secret_name_1, value=secret_data)
    sdk.secrets.create(workspace=DEFAULT_WORKSPACE, name=secret_name_2, value=secret_data)
    # List secrets and verify order
    # Get first secret first
    list_resp = sdk.secrets.list(workspace=DEFAULT_WORKSPACE)  # sort="created_at"
    secret_names = [secret_ref.name for secret_ref in list_resp.data]
    assert secret_name_1 in secret_names
    assert secret_name_2 in secret_names


def test_create_and_list_secrets_with_pagination(sdk: NeMoPlatform):
    """Test listing secrets with pagination across multiple pages."""
    num_secrets = 25
    secret_data = "paginationtest"

    # Create 25 secrets
    created_secret_names = []
    for i in range(num_secrets):
        secret_name = short_secret_name(f"page{i:02d}")
        sdk.secrets.create(workspace=DEFAULT_WORKSPACE, name=secret_name, value=secret_data)
        created_secret_names.append(secret_name)

    # Now we should be able to list them with pagination and an iterator
    for secret in sdk.secrets.list(workspace=DEFAULT_WORKSPACE):
        if secret.name in created_secret_names:
            created_secret_names.remove(secret.name)
    assert len(created_secret_names) == 0, "Not all created secrets were found in the list"


def test_create_secret_with_empty_data(sdk: NeMoPlatform):
    secret_name = short_secret_name("emptydata")
    try:
        sdk.secrets.create(workspace=DEFAULT_WORKSPACE, name=secret_name, value="")
        assert False, "Expected an error when creating a secret with empty data"
    except APIStatusError as e:
        assert e.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_create_and_delete_secret(sdk: NeMoPlatform):
    secret_name = short_secret_name("secret1")
    secret_value = "deletesecret"
    create_resp = sdk.secrets.create(workspace=DEFAULT_WORKSPACE, name=secret_name, value=secret_value)
    assert secret_name == create_resp.name
    sdk.secrets.delete(secret_name, workspace=DEFAULT_WORKSPACE)
    try:
        sdk.secrets.retrieve(secret_name, workspace=DEFAULT_WORKSPACE)
        assert False, "Expected an error when retrieving a deleted secret"
    except APIStatusError as e:
        assert e.status_code == status.HTTP_404_NOT_FOUND


def test_update_secret(sdk: NeMoPlatform):
    secret_name = short_secret_name("update")
    secret_value = "initialvalue"
    create_resp = sdk.secrets.create(workspace=DEFAULT_WORKSPACE, name=secret_name, value=secret_value)
    assert secret_name == create_resp.name
    assert create_resp.description is None
    # Update the secret
    updated_secret = sdk.secrets.update(secret_name, workspace=DEFAULT_WORKSPACE, description="Updated description")
    assert updated_secret.description == "Updated description"
    updated_secret = sdk.secrets.update(secret_name, workspace=DEFAULT_WORKSPACE, description="", value="newvalue")
    assert updated_secret.description == ""
    assert updated_secret.name == secret_name
    # Access the updated secret value
    secret_access_resp = sdk.secrets.access(secret_name, workspace=DEFAULT_WORKSPACE)
    assert secret_access_resp.value == "newvalue"


def test_rotate_encryption_keys(sdk: NeMoPlatform):
    """Test that secret rotation via SDK preserves secret data.

    This test verifies:
    1. Secrets can be created with the SDK
    2. The rotate_encryption_keys admin endpoint can be called via SDK
    3. After rotation, all secrets remain accessible with their original values
    """
    # Create multiple secrets across workspaces
    secrets_data = [
        (short_secret_name("rotate1"), "secret-value-1"),
        (short_secret_name("rotate2"), "secret-value-2"),
        (short_secret_name("rotate3"), "another-secret-value"),
    ]

    # Create secrets
    for secret_name, secret_value in secrets_data:
        sdk.secrets.create(workspace=DEFAULT_WORKSPACE, name=secret_name, value=secret_value)

    # Verify secrets are accessible before rotation
    for secret_name, expected_value in secrets_data:
        access_resp = sdk.secrets.access(secret_name, workspace=DEFAULT_WORKSPACE)
        assert access_resp.value == expected_value

    # Rotate encryption keys
    sdk.secrets.admin.rotate_encryption_keys()

    # Verify all secrets are still accessible with original values after rotation
    for secret_name, expected_value in secrets_data:
        access_resp = sdk.secrets.access(secret_name, workspace=DEFAULT_WORKSPACE)
        assert access_resp.value == expected_value, f"Secret {secret_name} value changed after rotation"


def test_rotate_encryption_keys_idempotent(sdk: NeMoPlatform):
    """Test that calling rotate_encryption_keys multiple times is safe.

    This test verifies that rotation is idempotent - calling it multiple
    times should not corrupt data or cause errors.
    """
    # Create a secret
    secret_name = short_secret_name("idempotent")
    secret_value = "idempotent-test-value"
    sdk.secrets.create(workspace=DEFAULT_WORKSPACE, name=secret_name, value=secret_value)

    # Rotate multiple times
    for _ in range(3):
        sdk.secrets.admin.rotate_encryption_keys()

    # Secret should still be accessible with original value
    access_resp = sdk.secrets.access(secret_name, workspace=DEFAULT_WORKSPACE)
    assert access_resp.value == secret_value
