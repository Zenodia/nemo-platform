# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import os
from unittest import mock

import nmp.evaluator.entities as entities
import pytest
from nemo_evaluator_sdk.values import SecretRef
from nmp.evaluator.app.evalfactory.simple_evals import (
    SimpleEvalsHandler,
)
from nmp.evaluator.app.values import SystemBenchmarkOfflineJob, SystemBenchmarkOnlineJob
from nmp.evaluator.config import EvaluatorSettings

from .util import default_adapter_config


class TestSimpleEvalsHandler:
    handler = SimpleEvalsHandler()

    def _test_job_dict(self, benchmark: entities.SystemBenchmark | None = None) -> dict:
        return {
            "benchmark": benchmark or SimpleEvalsHandler._system_benchmarks[0],
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

    def _test_job(
        self, job: dict | None = None, benchmark: entities.SystemBenchmark | None = None
    ) -> SystemBenchmarkOnlineJob:
        return SystemBenchmarkOnlineJob.model_validate(job or self._test_job_dict(benchmark))

    @mock.patch.dict(
        os.environ,
        {
            "NMP_EVALUATOR_EVALFACTORY_SIMPLE_EVALS": "my-container",
        },
    )
    def test_docker_image(self):
        assert SimpleEvalsHandler.docker_image() == "nvcr.io/nvidia/eval-factory/simple-evals:26.01", (
            "settings is loaded before env override, expect defaults"
        )
        assert EvaluatorSettings().evalfactory.simple_evals == "my-container", "failed environment variable override"

    def test_supported_model_type(self):
        for system_benchmark in SimpleEvalsHandler._system_benchmarks:
            assert system_benchmark.name in SimpleEvalsHandler.SUPPORTED_MODEL_TYPE, (
                f"missing mapping for benchmark {system_benchmark.name} to supported model types."
            )

        assert len(SimpleEvalsHandler._system_benchmarks) == len(SimpleEvalsHandler.SUPPORTED_MODEL_TYPE), (
            "missing system benchmark definition or benchmark mapping to supported model types"
        )

    def test_system_benchmarks(self):
        system_benchmarks = SimpleEvalsHandler.system_benchmarks()
        assert len(system_benchmarks) == 54

        for system_benchmark in system_benchmarks:
            assert system_benchmark.labels.get("eval_harness") == "simple_evals"
            assert system_benchmark.supported_job_types == ["online"], "only online is supported for LM Eval Harness"

    def test_secrets(self):
        job = self._test_job()
        secrets = self.handler.benchmark_job_secrets(job)
        assert len(secrets) == 2, "expected optional secret and judge"
        assert next(iter(secrets.values())) == SecretRef(root="my-hf-secret")

        del job.benchmark_params["hf_token"]
        del job.benchmark_params["judge"]["model"]["api_key_secret"]
        secrets = self.handler.benchmark_job_secrets(job)
        assert len(secrets) == 0, "no secrets expected"

    def test_missing_req_param(self):
        job = self._test_job()
        del job.benchmark_params["judge"]

        with pytest.raises(ValueError, match="missing required parameter judge"):
            self.handler.augment_benchmark_job(job, "output_dir")

    def test_unsupported_job_type(self):
        job = SystemBenchmarkOfflineJob.model_validate(
            {
                "benchmark": SimpleEvalsHandler._system_benchmarks[1],
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
        job.model.url = "http://nim.test/v1/completions"
        with pytest.raises(
            ValueError,
            match="completions detected from job.model.url but is not supported for job .*, expected \['chat'\]",
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
                }
            },
            "config": {
                "type": "AA_AIME_2024",
                "params": {
                    "extra": {
                        "hf_token": "my-hf-secret",
                        "judge": {
                            # api_key is the env var name (Jinja template adds $ prefix)
                            "api_key": "judge_api_key_secret",
                            "api_key_name": "judge_api_key_secret",
                            "model_id": "my/judge",
                            "url": "http://nim.test/v1/completions",
                            "backend": "generic",
                        },
                        "model_type": "chat",
                    },
                },
            },
            "output_dir": "output_dir",
        }
        assert ef_job.model_dump(mode="json", exclude_none=True) == expected
