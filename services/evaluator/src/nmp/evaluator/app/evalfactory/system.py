# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

from typing import Protocol, runtime_checkable

import nmp.evaluator.app.jobs.evalfactory.models as ef
from nemo_evaluator_sdk.values import SecretRef
from nmp.evaluator.app.evalfactory.agentic_eval import AgenticEvalHandler
from nmp.evaluator.app.evalfactory.bfcl import BFCLHandler
from nmp.evaluator.app.evalfactory.bigcode import BigCodeEvaluationHarnessHandler
from nmp.evaluator.app.evalfactory.lm_eval_harness import LMEvalHarnessHandler
from nmp.evaluator.app.evalfactory.retriever import RetrieverHandler
from nmp.evaluator.app.evalfactory.safety_harness import SafetyHarnessHandler
from nmp.evaluator.app.evalfactory.simple_evals import SimpleEvalsHandler
from nmp.evaluator.app.values import MetricJob, SystemBenchmark, SystemBenchmarkJob, SystemMetric


@runtime_checkable
class SystemMetricsHandler(Protocol):
    """
    Handles system metrics for EvalFactory containers.
    """

    @classmethod
    def container_command(cls, job: ef.EvaluationJob, config_file_path: str) -> list[str]:
        """The container command to run the evaluation with EvalFactory."""
        ...

    @classmethod
    def docker_image(cls) -> str:
        """The Docker image to use to run the EvalFactory container."""
        ...

    @classmethod
    def system_metrics(cls) -> list[SystemMetric]:
        """List of system metrics available to run evaluation jobs."""
        ...

    def augment_metric_job(self, job: MetricJob, output_dir: str) -> ef.EvaluationJob:
        """Converts Evaluator MS metrics job to EvalFactory job"""
        ...

    def metric_job_secrets(self, job: MetricJob) -> dict[str, SecretRef]:
        """Job secrets for the metric. Returns a dictionary of environment variables to the secret reference"""
        ...


@runtime_checkable
class SystemBenchmarkHandler(Protocol):
    """
    Handles system metrics for EvalFactory containers.
    """

    @classmethod
    def container_command(cls, job: ef.EvaluationJob, config_file_path: str) -> list[str]:
        """The container command to run the evaluation with EvalFactory."""
        ...

    @classmethod
    def docker_image(cls) -> str:
        """The Docker image to use to run the EvalFactory container."""
        ...

    @classmethod
    def system_benchmarks(cls) -> list[SystemBenchmark]:
        """List of system benchmarks available to run evaluation jobs."""
        ...

    def augment_benchmark_job(self, job: SystemBenchmarkJob, output_dir: str) -> ef.EvaluationJob:
        """Converts Evaluator MS benchmark job to EvalFactory job"""
        ...

    def benchmark_job_secrets(self, job: SystemBenchmarkJob) -> dict[str, SecretRef]:
        """Job secrets for the metric. Returns a dictionary of environment variables to the secret reference"""
        ...


_METRIC_HANDLERS: list[SystemMetricsHandler] = [
    AgenticEvalHandler(),
    RetrieverHandler(),
]

_METRIC_HANDLERS_BY_SYSTEM_METRIC_NAME: dict[str, SystemMetricsHandler] = {}
_SYSTEM_METRICS_BY_NAME: dict[str, SystemMetric] = {}
system_metrics_count = 0
for handler in _METRIC_HANDLERS:
    isinstance(handler, SystemMetricsHandler)
    system_metrics = handler.system_metrics()
    system_metrics_count += len(system_metrics)
    for metric in system_metrics:
        _METRIC_HANDLERS_BY_SYSTEM_METRIC_NAME[metric.name] = handler
        _SYSTEM_METRICS_BY_NAME[metric.name] = metric

assert len(_SYSTEM_METRICS_BY_NAME) == system_metrics_count, "duplicate system metric name"


def get_system_metric(name: str) -> SystemMetric:
    metric = _SYSTEM_METRICS_BY_NAME.get(name)
    if not metric:
        raise ValueError(
            f"Unknown system metric '{name}'. Supported system metrics: {list(_SYSTEM_METRICS_BY_NAME.keys())}"
        )
    return metric


def get_system_metric_handler(name: str) -> SystemMetricsHandler:
    handler = _METRIC_HANDLERS_BY_SYSTEM_METRIC_NAME.get(name)

    if not handler:
        raise ValueError(
            f"Unknown system metric '{name}'. Supported system metrics: {list(_SYSTEM_METRICS_BY_NAME.keys())}"
        )

    return handler


def get_all_system_metrics() -> list[SystemMetric]:
    return list(_SYSTEM_METRICS_BY_NAME.values())


_BENCHMARK_HANDLERS: list[SystemBenchmarkHandler] = [
    BFCLHandler(),
    BigCodeEvaluationHarnessHandler(),
    LMEvalHarnessHandler(),
    SafetyHarnessHandler(),
    SimpleEvalsHandler(),
]
_BENCHMARK_HANDLERS_BY_SYSTEM_BENCHMARK_NAME: dict[str, SystemBenchmarkHandler] = {}
_SYSTEM_BENCHMARKS_BY_NAME: dict[str, SystemBenchmark] = {}
system_benchmarks_count = 0
for handler in _BENCHMARK_HANDLERS:
    isinstance(handler, SystemBenchmarkHandler)
    system_benchmarks = handler.system_benchmarks()
    system_benchmarks_count += len(system_benchmarks)
    for benchmark in system_benchmarks:
        _BENCHMARK_HANDLERS_BY_SYSTEM_BENCHMARK_NAME[benchmark.name] = handler
        _SYSTEM_BENCHMARKS_BY_NAME[benchmark.name] = benchmark

assert len(_SYSTEM_BENCHMARKS_BY_NAME) == system_benchmarks_count, "duplicate system benchmark name"


def get_system_benchmark_handler(name: str) -> SystemBenchmarkHandler:
    handler = _BENCHMARK_HANDLERS_BY_SYSTEM_BENCHMARK_NAME.get(name)

    if not handler:
        raise ValueError(
            f"Unknown system benchmark '{name}'. Supported system benchmarks: {list(_SYSTEM_BENCHMARKS_BY_NAME.keys())}"
        )

    return handler


def get_all_system_benchmarks() -> list[SystemBenchmark]:
    return list(_SYSTEM_BENCHMARKS_BY_NAME.values())
