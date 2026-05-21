# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import os
from unittest import mock

import pytest
from nemo_evaluator_sdk.values import SecretRef
from nmp.evaluator.app.evalfactory.bfcl import BFCLHandler
from nmp.evaluator.app.values import SystemBenchmarkOfflineJob, SystemBenchmarkOnlineJob
from nmp.evaluator.config import EvaluatorSettings


class TestBFCLHandler:
    handler = BFCLHandler()

    def _test_job_ast(self) -> SystemBenchmarkOnlineJob:
        """Job for AST benchmark (no secrets)."""
        benchmark = next(m for m in BFCLHandler._system_benchmarks if m.name == "bfclv3-simple")
        return SystemBenchmarkOnlineJob.model_validate(
            {
                "benchmark": benchmark,
                "model": {"url": "http://nim.test", "name": "my/model"},
                "benchmark_params": {},
            }
        )

    def _test_job_exec(self) -> SystemBenchmarkOnlineJob:
        """Job for exec benchmark (with secrets)."""
        benchmark = next(m for m in BFCLHandler._system_benchmarks if m.name == "bfclv3-exec-simple")
        return SystemBenchmarkOnlineJob.model_validate(
            {
                "benchmark": benchmark,
                "model": {"url": "http://nim.test", "name": "my/model"},
                "benchmark_params": {
                    "rapid_api_key": "my-rapid-secret",
                    "exchangerate_api_key": "my-exchangerate-secret",
                    "omdb_api_key": "my-omdb-secret",
                    "geocode_api_key": "my-geocode-secret",
                },
            }
        )

    @mock.patch.dict(
        os.environ,
        {
            "NMP_EVALUATOR_EVALFACTORY_BFCL": "my-container",
        },
    )
    def test_docker_image(self):
        assert BFCLHandler.docker_image() == "nvcr.io/nvidia/eval-factory/bfcl:26.01", (
            "settings is loaded before env override, expect defaults"
        )
        assert EvaluatorSettings().evalfactory.bfcl == "my-container", "failed environment variable override"

    def test_system_benchmarks_count(self):
        # 22 individual task benchmarks (17 AST + 5 exec)
        assert len(BFCLHandler.system_benchmarks()) == 22

    def test_all_benchmarks_are_online_only(self):
        for benchmark in BFCLHandler.system_benchmarks():
            assert benchmark.labels.get("eval_harness") == "bfcl"
            assert benchmark.supported_job_types == ["online"]

    def test_ast_benchmarks_no_required_params(self):
        ast_benchmarks = [
            m
            for m in BFCLHandler._system_benchmarks
            if not m.name.startswith("bfclv3-exec") and m.name != "bfclv3-rest"
        ]
        for benchmark in ast_benchmarks:
            assert len(benchmark.required_params) == 0, f"{benchmark.name} should not require API keys"

    def test_exec_benchmarks_require_api_keys(self):
        exec_benchmarks = [
            m for m in BFCLHandler._system_benchmarks if m.name.startswith("bfclv3-exec") or m.name == "bfclv3-rest"
        ]
        assert len(exec_benchmarks) == 5
        for benchmark in exec_benchmarks:
            assert len(benchmark.required_params) == 4, f"{benchmark.name} should require 4 API keys"

    def test_secrets_ast_benchmark(self):
        secrets = self.handler.benchmark_job_secrets(self._test_job_ast())
        assert len(secrets) == 0

    def test_secrets_exec_benchmark(self):
        secrets = self.handler.benchmark_job_secrets(self._test_job_exec())
        assert secrets == {
            "RAPID_API_KEY": SecretRef(root="my-rapid-secret"),
            "EXCHANGERATE_API_KEY": SecretRef(root="my-exchangerate-secret"),
            "OMDB_API_KEY": SecretRef(root="my-omdb-secret"),
            "GEOCODE_API_KEY": SecretRef(root="my-geocode-secret"),
        }

    def test_unsupported_offline_job(self):
        benchmark = next(m for m in BFCLHandler._system_benchmarks if m.name == "bfclv3-simple")
        job = SystemBenchmarkOfflineJob.model_validate(
            {
                "benchmark": benchmark,
                "dataset": {"rows": [{"input": "test"}]},
                "benchmark_params": {},
            }
        )
        with pytest.raises(ValueError, match="benchmark does not support offline evaluations"):
            self.handler.augment_benchmark_job(job, "output_dir")

    def test_augment_benchmark_job_ast_benchmark(self):
        ef_job = self.handler.augment_benchmark_job(self._test_job_ast(), "output_dir")

        assert ef_job.config is not None
        assert ef_job.config.params is not None
        assert ef_job.config.type == "bfclv3"
        assert ef_job.config.params.task == "simple"

    def test_augment_benchmark_job_exec_benchmark(self):
        ef_job = self.handler.augment_benchmark_job(self._test_job_exec(), "output_dir")

        assert ef_job.config is not None
        assert ef_job.config.params is not None
        assert ef_job.config.type == "bfclv3"
        assert ef_job.config.params.task == "exec_simple"

    def test_task_derived_from_benchmark_name(self):
        """Task category is derived from benchmark name by removing prefix and converting dashes."""
        for benchmark in BFCLHandler._system_benchmarks:
            expected_task = benchmark.name.removeprefix("bfclv3-").replace("-", "_")
            assert expected_task, f"Could not derive task from {benchmark.name}"
