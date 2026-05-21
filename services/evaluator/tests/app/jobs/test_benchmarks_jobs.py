# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Unit tests for compile_benchmark_job function."""

import shlex
from typing import Any, Protocol, cast, runtime_checkable

import pytest
from nemo_evaluator_sdk.enums import MetricType
from nmp.evaluator.app.evalfactory.safety_harness import SafetyHarnessHandler
from nmp.evaluator.app.evalfactory.system import get_system_benchmark_handler
from nmp.evaluator.app.jobs.benchmarks import compile_benchmark_job
from nmp.evaluator.app.jobs.constants import NEMO_EVAL_HARNESS
from nmp.evaluator.app.jobs.metrics import generate_config_file_from_env_command_str
from nmp.evaluator.app.values import BenchmarkOfflineJob, BenchmarkOnlineJob, SystemBenchmarkOnlineJob
from nmp.evaluator.config import settings


@pytest.fixture
def custom_offline_benchmark_job() -> BenchmarkOfflineJob:
    return BenchmarkOfflineJob.model_validate(
        {
            "benchmark": {
                "name": "bench",
                "dataset": "ws/dataset",
                "metrics": [
                    {
                        "metric_ref": "ws/m1",
                        "metric": {
                            "type": "exact-match",
                            "reference": "{{item.reference}}",
                        },
                    }
                ],
            }
        }
    )


@pytest.mark.asyncio
async def test_compile_system_benchmark_sets_eval_harness_on_results_step():
    benchmark = next(b for b in SafetyHarnessHandler._system_benchmarks if b.name == "aegis-v2")
    job = SystemBenchmarkOnlineJob.model_validate(
        {
            "benchmark": benchmark,
            "model": {"url": "http://nim.test", "name": "my/model"},
            "benchmark_params": {
                "hf_token": "my-hf-secret",
                "judge": {
                    "model": {
                        "name": "my/judge",
                        "url": "http://nim.test/v1/completions",
                        "api_key_secret": "my-judge-secret",
                    }
                },
            },
        }
    )

    result = await compile_benchmark_job(job)
    steps = list(result["steps"])

    assert len(steps) == 2
    assert steps[0]["name"] == "evaluation"
    assert steps[1]["name"] == "results"
    assert _get_step_env_value(steps[1], NEMO_EVAL_HARNESS) == "safety_harness"
    config_file_command_str, config_file_path = generate_config_file_from_env_command_str()
    handler = get_system_benchmark_handler(job.benchmark.name)
    ef_job_config = handler.augment_benchmark_job(job.model_copy(deep=True), settings.jobs.results_dir)
    container_command = handler.container_command(ef_job_config, config_file_path)
    assert _get_container(steps[0]).get("command") == [
        "/bin/sh",
        "-c",
        config_file_command_str + " && exec " + shlex.join(container_command),
    ]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("model_url", "model_name"),
    [
        (
            "https://api.example.com/v1/chat/completions?api-version=2024-10-01&deployment=gpt-4o",
            "Llama 3.1 70B Instruct",
        ),
        (
            "http://nim.test/v1/chat/completions;profile=default",
            "my/model; sleep 1",
        ),
    ],
    ids=[
        "realistic_url_and_name",
        "semicolon_meta_chars",
    ],
)
async def test_compile_system_benchmark_shell_escapes_dynamic_command_args(model_url: str, model_name: str):
    benchmark = next(b for b in SafetyHarnessHandler._system_benchmarks if b.name == "aegis-v2")
    job = SystemBenchmarkOnlineJob.model_validate(
        {
            "benchmark": benchmark,
            "model": {
                "url": model_url,
                "name": model_name,
            },
            "benchmark_params": {
                "hf_token": "my-hf-secret",
                "judge": {
                    "model": {
                        "name": "my/judge",
                        "url": "http://nim.test/v1/completions",
                        "api_key_secret": "my-judge-secret",
                    }
                },
            },
        }
    )

    result = await compile_benchmark_job(job)
    steps = list(result["steps"])
    config_file_command_str, config_file_path = generate_config_file_from_env_command_str()
    handler = get_system_benchmark_handler(job.benchmark.name)
    ef_job_config = handler.augment_benchmark_job(job.model_copy(deep=True), settings.jobs.results_dir)
    container_command = handler.container_command(ef_job_config, config_file_path)
    shell_command = _get_container(steps[0]).get("command", [])[2]

    assert _get_container(steps[0]).get("command") == [
        "/bin/sh",
        "-c",
        config_file_command_str + " && exec " + shlex.join(container_command),
    ]
    assert f"--model_id {model_name}" not in shell_command
    assert f"--model_url {model_url}" not in shell_command


