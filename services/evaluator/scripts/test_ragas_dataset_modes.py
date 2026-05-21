#!/usr/bin/env python3
# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""
Test script for RAGAS evaluation metrics using DatasetRows, FilesetUrn, and InlineFileset.

This script tests RAGAS metrics with three dataset modes:
1. DatasetRows - Dataset rows embedded directly in the API request
2. FilesetUrn - Dataset uploaded to Files API first, then referenced by URN
3. InlineFileset - Dataset from HuggingFace with storage config (e.g., ramadhani/ragas-subject-test-01)

Usage:
    # Test with DatasetRows (default)
    python test_ragas_dataset_modes.py \
        --model-endpoint https://integrate.api.nvidia.com/v1/chat/completions \
        --model-name meta/llama-3.1-8b-instruct \
        --model-api-key <YOUR_API_KEY> \
        --embedding-endpoint https://integrate.api.nvidia.com/v1 \
        --embedding-model nvidia/nv-embedqa-e5-v5 \
        --embedding-api-key <YOUR_API_KEY> \
        --judge-endpoint https://integrate.api.nvidia.com/v1/chat/completions \
        --judge-model meta/llama-3.1-8b-instruct \
        --judge-api-key <YOUR_API_KEY>

    # Test with FilesetUrn (upload to Files API)
    python test_ragas_dataset_modes.py --use-fileset-urn \
        --model-endpoint https://integrate.api.nvidia.com/v1/chat/completions \
        --model-name meta/llama-3.1-8b-instruct \
        --model-api-key <YOUR_API_KEY> \
        --embedding-endpoint https://integrate.api.nvidia.com/v1 \
        --embedding-model nvidia/nv-embedqa-e5-v5 \
        --embedding-api-key <YOUR_API_KEY> \
        --judge-endpoint https://integrate.api.nvidia.com/v1/chat/completions \
        --judge-model meta/llama-3.1-8b-instruct \
        --judge-api-key <YOUR_API_KEY>

    # Test with InlineFileset (HuggingFace dataset - uses default public repo NotYours/test_ragas_dataset)
    # Note: --hf-token is optional for public repos
    python test_ragas_dataset_modes.py --use-inline-fileset \
        --model-endpoint https://integrate.api.nvidia.com/v1/chat/completions \
        --model-name meta/llama-3.1-8b-instruct \
        --model-api-key <YOUR_API_KEY> \
        --embedding-endpoint https://integrate.api.nvidia.com/v1 \
        --embedding-model nvidia/nv-embedqa-e5-v5 \
        --embedding-api-key <YOUR_API_KEY> \
        --judge-endpoint https://integrate.api.nvidia.com/v1/chat/completions \
        --judge-model meta/llama-3.1-8b-instruct \
        --judge-api-key <YOUR_API_KEY>

    # Test all three modes (uses default public HF repo NotYours/test_ragas_dataset for InlineFileset)
    python test_ragas_dataset_modes.py --test-all-modes \
        --model-endpoint https://integrate.api.nvidia.com/v1/chat/completions \
        --model-name meta/llama-3.1-8b-instruct \
        --model-api-key <YOUR_API_KEY> \
        --embedding-endpoint https://integrate.api.nvidia.com/v1 \
        --embedding-model nvidia/nv-embedqa-e5-v5 \
        --embedding-api-key <YOUR_API_KEY> \
        --judge-endpoint https://integrate.api.nvidia.com/v1/chat/completions \
        --judge-model meta/llama-3.1-8b-instruct \
        --judge-api-key <YOUR_API_KEY>
"""

import argparse
import asyncio
import json
import os
import subprocess
import sys
import threading
import time
import uuid
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import httpx
from nemo_platform import AsyncNeMoPlatform

# Default configuration
DEFAULT_BASE_URL = "http://localhost:8080"
DEFAULT_WORKSPACE = "default"

# Path to test datasets (relative to evaluator service root)
DEFAULT_DATASET_FILE = "tests/datasets/rag-retriever/small_dataset_with_retrieved_context.jsonl"

# Secret names
MODEL_API_KEY_SECRET = "model-api-key"
EMBEDDING_API_KEY_SECRET = "embedding-api-key"
JUDGE_API_KEY_SECRET = "judge-api-key"
JUDGE_EMBEDDING_API_KEY_SECRET = "judge-embedding-api-key"
HF_TOKEN_SECRET = "hf-token"

# Default HuggingFace dataset for InlineFileset mode
DEFAULT_HF_REPO_ID = "NotYours/test_ragas_dataset"
DEFAULT_HF_DATASET_PATH = "dataset.json"

# RAGAS metrics to test (subset that works with offline evaluation)
# These metrics evaluate pre-computed contexts and answers
# Note: All RAGAS metrics have the "rag-" prefix
RAGAS_OFFLINE_METRICS = [
    "rag-faithfulness",
    "rag-answer-correctness",
    "rag-answer-relevancy",
    "rag-context-recall",
]

# Thread-safe printing
_print_lock = threading.Lock()


def safe_print(*args, **kwargs):
    """Thread-safe print function."""
    with _print_lock:
        print(*args, **kwargs)


@dataclass
class JobResult:
    """Result of a metric job run."""

    metric: str
    mode: str  # "inline" or "fileset"
    job_name: str
    job_id: str
    status: str
    duration_seconds: float
    container_logs: str | None = None
    error: str | None = None


# ============================================================================
# Dataset Loading
# ============================================================================


def load_dataset_from_file(file_path: str) -> list[dict]:
    """Load dataset from a JSONL or JSON file.

    Args:
        file_path: Path to the dataset file (.jsonl or .json)

    Returns:
        List of dataset rows
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Dataset file not found: {file_path}")

    rows = []
    if path.suffix == ".jsonl":
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line:
                    rows.append(json.loads(line))
    elif path.suffix == ".json":
        with open(path) as f:
            data = json.load(f)
            if isinstance(data, list):
                rows = data
            else:
                rows = [data]
    else:
        raise ValueError(f"Unsupported file format: {path.suffix}. Use .jsonl or .json")

    return rows


