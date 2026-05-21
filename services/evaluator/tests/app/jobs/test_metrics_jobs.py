# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Unit tests for compile_metric_job function."""

import shlex
from typing import Any, Protocol, cast, runtime_checkable

import pytest
from nmp.common.files.storage_config import HuggingfaceStorageConfig
from nmp.evaluator.app.evalfactory.agentic_eval import AgenticEvalHandler
from nmp.evaluator.app.evalfactory.retriever import RetrieverHandler
from nmp.evaluator.app.evalfactory.system import get_system_metric_handler
from nmp.evaluator.app.jobs.constants import NEMO_EVAL_HARNESS
from nmp.evaluator.app.jobs.metrics import compile_metric_job, generate_config_file_from_env_command_str
from nmp.evaluator.app.values import Fileset, MetricOfflineJob, MetricOnlineJob, MetricRetrieverJob
from nmp.evaluator.config import settings


def _hf_storage_config() -> HuggingfaceStorageConfig:
    """Create a Hugging Face storage config for inline Fileset tests."""
    return HuggingfaceStorageConfig(repo_id="test-org/test-dataset", repo_type="dataset")


class TestCompileMetricJob:
    """Tests for compile_metric_job function."""

    @pytest.mark.asyncio
    async def test_compile_retriever_job(self):
        """Test compile_metric_job for a Retriever job produces evaluation and results steps."""
        metric = next(m for m in RetrieverHandler._system_metrics if m.name == "retriever-map")
        job = MetricRetrieverJob.model_validate(
            {
                "metric": metric,
                "retriever_pipeline": {
                    "embeddings_model": {"url": "http://embedding.test", "name": "my/embedding-model"},
                },
                "dataset": {"path": "test", "storage": {"type": "huggingface", "repo_id": "test/test"}},
                "metric_params": {},
            }
        )

        result = await compile_metric_job(job)
        steps = list(result["steps"])

        # Retriever jobs should have: dataset-download, evaluation, results
        assert len(steps) == 3
        assert steps[0]["name"] == "dataset-download"
        assert steps[1]["name"] == "evaluation"
        assert steps[2]["name"] == "results"
        assert _get_step_env_value(steps[2], NEMO_EVAL_HARNESS) == "retriever"
        config_file_command_str, config_file_path = generate_config_file_from_env_command_str()
        handler = get_system_metric_handler(metric.name)
        ef_job_config = handler.augment_metric_job(job, settings.jobs.results_dir)
        container_command = handler.container_command(ef_job_config, config_file_path)
        assert _get_container(steps[1]).get("command") == [
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
                "http://judge.test/v1/chat/completions;profile=default",
                "judge; sleep 1",
            ),
        ],
        ids=[
            "realistic_url_and_name",
            "semicolon_meta_chars",
        ],
    )
    async def test_compile_system_metric_shell_escapes_dynamic_command_args(self, model_url: str, model_name: str):
        """System metric EvalFactory command should quote dynamic arguments for /bin/sh -c."""
        metric = next(m for m in AgenticEvalHandler._system_metrics if m.name == "trajectory-evaluation")
        job = MetricOfflineJob.model_validate(
            {
                "metric": metric,
                "dataset": {"path": "test", "storage": {"type": "huggingface", "repo_id": "test/test"}},
                "metric_params": {
                    "judge": {
                        "model": {
                            "url": model_url,
                            "name": model_name,
                        },
                    },
                    "trajectory_used_tools": "tool1,tool2",
                },
            }
        )

        result = await compile_metric_job(job)
        steps = list(result["steps"])
        config_file_command_str, config_file_path = generate_config_file_from_env_command_str()
        handler = get_system_metric_handler(metric.name)
        ef_job_config = handler.augment_metric_job(job, settings.jobs.results_dir)
        container_command = handler.container_command(ef_job_config, config_file_path)
        shell_command = _get_container(steps[1]).get("command", [])[2]

        assert _get_container(steps[1]).get("command") == [
            "/bin/sh",
            "-c",
            config_file_command_str + " && exec " + shlex.join(container_command),
        ]
        assert f"--model_id {model_name}" not in shell_command
        assert f"--model_url {model_url}" not in shell_command

    @pytest.mark.asyncio
    async def test_compile_agentic_job_inline_model(self):
        """Test that inline models (not URNs) don't trigger resolution."""
        metric = next(m for m in AgenticEvalHandler._system_metrics if m.name == "trajectory-evaluation")

        # Job with an already-inline model (not a URN string)
        job = MetricOfflineJob.model_validate(
            {
                "metric": metric,
                "dataset": {"path": "test", "storage": {"type": "huggingface", "repo_id": "test/test"}},
                "metric_params": {
                    "judge": {
                        "model": {"url": "http://judge.test/v1/chat/completions", "name": "my/judge"},
                    },
                    "trajectory_used_tools": "tool1,tool2",
                },
            }
        )

        result = await compile_metric_job(job)
        steps = list(result["steps"])

        # Agentic jobs should have: dataset-download, evaluation, results
        assert len(steps) == 3
        assert steps[0]["name"] == "dataset-download"
        assert steps[1]["name"] == "evaluation"
        assert steps[2]["name"] == "results"
        assert _get_step_env_value(steps[2], NEMO_EVAL_HARNESS) == "agentic_eval"

    @pytest.mark.asyncio
    async def test_compile_custom_metric_uses_python_entrypoint(self):
        """Evaluator-owned custom metric step should run task directly, not via /bin/sh."""
        job = MetricOnlineJob.model_validate(
            {
                "model": {"url": "http://nim.test/v1/chat/completions", "name": "my/model"},
                "dataset": {"rows": [{"input": "hello", "expected": "hello"}]},
                "prompt_template": {"messages": [{"role": "user", "content": "{{input}}"}]},
                "metric": {"type": "exact-match", "reference": "{{item.expected}}"},
            }
        )

        result = await compile_metric_job(job)
        steps = list(result["steps"])

        assert len(steps) == 1
        assert steps[0]["name"] == "evaluation"
        assert _get_container(steps[0]).get("entrypoint") == [
            "python",
            "-m",
            "nmp.evaluator.tasks.evaluate_metric",
        ]

    @pytest.mark.asyncio
    async def test_compile_custom_metric_inline_fileset_adds_download_step(self):
        """Custom metric jobs should download inline Fileset datasets before evaluation."""
        job = MetricOfflineJob.model_validate(
            {
                "metric": {
                    "type": "exact-match",
                    "reference": "{{item.expected}}",
                    "candidate": "{{item.output}}",
                },
                "dataset": Fileset(storage=_hf_storage_config(), path="data/validation.jsonl"),
            }
        )

        result = await compile_metric_job(job)
        steps = list(result["steps"])

        assert [step["name"] for step in steps] == ["dataset-download", "evaluation"]
        assert _get_container(steps[1]).get("entrypoint") == [
            "python",
            "-m",
            "nmp.evaluator.tasks.evaluate_metric",
        ]


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
