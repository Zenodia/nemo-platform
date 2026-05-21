# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Verify that the agent created a custom audit config with selected probes,
created an audit target, and launched an audit job with the custom config.

The inference provider is pre-configured by the Dockerfile setup script.
Tests focus on the custom probes workflow: config creation with specific probes,
target creation, and job launch with the custom config.

Tests:
- Audit target exists and references a model through the pre-configured provider
- Custom audit config exists with the three specified probes
- Audit job was created with spec referencing the custom config and target
- Agent trajectory shows config verification and job status checking
"""

import base64
import json
import os

import pytest
from nemo_platform import NeMoPlatform
from trace_reader import get_session

WORKSPACE = "default"
TARGET_NAME = "custom-audit-target"
CONFIG_NAME = "custom-probes-config"
JOB_NAME = "custom-probes-job"
EXPECTED_PROBES = ["dan.DanInTheWild", "dan.AutoDANCached", "dan.Ablation_Dan_11_0"]


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
    """Verify the audit target references a model."""
    target = client.audit.targets.retrieve(TARGET_NAME)
    assert isinstance(target.model, str) and len(target.model) > 0, f"Target '{TARGET_NAME}' has no model configured"
    print(f"Target model: {target.model}, type: {target.type}")


# --- Custom audit config checks ---


def test_custom_config_exists(client: NeMoPlatform) -> None:
    """Verify the custom audit config was created."""
    configs = client.audit.configs.list()
    config_names = [c.name for c in configs]
    assert CONFIG_NAME in config_names, f"Config '{CONFIG_NAME}' not found. Found: {config_names}"


def test_custom_config_description(client: NeMoPlatform) -> None:
    """Verify the custom config has the correct description."""
    config = client.audit.configs.retrieve(name=CONFIG_NAME)
    assert config.description == "Custom config with selected probes", (
        f"Expected description 'Custom config with selected probes', got '{config.description}'"
    )


def _get_probes_from_config(config: object) -> list[str]:
    """Extract probe names from a config, checking both probes dict and probe_spec string."""
    plugins = config.plugins

    # Check plugins.probes dict first (keys are probe names)
    probes_dict = plugins.probes if hasattr(plugins, "probes") else {}
    if isinstance(probes_dict, dict) and probes_dict:
        return list(probes_dict.keys())

    # Fall back to probe_spec (comma-separated string like "dan.DanInTheWild,dan.AutoDANCached")
    probe_spec = plugins.probe_spec if hasattr(plugins, "probe_spec") else ""
    if isinstance(probe_spec, str) and probe_spec and probe_spec != "all":
        return [p.strip() for p in probe_spec.split(",")]

    return []


def test_custom_config_has_selected_probes(client: NeMoPlatform) -> None:
    """Verify the custom config uses the three specified probes."""
    config = client.audit.configs.retrieve(name=CONFIG_NAME)
    # Probes may be in plugins.probes dict (keys) or in probe_spec (comma-separated string)
    probe_names = _get_probes_from_config(config)

    for probe in EXPECTED_PROBES:
        assert probe in probe_names, f"Expected probe '{probe}' in config probes, got: {probe_names}"

    print(f"Config probes: {probe_names}")


# --- Audit job checks ---


def test_audit_job_exists(client: NeMoPlatform) -> None:
    """Verify the audit job was created."""
    jobs = client.audit.jobs.list()
    job_names = [j.name for j in jobs.data]
    assert JOB_NAME in job_names, f"Job '{JOB_NAME}' not found. Found: {job_names}"


def test_audit_job_spec(client: NeMoPlatform) -> None:
    """Verify the audit job has a valid spec with config and target."""
    job = client.audit.jobs.retrieve(JOB_NAME)
    assert job.spec is not None, f"Job '{JOB_NAME}' has no spec"
    spec = job.spec

    # Verify config reference exists
    assert spec.config is not None, "Job spec has no config reference"
    # The config may be a string reference or an inlined config object
    config_ref = spec.config
    if isinstance(config_ref, str):
        assert CONFIG_NAME in config_ref, f"Job config should reference '{CONFIG_NAME}', got '{config_ref}'"
    else:
        # Config is inlined — verify it contains the expected probes
        # Check both probes dict and probe_spec string
        config_dict = config_ref if isinstance(config_ref, dict) else {}
        if hasattr(config_ref, "plugins"):
            # SDK object — use the shared helper
            class _FakeConfig:
                plugins = config_ref.plugins

            probe_names = _get_probes_from_config(_FakeConfig())
        elif isinstance(config_dict, dict):
            plugins = config_dict.get("plugins", {})
            probes = plugins.get("probes", {}) if isinstance(plugins, dict) else {}
            probe_spec = plugins.get("probe_spec", "") if isinstance(plugins, dict) else ""
            if isinstance(probes, dict) and probes:
                probe_names = list(probes.keys())
            elif isinstance(probe_spec, str) and probe_spec and probe_spec != "all":
                probe_names = [p.strip() for p in probe_spec.split(",")]
            else:
                probe_names = []
        else:
            probe_names = []
        has_expected = all(p in probe_names for p in EXPECTED_PROBES)
        assert has_expected, (
            f"Inlined job config should contain all expected probes {EXPECTED_PROBES}, got: {probe_names}"
        )
    print(f"Job config: {config_ref}")

    # Verify target reference exists
    assert spec.target is not None, "Job spec has no target reference"
    print(f"Job target: {spec.target}")


# --- Agent trajectory checks ---


def _has_token(cmd: str, token: str) -> bool:
    """Check if token appears as a whole word in cmd (not as a substring of another word)."""
    import re

    return bool(re.search(r"(?:^|[\s/\-_.])(" + re.escape(token) + r")(?:[\s/\-_.]|$)", cmd))


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


def test_agent_verified_config() -> None:
    """Verify the agent retrieved the config to confirm probe selection."""
    session = get_session()
    commands = session.get_bash_commands()

    has_config_get = any(
        _has_token(cmd, "audit") and _has_token(cmd, "configs") and _has_token(cmd, "get") for cmd in commands
    )

    has_config_list = any(
        _has_token(cmd, "audit") and _has_token(cmd, "configs") and _has_token(cmd, "list") for cmd in commands
    )

    assert has_config_get or has_config_list, (
        "Agent never verified the custom config. Expected the agent to retrieve or list configs after creation."
    )


def test_agent_created_custom_config() -> None:
    """Verify the agent created the custom config via CLI."""
    session = get_session()
    commands = session.get_bash_commands()

    def has_command(*patterns: str) -> bool:
        return any(all(p in cmd for p in patterns) for cmd in commands)

    # Agent may create config with inline args or via --input-file with JSON
    # (when using --input-file, CONFIG_NAME is in a separate cat/echo command that writes the JSON file)
    has_inline_create = has_command("audit", "configs", "create", CONFIG_NAME)
    has_file_create = any(
        all(p in cmd for p in ["audit", "configs", "create"]) and CONFIG_NAME in cmd for cmd in commands
    )

    assert has_inline_create or has_file_create, f"Agent did not create '{CONFIG_NAME}'. Commands: {commands}"


def test_agent_attempted_results_retrieval() -> None:
    """Verify the agent attempted to retrieve job results or hit logs."""
    session = get_session()
    commands = session.get_bash_commands()

    result_tokens = ["result", "results", "hitlog", "hit-log", "hit_log", "log", "logs"]

    # Check for commands containing "audit" + "job"/"jobs" + a result token as whole words
    has_results_attempt = any(
        _has_token(cmd, "audit")
        and (_has_token(cmd, "job") or _has_token(cmd, "jobs"))
        and any(_has_token(cmd, rt) for rt in result_tokens)
        for cmd in commands
    )

    assert has_results_attempt, (
        "Agent never attempted to retrieve job results or hit logs. "
        f"Looked for audit job results/log commands in {len(commands)} bash commands."
    )
