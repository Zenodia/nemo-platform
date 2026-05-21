#!/usr/bin/env python3
# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""
Test script for Remote Metrics evaluation using NAT (NeMo Agent Toolkit) and generic remote endpoints.

This script tests remote metrics via NeMo Platform SDK with two modes:
1. Live Evaluation - Using client.evaluation.metrics.evaluate() for immediate results
2. Job Evaluation - Using client.evaluation.metric_jobs.create() for async job execution

Remote Metric Types:
- NAT Remote Metric: Fixed payload structure for NeMo Agent Toolkit evaluators
- Generic Remote Metric: Configurable body/scores with Jinja templating

Usage:
    # Test NAT remote metric via live evaluation (default)
    python test_remote_metrics.py --test-live \
        --nat-endpoint http://localhost:8000/evaluate_item \
        --evaluator-name similarity_eval

    # Test NAT remote metric via job evaluation
    python test_remote_metrics.py --test-job \
        --nat-endpoint http://localhost:8000/evaluate_item \
        --evaluator-name similarity_eval

    # Test both modes
    python test_remote_metrics.py --test-all \
        --nat-endpoint http://localhost:8000/evaluate_item \
        --evaluator-name similarity_eval

    # Test generic remote metric
    python test_remote_metrics.py --test-generic-remote \
        --remote-endpoint http://localhost:8000/custom_eval \
        --remote-body '{"query": "{{ item.input_obj }}", "response": "{{ item.output_obj }}"}' \
        --remote-scores '[{"name": "custom_score", "json_path": "$.score"}]'

    # Test NAT live evaluation with API key secret
    # First create the secret, then reference it by name
    python test_remote_metrics.py --test-live \
        --nat-endpoint http://localhost:8001/evaluate_item \
        --evaluator-name similarity_eval \
        --nat-api-key "your-api-key-value"

    # Test NAT job evaluation with API key secret
    # For jobs, the endpoint must use host.docker.internal for container access
    python test_remote_metrics.py --test-job \
        --nat-endpoint-job http://host.docker.internal:8001/evaluate_item \
        --evaluator-name similarity_eval \
        --nat-api-key "your-api-key-value"

    # Run dedicated secret integration tests (creates temp secret, tests both live + job)
    python test_remote_metrics.py --test-secrets \
        --nat-endpoint http://localhost:8001/evaluate_item \
        --nat-endpoint-job http://host.docker.internal:8001/evaluate_item \
        --evaluator-name similarity_eval

Example NAT payload sent:
    {
        "evaluator_name": "similarity_eval",
        "item": {
          "id": "test_item_1",
          "input_obj": "What is LangSmith?",
          "expected_output_obj": "LangSmith is a platform for building production-grade LLM applications.",
          "output_obj": "LangSmith is a platform for building llm",
          "trajectory": [],
          "expected_trajectory": [],
          "full_dataset_entry": {}
        }
    }