def get_sample_ragas_dataset() -> list[dict]:
    """Get a sample RAGAS dataset for testing.

    Returns dataset in RAGAS columnar format where each field is a list.
    This matches the format expected by RAGAS evaluation.
    """
    # RAGAS expects columnar format: each field is a list of values
    return [
        {
            "question": [
                "When did the 2024 SF Taiwan Day take place?",
                "Where did the 2024 SF Taiwan Day take place?",
                "Who threw the first pitch during the 2024 SF Taiwan Day?",
            ],
            "contexts": [
                [
                    "The 2024 SF Taiwan Day was held on May 25th at the Oakland Coliseum. NVIDIA founder and CEO Jensen Huang threw the ceremonial first pitch."
                ],
                [
                    "The 2024 SF Taiwan Day was held on May 25th at the Oakland Coliseum. NVIDIA founder and CEO Jensen Huang threw the ceremonial first pitch."
                ],
                [
                    "The 2024 SF Taiwan Day was held on May 25th at the Oakland Coliseum. NVIDIA founder and CEO Jensen Huang threw the ceremonial first pitch."
                ],
            ],
            "ground_truth": [
                "May 25th",
                "Oakland Coliseum",
                "NVIDIA founder and CEO Jensen Huang",
            ],
            "answer": [
                "The 2024 SF Taiwan Day took place on May 25th.",
                "The 2024 SF Taiwan Day took place at the Oakland Coliseum.",
                "Jensen Huang, NVIDIA's founder and CEO, threw the ceremonial first pitch.",
            ],
        }
    ]


# ============================================================================
# FilesetUrn Support - For testing with data uploaded to Files API
# ============================================================================


async def create_dataset_fileset(
    base_url: str,
    workspace: str,
    dataset_rows: list[dict],
    fileset_name: str | None = None,
) -> str:
    """
    Create a fileset and upload a dataset to it using the SDK.

    Args:
        base_url: API base URL
        workspace: Workspace ID
        dataset_rows: Dataset rows to upload
        fileset_name: Optional fileset name (auto-generated if not provided)

    Returns:
        The fileset URN (workspace/fileset-name)
    """
    if fileset_name is None:
        fileset_name = f"ragas-test-dataset-{uuid.uuid4().hex[:8]}"

    sdk = AsyncNeMoPlatform(base_url=base_url)

    # Create the fileset
    safe_print(f"  📁 Creating fileset: {fileset_name}")
    await sdk.files.filesets.create(
        workspace=workspace,
        name=fileset_name,
        description="Test dataset fileset for RAGAS evaluation",
    )

    # Upload dataset as JSON file (RAGAS columnar format)
    # RAGAS expects a dict with list values, not a list of dicts
    # If dataset_rows is [columnar_dict], unwrap it for HuggingFace Dataset.from_dict() compatibility
    if len(dataset_rows) == 1 and all(isinstance(v, list) for v in dataset_rows[0].values()):
        data_to_upload = dataset_rows[0]  # Unwrap columnar format
    else:
        data_to_upload = dataset_rows

    dataset_filename = "dataset.json"
    dataset_content = json.dumps(data_to_upload, indent=2).encode("utf-8")
    safe_print(f"  📤 Uploading {dataset_filename} ({len(dataset_content)} bytes)")
    await sdk.files.upload_content(
        content=dataset_content,
        remote_path=dataset_filename,
        fileset=fileset_name,
        workspace=workspace,
    )

    # Return full file path reference (workspace/fileset-name/filename)
    # The FilesetRef must point to the actual file, not just the fileset directory
    fileset_file_urn = f"{workspace}/{fileset_name}/{dataset_filename}"
    safe_print(f"  ✅ Fileset created: {fileset_file_urn}")
    return fileset_file_urn


def create_dataset_fileset_sync(
    base_url: str,
    workspace: str,
    dataset_rows: list[dict],
    fileset_name: str | None = None,
) -> str:
    """Synchronous wrapper for create_dataset_fileset."""
    return asyncio.run(create_dataset_fileset(base_url, workspace, dataset_rows, fileset_name))


async def delete_fileset(base_url: str, workspace: str, fileset_name: str) -> bool:
    """Delete a fileset using the SDK."""
    sdk = AsyncNeMoPlatform(base_url=base_url)
    try:
        await sdk.files.filesets.delete(fileset_name, workspace=workspace)
        return True
    except Exception:
        return False


def delete_fileset_sync(base_url: str, workspace: str, fileset_name: str) -> bool:
    """Synchronous wrapper for delete_fileset."""
    return asyncio.run(delete_fileset(base_url, workspace, fileset_name))


