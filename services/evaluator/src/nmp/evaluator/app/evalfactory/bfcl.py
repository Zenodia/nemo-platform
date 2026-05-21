# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import itertools

import nmp.evaluator.app.jobs.evalfactory.models as ef
from nemo_evaluator_sdk.values import SecretRef
from nmp.evaluator.app.evalfactory.convert import augment_online_job
from nmp.evaluator.app.evalfactory.handler import BaseSystemHandler
from nmp.evaluator.app.evalfactory.labels import LABEL_AGENTIC, new_labels
from nmp.evaluator.app.values import (
    Parameter,
    SystemBenchmark,
    SystemBenchmarkJob,
    SystemBenchmarkOnlineJob,
)
from nmp.evaluator.config import settings

# BFCL harness limitations (params passed but ignored by the harness):
# - temperature: Always 0.001 (BFCL ignores params.inference.temperature entirely)
# - max_tokens: NOT passed to the model (BFCL handles generation internally)
# - max_retries: NOT used by BFCL (no retry mechanism)
#
# Working params:
# - parallelism: Works, maps to --num-threads
# - limit_samples: Works, applies to the single task category for per-task metrics

# API keys required for executable test categories (exec_*, rest)
_api_key_params = [
    Parameter(
        name="rapid_api_key",
        type="secret",
        description="Secret reference to an API key for RapidAPI (free tier supported; subscription required).",
    ),
    Parameter(
        name="exchangerate_api_key",
        type="secret",
        description="Secret reference to an API key for ExchangeRate-API.",
    ),
    Parameter(
        name="omdb_api_key",
        type="secret",
        description="Secret reference to an API key for OMDb.",
    ),
    Parameter(
        name="geocode_api_key",
        type="secret",
        description="Secret reference to an API key for Geocode.",
    ),
]


