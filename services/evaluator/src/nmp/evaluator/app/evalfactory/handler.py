# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import itertools
from typing import Any

import jsonschema
import nmp.evaluator.app.jobs.evalfactory.models as ef
from nemo_evaluator_sdk.values import (
    Model,
    ReasoningParams,
    SecretRef,
    SupportedJobTypes,
)
from nmp.common.inference import InferenceParams
from nmp.evaluator.app.jobs.evalfactory.constants import EvalFactoryModelType
from nmp.evaluator.app.values import (
    MetricJob,
    MetricOfflineJob,
    MetricOnlineJob,
    MetricRetrieverJob,
    Parameter,
    SystemBenchmarkJob,
    SystemBenchmarkOfflineJob,
    SystemBenchmarkOnlineJob,
    SystemMetric,
)
from pydantic import BaseModel, Field

hf_token_param = Parameter(
    name="hf_token",
    type="secret",
    description="Hugging Face token for accessing datasets and tokenizers. Required for tasks that fetch from Hugging Face.",
)

harness_model_type_param = Parameter(
    name="model_type",
    type="string",
    description=f"Specify the model type for evaluation: [{EvalFactoryModelType.CHAT.value}, {EvalFactoryModelType.COMPLETIONS.value}] (default detected from job.model.url or {EvalFactoryModelType.CHAT.value}).",
)


class JudgeModelParamsInput(BaseModel):
    """Base input for judge model parameters.

    Note: ModelRef values (URN strings) are resolved to Model before this
    validation runs via resolve_param_models in the job compilation flow.
    """

    model: Model = Field(description="The LLM judge model configuration.")
    request_timeout: int | None = Field(
        default=None, description="Request timeout (seconds) for inference requests to the judge model."
    )
    max_retries: int | None = Field(
        default=None, description="Maximum number of retries for failed inference requests to the judge model."
    )
    inference: InferenceParams | None = Field(default=None, description="Parameters for judge model inference.")
    system_prompt: str | None = Field(
        default=None,
        description="Initial instructions that define the model's role and behavior for the conversation.",
    )
    reasoning: ReasoningParams | None = Field(
        default=None, description="Custom settings that control the judge model's reasoning behavior."
    )