def create_inline_fileset_spec(
    hf_repo_id: str,
    path: str,
    hf_token_secret: str | None = None,
) -> dict:
    """
    Create an InlineFileset dataset specification for HuggingFace datasets.

    Args:
        hf_repo_id: HuggingFace repository ID (e.g., "ramadhani/ragas-subject-test-01")
        path: Path to the dataset file within the repo (e.g., "dataset.json")
        hf_token_secret: Optional secret name for HuggingFace token

    Returns:
        InlineFileset dataset specification dict
    """
    storage_config: dict = {
        "type": "huggingface",
        "repo_id": hf_repo_id,
        "repo_type": "dataset",
    }
    if hf_token_secret:
        storage_config["token_secret"] = hf_token_secret

    return {
        "storage": storage_config,
        "path": path,
    }


# ============================================================================
# Secret Management
# ============================================================================


def ensure_secret(client: httpx.Client, base_url: str, workspace: str, secret_name: str, secret_value: str) -> bool:
    """Ensure a secret exists in the platform."""
    secrets_url = f"{base_url}/v2/workspaces/{workspace}/secrets"

    # Check if secret exists
    try:
        response = client.get(f"{secrets_url}/{secret_name}")
        if response.status_code == 200:
            safe_print(f"  Secret '{secret_name}' already exists")
            return True
    except Exception:
        pass

    # Create the secret
    try:
        response = client.post(
            secrets_url,
            json={"name": secret_name, "value": secret_value},
        )
        if response.status_code in (200, 201):
            safe_print(f"  Created secret '{secret_name}'")
            return True
        else:
            safe_print(f"  Failed to create secret '{secret_name}': {response.status_code}")
            return False
    except Exception as e:
        safe_print(f"  Error creating secret '{secret_name}': {e}")
        return False


# ============================================================================
# Job Payload Creation
# ============================================================================


def create_ragas_offline_job_payload(
    metric: str,
    # Dataset - one of: inline rows, fileset URN, or inline fileset spec
    dataset_rows: list[dict] | None = None,
    fileset_urn: str | None = None,
    inline_fileset_spec: dict | None = None,
    # RAG model config (required for RAG job type recognition)
    model_endpoint: str | None = None,
    model_name: str | None = None,
    model_api_key_secret: str | None = None,
    # Embedding model config (required for RAG job type recognition)
    embedding_endpoint: str | None = None,
    embedding_model: str | None = None,
    embedding_api_key_secret: str | None = None,
    # Judge LLM config
    judge_endpoint: str | None = None,
    judge_model: str | None = None,
    judge_api_key_secret: str | None = None,
    judge_request_timeout: int = 120,
    judge_max_retries: int = 3,
    # Judge embeddings config (optional, required for some metrics)
    judge_embedding_endpoint: str | None = None,
    judge_embedding_model: str | None = None,
    judge_embedding_api_key_secret: str | None = None,
    # Limit samples
    limit_samples: int | None = None,
) -> dict:
    """Create the job payload for a RAGAS RAG metric evaluation.

    RAG jobs require model and retriever_pipeline config to be recognized as RAG job type.

    Args:
        metric: The metric name (e.g., 'rag-faithfulness', 'rag-answer-correctness')
        dataset_rows: List of evaluation rows (mutually exclusive with fileset_urn/inline_fileset_spec)
        fileset_urn: FilesetUrn (workspace/fileset-name/file) for dataset
        inline_fileset_spec: InlineFileset spec dict with storage config and path
        model_endpoint: RAG model endpoint URL (required)
        model_name: RAG model name (required)
        model_api_key_secret: Secret name for RAG model API key
        embedding_endpoint: Embedding model endpoint URL (required)
        embedding_model: Embedding model name (required)
        embedding_api_key_secret: Secret name for embedding model API key
        judge_endpoint: Chat endpoint for judge model
        judge_model: Model name for the judge
        judge_api_key_secret: Secret name for judge API key
        judge_request_timeout: Request timeout for judge
        judge_max_retries: Max retries for judge requests
        judge_embedding_endpoint: Embeddings endpoint for judge (optional)
        judge_embedding_model: Embeddings model name (optional)
        judge_embedding_api_key_secret: Secret name for judge embeddings API key
        limit_samples: Number of samples to evaluate

    Returns:
        Job payload dictionary
    """
    # Validate exactly one dataset source is provided
    dataset_sources = [dataset_rows, fileset_urn, inline_fileset_spec]
    provided_sources = sum(1 for s in dataset_sources if s is not None)
    if provided_sources == 0:
        raise ValueError("One of dataset_rows, fileset_urn, or inline_fileset_spec must be provided")
    if provided_sources > 1:
        raise ValueError("Only one of dataset_rows, fileset_urn, or inline_fileset_spec can be provided")
    if not model_endpoint or not model_name:
        raise ValueError("model_endpoint and model_name are required for RAG jobs")
    if not embedding_endpoint or not embedding_model:
        raise ValueError("embedding_endpoint and embedding_model are required for RAG jobs")

    # Build RAG model config - API expects 'url' not 'endpoint'
    model_config: dict = {
        "url": model_endpoint,
        "name": model_name,
    }
    if model_api_key_secret:
        model_config["api_key_secret"] = model_api_key_secret

    # Build embedding model config - API expects 'url' not 'endpoint'
    embedding_model_config: dict = {
        "url": embedding_endpoint,
        "name": embedding_model,
    }
    if embedding_api_key_secret:
        embedding_model_config["api_key_secret"] = embedding_api_key_secret

    # Build retriever pipeline
    retriever_pipeline: dict = {
        "embedding_model": embedding_model_config,
    }

    # Build metric params
    metric_params: dict = {}

    # Add judge LLM config if provided
    if judge_endpoint and judge_model:
        judge_config: dict = {
            "model": {
                "url": judge_endpoint,
                "name": judge_model,
            },
            "request_timeout": judge_request_timeout,
            "max_retries": judge_max_retries,
            "inference_params": {
                "max_tokens": 4000,
            },
        }
        if judge_api_key_secret:
            judge_config["model"]["api_key_secret"] = judge_api_key_secret
        metric_params["judge_llm"] = judge_config

    # Add judge embeddings config if provided
    if judge_embedding_endpoint and judge_embedding_model:
        judge_embeddings_config: dict = {
            "model": {
                "url": judge_embedding_endpoint,
                "name": judge_embedding_model,
            }
        }
        if judge_embedding_api_key_secret:
            judge_embeddings_config["model"]["api_key_secret"] = judge_embedding_api_key_secret
        metric_params["judge_embeddings"] = judge_embeddings_config

    # Build dataset spec - one of: inline rows, FilesetUrn, or InlineFileset
    if fileset_urn:
        dataset_spec: dict | str = fileset_urn
    elif inline_fileset_spec:
        dataset_spec = inline_fileset_spec
    else:
        assert dataset_rows is not None
        rows = dataset_rows[:limit_samples] if limit_samples else dataset_rows
        dataset_spec = {"rows": rows}

    # Build job spec for RAG evaluation
    job_spec: dict = {
        "metric": f"system/{metric}",
        "model": model_config,
        "retriever_pipeline": retriever_pipeline,
        "dataset": dataset_spec,
    }

    if metric_params:
        job_spec["metric_params"] = metric_params

    if limit_samples:
        job_spec["limit_samples"] = limit_samples

    return {"spec": job_spec}


