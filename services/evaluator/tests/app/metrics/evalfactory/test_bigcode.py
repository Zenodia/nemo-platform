# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import os
from unittest import mock

import pytest
from nemo_evaluator_sdk.values import SecretRef
from nmp.evaluator.app.evalfactory.bigcode import BigCodeEvaluationHarnessHandler
from nmp.evaluator.app.values import SystemBenchmarkOfflineJob, SystemBenchmarkOnlineJob
from nmp.evaluator.config import EvaluatorSettings

from .util import default_adapter_config


class TestBigCodeEvaluationHarnessHandler:
    handler = BigCodeEvaluationHarnessHandler()

    def _test_job_dict(self) -> dict:
        return {
            "benchmark": BigCodeEvaluationHarnessHandler._system_benchmarks[1],
            "model": {
                "url": "http://nim.test",
                "name": "my/model",
            },
            "benchmark_params": {},
        }

    def _test_job_dict_secrets(self) -> dict:
        job = self._test_job_dict()
        job["benchmark_params"]["hf_token"] = "my-hf-secret"
        return job

    def _test_job(self, job: dict | None = None) -> SystemBenchmarkOnlineJob:
        return SystemBenchmarkOnlineJob.model_validate(job or self._test_job_dict_secrets())

    @mock.patch.dict(
        os.environ,
        {
            "NMP_EVALUATOR_EVALFACTORY_BIGCODE_EVALUATION_HARNESS": "my-container",
        },
    )
    def test_docker_image(self):
        assert (
            BigCodeEvaluationHarnessHandler.docker_image()
            == "nvcr.io/nvidia/eval-factory/bigcode-evaluation-harness:26.01"
        ), "settings is loaded before env override, expect defaults"
        assert EvaluatorSettings().evalfactory.bigcode_evaluation_harness == "my-container", (
            "failed environment variable override"
        )

    def test_supported_model_type(self):
        for system_benchmark in BigCodeEvaluationHarnessHandler._system_benchmarks:
            assert system_benchmark.name in BigCodeEvaluationHarnessHandler.SUPPORTED_MODEL_TYPE, (
                f"missing mapping for benchmark {system_benchmark.name} to supported model types."
            )

        assert len(BigCodeEvaluationHarnessHandler._system_benchmarks) == len(
            BigCodeEvaluationHarnessHandler.SUPPORTED_MODEL_TYPE
        ), "missing system benchmark definition or benchmark mapping to supported model types"

    def test_system_benchmarks(self):
        system_benchmarks = BigCodeEvaluationHarnessHandler.system_benchmarks()
        assert len(system_benchmarks) == 27

        for system_benchmark in system_benchmarks:
            assert system_benchmark.labels.get("eval_harness") == "bigcode_eval_harness"
            assert system_benchmark.supported_job_types == ["online"], (
                "only online is supported for BigCode Eval Harness"
            )

    def test_secrets(self):
        job = self._test_job(self._test_job_dict())
        secrets = self.handler.benchmark_job_secrets(job)
        assert len(secrets) == 0, "no secrets expected"

        job = self._test_job(self._test_job_dict_secrets())
        secrets = self.handler.benchmark_job_secrets(job)
        assert len(secrets) == 1, "expected optional secrets"
        assert next(iter(secrets.values())) == SecretRef(root="my-hf-secret")

    def test_unsupported_job_type(self):
        job = SystemBenchmarkOfflineJob.model_validate(
            {
                "benchmark": BigCodeEvaluationHarnessHandler._system_benchmarks[1],
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
        job = self._test_job(
            {
                "benchmark": BigCodeEvaluationHarnessHandler._system_benchmarks[0],
                "model": {
                    "url": "http://nim.test",
                    "name": "my/model",
                },
                "benchmark_params": {},
            }
        )
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
                "type": "humaneval_instruct",
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
