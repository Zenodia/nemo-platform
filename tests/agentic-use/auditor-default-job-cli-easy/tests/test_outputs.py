# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Verify that the agent created an audit target and launched a default audit
job via CLI.

The inference provider is pre-configured by the Dockerfile setup script.
Tests focus on the auditor workflow: target creation, job launch, status check.

Tests:
- Audit target exists and references a model through the pre-configured provider
- Audit job was created with valid spec referencing default config and target
- Agent trajectory shows config discovery and job status checking
"""

import base64
import json
import os

import pytest
from nemo_platform import NeMoPlatform
from trace_reader import get_session

WORKSPACE = "default"
TARGET_NAME = "audit-target"
JOB_NAME = "default-audit-job"


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
    return NeMoPlatform(base_url=nmp_base_url, workspace=WORKSPACE, access_token=_make_unsigned_jwt())


# --- Audit target checks ---


def test_audit_target_exists(client: NeMoPlatform) -> None:
    """Verify the audit target was created."""
    targets = client.audit.targets.list()
    target_names = [t.name for t in targets]
    assert TARGET_NAME in target_names, f"Target '{TARGET_NAME}' not found. Found: {target_names}"


def test_audit_target_model(client: NeMoPlatform) -> None:
    """Verify the audit target references the correct model."""
    target = client.audit.targets.retrieve(TARGET_NAME)
    assert target.model is not None and len(target.model) > 0, f"Target '{TARGET_NAME}' has no model configured"
    print(f"Target model: {target.model}, type: {target.type}")


# --- Audit job checks ---


def test_audit_job_exists(client: NeMoPlatform) -> None:
    """Verify the audit job was created."""
    jobs = client.audit.jobs.list()
    job_names = [j.name for j in jobs.data]
    assert JOB_NAME in job_names, f"Job '{JOB_NAME}' not found. Found: {job_names}"


def test_audit_job_spec(client: NeMoPlatform) -> None:
    """Verify the audit job has a valid spec with config and target references."""
    job = client.audit.jobs.retrieve(JOB_NAME)
    assert job.spec is not None, f"Job '{JOB_NAME}' has no spec"
    spec = job.spec

    # Verify config reference exists
    assert spec.config is not None, "Job spec has no config reference"
    print(f"Job config: {spec.config}")

    # Verify target reference exists
    assert spec.target is not None, "Job spec has no target reference"
    print(f"Job target: {spec.target}")


# --- Agent trajectory checks ---


def test_agent_checked_job_status() -> None:
    """Verify the agent attempted to check the audit job status."""
    session = get_session()
    commands = session.get_bash_commands()

    # The agent should have run a command to check job status
    status_indicators = ["get-status", "get_status", "status"]
    job_indicators = ["audit", "job"]

    has_status_check = any(
        all(ind in cmd for ind in job_indicators) and any(si in cmd for si in status_indicators) for cmd in commands
    )

    # Also accept if the agent retrieved the job details (which includes status)
    has_job_get = any(all(p in cmd for p in ["audit", "jobs", "get"]) for cmd in commands)

    assert has_status_check or has_job_get, (
        f"Agent never checked job status. Looked for audit job status/get commands in {len(commands)} bash commands."
    )


def test_agent_created_config() -> None:
    """Verify the agent created or interacted with an audit config."""
    session = get_session()
    commands = session.get_bash_commands()

    has_config_create = any(all(p in cmd for p in ["audit", "config"]) and "create" in cmd for cmd in commands)

    has_config_list = any(all(p in cmd for p in ["audit", "config"]) and "list" in cmd for cmd in commands)

    has_config_get = any(
        all(p in cmd for p in ["audit", "config"]) and ("get" in cmd or "default" in cmd) for cmd in commands
    )

    assert has_config_create or has_config_list or has_config_get, (
        "Agent never created or discovered an audit config. Expected the agent to create or find the default config."
    )