# ============================================================================
# Job Submission and Monitoring
# ============================================================================


def submit_job(client: httpx.Client, base_url: str, workspace: str, payload: dict) -> dict:
    """Submit a metric job and return the response."""
    url = f"{base_url}/v2/workspaces/{workspace}/evaluation/metric-jobs/"
    response = client.post(url, json=payload)
    if response.status_code >= 400:
        try:
            error_detail = response.json()
            safe_print(f"  API Error: {response.status_code} - {error_detail}")
        except Exception:
            safe_print(f"  API Error: {response.status_code} - {response.text}")
    response.raise_for_status()
    return response.json()


def get_job_status(client: httpx.Client, base_url: str, workspace: str, job_name: str) -> dict:
    """Get the current status of a job."""
    url = f"{base_url}/v2/workspaces/{workspace}/evaluation/metric-jobs/{job_name}"
    response = client.get(url)
    response.raise_for_status()
    return response.json()


def wait_for_job(
    client: httpx.Client,
    base_url: str,
    workspace: str,
    job_name: str,
    poll_interval: float = 2.0,
    timeout: float = 600.0,
    quiet: bool = False,
) -> dict:
    """Wait for a job to complete and return the final status."""
    start_time = time.time()
    terminal_statuses = {"completed", "error", "cancelled"}

    while True:
        elapsed = time.time() - start_time
        if elapsed > timeout:
            raise TimeoutError(f"Job {job_name} did not complete within {timeout} seconds")

        job = get_job_status(client, base_url, workspace, job_name)
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


# ============================================================================
# Test Runner
# ============================================================================


