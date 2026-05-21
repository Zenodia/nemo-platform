# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import os
from unittest import mock

import pytest
from nmp.evaluator.app.evalfactory.agentic_eval import (
    AgenticEvalHandler,
    SecretRef,
)
from nmp.evaluator.app.evalfactory.convert import INLINE_DATASET_FILENAME
from nmp.evaluator.app.values import MetricOfflineJob, MetricOnlineJob
from nmp.evaluator.config import EvaluatorSettings


class TestAgenticEvalHandler:
    handler = AgenticEvalHandler()

    def _test_job_dict(self) -> dict:
        return {
            "metric": AgenticEvalHandler._system_metrics[0],
            "dataset": {
                "rows": [{"input": "test"}],
            },
            "metric_params": {
                "judge": {"model": {"name": "my/judge", "url": "http://nim.test/v1/chat/completions"}},
                "trajectory_used_tools": "tool1,tool2",
            },
        }

    def _test_job(self, job: dict | None = None) -> MetricOfflineJob:
        return MetricOfflineJob.model_validate(job or self._test_job_dict())

    @mock.patch.dict(
        os.environ,
        {
            "NMP_EVALUATOR_EVALFACTORY_AGENTIC_EVAL": "my-container",
        },
    )
    def test_docker_image(self):
        assert AgenticEvalHandler.docker_image() == "nvcr.io/nvidia/eval-factory/agentic_eval:26.01", (
            "settings is loaded before env override, expect defaults"
        )
        assert EvaluatorSettings().evalfactory.agentic_eval == "my-container", "failed environment variable override"

    def test_system_metrics(self):
        system_metrics = AgenticEvalHandler.system_metrics()
        assert len(system_metrics) == 1

        for system_metric in system_metrics:
            assert system_metric.labels.get("eval_harness") == "agentic_eval"
            assert system_metric.supported_job_types == ["offline"], "only offline is supported for Agentic Eval"

        # Verify the only metric is trajectory-evaluation
        assert system_metrics[0].name == "trajectory-evaluation"

    def test_metric_job_secrets(self):
        job_dict = self._test_job_dict()
        job = MetricOfflineJob.model_validate(job_dict)
        secrets = self.handler.metric_job_secrets(job)
        assert len(secrets) == 0, "no secrets expected"

        job_dict["metric_params"]["judge"]["model"]["api_key_secret"] = "my-judge-secret"
        job = MetricOfflineJob.model_validate(job_dict)
        secrets = self.handler.metric_job_secrets(job)
        assert len(secrets) == 1, "expected secret for judge API key (NIM format)"
        assert secrets["judge_api_key_secret"] == SecretRef(root="my-judge-secret")

    def test_secrets_openai_format(self):
        """Test that OPENAI_API_KEY is also exported when judge model uses OpenAI format."""
        job_dict = self._test_job_dict()
        job_dict["metric_params"]["judge"]["model"]["api_key_secret"] = "my-judge-secret"
        job_dict["metric_params"]["judge"]["model"]["format"] = "openai"
        job = MetricOfflineJob.model_validate(job_dict)
        secrets = self.handler.metric_job_secrets(job)
        assert len(secrets) == 2, "expected both judge_api_key_secret and OPENAI_API_KEY"
        assert secrets["judge_api_key_secret"] == SecretRef(root="my-judge-secret")
        assert secrets["OPENAI_API_KEY"] == SecretRef(root="my-judge-secret")

    def test_unsupported_job_type(self):
        job = MetricOnlineJob.model_validate(
            {
                "metric": AgenticEvalHandler._system_metrics[0],
                "model": {
                    "url": "http://nim.test",
                    "name": "my/model",
                },
                "dataset": {"rows": [{"input": "test"}]},
                "prompt_template": "{{input}}",
                "metric_params": {},
            }
        )
        with pytest.raises(
            ValueError,
            match="metric does not support online evaluations with a model. Remove the model and specify a dataset.",
        ):
            self.handler.augment_metric_job(job, "output_dir")

    def test_missing_req_param(self):
        job = self._test_job()
        job.metric_params = {}
        with pytest.raises(ValueError, match="missing required parameter"):
            self.handler.augment_metric_job(job, "output_dir")

    def test_invalid_judge(self):
        job = self._test_job(
            {
                "metric": AgenticEvalHandler._system_metrics[0],
                "dataset": {
                    "rows": [{"input": "test"}],
                },
                "metric_params": {
                    "judge": {
                        "model": {
                            "url": "http://nim.test",
                            "name": "my/judge",
                        },
                    },
                    "trajectory_used_tools": "tool1,tool2",
                },
            }
        )
        with pytest.raises(
            ValueError, match="job.metric_params.judge.model.url must end in '/v1/chat/completions' for agentic judge"
        ):
            self.handler.augment_metric_job(job, "output_dir")

    def test_augment_metric_job(self):
        ef_job = self.handler.augment_metric_job(self._test_job(), "output_dir")
        result = ef_job.model_dump(mode="json", exclude_none=True)

        # Check dataset_path ends with expected suffix (actual base path varies in tests)
        dataset_path = result["config"]["params"]["extra"]["dataset_path"]
        assert dataset_path.endswith(f"/jobs/datasets/{INLINE_DATASET_FILENAME}")

        # Check the rest of the structure (trajectory-evaluation requires judge)
        assert result["target"]["api_endpoint"]["url"] == "http://nim.test/v1/chat/completions"
        assert result["target"]["api_endpoint"]["model_id"] == "my/judge"
        assert result["target"]["api_endpoint"]["type"] == "chat"
        assert result["config"]["type"] == "agentic_eval_trajectory_evaluation"
        assert result["config"]["params"]["extra"]["judge"] == {
            "model": {"name": "my/judge", "url": "http://nim.test/v1/chat/completions"}
        }
        assert result["config"]["params"]["extra"]["trajectory_used_tools"] == "tool1,tool2"
        assert result["config"]["params"]["extra"]["judge_model_args"] == {}
        assert result["config"]["params"]["extra"]["judge_model_type"] == "nvidia-nim"

    def test_augment_metric_job_with_api_key_secret(self):
        """Test that api_key_secret is correctly mapped to env var name."""
        job_dict = self._test_job_dict()
        job_dict["metric_params"]["judge"]["model"]["api_key_secret"] = "my-judge-secret"
        job = MetricOfflineJob.model_validate(job_dict)

        ef_job = self.handler.augment_metric_job(job, "output_dir")
        result = ef_job.model_dump(mode="json", exclude_none=True)

        # api_key should be the env var name (Jinja template adds $ prefix)
        assert result["target"]["api_endpoint"]["api_key_name"] == "judge_api_key_secret"
        # dataset_path should be in extra params for offline jobs
        assert result["config"]["params"]["extra"]["dataset_path"].endswith(f"/jobs/datasets/{INLINE_DATASET_FILENAME}")

    def test_augment_metric_job_trajectory_with_custom_tools(self):
        """Test trajectory-evaluation metric with custom tools parameter."""
        trajectory_metric = AgenticEvalHandler._system_metrics[0]
        assert trajectory_metric.name == "trajectory-evaluation"

        job = MetricOfflineJob.model_validate(
            {
                "metric": trajectory_metric,
                "dataset": {
                    "rows": [{"input": "test"}],
                },
                "metric_params": {
                    "trajectory_used_tools": "tool1,tool2,custom_tool",
                    "trajectory_custom_tools": {"custom_tool": "A custom tool for testing"},
                    "judge": {
                        "model": {
                            "name": "my/judge",
                            "url": "http://nim.test/v1/chat/completions",
                        }
                    },
                },
            }
        )

        ef_job = self.handler.augment_metric_job(job, "output_dir")
        result = ef_job.model_dump(mode="json", exclude_none=True)

        # Judge metrics use the judge endpoint
        assert result["target"]["api_endpoint"]["url"] == "http://nim.test/v1/chat/completions"
        assert result["target"]["api_endpoint"]["model_id"] == "my/judge"
        assert result["target"]["api_endpoint"]["type"] == "chat"
        assert result["config"]["type"] == "agentic_eval_trajectory_evaluation"
        # trajectory params should be in extra params
        assert result["config"]["params"]["extra"]["trajectory_used_tools"] == "tool1,tool2,custom_tool"
        assert result["config"]["params"]["extra"]["trajectory_custom_tools"] == {
            "custom_tool": "A custom tool for testing"
        }
        # dataset_path should be in extra params
        assert result["config"]["params"]["extra"]["dataset_path"].endswith(f"/jobs/datasets/{INLINE_DATASET_FILENAME}")
