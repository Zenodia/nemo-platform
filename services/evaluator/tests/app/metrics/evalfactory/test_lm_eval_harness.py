# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import os
from unittest import mock

import pytest
from nemo_evaluator_sdk.values import SecretRef
from nmp.evaluator.app.evalfactory.lm_eval_harness import LMEvalHarnessHandler
from nmp.evaluator.app.values import SystemBenchmarkOfflineJob, SystemBenchmarkOnlineJob
from nmp.evaluator.config import EvaluatorSettings

from .util import default_adapter_config


class TestLMEvalHarnessHandler:
    handler = LMEvalHarnessHandler()

    def _test_job_dict(self) -> dict:
        return {
            "benchmark": LMEvalHarnessHandler._system_benchmarks[1],
            "model": {
                "url": "http://nim.test",
                "name": "my/model",
            },
            "benchmark_params": {"hf_token": "my-hf-secret"},
        }

    def _test_job(self, job: dict | None = None) -> SystemBenchmarkOnlineJob:
        return SystemBenchmarkOnlineJob.model_validate(job or self._test_job_dict())

    @mock.patch.dict(
        os.environ,
        {
            "NMP_EVALUATOR_EVALFACTORY_LM_EVAL_HARNESS": "my-container",
        },
    )
    def test_docker_image(self):
        assert LMEvalHarnessHandler.docker_image() == "nvcr.io/nvidia/eval-factory/lm-evaluation-harness:26.01", (
            "settings is loaded before env override, expect defaults"
        )
        assert EvaluatorSettings().evalfactory.lm_eval_harness == "my-container", "failed environment variable override"

    def test_supported_model_type(self):
        for system_benchmark in LMEvalHarnessHandler._system_benchmarks:
            assert system_benchmark.name in LMEvalHarnessHandler.SUPPORTED_MODEL_TYPE, (
                f"missing mapping for benchmark {system_benchmark.name} to supported model types."
            )

        assert len(LMEvalHarnessHandler._system_benchmarks) == len(LMEvalHarnessHandler.SUPPORTED_MODEL_TYPE), (
            "missing system benchmark definition or benchmark mapping to supported model types"
        )

    def test_system_benchmarks(self):
        system_benchmarks = LMEvalHarnessHandler.system_benchmarks()
        assert len(system_benchmarks) == 20

        for system_benchmark in system_benchmarks:
            assert system_benchmark.labels.get("eval_harness") == "lm_eval_harness"
            assert system_benchmark.supported_job_types == ["online"], "only online is supported for LM Eval Harness"

    def test_secrets(self):
        job = self._test_job()
        secrets = self.handler.benchmark_job_secrets(job)
        assert len(secrets) == 1, "expected required secret"
        assert next(iter(secrets.values())) == SecretRef(root="my-hf-secret")

    def test_missing_req_param(self):
        job = self._test_job()
        del job.benchmark_params["hf_token"]

        with pytest.raises(ValueError, match="missing required parameter hf_token"):
            self.handler.augment_benchmark_job(job, "output_dir")

    def test_unsupported_job_type(self):
        job = SystemBenchmarkOfflineJob.model_validate(
            {
                "benchmark": LMEvalHarnessHandler._system_benchmarks[1],
                "dataset": {
                    "rows": [{"input": "test"}],
                },
                "benchmark_params": {},
            }
        )
        with pytest.raises(
            ValueError,
            match="benchmark does not support offline evaluations and a model is required. Specify a model to evaluate.",
        ):
            self.handler.augment_benchmark_job(job, "output_dir")

    def test_invalid_param_type(self):
        job = self._test_job()
        job.benchmark_params["hf_token"] = True
        with pytest.raises(ValueError, match="unexpected type for parameter hf_token"):
            self.handler.augment_benchmark_job(job, "output_dir")

    def test_unsupported_model_type(self):
        job = self._test_job()
        job.benchmark = LMEvalHarnessHandler._system_benchmarks[0]  # gpqa (completions only)
        job.benchmark_params["tokenizer"] = "meta/llama-3.2-3b-instruct"  # Required for completions benchmarks
        with pytest.raises(
            ValueError,
            match="chat detected from job.model.url but is not supported for job .*, expected \['completions'\]",
        ):
            self.handler.augment_benchmark_job(job, "output_dir")

    def test_augment_benchmark_job(self):
        ef_job = self.handler.augment_benchmark_job(self._test_job(), "output_dir")
        expected = {
            "target": {
                "api_endpoint": {
                    "url": "http://nim.test",
                    "model_id": "my/model",
                    "type": "chat",
                    "adapter_config": default_adapter_config,
                },
            },
            "config": {
                "type": "gpqa_diamond_cot",
                "params": {
                    "extra": {
                        "hf_token": "my-hf-secret",
                        "model_type": "chat",
                    },
                },
            },
            "output_dir": "output_dir",
        }
        assert ef_job.model_dump(mode="json", exclude_none=True) == expected
