# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import nmp.evaluator.app.jobs.evalfactory.models as ef
from nemo_evaluator_sdk.values import SecretRef, SupportedJobTypes
from nmp.evaluator.app.evalfactory.convert import _convert_config_params, _setup_adapter_config
from nmp.evaluator.app.evalfactory.handler import (
    BaseSystemHandler,
    JudgeModelParamsInput,
)
from nmp.evaluator.app.evalfactory.labels import LABEL_AGENTIC, new_labels
from nmp.evaluator.app.values import MetricJob, MetricOfflineJob, Parameter, SystemMetric
from nmp.evaluator.config import settings
from pydantic import model_validator
from typing_extensions import Self


class AgenticEvalJudgeModelParamsInput(JudgeModelParamsInput):
    """Judge model params for agentic evaluation with additional endpoint validation."""

    @model_validator(mode="after")
    def completions_endpoint(self) -> Self:
        if "/v1/chat/completions" not in self.model.url:
            raise ValueError(
                f"The path for job.metric_params.judge.model.url must end in '/v1/chat/completions' for agentic judge: {self.model.model_dump_json(exclude_none=True)}"
            )
        return self


trajectory_judge_param = Parameter(
    name="judge",
    type="object",
    description="The LLM judge to use for trajectory evaluation.",
    schema_=AgenticEvalJudgeModelParamsInput.model_json_schema(),
)
trajectory_used_tools_param = Parameter(
    name="trajectory_used_tools",
    type="string",
    description="Comma-separated list of tool names that were available to the agent during execution. This helps the evaluator understand what tools the agent had at its disposal. Example: 'wikipedia_search,current_datetime,code_generation,dummy_custom_tool'",
)
trajectory_custom_tools_param = Parameter(
    name="trajectory_custom_tools",
    type="object",
    description="""Required for any tools that are not part of the Nemo agent toolkit default functions. This helps the judge LLM understand the purpose of each custom tool. Example:
{
  "dummy_custom_tool": "Do nothing. This tool is for test only",
  "code_generation": "Useful to generate Python code. For any questions about code generation, you must only use this tool!",
  "wikipedia_search": "Tool that retrieves relevant contexts from wikipedia search for the given question.\n\n  Args:\n    _type (str): The type of the object.\n    max_results (int): Description unavailable. Defaults to 2."
}
""",
)


class AgenticEvalHandler(BaseSystemHandler):
    @classmethod
    def docker_image(cls) -> str:
        return settings.evalfactory.agentic_eval

    @classmethod
    def system_metrics(self) -> list[SystemMetric]:
        return self._system_metrics

    def metric_job_secrets(self, job: MetricJob) -> dict[str, SecretRef]:
        """Job secrets for the metric. Returns a dictionary of environment variables to the secret reference"""
        assert isinstance(job, MetricOfflineJob)
        assert isinstance(job.metric, SystemMetric)
        # Special handling for agentic_eval where judge.model.api_key_secret can't be easily represented
        # by Parameter
        secrets = super().metric_job_secrets(job)
        judge_raw_param = job.metric_params.get("judge")
        if judge_raw_param:
            judge = AgenticEvalJudgeModelParamsInput.model_validate(judge_raw_param)
            if judge.model.api_key_secret:
                secrets["judge_api_key_secret"] = judge.model.api_key_secret
                # OpenAI Python client expects OPENAI_API_KEY environment variable
                if judge.model.format == "openai":
                    secrets["OPENAI_API_KEY"] = judge.model.api_key_secret
        return secrets

    def augment_metric_job(self, job: MetricJob, output_dir: str) -> ef.EvaluationJob:
        self.validate_supported_metric_job_types(job)
        assert isinstance(job, MetricOfflineJob)
        assert isinstance(job.metric, SystemMetric)
        self.validate_params(job.metric_params, job.metric.required_params, job.metric.optional_params)

        judge: AgenticEvalJudgeModelParamsInput | None = None

        # Validate judge model
        if job.metric.name in self._require_judge:
            judge_raw_param = job.metric_params.get("judge")
            if not judge_raw_param:
                raise ValueError(
                    f"job.metric_params.judge.model is required for evaluation with metric {job.metric.name}"
                )
            judge = AgenticEvalJudgeModelParamsInput.model_validate(judge_raw_param)

            # Merge judge parameters
            judge_model_args = job.metric_params.get("judge_model_args", {})
            if judge.inference:
                judge_inference_params = judge.inference.model_dump(mode="json", exclude_none=True)
                if judge_inference_params:
                    judge_model_args.update(judge_inference_params)
            if judge.max_retries:
                judge_model_args["max_retries"] = judge.max_retries
            job.metric_params["judge_model_args"] = judge_model_args
            job.metric_params["judge_model_type"] = "openai" if judge.model.format == "openai" else "nvidia-nim"

        # EvalFactory expects metric names with 'agentic_eval_' prefix and underscores instead of hyphens
        metric_name = "agentic_eval_" + job.metric.name.replace("-", "_")

        # can't use augment_job like other handlers because AgenticEval is a special snowflake
        # that shims judge model as target.model
        if judge is not None:
            return ef.EvaluationJob(
                target=ef.EvaluationTarget(
                    api_endpoint=ef.APIEndpoint(
                        url=judge.model.url,
                        model_id=judge.model.name,
                        # Use the env var name (must match key in secrets() method) - the Jinja template adds the $ prefix
                        api_key="judge_api_key_secret" if judge.model.api_key_secret else None,
                        # api_key_name does not work for agentic_eval:26.01
                        api_key_name="judge_api_key_secret" if judge.model.api_key_secret else None,
                        type="chat" if "/chat" in judge.model.url else "completions",
                        adapter_config=_setup_adapter_config(job, output_dir, judge.system_prompt, judge.reasoning),
                    )
                ),
                config=ef.RunConfig(
                    type=metric_name,  # Evaluator system metric name is the EF config name
                    params=_convert_config_params(job, exclude={"judge"}),
                ),
                output_dir=output_dir,
            )

        # Metrics without a judge
        # These metrics don't call an external model, but the container command still needs
        # model_id, url, and type - we provide placeholders that EvalFactory will ignore
        return ef.EvaluationJob(
            target=ef.EvaluationTarget(
                api_endpoint=ef.APIEndpoint(
                    url="none",  # Placeholder - no target endpoint for non-judge metrics
                    model_id="none",  # Placeholder
                    type="chat",  # Placeholder - required by container_command
                    adapter_config=_setup_adapter_config(job, output_dir, None, None),
                )
            ),
            config=ef.RunConfig(
                type=metric_name,
                params=_convert_config_params(job, exclude=set()),
            ),
            output_dir=output_dir,
        )

    _require_judge = {
        "trajectory-evaluation",
    }

    _system_metrics = [
        SystemMetric(
            name="trajectory-evaluation",
            description="Evaluates agent decision-making by analyzing the sequence of actions taken to accomplish a goal",
            labels=new_labels("agentic_eval", LABEL_AGENTIC),
            supported_job_types=[SupportedJobTypes.OFFLINE],
            required_params=[trajectory_judge_param, trajectory_used_tools_param],
            optional_params=[trajectory_custom_tools_param],
        ),
    ]