"""

import argparse
import json
import os
import subprocess
import sys
import threading
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from nemo_platform import NeMoPlatform
from nemo_platform.types.evaluation import (
    EvaluateDatasetRowsParam,
    NeMoAgentToolkitRemoteMetricParam,
    RemoteMetricParam,
    RemoteScoreParam,
)

# Default configuration
DEFAULT_BASE_URL = "http://localhost:8000"
DEFAULT_WORKSPACE = "default"

# Remote metric configuration
# Note: For job-based evaluation, the job runs in a Docker container.
# Use host.docker.internal to access services on the host machine.
DEFAULT_NAT_ENDPOINT_LIVE = "http://localhost:8001/evaluate_item"
DEFAULT_NAT_ENDPOINT_JOB = "http://host.docker.internal:8001/evaluate_item"
DEFAULT_NAT_EVALUATOR_NAME = "similarity_eval"
NAT_API_KEY_SECRET = "nat-api-key"
REMOTE_API_KEY_SECRET = "remote-api-key"

# Thread-safe printing
_print_lock = threading.Lock()


def safe_print(*args, **kwargs):
    """Thread-safe print function."""
    with _print_lock:
        print(*args, **kwargs)


@dataclass
class TestResult:
    """Result of a remote metric test."""

    test_name: str
    mode: str  # "live" or "job"
    status: str
    duration_seconds: float
    job_name: str | None = None
    job_id: str | None = None
    response_data: dict | None = None
    container_logs: str | None = None
    error: str | None = None


# ============================================================================
# Sample Dataset for Remote Metric Testing
# ============================================================================


def get_sample_remote_metric_dataset() -> list[dict]:
    """Get sample dataset items for remote metric testing.

    Returns dataset in row format where each dict is a single evaluation item.
    This matches the format expected by the NAT evaluator.
    """
    return [
        {
            "id": "test_item_1",
            "input_obj": "What is LangSmith?",
            "expected_output_obj": "LangSmith is a platform for building production-grade LLM applications.",
            "output_obj": "LangSmith is a platform for building llm",
            "trajectory": [],
            "expected_trajectory": [],
            "full_dataset_entry": {},
        },
        {
            "id": "test_item_2",
            "input_obj": "What is the capital of France?",
            "expected_output_obj": "The capital of France is Paris.",
            "output_obj": "Paris is the capital of France, located in the north-central part of the country.",
            "trajectory": [],
            "expected_trajectory": [],
            "full_dataset_entry": {},
        },
        {
            "id": "test_item_3",
            "input_obj": "What is NVIDIA known for?",
            "expected_output_obj": "NVIDIA is known for designing graphics processing units (GPUs) and AI computing.",
            "output_obj": "NVIDIA makes GPUs and AI chips.",
            "trajectory": [],
            "expected_trajectory": [],
            "full_dataset_entry": {},
        },
    ]


# ============================================================================
# Live Evaluation - Using SDK client.evaluation.metrics.evaluate()
# ============================================================================


def run_live_nat_test(
    client: NeMoPlatform,
    workspace: str,
    nat_endpoint: str,
    evaluator_name: str,
    dataset_rows: list[dict],
    api_key_secret: str | None = None,
    timeout_seconds: float = 30.0,
    max_retries: int = 3,
    quiet: bool = False,
) -> TestResult:
    """Run live NAT remote metric evaluation using SDK.

    Uses the NeMoAgentToolkitRemoteMetricParam type which automatically
    handles the NAT payload structure.

    Args:
        client: NeMo Platform SDK client
        workspace: Workspace name
        nat_endpoint: NAT endpoint URL
        evaluator_name: NAT evaluator name
        dataset_rows: Evaluation dataset
        api_key_secret: Optional API key secret name
        timeout_seconds: Per-request timeout
        max_retries: Max retries per request
        quiet: Reduce output verbosity

    Returns:
        Test result
    """
    test_name = f"live_nat_{evaluator_name}"
    start_time = time.time()

    # Build metric using proper SDK TypedDict
    metric: NeMoAgentToolkitRemoteMetricParam = {
        "type": "nemo-agent-toolkit-remote",
        "url": nat_endpoint,
        "evaluator_name": evaluator_name,
        "timeout_seconds": timeout_seconds,
        "max_retries": max_retries,
    }
    if api_key_secret:
        metric["api_key_secret"] = api_key_secret

    # Build dataset using proper SDK TypedDict
    dataset: EvaluateDatasetRowsParam = {"rows": dataset_rows}

    if not quiet:
        safe_print(f"\n{'=' * 60}")
        safe_print(f"LIVE EVALUATION TEST - {test_name}")
        safe_print(f"{'=' * 60}")
        safe_print(f"NAT Endpoint: {nat_endpoint}")
        safe_print(f"Evaluator: {evaluator_name}")
        safe_print(f"Dataset rows: {len(dataset_rows)}")
        safe_print(f"Metric spec: {json.dumps(metric, indent=2)}")
        safe_print(f"{'=' * 60}")

    try:
        if not quiet:
            safe_print("  Running evaluation via SDK...")

        # Use SDK's evaluate method with proper types
        result = client.evaluation.metrics.evaluate(
            workspace=workspace,
            metric=metric,
            dataset=dataset,
        )
        result_data = result.model_dump()
        duration = time.time() - start_time

        if not quiet:
            safe_print(f"  ✅ Evaluation completed in {duration:.2f}s")
            safe_print(f"  Result: {json.dumps(result_data, indent=2)}")
        else:
            safe_print(f"[{test_name}] ✅ completed ({duration:.2f}s)")

        return TestResult(
            test_name=test_name,
            mode="live",
            status="completed",
            duration_seconds=duration,
            response_data=result_data,
        )

    except Exception as e:
        duration = time.time() - start_time
        error_msg = str(e)
        safe_print(f"[{test_name}] ❌ ERROR: {error_msg}")
        return TestResult(
            test_name=test_name,
            mode="live",
            status="error",
            duration_seconds=duration,
            error=error_msg,
        )


def run_live_generic_remote_test(
    client: NeMoPlatform,
    workspace: str,
    remote_endpoint: str,
    body_template: dict,
    scores: list[RemoteScoreParam],
    dataset_rows: list[dict],
    api_key_secret: str | None = None,
    timeout_seconds: float = 30.0,
    max_retries: int = 3,
    quiet: bool = False,
) -> TestResult:
    """Run live generic remote metric evaluation using SDK.

    Uses the RemoteMetricParam type.

    Args:
        client: NeMo Platform SDK client
        workspace: Workspace name
        remote_endpoint: Remote endpoint URL
        body_template: Request body template (Jinja)
        scores: Score configurations list (each with 'name' and 'json_path')
        dataset_rows: Evaluation dataset
        api_key_secret: Optional API key secret name
        timeout_seconds: Per-request timeout
        max_retries: Max retries per request
        quiet: Reduce output verbosity

    Returns:
        Test result
    """
    test_name = "live_generic_remote"
    start_time = time.time()

    # Build metric using proper SDK TypedDict
    metric: RemoteMetricParam = {
        "type": "remote",
        "url": remote_endpoint,
        "body": body_template,
        "scores": scores,
        "timeout_seconds": timeout_seconds,
        "max_retries": max_retries,
    }
    if api_key_secret:
        metric["api_key_secret"] = api_key_secret

    # Build dataset using proper SDK TypedDict
    dataset: EvaluateDatasetRowsParam = {"rows": dataset_rows}

    if not quiet:
        safe_print(f"\n{'=' * 60}")
        safe_print(f"LIVE EVALUATION TEST - {test_name}")
        safe_print(f"{'=' * 60}")
        safe_print(f"Endpoint: {remote_endpoint}")
        safe_print(f"Body template: {body_template}")
        safe_print(f"Scores: {scores}")
        safe_print(f"Dataset rows: {len(dataset_rows)}")
        safe_print(f"Metric spec: {json.dumps(metric, indent=2)}")
        safe_print(f"{'=' * 60}")

    try:
        if not quiet:
            safe_print("  Running evaluation via SDK...")

        # Use SDK's evaluate method with proper types
        result = client.evaluation.metrics.evaluate(
            workspace=workspace,
            metric=metric,
            dataset=dataset,
        )
        result_data = result.model_dump()
        duration = time.time() - start_time

        if not quiet:
            safe_print(f"  ✅ Evaluation completed in {duration:.2f}s")
            safe_print(f"  Result: {json.dumps(result_data, indent=2)}")
        else:
            safe_print(f"[{test_name}] ✅ completed ({duration:.2f}s)")

        return TestResult(
            test_name=test_name,
            mode="live",
            status="completed",
            duration_seconds=duration,
            response_data=result_data,
        )

    except Exception as e:
        duration = time.time() - start_time
        error_msg = str(e)
        safe_print(f"[{test_name}] ❌ ERROR: {error_msg}")
        return TestResult(
            test_name=test_name,
            mode="live",
            status="error",
            duration_seconds=duration,
            error=error_msg,
        )


# ============================================================================
# Job Evaluation - Submit Evaluation Jobs using NeMo Platform SDK
# ============================================================================


def create_secrets(client: NeMoPlatform, workspace: str, secrets: dict[str, str]) -> dict[str, bool]:
    """Create secrets in the platform using SDK.

    Args:
        client: NeMo Platform SDK client
        workspace: Workspace name
        secrets: Dict mapping secret names to values

    Returns:
        Dict mapping secret names to success status
    """
    results = {}
    for name, value in secrets.items():
        try:
            client.secrets.create(workspace=workspace, name=name, value=value)
            safe_print(f"  ✅ Created secret: {name}")
            results[name] = True
        except Exception as e:
            if "already exists" in str(e).lower() or "409" in str(e):
                safe_print(f"  Secret already exists: {name}")
                results[name] = True
            else:
                safe_print(f"  ❌ Failed to create secret {name}: {e}")
                results[name] = False
    return results


def delete_secret(client: NeMoPlatform, workspace: str, name: str) -> bool:
    """Delete a secret from the platform using SDK.

    Args:
        client: NeMo Platform SDK client
        workspace: Workspace name
        name: Secret name to delete

    Returns:
        True if deleted successfully, False otherwise
    """
    try:
        client.secrets.delete(name=name, workspace=workspace)
        safe_print(f"  ✅ Deleted secret: {name}")
        return True
    except Exception as e:
        if "not found" in str(e).lower() or "404" in str(e):
            safe_print(f"  Secret not found: {name}")
            return True
        safe_print(f"  ❌ Failed to delete secret {name}: {e}")
        return False


# ============================================================================
# Secret Integration Tests
# ============================================================================


def run_secrets_test(
    client: NeMoPlatform,
    workspace: str,
    nat_endpoint_live: str,
    nat_endpoint_job: str,
    evaluator_name: str,
    dataset_rows: list[dict],
    test_live: bool = True,
    test_job: bool = True,
    timeout_seconds: float = 30.0,
    max_retries: int = 3,
    job_timeout: float = 300.0,
    quiet: bool = False,
) -> list[TestResult]:
    """Run integration tests for secret handling in remote metrics.

    This test specifically validates that:
    1. Secrets can be created in the platform
    2. Secret references work in live evaluation (resolved via SDK)
    3. Secret references work in job evaluation (injected as env vars)

    Args:
        client: NeMo Platform SDK client
        workspace: Workspace name
        nat_endpoint_live: NAT endpoint URL for live tests
        nat_endpoint_job: NAT endpoint URL for job tests (use host.docker.internal)
        evaluator_name: NAT evaluator name
        dataset_rows: Evaluation dataset
        test_live: Run live evaluation test with secrets
        test_job: Run job evaluation test with secrets
        timeout_seconds: Per-request timeout
        max_retries: Max retries per request
        job_timeout: Overall job timeout
        quiet: Reduce output verbosity

    Returns:
        List of test results
    """
    results = []
    test_secret_name = "test-remote-api-key"
    test_secret_value = "test-secret-value-12345"  # Dummy value for testing

    if not quiet:
        safe_print(f"\n{'=' * 60}")
        safe_print("SECRET INTEGRATION TESTS")
        safe_print(f"{'=' * 60}")
        safe_print(f"Test secret name: {test_secret_name}")
        safe_print(f"NAT endpoint (live): {nat_endpoint_live}")
        safe_print(f"NAT endpoint (job): {nat_endpoint_job}")
        safe_print(f"Evaluator: {evaluator_name}")
        safe_print(f"{'=' * 60}")

    # Step 1: Create test secret
    safe_print("\n[Secrets Test] Creating test secret...")
    secret_created = create_secrets(client, workspace, {test_secret_name: test_secret_value})
    if not secret_created.get(test_secret_name):
        safe_print("[Secrets Test] ❌ Failed to create test secret")
        return [
            TestResult(
                test_name="secrets_setup",
                mode="setup",
                status="error",
                duration_seconds=0.0,
                error="Failed to create test secret",
            )
        ]

    # Step 2: Test live evaluation with secret reference
    if test_live:
        safe_print("\n[Secrets Test] Testing live evaluation with secret reference...")
        live_result = run_live_nat_test(
            client=client,
            workspace=workspace,
            nat_endpoint=nat_endpoint_live,
            evaluator_name=evaluator_name,
            dataset_rows=dataset_rows[:1],  # Use single row for quick test
            api_key_secret=test_secret_name,
            timeout_seconds=timeout_seconds,
            max_retries=max_retries,
            quiet=quiet,
        )
        live_result.test_name = "secrets_live_eval"
        results.append(live_result)

        if live_result.status == "completed":
            safe_print("[Secrets Test] ✅ Live evaluation with secret passed")
        else:
            safe_print(f"[Secrets Test] ❌ Live evaluation with secret failed: {live_result.error}")

    # Step 3: Test job evaluation with secret reference
    if test_job:
        safe_print("\n[Secrets Test] Testing job evaluation with secret reference...")
        job_result = run_nat_job_test(
            client=client,
            workspace=workspace,
            nat_endpoint=nat_endpoint_job,
            evaluator_name=evaluator_name,
            dataset_rows=dataset_rows[:1],  # Use single row for quick test
            api_key_secret=test_secret_name,
            timeout_seconds=timeout_seconds,
            max_retries=max_retries,
            limit_samples=1,
            job_timeout=job_timeout,
            quiet=quiet,
        )
        job_result.test_name = "secrets_job_eval"
        results.append(job_result)

        if job_result.status == "completed":
            safe_print("[Secrets Test] ✅ Job evaluation with secret passed")
        else:
            safe_print(f"[Secrets Test] ❌ Job evaluation with secret failed: {job_result.error}")

    # Step 4: Test with non-existent secret (should fail gracefully)
    if test_live:
        safe_print("\n[Secrets Test] Testing live evaluation with non-existent secret...")
        start_time = time.time()
        try:
            missing_secret_result = run_live_nat_test(
                client=client,
                workspace=workspace,
                nat_endpoint=nat_endpoint_live,
                evaluator_name=evaluator_name,
                dataset_rows=dataset_rows[:1],
                api_key_secret="nonexistent-secret-12345",
                timeout_seconds=timeout_seconds,
                max_retries=max_retries,
                quiet=True,  # Always quiet for expected failure
            )
            # If it completed, check if it actually used the secret
            # Note: Some endpoints may not require authentication
            duration = time.time() - start_time
            results.append(
                TestResult(
                    test_name="secrets_missing_secret",
                    mode="live",
                    status="completed" if missing_secret_result.status == "error" else "warning",
                    duration_seconds=duration,
                    response_data=missing_secret_result.response_data,
                    error=missing_secret_result.error,
                )
            )
            if missing_secret_result.status == "error":
                safe_print("[Secrets Test] ✅ Missing secret correctly rejected")
            else:
                safe_print("[Secrets Test] ⚠️  Missing secret test: endpoint may not require auth")
        except Exception as e:
            duration = time.time() - start_time
            error_msg = str(e)
            if "not found" in error_msg.lower() or "secret" in error_msg.lower():
                safe_print(f"[Secrets Test] ✅ Missing secret correctly rejected: {error_msg}")
                results.append(
                    TestResult(
                        test_name="secrets_missing_secret",
                        mode="live",
                        status="completed",
                        duration_seconds=duration,
                        error=f"Expected error: {error_msg}",
                    )
                )
            else:
                safe_print(f"[Secrets Test] ❌ Unexpected error: {error_msg}")
                results.append(
                    TestResult(
                        test_name="secrets_missing_secret",
                        mode="live",
                        status="error",
                        duration_seconds=duration,
                        error=error_msg,
                    )
                )

    # Cleanup: Delete test secret
    if not quiet:
        safe_print("\n[Secrets Test] Cleaning up test secret...")
    delete_secret(client, workspace, test_secret_name)

    return results


def create_nat_remote_metric_job_spec(
    evaluator_name: str,
    nat_endpoint: str,
    dataset_rows: list[dict],
    workspace: str = DEFAULT_WORKSPACE,
    api_key_secret: str | None = None,
    timeout_seconds: float = 30.0,
    max_retries: int = 3,
    limit_samples: int | None = None,
) -> dict:
    """Create job spec for NAT remote metric evaluation.

    Args:
        workspace: Workspace for the metric
        evaluator_name: Name of the NAT evaluator (e.g., "similarity_eval")
        nat_endpoint: URL of the NAT endpoint
        dataset_rows: List of evaluation items
        api_key_secret: Optional secret name for API key
        timeout_seconds: Request timeout
        max_retries: Max retry attempts
        limit_samples: Limit number of samples

    Returns:
        Job spec dictionary (to pass to client.evaluation.metric_jobs.create)
    """
    # Build NAT remote metric config
    # Note: type uses hyphens, not underscores
    # For job-based evaluation, workspace is required for inline metrics
    metric_config: dict = {
        "type": "nemo-agent-toolkit-remote",
        "workspace": workspace,
        "url": nat_endpoint,
        "evaluator_name": evaluator_name,
        "timeout_seconds": timeout_seconds,
        "max_retries": max_retries,
    }
    if api_key_secret:
        metric_config["api_key_secret"] = api_key_secret

    # Build dataset spec
    rows = dataset_rows[:limit_samples] if limit_samples else dataset_rows
    dataset_spec = {"rows": rows}

    # Build job spec
    job_spec: dict = {
        "metric": metric_config,
        "dataset": dataset_spec,
    }

    if limit_samples:
        job_spec["limit_samples"] = limit_samples

    return job_spec


def create_generic_remote_metric_job_spec(
    remote_endpoint: str,
    body_template: dict,
    scores: list[dict],
    dataset_rows: list[dict],
    workspace: str = DEFAULT_WORKSPACE,
    description: str | None = None,
    api_key_secret: str | None = None,
    timeout_seconds: float = 30.0,
    max_retries: int = 3,
    limit_samples: int | None = None,
) -> dict:
    """Create job spec for generic remote metric evaluation.

    Args:
        workspace: Workspace for the metric
        remote_endpoint: URL of the remote endpoint
        body_template: Request body template with Jinja placeholders
        scores: Score configurations list (each with 'name' and 'json_path')
        dataset_rows: List of evaluation items
        description: Optional metric description
        api_key_secret: Optional secret name for API key
        timeout_seconds: Request timeout
        max_retries: Max retry attempts
        limit_samples: Limit number of samples

    Returns:
        Job spec dictionary
    """
    # Build generic remote metric config
    # For job-based evaluation, workspace is required for inline metrics
    metric_config: dict = {
        "type": "remote",
        "workspace": workspace,
        "url": remote_endpoint,
        "body": body_template,
        "scores": scores,
        "timeout_seconds": timeout_seconds,
        "max_retries": max_retries,
    }
    if description:
        metric_config["description"] = description
    if api_key_secret:
        metric_config["api_key_secret"] = api_key_secret

    # Build dataset spec
    rows = dataset_rows[:limit_samples] if limit_samples else dataset_rows
    dataset_spec = {"rows": rows}

    # Build job spec
    job_spec: dict = {
        "metric": metric_config,
        "dataset": dataset_spec,
    }

    if limit_samples:
        job_spec["limit_samples"] = limit_samples

    return job_spec


def submit_job_with_sdk(client: NeMoPlatform, workspace: str, job_spec: dict) -> dict:
    """Submit a metric job using NeMo Platform SDK.

    Args:
        client: NeMo Platform SDK client
        workspace: Workspace name
        job_spec: Job specification dict

    Returns:
        Job response as dict
    """
    job = client.evaluation.metric_jobs.create(
        workspace=workspace,
        spec=job_spec,  # ty: ignore[invalid-argument-type] - CLI helper intentionally accepts arbitrary dict payloads
    )
    return job.model_dump()


def get_job_status_with_sdk(client: NeMoPlatform, workspace: str, job_name: str) -> dict:
    """Get job status using NeMo Platform SDK.

    Args:
        client: NeMo Platform SDK client
        workspace: Workspace name
        job_name: Name of the job

    Returns:
        Job status as dict
    """
    job = client.evaluation.metric_jobs.retrieve(job_name, workspace=workspace)
    return job.model_dump()


def wait_for_job_with_sdk(
    client: NeMoPlatform,
    workspace: str,
    job_name: str,
    poll_interval: float = 2.0,
    timeout: float = 600.0,
    quiet: bool = False,
) -> dict:
    """Wait for a job to complete using NeMo Platform SDK.

    Args:
        client: NeMo Platform SDK client
        workspace: Workspace name
        job_name: Name of the job
        poll_interval: Polling interval in seconds
        timeout: Maximum wait time in seconds
        quiet: Reduce output verbosity

    Returns:
        Final job status as dict
    """
    start_time = time.time()
    terminal_statuses = {"completed", "error", "cancelled"}

    while True:
        elapsed = time.time() - start_time
        if elapsed > timeout:
            raise TimeoutError(f"Job {job_name} did not complete within {timeout} seconds")

        job = get_job_status_with_sdk(client, workspace, job_name)
        status = job.get("status", "unknown")

        if status in terminal_statuses:
            return job

        if not quiet:
            safe_print(f"  Job status: {status} (elapsed: {elapsed:.1f}s)")
        time.sleep(poll_interval)


def get_container_logs(job_name: str) -> str | None:
    """Get logs from the Docker container for a job."""
    container_name = f"{job_name}-evaluation"
    try:
        result = subprocess.run(
            ["docker", "logs", container_name],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0:
            return result.stdout + result.stderr
        return f"Error getting logs: {result.stderr}"
    except subprocess.TimeoutExpired:
        return "Error: Timeout getting container logs"
    except FileNotFoundError:
        return "Error: Docker not found"
    except Exception as e:
        return f"Error getting logs: {e}"


def run_nat_job_test(
    client: NeMoPlatform,
    workspace: str,
    nat_endpoint: str,
    evaluator_name: str,
    dataset_rows: list[dict],
    api_key_secret: str | None = None,
    timeout_seconds: float = 30.0,
    max_retries: int = 3,
    limit_samples: int | None = None,
    job_timeout: float = 600.0,
    quiet: bool = False,
) -> TestResult:
    """Run NAT remote metric evaluation via job submission using SDK.

    Args:
        client: NeMo Platform SDK client
        workspace: Workspace name
        nat_endpoint: NAT endpoint URL
        evaluator_name: NAT evaluator name
        dataset_rows: Evaluation dataset
        api_key_secret: Optional API key secret name
        timeout_seconds: Per-request timeout
        max_retries: Max retries per request
        limit_samples: Limit samples to evaluate
        job_timeout: Overall job timeout
        quiet: Reduce output verbosity

    Returns:
        Test result
    """
    test_name = f"job_nat_{evaluator_name}"
    start_time = time.time()

    if not quiet:
        safe_print(f"\n{'=' * 60}")
        safe_print("JOB EVALUATION TEST - NAT Remote Metric (SDK)")
        safe_print(f"{'=' * 60}")
        safe_print(f"Endpoint: {nat_endpoint}")
        safe_print(f"Evaluator: {evaluator_name}")
        safe_print(f"Dataset rows: {len(dataset_rows)}")
        safe_print(f"{'=' * 60}")

    try:
        # Create job spec (workspace defaults to "default")
        job_spec = create_nat_remote_metric_job_spec(
            evaluator_name=evaluator_name,
            nat_endpoint=nat_endpoint,
            dataset_rows=dataset_rows,
            workspace=workspace,
            api_key_secret=api_key_secret,
            timeout_seconds=timeout_seconds,
            max_retries=max_retries,
            limit_samples=limit_samples,
        )

        if not quiet:
            safe_print("  Submitting job via SDK...")
            safe_print(f"  Job spec: {json.dumps(job_spec, indent=2)}")

        job_response = submit_job_with_sdk(client, workspace, job_spec)
        job_name = job_response["name"]
        job_id = job_response["id"]

        if not quiet:
            safe_print(f"  Job created: {job_name} ({job_id})")
        else:
            safe_print(f"[{test_name}] Job submitted: {job_name}")

        # Wait for completion
        if not quiet:
            safe_print("  Waiting for completion...")
        final_job = wait_for_job_with_sdk(client, workspace, job_name, timeout=job_timeout, quiet=quiet)
        status = final_job.get("status", "unknown")
        duration = time.time() - start_time

        # Get container logs
        if not quiet:
            safe_print("  Getting container logs...")
        logs = get_container_logs(job_name)

        if not quiet:
            safe_print(f"  Status: {status}")
            safe_print(f"  Duration: {duration:.1f}s")
            safe_print(f"  Job result: {json.dumps(final_job, indent=2)}")
        else:
            status_icon = "✅" if status == "completed" else "❌"
            safe_print(f"[{test_name}] {status_icon} {status} ({duration:.1f}s)")

        return TestResult(
            test_name=test_name,
            mode="job",
            status=status,
            duration_seconds=duration,
            job_name=job_name,
            job_id=job_id,
            response_data=final_job,
            container_logs=logs,
        )

    except Exception as e:
        duration = time.time() - start_time
        safe_print(f"[{test_name}] ❌ ERROR: {e}")
        return TestResult(
            test_name=test_name,
            mode="job",
            status="error",
            duration_seconds=duration,
            error=str(e),
        )


def run_generic_remote_job_test(
    client: NeMoPlatform,
    workspace: str,
    remote_endpoint: str,
    body_template: dict,
    scores: list[dict],
    dataset_rows: list[dict],
    description: str | None = None,
    api_key_secret: str | None = None,
    timeout_seconds: float = 30.0,
    max_retries: int = 3,
    limit_samples: int | None = None,
    job_timeout: float = 600.0,
    quiet: bool = False,
) -> TestResult:
    """Run generic remote metric evaluation via job submission using SDK.

    Args:
        client: NeMo Platform SDK client
        workspace: Workspace name
        remote_endpoint: Remote endpoint URL
        body_template: Request body template
        scores: Score configurations list (each with 'name' and 'json_path')
        dataset_rows: Evaluation dataset
        description: Optional metric description
        api_key_secret: Optional API key secret name
        timeout_seconds: Per-request timeout
        max_retries: Max retries per request
        limit_samples: Limit samples to evaluate
        job_timeout: Overall job timeout
        quiet: Reduce output verbosity

    Returns:
        Test result
    """
    test_name = "job_generic_remote"
    start_time = time.time()

    if not quiet:
        safe_print(f"\n{'=' * 60}")
        safe_print("JOB EVALUATION TEST - Generic Remote Metric (SDK)")
        safe_print(f"{'=' * 60}")
        safe_print(f"Endpoint: {remote_endpoint}")
        safe_print(f"Body template: {body_template}")
        safe_print(f"Scores: {scores}")
        safe_print(f"Dataset rows: {len(dataset_rows)}")
        safe_print(f"{'=' * 60}")

    try:
        # Create job spec (workspace defaults to "default")
        job_spec = create_generic_remote_metric_job_spec(
            remote_endpoint=remote_endpoint,
            body_template=body_template,
            scores=scores,
            dataset_rows=dataset_rows,
            workspace=workspace,
            description=description,
            api_key_secret=api_key_secret,
            timeout_seconds=timeout_seconds,
            max_retries=max_retries,
            limit_samples=limit_samples,
        )

        if not quiet:
            safe_print("  Submitting job via SDK...")
            safe_print(f"  Job spec: {json.dumps(job_spec, indent=2)}")

        job_response = submit_job_with_sdk(client, workspace, job_spec)
        job_name = job_response["name"]
        job_id = job_response["id"]

        if not quiet:
            safe_print(f"  Job created: {job_name} ({job_id})")
        else:
            safe_print(f"[{test_name}] Job submitted: {job_name}")

        # Wait for completion
        if not quiet:
            safe_print("  Waiting for completion...")
        final_job = wait_for_job_with_sdk(client, workspace, job_name, timeout=job_timeout, quiet=quiet)
        status = final_job.get("status", "unknown")
        duration = time.time() - start_time

        # Get container logs
        if not quiet:
            safe_print("  Getting container logs...")
        logs = get_container_logs(job_name)

        if not quiet:
            safe_print(f"  Status: {status}")
            safe_print(f"  Duration: {duration:.1f}s")
            safe_print(f"  Job result: {json.dumps(final_job, indent=2)}")
        else:
            status_icon = "✅" if status == "completed" else "❌"
            safe_print(f"[{test_name}] {status_icon} {status} ({duration:.1f}s)")

        return TestResult(
            test_name=test_name,
            mode="job",
            status=status,
            duration_seconds=duration,
            job_name=job_name,
            job_id=job_id,
            response_data=final_job,
            container_logs=logs,
        )

    except Exception as e:
        duration = time.time() - start_time
        safe_print(f"[{test_name}] ❌ ERROR: {e}")
        return TestResult(
            test_name=test_name,
            mode="job",
            status="error",
            duration_seconds=duration,
            error=str(e),
        )


# ============================================================================
# Results Reporting
# ============================================================================


def save_results(results: list[TestResult], output_dir: Path) -> None:
    """Save test results to files."""
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Save individual logs
    for result in results:
        if result.container_logs:
            log_file = output_dir / f"{result.test_name}_{result.mode}_{timestamp}.log"
            log_file.write_text(result.container_logs)
            print(f"  Saved logs: {log_file}")

    # Save summary
    summary = {
        "timestamp": timestamp,
        "results": [
            {
                "test_name": r.test_name,
                "mode": r.mode,
                "job_name": r.job_name,
                "job_id": r.job_id,
                "status": r.status,
                "duration_seconds": r.duration_seconds,
                "response_data": r.response_data,
                "error": r.error,
            }
            for r in results
        ],
    }
    summary_file = output_dir / f"summary_{timestamp}.json"
    summary_file.write_text(json.dumps(summary, indent=2))
    print(f"  Saved summary: {summary_file}")


def print_summary(results: list[TestResult]) -> None:
    """Print a summary of all test results."""
    print(f"\n{'=' * 60}")
    print("TEST SUMMARY")
    print(f"{'=' * 60}")

    passed = sum(1 for r in results if r.status == "completed")
    failed = sum(1 for r in results if r.status not in ("completed", "skipped"))
    skipped = sum(1 for r in results if r.status == "skipped")
    total = len(results)

    print(f"Total: {total}, Passed: {passed}, Failed: {failed}, Skipped: {skipped}")
    print()

    # Group by mode
    live_results = [r for r in results if r.mode == "live"]
    job_results = [r for r in results if r.mode == "job"]

    if live_results:
        print("Live Evaluation Tests (SDK evaluate):")
        for result in live_results:
            status_icon = "✅" if result.status == "completed" else "❌" if result.status != "skipped" else "⏭️"
            print(f"  {status_icon} {result.test_name}: {result.status} ({result.duration_seconds:.2f}s)")
            if result.error:
                print(f"      Error: {result.error}")

    if job_results:
        print("\nJob Evaluation Tests (SDK metric_jobs):")
        for result in job_results:
            status_icon = "✅" if result.status == "completed" else "❌" if result.status != "skipped" else "⏭️"
            print(f"  {status_icon} {result.test_name}: {result.status} ({result.duration_seconds:.1f}s)")
            if result.job_name:
                print(f"      Job: {result.job_name}")
            if result.error:
                print(f"      Error: {result.error}")


# ============================================================================
# Main
# ============================================================================


def main():
    parser = argparse.ArgumentParser(
        description="Test Remote Metrics evaluation via NeMo Platform SDK (live and job modes)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Test Modes:
  - Live Evaluation: Using client.evaluation.metrics.evaluate() for immediate results
  - Job Evaluation: Using client.evaluation.metric_jobs.create() for async job execution

Remote Metric Types:
  - NAT (NeMo Agent Toolkit): Fixed payload structure {evaluator_name, item}
  - Generic Remote: Configurable body template and score extraction

Example (NAT live evaluation):
  python test_remote_metrics.py --test-live \\
      --nat-endpoint http://localhost:8000/evaluate_item \\
      --evaluator-name similarity_eval

Example (NAT job evaluation):
  python test_remote_metrics.py --test-job \\
      --nat-endpoint http://localhost:8000/evaluate_item \\
      --evaluator-name similarity_eval

Example (both modes):
  python test_remote_metrics.py --test-all \\
      --nat-endpoint http://localhost:8000/evaluate_item \\
      --evaluator-name similarity_eval

Example (Generic remote metric):
  python test_remote_metrics.py --test-live --test-generic-remote \\
      --remote-endpoint http://localhost:8000/custom_eval \\
      --remote-body '{"evaluator_name": "my_eval", "item": "{{ item }}"}' \\
      --remote-scores '[{"name": "score", "json_path": "$.result.score"}]'

Example (NAT live evaluation with API key secret):
  python test_remote_metrics.py --test-live \\
      --nat-endpoint http://localhost:8001/evaluate_item \\
      --evaluator-name similarity_eval \\
      --nat-api-key "your-api-key-value"

Example (NAT job evaluation with API key secret):
  python test_remote_metrics.py --test-job \\
      --nat-endpoint-job http://host.docker.internal:8001/evaluate_item \\
      --evaluator-name similarity_eval \\
      --nat-api-key "your-api-key-value"

Example (Secret integration tests):
  python test_remote_metrics.py --test-secrets \\
      --nat-endpoint http://localhost:8001/evaluate_item \\
      --nat-endpoint-job http://host.docker.internal:8001/evaluate_item \\
      --evaluator-name similarity_eval
        """,
    )

    # Test mode selection
    parser.add_argument(
        "--test-live",
        action="store_true",
        help="Run live evaluation tests (SDK evaluate)",
    )
    parser.add_argument(
        "--test-job",
        action="store_true",
        help="Run job evaluation tests (SDK metric_jobs)",
    )
    parser.add_argument(
        "--test-all",
        action="store_true",
        help="Run both live and job tests",
    )
    parser.add_argument(
        "--test-generic-remote",
        action="store_true",
        help="Test generic remote metric (requires --remote-endpoint, --remote-body, --remote-scores)",
    )
    parser.add_argument(
        "--test-secrets",
        action="store_true",
        help="Run secret integration tests (creates temp secret, tests live + job evaluation)",
    )

    # NAT endpoint configuration
    parser.add_argument(
        "--nat-endpoint",
        default=None,
        help=f"NAT endpoint URL for live tests (default: {DEFAULT_NAT_ENDPOINT_LIVE})",
    )
    parser.add_argument(
        "--nat-endpoint-job",
        default=None,
        help=f"NAT endpoint URL for job tests - use host.docker.internal for container access (default: {DEFAULT_NAT_ENDPOINT_JOB})",
    )
    parser.add_argument(
        "--evaluator-name",
        default=DEFAULT_NAT_EVALUATOR_NAME,
        help=f"NAT evaluator name (default: {DEFAULT_NAT_EVALUATOR_NAME})",
    )
    parser.add_argument(
        "--nat-api-key",
        default=os.environ.get("NAT_API_KEY"),
        help="API key for NAT endpoint (stored as secret). Can also be set via NAT_API_KEY env var.",
    )

    # Generic remote metric configuration
    parser.add_argument(
        "--remote-endpoint",
        help="Generic remote endpoint URL",
    )
    parser.add_argument(
        "--remote-body",
        type=json.loads,
        help='Request body template as JSON (e.g., \'{"query": "{{ item.input_obj }}"}\')',
    )
    parser.add_argument(
        "--remote-scores",
        type=json.loads,
        help='Score configurations as JSON list (e.g., \'[{"name": "score", "json_path": "$.result.score"}]\')',
    )
    parser.add_argument(
        "--remote-api-key",
        default=os.environ.get("REMOTE_API_KEY"),
        help="API key for generic remote endpoint. Can also be set via REMOTE_API_KEY env var.",
    )

    # Platform configuration
    parser.add_argument(
        "--base-url",
        default=DEFAULT_BASE_URL,
        help=f"Platform base URL (default: {DEFAULT_BASE_URL})",
    )
    parser.add_argument(
        "--workspace",
        default=DEFAULT_WORKSPACE,
        help=f"Workspace to use (default: {DEFAULT_WORKSPACE})",
    )

    # Test configuration
    parser.add_argument(
        "--limit-samples",
        type=int,
        default=None,
        help="Limit number of samples to evaluate",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=30.0,
        help="Per-request timeout in seconds (default: 30)",
    )
    parser.add_argument(
        "--job-timeout",
        type=float,
        default=600.0,
        help="Overall job timeout in seconds (default: 600 = 10 min)",
    )
    parser.add_argument(
        "--max-retries",
        type=int,
        default=3,
        help="Max retries per request (default: 3)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("./remote-metric-test-results"),
        help="Directory to save results (default: ./remote-metric-test-results)",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Reduce output verbosity",
    )

    args = parser.parse_args()

    # Determine test modes
    run_live = args.test_live or args.test_all
    run_job = args.test_job or args.test_all
    run_generic = args.test_generic_remote
    run_secrets = args.test_secrets

    # Default to live test if no mode specified
    if not run_live and not run_job and not run_generic and not run_secrets:
        run_live = True

    if run_generic and not (args.remote_endpoint and args.remote_body and args.remote_scores):
        parser.error("--test-generic-remote requires --remote-endpoint, --remote-body, and --remote-scores")

    # Determine endpoints (use different defaults for live vs job due to Docker networking)
    nat_endpoint_live = args.nat_endpoint or DEFAULT_NAT_ENDPOINT_LIVE
    nat_endpoint_job = args.nat_endpoint_job or DEFAULT_NAT_ENDPOINT_JOB

    # Load sample dataset
    dataset_rows = get_sample_remote_metric_dataset()
    if args.limit_samples:
        dataset_rows = dataset_rows[: args.limit_samples]

    print(f"\n{'=' * 60}")
    print("Remote Metrics Test (SDK)")
    print(f"{'=' * 60}")
    print(f"Platform URL: {args.base_url}")
    print(f"Workspace: {args.workspace}")
    if run_live:
        print(f"NAT Endpoint (live): {nat_endpoint_live}")
    if run_job:
        print(f"NAT Endpoint (job): {nat_endpoint_job}")
    print(f"Evaluator: {args.evaluator_name}")
    if run_generic:
        print(f"Generic Remote Endpoint: {args.remote_endpoint}")
    print(f"Dataset rows: {len(dataset_rows)}")
    print(f"Test modes: live={run_live}, job={run_job}, generic={run_generic}, secrets={run_secrets}")
    print(f"Output dir: {args.output_dir}")

    results: list[TestResult] = []

    # Connect to NeMo Platform using SDK
    print(f"\nConnecting to NeMo Platform at {args.base_url} using SDK...")
    client = NeMoPlatform(base_url=args.base_url)

    # Ensure API key secrets exist
    secrets_to_create = {}
    nat_api_key_secret = None
    if args.nat_api_key:
        secrets_to_create[NAT_API_KEY_SECRET] = args.nat_api_key
        nat_api_key_secret = NAT_API_KEY_SECRET

    remote_api_key_secret = None
    if args.remote_api_key and run_generic:
        secrets_to_create[REMOTE_API_KEY_SECRET] = args.remote_api_key
        remote_api_key_secret = REMOTE_API_KEY_SECRET

    if secrets_to_create:
        print("\nCreating secrets...")
        create_secrets(client, args.workspace, secrets_to_create)

    # Run live NAT evaluation test (uses localhost since it runs on host)
    if run_live and not run_generic:
        live_result = run_live_nat_test(
            client=client,
            workspace=args.workspace,
            nat_endpoint=nat_endpoint_live,
            evaluator_name=args.evaluator_name,
            dataset_rows=dataset_rows,
            api_key_secret=nat_api_key_secret,
            timeout_seconds=args.timeout,
            max_retries=args.max_retries,
            quiet=args.quiet,
        )
        results.append(live_result)

    # Run live generic remote evaluation test
    if run_live and run_generic:
        live_generic_result = run_live_generic_remote_test(
            client=client,
            workspace=args.workspace,
            remote_endpoint=args.remote_endpoint,
            body_template=args.remote_body,
            scores=args.remote_scores,
            dataset_rows=dataset_rows,
            api_key_secret=remote_api_key_secret,
            timeout_seconds=args.timeout,
            max_retries=args.max_retries,
            quiet=args.quiet,
        )
        results.append(live_generic_result)

    # Run NAT remote metric job test (uses host.docker.internal since job runs in container)
    if run_job and not run_generic:
        job_result = run_nat_job_test(
            client=client,
            workspace=args.workspace,
            nat_endpoint=nat_endpoint_job,
            evaluator_name=args.evaluator_name,
            dataset_rows=dataset_rows,
            api_key_secret=nat_api_key_secret,
            timeout_seconds=args.timeout,
            max_retries=args.max_retries,
            limit_samples=args.limit_samples,
            job_timeout=args.job_timeout,
            quiet=args.quiet,
        )
        results.append(job_result)

    # Run generic remote metric job test
    if run_job and run_generic:
        generic_result = run_generic_remote_job_test(
            client=client,
            workspace=args.workspace,
            remote_endpoint=args.remote_endpoint,
            body_template=args.remote_body,
            scores=args.remote_scores,
            dataset_rows=dataset_rows,
            api_key_secret=remote_api_key_secret,
            timeout_seconds=args.timeout,
            max_retries=args.max_retries,
            limit_samples=args.limit_samples,
            job_timeout=args.job_timeout,
            quiet=args.quiet,
        )
        results.append(generic_result)

    # Run secret integration tests
    if run_secrets:
        secrets_results = run_secrets_test(
            client=client,
            workspace=args.workspace,
            nat_endpoint_live=nat_endpoint_live,
            nat_endpoint_job=nat_endpoint_job,
            evaluator_name=args.evaluator_name,
            dataset_rows=dataset_rows,
            test_live=True,
            test_job=True,
            timeout_seconds=args.timeout,
            max_retries=args.max_retries,
            job_timeout=args.job_timeout,
            quiet=args.quiet,
        )
        results.extend(secrets_results)

    # Save and print results
    save_results(results, args.output_dir)
    print_summary(results)

    # Return exit code based on results
    failed = sum(1 for r in results if r.status not in ("completed", "skipped"))
    sys.exit(1 if failed > 0 else 0)


if __name__ == "__main__":
    main()