def run_metric_test(
    client: httpx.Client,
    base_url: str,
    workspace: str,
    metric: str,
    mode: str,  # "inline", "fileset", or "inline_fileset"
    dataset_rows: list[dict] | None,
    fileset_urn: str | None,
    inline_fileset_spec: dict | None,
    # RAG model config
    model_endpoint: str,
    model_name: str,
    model_api_key_secret: str | None,
    # Embedding model config
    embedding_endpoint: str,
    embedding_model: str,
    embedding_api_key_secret: str | None,
    # Judge LLM config
    judge_endpoint: str | None,
    judge_model: str | None,
    judge_api_key_secret: str | None,
    judge_request_timeout: int,
    judge_max_retries: int,
    judge_embedding_endpoint: str | None,
    judge_embedding_model: str | None,
    judge_embedding_api_key_secret: str | None,
    limit_samples: int | None,
    timeout: float,
    quiet: bool = False,
) -> JobResult:
    """Run a single metric test and return the result."""
    if not quiet:
        safe_print(f"\n{'=' * 60}")
        safe_print(f"Testing: {metric} (mode: {mode})")
        safe_print(f"  Dataset mode: {mode}")
        if mode == "inline":
            safe_print(f"  Dataset rows: {len(dataset_rows or [])}")
        elif mode == "fileset":
            safe_print(f"  Fileset URN: {fileset_urn}")
        elif mode == "inline_fileset":
            safe_print(f"  InlineFileset: {inline_fileset_spec}")
        if judge_endpoint and judge_model:
            safe_print(f"  Judge LLM: {judge_model}")
        if judge_embedding_endpoint and judge_embedding_model:
            safe_print(f"  Judge embeddings: {judge_embedding_model}")
        safe_print(f"{'=' * 60}")
    else:
        safe_print(f"[{metric}:{mode}] Starting...")

    start_time = time.time()

    try:
        # Create payload based on mode
        if mode == "fileset":
            payload = create_ragas_offline_job_payload(
                metric=metric,
                fileset_urn=fileset_urn,
                model_endpoint=model_endpoint,
                model_name=model_name,
                model_api_key_secret=model_api_key_secret,
                embedding_endpoint=embedding_endpoint,
                embedding_model=embedding_model,
                embedding_api_key_secret=embedding_api_key_secret,
                judge_endpoint=judge_endpoint,
                judge_model=judge_model,
                judge_api_key_secret=judge_api_key_secret,
                judge_request_timeout=judge_request_timeout,
                judge_max_retries=judge_max_retries,
                judge_embedding_endpoint=judge_embedding_endpoint,
                judge_embedding_model=judge_embedding_model,
                judge_embedding_api_key_secret=judge_embedding_api_key_secret,
                limit_samples=limit_samples,
            )
        elif mode == "inline_fileset":
            payload = create_ragas_offline_job_payload(
                metric=metric,
                inline_fileset_spec=inline_fileset_spec,
                model_endpoint=model_endpoint,
                model_name=model_name,
                model_api_key_secret=model_api_key_secret,
                embedding_endpoint=embedding_endpoint,
                embedding_model=embedding_model,
                embedding_api_key_secret=embedding_api_key_secret,
                judge_endpoint=judge_endpoint,
                judge_model=judge_model,
                judge_api_key_secret=judge_api_key_secret,
                judge_request_timeout=judge_request_timeout,
                judge_max_retries=judge_max_retries,
                judge_embedding_endpoint=judge_embedding_endpoint,
                judge_embedding_model=judge_embedding_model,
                judge_embedding_api_key_secret=judge_embedding_api_key_secret,
                limit_samples=limit_samples,
            )
        else:  # inline
            payload = create_ragas_offline_job_payload(
                metric=metric,
                dataset_rows=dataset_rows,
                model_endpoint=model_endpoint,
                model_name=model_name,
                model_api_key_secret=model_api_key_secret,
                embedding_endpoint=embedding_endpoint,
                embedding_model=embedding_model,
                embedding_api_key_secret=embedding_api_key_secret,
                judge_endpoint=judge_endpoint,
                judge_model=judge_model,
                judge_api_key_secret=judge_api_key_secret,
                judge_request_timeout=judge_request_timeout,
                judge_max_retries=judge_max_retries,
                judge_embedding_endpoint=judge_embedding_endpoint,
                judge_embedding_model=judge_embedding_model,
                judge_embedding_api_key_secret=judge_embedding_api_key_secret,
                limit_samples=limit_samples,
            )

        if not quiet:
            safe_print("  Submitting job...")
            safe_print(f"  Payload: {json.dumps(payload, indent=2)}")

        job_response = submit_job(client, base_url, workspace, payload)
        job_name = job_response["name"]
        job_id = job_response["id"]

        if not quiet:
            safe_print(f"  Job created: {job_name} ({job_id})")
        else:
            safe_print(f"[{metric}:{mode}] Job submitted: {job_name}")

        # Wait for completion
        if not quiet:
            safe_print("  Waiting for completion...")
        final_job = wait_for_job(client, base_url, workspace, job_name, timeout=timeout, quiet=quiet)
        status = final_job.get("status", "unknown")
        duration = time.time() - start_time

        # Get container logs
        if not quiet:
            safe_print("  Getting container logs...")
        logs = get_container_logs(job_name)

        if not quiet:
            safe_print(f"  Status: {status}")
            safe_print(f"  Duration: {duration:.1f}s")
        else:
            status_icon = "✅" if status == "completed" else "❌"
            safe_print(f"[{metric}:{mode}] {status_icon} {status} ({duration:.1f}s)")

        return JobResult(
            metric=metric,
            mode=mode,
            job_name=job_name,
            job_id=job_id,
            status=status,
            duration_seconds=duration,
            container_logs=logs,
        )

    except Exception as e:
        duration = time.time() - start_time
        safe_print(f"[{metric}:{mode}] ❌ ERROR: {e}")
        return JobResult(
            metric=metric,
            mode=mode,
            job_name="",
            job_id="",
            status="error",
            duration_seconds=duration,
            error=str(e),
        )


# ============================================================================
# Results Reporting
# ============================================================================


def save_results(results: list[JobResult], output_dir: Path) -> None:
    """Save test results to files."""
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Save individual logs
    for result in results:
        if result.container_logs:
            log_file = output_dir / f"{result.metric}_{result.mode}_{timestamp}.log"
            log_file.write_text(result.container_logs)
            print(f"  Saved logs: {log_file}")

    # Save summary
    summary = {
        "timestamp": timestamp,
        "results": [
            {
                "metric": r.metric,
                "mode": r.mode,
                "job_name": r.job_name,
                "job_id": r.job_id,
                "status": r.status,
                "duration_seconds": r.duration_seconds,
                "error": r.error,
            }
            for r in results
        ],
    }
    summary_file = output_dir / f"summary_{timestamp}.json"
    summary_file.write_text(json.dumps(summary, indent=2))
    print(f"  Saved summary: {summary_file}")