class BFCLHandler(BaseSystemHandler):
    @classmethod
    def docker_image(cls) -> str:
        return settings.evalfactory.bfcl

    @classmethod
    def system_benchmarks(cls) -> list[SystemBenchmark]:
        return cls._system_benchmarks

    def augment_benchmark_job(self, job: SystemBenchmarkJob, output_dir: str) -> ef.EvaluationJob:
        self.validate_supported_benchmark_job_types(job)
        self.validate_params(job.benchmark_params, job.benchmark.required_params, job.benchmark.optional_params)
        assert isinstance(job, SystemBenchmarkOnlineJob)

        # Extract task category from benchmark name: "bfclv3-parallel-multiple" → "parallel_multiple"
        task_category = job.benchmark.name.removeprefix("bfclv3-").replace("-", "_")

        # Create a copy to avoid mutating the shared SystemBenchmark object
        job.benchmark = job.benchmark.model_copy(update={"name": "bfclv3"})

        ef_job = augment_online_job(job, output_dir)

        # Override the config type to use the BFCL harness name, and set the task category
        # Note: We don't mutate job.benchmark.name as it's a shared SystemBenchmark object
        if ef_job.config:
            ef_job.config.type = "bfclv3"
            if ef_job.config.params:
                ef_job.config.params.task = task_category

        return ef_job

    def benchmark_job_secrets(self, job: SystemBenchmarkJob) -> dict[str, SecretRef]:
        """BFCL secrets mapping: parameter name (uppercase) → secret reference."""
        secrets = {}
        for param in itertools.chain(job.benchmark.required_params, job.benchmark.optional_params):
            if param.type == "secret":
                secret_ref = job.benchmark_params.get(param.name)
                if secret_ref:
                    secrets[param.name.upper()] = SecretRef(secret_ref)
        return secrets

    _system_benchmarks = [
        # === Single-turn AST (no API keys) ===
        SystemBenchmark(
            name="bfclv3-simple",
            description="BFCL v3 simple single-turn function calling. Tests basic function call generation.",
            labels=new_labels("bfcl", LABEL_AGENTIC),
        ),
        SystemBenchmark(
            name="bfclv3-parallel",
            description="BFCL v3 parallel single-turn function calling. Tests multiple parallel function calls.",
            labels=new_labels("bfcl", LABEL_AGENTIC),
        ),
        SystemBenchmark(
            name="bfclv3-multiple",
            description="BFCL v3 multiple single-turn function calling. Tests sequential function calls.",
            labels=new_labels("bfcl", LABEL_AGENTIC),
        ),
        SystemBenchmark(
            name="bfclv3-parallel-multiple",
            description="BFCL v3 parallel-multiple single-turn function calling. Tests complex call patterns.",
            labels=new_labels("bfcl", LABEL_AGENTIC),
        ),
        # === Language-specific AST (no API keys) ===
        SystemBenchmark(
            name="bfclv3-java",
            description="BFCL v3 Java function calling. Tests function calls with Java-style APIs.",
            labels=new_labels("bfcl", LABEL_AGENTIC),
        ),
        SystemBenchmark(
            name="bfclv3-javascript",
            description="BFCL v3 JavaScript function calling. Tests function calls with JavaScript-style APIs.",
            labels=new_labels("bfcl", LABEL_AGENTIC),
        ),
        # === Irrelevance detection (no API keys) ===
        SystemBenchmark(
            name="bfclv3-irrelevance",
            description="BFCL v3 irrelevance detection. Tests ability to detect when no function call is needed.",
            labels=new_labels("bfcl", LABEL_AGENTIC),
        ),
        # === Live AST (no API keys) ===
        SystemBenchmark(
            name="bfclv3-live-simple",
            description="BFCL v3 live simple. Tests function calling with real-world API schemas.",
            labels=new_labels("bfcl", LABEL_AGENTIC),
        ),
        SystemBenchmark(
            name="bfclv3-live-multiple",
            description="BFCL v3 live multiple. Tests sequential calls with real-world API schemas.",
            labels=new_labels("bfcl", LABEL_AGENTIC),
        ),
        SystemBenchmark(
            name="bfclv3-live-parallel",
            description="BFCL v3 live parallel. Tests parallel calls with real-world API schemas.",
            labels=new_labels("bfcl", LABEL_AGENTIC),
        ),
        SystemBenchmark(
            name="bfclv3-live-parallel-multiple",
            description="BFCL v3 live parallel-multiple. Tests complex patterns with real-world API schemas.",
            labels=new_labels("bfcl", LABEL_AGENTIC),
        ),
        SystemBenchmark(
            name="bfclv3-live-irrelevance",
            description="BFCL v3 live irrelevance. Tests irrelevance detection with real-world API schemas.",
            labels=new_labels("bfcl", LABEL_AGENTIC),
        ),
        SystemBenchmark(
            name="bfclv3-live-relevance",
            description="BFCL v3 live relevance. Tests relevance detection with real-world API schemas.",
            labels=new_labels("bfcl", LABEL_AGENTIC),
        ),
        # === Multi-turn AST (no API keys) ===
        SystemBenchmark(
            name="bfclv3-multi-turn-base",
            description="BFCL v3 multi-turn base. Tests multi-turn conversation with function calling.",
            labels=new_labels("bfcl", LABEL_AGENTIC),
        ),
        SystemBenchmark(
            name="bfclv3-multi-turn-miss-func",
            description="BFCL v3 multi-turn missing function. Tests handling of unavailable functions.",
            labels=new_labels("bfcl", LABEL_AGENTIC),
        ),
        SystemBenchmark(
            name="bfclv3-multi-turn-miss-param",
            description="BFCL v3 multi-turn missing parameter. Tests handling of incomplete information.",
            labels=new_labels("bfcl", LABEL_AGENTIC),
        ),
        SystemBenchmark(
            name="bfclv3-multi-turn-long-context",
            description="BFCL v3 multi-turn long context. Tests function calling with extended context.",
            labels=new_labels("bfcl", LABEL_AGENTIC),
        ),
        # === Executable (require API keys) ===
        SystemBenchmark(
            name="bfclv3-exec-simple",
            description="BFCL v3 executable simple. Executes function calls against real APIs. Requires API keys.",
            labels=new_labels("bfcl", LABEL_AGENTIC),
            required_params=_api_key_params,
        ),
        SystemBenchmark(
            name="bfclv3-exec-parallel",
            description="BFCL v3 executable parallel. Executes parallel function calls against real APIs. Requires API keys.",
            labels=new_labels("bfcl", LABEL_AGENTIC),
            required_params=_api_key_params,
        ),
        SystemBenchmark(
            name="bfclv3-exec-multiple",
            description="BFCL v3 executable multiple. Executes sequential function calls against real APIs. Requires API keys.",
            labels=new_labels("bfcl", LABEL_AGENTIC),
            required_params=_api_key_params,
        ),
        SystemBenchmark(
            name="bfclv3-exec-parallel-multiple",
            description="BFCL v3 executable parallel-multiple. Executes complex call patterns against real APIs. Requires API keys.",
            labels=new_labels("bfcl", LABEL_AGENTIC),
            required_params=_api_key_params,
        ),
        SystemBenchmark(
            name="bfclv3-rest",
            description="BFCL v3 REST API. Tests REST API call generation and execution. Requires API keys.",
            labels=new_labels("bfcl", LABEL_AGENTIC),
            required_params=_api_key_params,
        ),
    ]
