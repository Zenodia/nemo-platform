# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import nmp.evaluator.app.jobs.evalfactory.models as ef
from nemo_evaluator_sdk.values import SecretRef
from nmp.evaluator.app.evalfactory.convert import augment_online_job
from nmp.evaluator.app.evalfactory.handler import (
    BaseSystemHandler,
    JudgeModelParamsInput,
    hf_token_param,
)
from nmp.evaluator.app.evalfactory.labels import LABEL_CONTENT_SAFETY, new_labels
from nmp.evaluator.app.values import (
    Parameter,
    SystemBenchmark,
    SystemBenchmarkJob,
    SystemBenchmarkOnlineJob,
)
from nmp.evaluator.config import settings
from pydantic import BaseModel, Field, model_validator
from typing_extensions import Self


class _BaseSafetyHarnessJudgeModelParams(BaseModel):
    parallelism: int | None = Field(default=None, description="")
    request_timeout: int | None = Field(default=None, description="")
    max_retries: int | None = Field(default=None, description="")


class SafetyHarnessJudgeModelParamsInput(JudgeModelParamsInput):
    # Safety harness specific judge params
    parallelism: int | None = Field(default=None, description="Concurrency for judge model requests.")

    @model_validator(mode="after")
    def completions_endpoint(self) -> Self:
        if "/v1/completions" not in self.model.url:
            raise ValueError(
                f"job.benchmark_params.judge.model.url must end in '/v1/completions' for safety judge: {self.model.model_dump_json(exclude_none=True)}"
            )
        return self


class SafetyHarnessJudgeModelParams(_BaseSafetyHarnessJudgeModelParams):
    url: str
    model_id: str
    api_key: str | None
    api_key_name: str | None


safety_harness_judge_param = Parameter(
    name="judge",
    type="object",
    description="The LLM safety judge for the evaluation.",
    schema_=SafetyHarnessJudgeModelParamsInput.model_json_schema(),
)


class SafetyHarnessHandler(BaseSystemHandler):
    @classmethod
    def docker_image(cls) -> str:
        return settings.evalfactory.safety_harness

    @classmethod
    def system_benchmarks(cls) -> list[SystemBenchmark]:
        return cls._system_benchmarks

    def benchmark_job_secrets(self, job: SystemBenchmarkJob) -> dict[str, SecretRef]:
        """Job secrets for the metric. Returns a dictionary of environment variables to the secret reference"""
        # Special handling for Safety Harness where judge.model.api_key_secret can't be easily represented
        # by MetricParameter
        secrets = super().benchmark_job_secrets(job)
        judge_raw_param = job.benchmark_params.get("judge")
        if judge_raw_param:
            judge = SafetyHarnessJudgeModelParamsInput.model_validate(judge_raw_param)
            if judge.model.api_key_secret:
                secrets["judge_api_key_secret"] = judge.model.api_key_secret
        return secrets

    def augment_benchmark_job(self, job: SystemBenchmarkJob, output_dir: str) -> ef.EvaluationJob:
        self.validate_supported_benchmark_job_types(job)
        self.validate_params(job.benchmark_params, job.benchmark.required_params, job.benchmark.optional_params)
        assert isinstance(job, SystemBenchmarkOnlineJob)

        # Validate judge model
        judge_raw_param = job.benchmark_params.get("judge")
        if not judge_raw_param:
            raise ValueError(
                f"job.benchmark_params.judge.model is required for evaluation with metric {job.benchmark.name}"
            )
        judge = SafetyHarnessJudgeModelParamsInput.model_validate(judge_raw_param)
        augmented_judge = SafetyHarnessJudgeModelParams(
            **judge.model_dump(exclude_none=True, exclude={"model"}),
            url=judge.model.url,
            model_id=judge.model.name,
            # Use the env var name (must match key in secrets() method) - the Jinja template adds the $ prefix
            api_key="judge_api_key_secret" if judge.model.api_key_secret else None,
            api_key_name="judge_api_key_secret" if judge.model.api_key_secret else None,
        )
        job.benchmark_params["judge"] = augmented_judge.model_dump(exclude_none=True)

        ef_job = augment_online_job(job, output_dir)

        # Safety Harness config type uses underscores instead of hyphens
        # Note: We set this on the EF job config, not on the original metric to avoid mutating shared state
        if ef_job.config:
            ef_job.config.type = job.benchmark.name.replace("-", "_")

        return ef_job

    _system_benchmarks = [
        SystemBenchmark(
            name="aegis-v2",
            description="Nemotron Content Safety V2: Evaluates model safety risks based on 12 top-level hazard categories.",
            labels=new_labels("safety_harness", LABEL_CONTENT_SAFETY),
            required_params=[hf_token_param, safety_harness_judge_param],
        ),
        SystemBenchmark(
            name="wildguard",
            description="WildGuard (allenai/wildguard): Evaluates model safety risks based on the following top-level categories: privacy, misinformation, harmful language, and malicious uses.",
            labels=new_labels("safety_harness", LABEL_CONTENT_SAFETY),
            required_params=[hf_token_param, safety_harness_judge_param],
        ),
    ]