class BaseSystemHandler:
    def image_env_var_name(self) -> str:
        raise NotImplementedError

    def container_command(self, job: ef.EvaluationJob, config_file_path: str) -> list[str]:
        assert isinstance(job.target, ef.EvaluationTarget)
        assert isinstance(job.target.api_endpoint, ef.APIEndpoint)
        assert job.config is not None
        assert job.config.type is not None
        assert job.output_dir is not None
        assert job.target.api_endpoint.type is not None

        cmd = [
            "nemo-evaluator",
            "run_eval",
            "--run_config",
            config_file_path,
            "--output_dir",
            job.output_dir,
            "--eval_type",
            job.config.type,
        ]

        # Only include model arguments if they have non-empty values
        # For retriever evaluations, these are empty since there's no target model
        if job.target.api_endpoint.model_id:
            cmd.extend(["--model_id", job.target.api_endpoint.model_id])
        if job.target.api_endpoint.url:
            cmd.extend(["--model_url", job.target.api_endpoint.url])
        if job.target.api_endpoint.type:
            cmd.extend(["--model_type", job.target.api_endpoint.type])

        return cmd

    def validate_supported_metric_job_types(self, job: MetricJob):
        metric_name = job.metric.name if isinstance(job.metric, SystemMetric) else job.metric.type
        # Validate job type against metric's supported job types
        if isinstance(job, MetricRetrieverJob):
            if SupportedJobTypes.RETRIEVER not in job.metric.supported_job_types:
                raise ValueError(
                    f"{metric_name} metric does not support retriever evaluations. Check metric's supported_job_types."
                )
        elif isinstance(job, MetricOnlineJob):
            if SupportedJobTypes.ONLINE not in job.metric.supported_job_types:
                raise ValueError(
                    f"{metric_name} metric does not support online evaluations with a model. Remove the model and specify a dataset."
                )
        elif isinstance(job, MetricOfflineJob):
            if SupportedJobTypes.OFFLINE not in job.metric.supported_job_types:
                raise ValueError(
                    f"{metric_name} metric does not support offline evaluations and a model is required. Specify a model to evaluate."
                )
        else:
            raise Exception(f"unexpected MetricJob for evalfactory metric handlers: {type(job)}")

    def validate_supported_benchmark_job_types(self, job: SystemBenchmarkJob):
        # Validate job type against metric's supported job types
        if isinstance(job, SystemBenchmarkOnlineJob):
            if SupportedJobTypes.ONLINE not in job.benchmark.supported_job_types:
                raise ValueError(
                    f"{job.benchmark.name} benchmark does not support online evaluations with a model. Remove the model and specify a dataset."
                )
        elif isinstance(job, SystemBenchmarkOfflineJob):
            if SupportedJobTypes.OFFLINE not in job.benchmark.supported_job_types:
                raise ValueError(
                    f"{job.benchmark.name} benchmark does not support offline evaluations and a model is required. Specify a model to evaluate."
                )
        else:
            raise Exception(f"unexpected SystemBenchmarkJob for evalfactory benchmark handlers: {type(job)}")

    def validate_params(self, params: dict, required_params: list[Parameter], optional_params: list[Parameter]):
        errs: list[str] = []
        try:
            self.validate_required_params(params, required_params)
        except ValueError as e:
            errs.append(str(e))

        for opt_param in optional_params:
            param = params.get(opt_param.name)
            if param:
                try:
                    self._validate_param_type(opt_param, param)
                except ValueError as e:
                    errs.append(str(e))
        if errs:
            raise ValueError("\n".join(errs))

    def _validate_param_type(self, param_def: Parameter, input_param: Any):
        """
        Validates the user-input parameter value type for the defined parameter of the system metric or benchmark.
        """
        if param_def.type == "secret":
            if not isinstance(input_param, str):
                raise ValueError(
                    f"unexpected type for parameter {param_def.name} {param_def.model_dump_json(exclude_none=True)}: type({input_param}) {type(input_param)}"
                )
        else:
            try:
                jsonschema.validate(input_param, {"type": param_def.type})
            except jsonschema.ValidationError:
                raise ValueError(
                    f"unexpected type for parameter {param_def.name} {param_def.model_dump_json(exclude_none=True)}: type({input_param}) {type(input_param)}"
                )

    def validate_required_params(self, params: dict, required_params: list[Parameter]):
        """
        Validate required parameters for a given system metric or benchmark are set in job.*_params.
        """
        errs: list[str] = []
        for req_param in required_params:
            param = params.get(req_param.name)
            if not param:
                errs.append(
                    f"missing required parameter {req_param.name}: {req_param.model_dump_json(exclude_none=True)}"
                )
                continue
            try:
                self._validate_param_type(req_param, param)
            except ValueError as e:
                errs.append(str(e))
        if errs:
            raise ValueError("\n".join(errs))

    def augment_harness_supported_model_types(
        self, job: SystemBenchmarkJob, supported_model_types: set[EvalFactoryModelType] | None
    ):
        # Validate chat/completions model with benchmark type
        assert isinstance(job, SystemBenchmarkOnlineJob)
        if not supported_model_types:
            raise Exception(f"Unexpected benchmark for {self.__class__.__name__}: {job.benchmark.name}")

        endpoint_type = (
            EvalFactoryModelType.COMPLETIONS if "/v1/completions" in job.model.url else EvalFactoryModelType.CHAT
        )
        if endpoint_type not in supported_model_types:
            raise ValueError(
                f"{endpoint_type.value} detected from job.model.url but is not supported for job {job.benchmark.name}, expected {[mt.value for mt in supported_model_types]}"
            )

        model_type = job.benchmark_params.get("model_type")
        if not model_type:
            model_type = endpoint_type  # Default to endpoint type
            job.benchmark_params["model_type"] = model_type
        else:
            model_type = EvalFactoryModelType(model_type)
        if model_type not in supported_model_types:
            raise ValueError(
                f"model type {model_type.value} is not supported for benchmark {job.benchmark.name}, expected {[mt.value for mt in supported_model_types]}. Set job.benchmark_params.model_type with the correct type or update the job.model.url path to '/v1/chat/completions' for 'chat' or '/v1/completions' for 'completions'."
            )

        if endpoint_type != model_type:
            raise ValueError(
                f"mismatch model endpoint with configured model type {model_type.value} for benchmark {job.benchmark.name}, job.benchmark_params.model_type {model_type.value} does not match detected {endpoint_type.value} from job.model.url."
            )

    def _secrets(self, params: dict, required_params: list[Parameter], optional_params: list[Parameter]):
        secrets = {}
        for param in itertools.chain(required_params, optional_params):
            if param.type == "secret":
                secret_ref = params.get(param.name)
                if secret_ref:
                    secret_env = secret_ref
                    if param.name == hf_token_param.name:
                        # special handling of HF_TOKEN env for EvalFactory
                        secret_env = "HF_TOKEN"
                    secrets[secret_env] = SecretRef(secret_ref)
        return secrets

    def metric_job_secrets(self, job: MetricJob) -> dict[str, SecretRef]:
        """Job secrets for the metric. Returns a dictionary of environment variables to the secret reference"""
        assert isinstance(job.metric, SystemMetric)
        return self._secrets(job.metric_params, job.metric.required_params, job.metric.optional_params)

    def benchmark_job_secrets(self, job: SystemBenchmarkJob) -> dict[str, SecretRef]:
        """Job secrets for the benchmark. Returns a dictionary of environment variables to the secret reference"""
        return self._secrets(job.benchmark_params, job.benchmark.required_params, job.benchmark.optional_params)
