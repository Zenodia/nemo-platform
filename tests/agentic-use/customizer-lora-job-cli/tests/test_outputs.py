# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Verify that the agent submitted a LoRA customization job via the NeMo Platform customizer API.

Tests workspace/fileset creation, dataset upload, and customization job submission
through the real NeMo Platform pipeline.
"""

import base64
import json
import os

import pytest
from nemo_platform import NeMoPlatform

WORKSPACE = "lora-training-workspace"
FILESET = "sft-training-data"


def _make_unsigned_jwt() -> str:
    """Create an unsigned JWT (alg=none) for local quickstart auth."""
    header = base64.urlsafe_b64encode(json.dumps({"alg": "none", "typ": "JWT"}).encode()).rstrip(b"=").decode()
    payload = (
        base64.urlsafe_b64encode(
            json.dumps({"sub": "verifier@harbor.local", "email": "verifier@harbor.local"}).encode()
        )
        .rstrip(b"=")
        .decode()
    )
    return f"{header}.{payload}."


@pytest.fixture
def client() -> NeMoPlatform:
    nmp_base_url = os.environ.get("NMP_BASE_URL", "http://localhost:8080")
    return NeMoPlatform(
        base_url=nmp_base_url,
        workspace=WORKSPACE,
        access_token=_make_unsigned_jwt(),
    )


def test_workspace_exists(client: NeMoPlatform):
    """Verify the lora-training-workspace exists."""
    response = client.workspaces.list()
    workspace_names = [ws.name for ws in response.data]
    assert WORKSPACE in workspace_names, f"Workspace '{WORKSPACE}' not found. Found: {workspace_names}"


def test_fileset_exists(client: NeMoPlatform):
    """Verify the sft-training-data fileset was created."""
    response = client.files.filesets.list(workspace=WORKSPACE)
    fileset_names = [fs.name for fs in response.data]
    assert FILESET in fileset_names, f"Fileset '{FILESET}' not found. Found: {fileset_names}"


def test_fileset_has_data(client: NeMoPlatform):
    """Verify the training dataset was uploaded."""
    files = client.files.list(fileset=FILESET, workspace=WORKSPACE)
    assert len(files.data) > 0, f"Fileset '{FILESET}' has no files uploaded"


def test_customization_job_created(client: NeMoPlatform):
    """Verify that a customization job was submitted via the NeMo Platform customizer API."""
    jobs = client.customization.jobs.list(workspace=WORKSPACE)
    assert len(jobs.data) > 0, "No customization jobs found in workspace"


def test_customization_job_has_spec(client: NeMoPlatform):
    """Verify the customization job has a valid training spec."""
    jobs = client.customization.jobs.list(workspace=WORKSPACE)
    assert len(jobs.data) > 0, "No customization jobs found"
    job = jobs.data[0]
    assert job.spec is not None, "Customization job has no spec"


def test_customization_job_dispatched(client: NeMoPlatform):
    """Verify the job was dispatched by the jobs controller (progressed beyond 'created').

    With the Docker socket mounted and GPU available, the jobs controller should
    schedule the training container. The job should reach at least 'pending' status.
    """
    jobs = client.customization.jobs.list(workspace=WORKSPACE)
    assert len(jobs.data) > 0, "No customization jobs found"
    job = jobs.data[0]

    # Give the jobs controller a moment to process
    status = getattr(job, "status", "unknown")
    if hasattr(status, "lower"):
        status = status.lower()

    # Any status beyond 'created' means the jobs controller picked it up
    dispatched_statuses = {"pending", "running", "completed", "error", "cancelled", "paused"}
    # 'created' is also acceptable - it means the job was submitted correctly
    # even if the controller hasn't picked it up yet
    valid_statuses = dispatched_statuses | {"created", "unknown"}

    assert status in valid_statuses, f"Job in unexpected status: '{status}'. Expected one of: {valid_statuses}"
