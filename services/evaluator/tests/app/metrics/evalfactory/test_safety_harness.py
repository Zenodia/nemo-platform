# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import os
from unittest import mock

import pytest
from nemo_evaluator_sdk.values import SecretRef
from nmp.evaluator.app.evalfactory.safety_harness import (
    SafetyHarnessHandler,
)
from nmp.evaluator.app.values import SystemBenchmarkOfflineJob, SystemBenchmarkOnlineJob
from nmp.evaluator.config import EvaluatorSettings

from .util import default_adapter_config


class TestSafetyHarnessHandler:
    handler = SafetyHarnessHandler()

    def _test_job_dict(self) -> dict:
        return {
            "benchmark": SafetyHarnessHandler._system_benchmarks[0],
            "model": {
                "url": "http://nim.test",
                "name": "my/model",
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

    def _test_job(self, job: dict | None = None) -> SystemBenchmarkOnlineJob:
        return SystemBenchmarkOnlineJob.model_validate(job or self._test_job_dict())

    @mock.patch.dict(
        os.environ,
        {
            "NMP_EVALUATOR_EVALFACTORY_SAFETY_HARNESS": "my-container",
        },
    )
    def test_docker_image(self):
        assert SafetyHarnessHandler.docker_image() == "nvcr.io/nvidia/eval-factory/safety-harness:26.01", (
            "settings is loaded before env override, expect defaults"
        )
        assert EvaluatorSettings().evalfactory.safety_harness == "my-container", "failed environment variable override"

    def test_system_benchmarks(self):
        system_benchmarks = SafetyHarnessHandler.system_benchmarks()
        assert len(system_benchmarks) == 2

        for system_benchmark in system_benchmarks:
            assert system_benchmark.labels.get("eval_harness") == "safety_harness"
            assert system_benchmark.supported_job_types == ["online"], "only online is supported for LM Eval Harness"
            assert len(system_benchmark.required_params) == 2
            for param in system_benchmark.required_params:
                if param.name == "judge":
                    assert param.schema_ is not None, "expected schema for judge parameter"
                    assert '"schema":' in param.model_dump_json(by_alias=True), (
                        "expected schema to serialize for judge parameter"
                    )

    def test_secrets(self):
        job = self._test_job()
        secrets = self.handler.benchmark_job_secrets(job)
        assert len(secrets) == 2, "expected required secret and judge"
        assert next(iter(secrets.values())) == SecretRef(root="my-hf-secret")

    def test_missing_req_param(self):
        job = self._test_job()
        del job.benchmark_params["hf_token"]

        with pytest.raises(ValueError, match="missing required parameter hf_token"):
            self.handler.augment_benchmark_job(job, "output_dir")

    def test_unsupported_job_type(self):
        job = SystemBenchmarkOfflineJob.model_validate(
            {
                "benchmark": SafetyHarnessHandler._system_benchmarks[1],
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

    def test_unsupported_judge_url(self):
        job = self._test_job()
        job.benchmark_params["judge"]["model"]["url"] = "http://nim.test/v1/chat/completions"
        with pytest.raises(
            ValueError,
            match="job.benchmark_params.judge.model.url must end in '/v1/completions' for safety judge",
        ):
            self.handler.augment_benchmark_job(job, "output_dir")

    def test_augment_job(self):
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
                "type": "aegis_v2",
                "params": {
                    "extra": {
                        "hf_token": "my-hf-secret",
                        "judge": {
                            # api_key is the env var name (Jinja template adds $ prefix)
                            "api_key": "judge_api_key_secret",
                            "api_key_name": "judge_api_key_secret",
                            "model_id": "my/judge",
                            "url": "http://nim.test/v1/completions",
                        },
                    },
                },
            },
            "output_dir": "output_dir",
        }
        assert ef_job.model_dump(mode="json", exclude_none=True) == expected