@runtime_checkable
class SupportsModelDump(Protocol):
    def model_dump(self, *, mode: str, exclude_none: bool) -> dict[str, object]: ...


def _get_step_env_value(step: object, name: str) -> str | None:
    step_dict: dict[str, object]
    if not isinstance(step, dict):
        assert isinstance(step, SupportsModelDump)
        step_dict = step.model_dump(mode="json", exclude_none=True)
    else:
        step_dict = {str(key): value for key, value in step.items()}
    envs = step_dict.get("environment")
    if not isinstance(envs, list):
        return None
    for env in envs:
        if not isinstance(env, dict):
            continue
        env_dict = {str(key): value for key, value in env.items()}
        if env_dict.get("name") == name:
            value = env_dict.get("value")
            return value if isinstance(value, str) else None
    return None


def _get_container(step: object) -> dict[str, Any]:
    step_dict = cast(dict[str, Any], step)
    return cast(dict[str, Any], step_dict["executor"]["container"])


@pytest.mark.asyncio
async def test_compile_offline_benchmark_passes_inner_metric_to_new_metric(
    monkeypatch: pytest.MonkeyPatch, custom_offline_benchmark_job: BenchmarkOfflineJob
):
    seen_metric_types: list[MetricType] = []

    class _Metric:
        def secrets(self) -> dict[str, object]:
            return {}

    async def _fake_new_metric(metric_config, *_args, **_kwargs):
        assert hasattr(metric_config, "type"), "Expected inner metric config, got benchmark wrapper"
        seen_metric_types.append(metric_config.type)
        return _Metric()

    monkeypatch.setattr("nmp.evaluator.app.jobs.benchmarks.new_metric", _fake_new_metric)

    await compile_benchmark_job(custom_offline_benchmark_job)
    assert seen_metric_types == [MetricType.EXACT_MATCH]


@pytest.mark.asyncio
async def test_compile_online_benchmark_passes_inner_metric_to_new_metric(monkeypatch: pytest.MonkeyPatch):
    seen_metric_types: list[MetricType] = []

    class _Metric:
        def secrets(self) -> dict[str, object]:
            return {}

    async def _fake_new_metric(metric_config, *_args, **_kwargs):
        assert hasattr(metric_config, "type"), "Expected inner metric config, got benchmark wrapper"
        seen_metric_types.append(metric_config.type)
        return _Metric()

    monkeypatch.setattr("nmp.evaluator.app.jobs.benchmarks.new_metric", _fake_new_metric)

    job = BenchmarkOnlineJob.model_validate(
        {
            "benchmark": {
                "name": "bench",
                "dataset": "ws/dataset",
                "metrics": [
                    {
                        "metric_ref": "ws/m1",
                        "metric": {
                            "type": "exact-match",
                            "reference": "{{item.reference}}",
                        },
                    }
                ],
            },
            "model": {"url": "http://nim.test/v1", "name": "my/model"},
            "prompt_template": "{{item.input}}",
        }
    )

    await compile_benchmark_job(job)
    assert seen_metric_types == [MetricType.EXACT_MATCH]


@pytest.mark.asyncio
async def test_compile_custom_benchmark_uses_python_entrypoint(custom_offline_benchmark_job: BenchmarkOfflineJob):
    """Evaluator-owned custom benchmark step should run task directly, not via /bin/sh."""

    result = await compile_benchmark_job(custom_offline_benchmark_job)
    steps = list(result["steps"])

    assert len(steps) == 2
    assert steps[1]["name"] == "evaluation"
    assert _get_container(steps[1]).get("entrypoint") == [
        "python",
        "-m",
        "nmp.evaluator.tasks.evaluate_benchmark",
    ]