def print_summary(results: list[JobResult]) -> None:
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
    inline_results = [r for r in results if r.mode == "inline"]
    fileset_results = [r for r in results if r.mode == "fileset"]
    inline_fileset_results = [r for r in results if r.mode == "inline_fileset"]

    if inline_results:
        print("DatasetRows mode:")
        for result in inline_results:
            status_icon = "✅" if result.status == "completed" else "❌" if result.status != "skipped" else "⏭️"
            print(f"  {status_icon} {result.metric}: {result.status} ({result.duration_seconds:.1f}s)")
            if result.error:
                print(f"      Error: {result.error}")

    if fileset_results:
        print("\nFilesetUrn mode:")
        for result in fileset_results:
            status_icon = "✅" if result.status == "completed" else "❌" if result.status != "skipped" else "⏭️"
            print(f"  {status_icon} {result.metric}: {result.status} ({result.duration_seconds:.1f}s)")
            if result.error:
                print(f"      Error: {result.error}")

    if inline_fileset_results:
        print("\nInlineFileset mode (HuggingFace):")
        for result in inline_fileset_results:
            status_icon = "✅" if result.status == "completed" else "❌" if result.status != "skipped" else "⏭️"
            print(f"  {status_icon} {result.metric}: {result.status} ({result.duration_seconds:.1f}s)")
            if result.error:
                print(f"      Error: {result.error}")


# ============================================================================
# Main
# ============================================================================


def main():
    parser = argparse.ArgumentParser(
        description="Test RAGAS evaluation metrics with DatasetRows and FilesetUrn modes",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Available RAGAS metrics:
  {", ".join(RAGAS_OFFLINE_METRICS)}

Dataset modes:
  - DatasetRows: Dataset rows embedded directly in API request (default)
  - FilesetUrn: Dataset uploaded to Files API and referenced by URN
  - InlineFileset: Dataset from HuggingFace with storage config

Example (all modes - uses default public HF repo NotYours/test_ragas_dataset for InlineFileset):
  python test_ragas_dataset_modes.py --test-all-modes \\
      --model-endpoint https://integrate.api.nvidia.com/v1/chat/completions \\
      --model-name meta/llama-3.1-8b-instruct \\
      --model-api-key $NVIDIA_API_KEY \\
      --embedding-endpoint https://integrate.api.nvidia.com/v1 \\
      --embedding-model nvidia/nv-embedqa-e5-v5 \\
      --embedding-api-key $NVIDIA_API_KEY \\
      --judge-endpoint https://integrate.api.nvidia.com/v1/chat/completions \\
      --judge-model meta/llama-3.1-8b-instruct \\
      --judge-api-key $NVIDIA_API_KEY

Example (InlineFileset only - default: NotYours/test_ragas_dataset/dataset.json):
  python test_ragas_dataset_modes.py --use-inline-fileset \\
      --model-endpoint https://integrate.api.nvidia.com/v1/chat/completions \\
      ...

Example (InlineFileset with private repo):
  python test_ragas_dataset_modes.py --use-inline-fileset \\
      --hf-repo-id my-org/private-dataset --hf-token $HF_TOKEN \\
      --model-endpoint https://integrate.api.nvidia.com/v1/chat/completions \\
      ...
        """,
    )

    # Metrics selection
    parser.add_argument(
        "--metrics",
        nargs="+",
        choices=RAGAS_OFFLINE_METRICS,
        help=f"Specific metrics to test (default: {RAGAS_OFFLINE_METRICS[0]})",
    )

    # Dataset mode
    parser.add_argument(
        "--use-fileset-urn",
        action="store_true",
        help="Use FilesetUrn mode (upload dataset to Files API)",
    )
    parser.add_argument(
        "--use-inline-fileset",
        action="store_true",
        help="Use InlineFileset mode (HuggingFace dataset with storage config)",
    )
    parser.add_argument(
        "--test-both-modes",
        action="store_true",
        help="Test both DatasetRows and FilesetUrn modes",
    )
    parser.add_argument(
        "--test-all-modes",
        action="store_true",
        help="Test all three modes: DatasetRows, FilesetUrn, and InlineFileset",
    )

    # Dataset source
    parser.add_argument(
        "--dataset-file",
        type=str,
        default=None,
        help="Path to dataset file (.jsonl or .json). Default: uses built-in sample dataset",
    )
    parser.add_argument(
        "--limit-samples",
        type=int,
        default=None,
        help="Limit number of samples to evaluate",
    )

    # HuggingFace InlineFileset config
    parser.add_argument(
        "--hf-repo-id",
        type=str,
        default=DEFAULT_HF_REPO_ID,
        help=f"HuggingFace dataset repo ID (default: {DEFAULT_HF_REPO_ID})",
    )
    parser.add_argument(
        "--hf-dataset-path",
        type=str,
        default=DEFAULT_HF_DATASET_PATH,
        help=f"Path to dataset file within HF repo (default: {DEFAULT_HF_DATASET_PATH})",
    )
    parser.add_argument(
        "--hf-token",
        type=str,
        default=os.environ.get("HF_TOKEN"),
        help="HuggingFace token (optional for public repos, required for private). Can also be set via HF_TOKEN env var.",
    )

    # API config
    parser.add_argument(
        "--base-url",
        default=DEFAULT_BASE_URL,
        help=f"Base URL of the platform (default: {DEFAULT_BASE_URL})",
    )
    parser.add_argument(
        "--workspace",
        default=DEFAULT_WORKSPACE,
        help=f"Workspace to use (default: {DEFAULT_WORKSPACE})",
    )

    # RAG model config (required for RAG job type)
    parser.add_argument(
        "--model-endpoint",
        required=True,
        help="RAG model endpoint URL (required for RAG job type)",
    )
    parser.add_argument(
        "--model-name",
        required=True,
        help="RAG model name (required for RAG job type)",
    )
    parser.add_argument(
        "--model-api-key",
        default=os.environ.get("MODEL_API_KEY"),
        help="API key for RAG model. Can also be set via MODEL_API_KEY env var.",
    )

    # Embedding model config (required for RAG job type)
    parser.add_argument(
        "--embedding-endpoint",
        required=True,
        help="Embedding model endpoint URL (required for RAG job type)",
    )
    parser.add_argument(
        "--embedding-model",
        required=True,
        help="Embedding model name (required for RAG job type)",
    )
    parser.add_argument(
        "--embedding-api-key",
        default=os.environ.get("EMBEDDING_API_KEY"),
        help="API key for embedding model. Can also be set via EMBEDDING_API_KEY env var.",
    )

    # Judge LLM config
    parser.add_argument(
        "--judge-endpoint",
        required=True,
        help="Judge LLM endpoint URL (required)",
    )
    parser.add_argument(
        "--judge-model",
        required=True,
        help="Judge LLM model name (required)",
    )
    parser.add_argument(
        "--judge-api-key",
        default=os.environ.get("JUDGE_API_KEY"),
        help="API key for judge LLM. Can also be set via JUDGE_API_KEY env var.",
    )
    parser.add_argument(
        "--judge-request-timeout",
        type=int,
        default=120,
        help="Request timeout for judge LLM in seconds (default: 120)",
    )
    parser.add_argument(
        "--judge-max-retries",
        type=int,
        default=3,
        help="Max retries for judge LLM requests (default: 3)",
    )

    # Judge embeddings config (optional)
    parser.add_argument(
        "--judge-embedding-endpoint",
        help="Judge embeddings endpoint URL (optional)",
    )
    parser.add_argument(
        "--judge-embedding-model",
        help="Judge embeddings model name (optional)",
    )
    parser.add_argument(
        "--judge-embedding-api-key",
        default=os.environ.get("JUDGE_EMBEDDING_API_KEY"),
        help="API key for judge embeddings. Can also be set via JUDGE_EMBEDDING_API_KEY env var.",
    )

    # Job config
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("./ragas-dataset-test-results"),
        help="Directory to save results (default: ./ragas-dataset-test-results)",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=600.0,
        help="Timeout per job in seconds (default: 600 = 10 min)",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Reduce output verbosity",
    )

    args = parser.parse_args()

    # Determine which metrics to test
    metrics_to_test = args.metrics or [RAGAS_OFFLINE_METRICS[0]]

    # Determine which modes to test
    modes_to_test = []
    if args.test_all_modes:
        modes_to_test = ["inline", "fileset", "inline_fileset"]
    elif args.test_both_modes:
        modes_to_test = ["inline", "fileset"]
    elif args.use_inline_fileset:
        modes_to_test = ["inline_fileset"]
    elif args.use_fileset_urn:
        modes_to_test = ["fileset"]
    else:
        modes_to_test = ["inline"]

    # Load dataset
    if args.dataset_file:
        print(f"Loading dataset from: {args.dataset_file}")
        dataset_rows = load_dataset_from_file(args.dataset_file)
    else:
        print("Using built-in sample RAGAS dataset")
        dataset_rows = get_sample_ragas_dataset()

    if args.limit_samples:
        dataset_rows = dataset_rows[: args.limit_samples]

    print(f"\n{'=' * 60}")
    print("RAGAS Dataset Modes Test")
    print(f"{'=' * 60}")
    print(f"Base URL: {args.base_url}")
    print(f"Workspace: {args.workspace}")
    print(f"Metrics to test: {', '.join(metrics_to_test)}")
    print(f"Modes to test: {', '.join(modes_to_test)}")
    print(f"Dataset rows: {len(dataset_rows)}")
    print(f"RAG model: {args.model_name}")
    print(f"Embedding model: {args.embedding_model}")
    print(f"Judge LLM: {args.judge_model}")
    if args.judge_embedding_model:
        print(f"Judge embeddings: {args.judge_embedding_model}")
    if "inline_fileset" in modes_to_test:
        print(f"HF repo: {args.hf_repo_id}")
        print(f"HF dataset path: {args.hf_dataset_path}")
        print(f"HF token: {'provided' if args.hf_token else 'not provided (public repo)'}")
    print(f"Output dir: {args.output_dir}")

    results: list[JobResult] = []
    created_filesets: list[str] = []  # Track filesets for cleanup

    with httpx.Client(timeout=30.0, follow_redirects=True) as client:
        # Create model API key secret if provided
        model_api_key_secret = None
        if args.model_api_key:
            print("\nEnsuring model API key secret exists...")
            if ensure_secret(client, args.base_url, args.workspace, MODEL_API_KEY_SECRET, args.model_api_key):
                model_api_key_secret = MODEL_API_KEY_SECRET

        # Create embedding API key secret if provided
        embedding_api_key_secret = None
        if args.embedding_api_key:
            print("Ensuring embedding API key secret exists...")
            if ensure_secret(client, args.base_url, args.workspace, EMBEDDING_API_KEY_SECRET, args.embedding_api_key):
                embedding_api_key_secret = EMBEDDING_API_KEY_SECRET

        # Create judge API key secret if provided
        judge_api_key_secret = None
        if args.judge_api_key:
            print("Ensuring judge API key secret exists...")
            if ensure_secret(client, args.base_url, args.workspace, JUDGE_API_KEY_SECRET, args.judge_api_key):
                judge_api_key_secret = JUDGE_API_KEY_SECRET

        # Create judge embedding API key secret if provided
        judge_embedding_api_key_secret = None
        if args.judge_embedding_api_key:
            print("Ensuring judge embedding API key secret exists...")
            if ensure_secret(
                client, args.base_url, args.workspace, JUDGE_EMBEDDING_API_KEY_SECRET, args.judge_embedding_api_key
            ):
                judge_embedding_api_key_secret = JUDGE_EMBEDDING_API_KEY_SECRET

        # Create HuggingFace token secret if provided and inline_fileset mode is used
        hf_token_secret = None
        if args.hf_token and "inline_fileset" in modes_to_test:
            print("Ensuring HuggingFace token secret exists...")
            if ensure_secret(client, args.base_url, args.workspace, HF_TOKEN_SECRET, args.hf_token):
                hf_token_secret = HF_TOKEN_SECRET

        # Test each combination of metric and mode
        for mode in modes_to_test:
            fileset_urn = None
            inline_fileset_spec = None

            # Create fileset if needed
            if mode == "fileset":
                print(f"\n📁 Creating fileset for {mode} mode...")
                try:
                    fileset_name = f"ragas-test-{uuid.uuid4().hex[:8]}"
                    fileset_urn = create_dataset_fileset_sync(
                        args.base_url,
                        args.workspace,
                        dataset_rows,
                        fileset_name=fileset_name,
                    )
                    created_filesets.append(fileset_name)
                except Exception as e:
                    print(f"  ❌ Failed to create fileset: {e}")
                    # Add error results for all metrics in this mode
                    for metric in metrics_to_test:
                        results.append(
                            JobResult(
                                metric=metric,
                                mode=mode,
                                job_name="",
                                job_id="",
                                status="error",
                                duration_seconds=0,
                                error=f"Failed to create fileset: {e}",
                            )
                        )
                    continue
            elif mode == "inline_fileset":
                print("\n📁 Creating InlineFileset spec for HuggingFace dataset...")
                print(f"  HF repo: {args.hf_repo_id}")
                print(f"  Dataset path: {args.hf_dataset_path}")
                print(f"  Using token: {'yes' if hf_token_secret else 'no (public repo)'}")
                inline_fileset_spec = create_inline_fileset_spec(
                    hf_repo_id=args.hf_repo_id,
                    path=args.hf_dataset_path,
                    hf_token_secret=hf_token_secret,
                )

            # Run tests for each metric
            for metric in metrics_to_test:
                result = run_metric_test(
                    client=client,
                    base_url=args.base_url,
                    workspace=args.workspace,
                    metric=metric,
                    mode=mode,
                    dataset_rows=dataset_rows if mode == "inline" else None,
                    fileset_urn=fileset_urn if mode == "fileset" else None,
                    inline_fileset_spec=inline_fileset_spec if mode == "inline_fileset" else None,
                    model_endpoint=args.model_endpoint,
                    model_name=args.model_name,
                    model_api_key_secret=model_api_key_secret,
                    embedding_endpoint=args.embedding_endpoint,
                    embedding_model=args.embedding_model,
                    embedding_api_key_secret=embedding_api_key_secret,
                    judge_endpoint=args.judge_endpoint,
                    judge_model=args.judge_model,
                    judge_api_key_secret=judge_api_key_secret,
                    judge_request_timeout=args.judge_request_timeout,
                    judge_max_retries=args.judge_max_retries,
                    judge_embedding_endpoint=args.judge_embedding_endpoint,
                    judge_embedding_model=args.judge_embedding_model,
                    judge_embedding_api_key_secret=judge_embedding_api_key_secret,
                    limit_samples=args.limit_samples,
                    timeout=args.timeout,
                    quiet=args.quiet,
                )
                results.append(result)

    # Cleanup filesets
    if created_filesets:
        print(f"\n🧹 Cleaning up {len(created_filesets)} filesets...")
        for fileset_name in created_filesets:
            try:
                if delete_fileset_sync(args.base_url, args.workspace, fileset_name):
                    print(f"  ✅ Deleted fileset: {fileset_name}")
                else:
                    print(f"  ⚠️  Could not delete fileset: {fileset_name}")
            except Exception as e:
                print(f"  ⚠️  Error deleting fileset {fileset_name}: {e}")

    # Save and print results
    save_results(results, args.output_dir)
    print_summary(results)

    # Return exit code based on results
    failed = sum(1 for r in results if r.status not in ("completed", "skipped"))
    sys.exit(1 if failed > 0 else 0)


if __name__ == "__main__":
    main()
