# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import nmp.evaluator.app.jobs.evalfactory.models as ef
from nemo_evaluator_sdk.values import DatasetRows, ReasoningParams, RunConfig, RunConfigOnlineModel
from nmp.common.config import get_platform_config
from nmp.evaluator.app.datasets.nmp_datasets.fileset import get_local_dataset_path
from nmp.evaluator.app.jobs.progress_tracking import (
    get_progress_tracking_interval,
    get_progress_tracking_url,
)
from nmp.evaluator.app.values import (
    BuiltInDataset,
    Fileset,
    FilesetRef,
    MetricOfflineJob,
    MetricOnlineJob,
    SystemBenchmarkJob,
    SystemBenchmarkOnlineJob,
    SystemMetric,
)
from nmp.evaluator.config import settings

# Filename for inline dataset written by the download_fileset task
INLINE_DATASET_FILENAME = "dataset.json"


def get_dataset_config(
    dataset: DatasetRows | Fileset | FilesetRef | BuiltInDataset,
    dataset_format: str | None = None,
    output_dir: str | None = None,
) -> ef.Dataset:
    """Extract dataset configuration from the job dataset.

    This function converts metric job dataset specifications to EvalFactory dataset configs.
    BuiltInDataset uses the dataset name directly (downloaded at runtime).
    All other types resolve to a local path via get_local_dataset_path.

    Args:
        dataset: The dataset from the job (DatasetRows, Fileset, FilesetRef, or BuiltInDataset).
        dataset_format: The format of the dataset (e.g., "beir", "ragas"). Optional.
        output_dir: Directory where datasets are stored. Required for non-BuiltInDataset types.

    Returns:
        EvalFactory Dataset config.
    """
    # BuiltInDataset - well-known datasets (BEIR, RAGAS) downloaded at runtime
    if isinstance(dataset, BuiltInDataset):
        if dataset.root == "ragas/amnesty_qa":
            return ef.Dataset(
                format="ragas",
                path="explodinggradients/amnesty_qa",
                dataset_name="english_v2",
                split="eval",
            )
        return ef.Dataset(format=dataset.format, path=dataset.name)

    # All other types (DatasetRows, Fileset, FilesetRef) resolve to local path
    config = ef.Dataset(path=get_local_dataset_path(dataset, output_dir))
    if dataset_format:
        config.format = dataset_format
    return config


def augment_online_job(job: MetricOnlineJob | SystemBenchmarkOnlineJob, output_dir: str) -> ef.EvaluationJob:
    """
    Converts Evaluator MS metric job to EvalFactory job.
    """
    params = job.params or RunConfigOnlineModel()
    # Evaluator system metric/benchmark name is the EF config name
    if isinstance(job, MetricOnlineJob):
        assert isinstance(job.metric, SystemMetric)
        config_type = job.metric.name
    else:
        config_type = job.benchmark.name

    return ef.EvaluationJob(
        target=ef.EvaluationTarget(
            api_endpoint=ef.APIEndpoint(
                url=job.model.url,
                model_id=job.model.name,
                # api_key is an environment variable, where - is an unsupported character.
                api_key_name=job.model.api_key_env if job.model.api_key_secret else None,
                type="completions" if "/v1/completions" in job.model.url else "chat",
                adapter_config=_setup_adapter_config(job, output_dir, params.system_prompt, params.reasoning),
            )
        ),
        config=ef.RunConfig(
            type=config_type,
            params=_convert_config_params(job),
        ),
        output_dir=output_dir,
    )


def _convert_config_params(
    job: MetricOfflineJob | MetricOnlineJob | SystemBenchmarkJob,
    exclude: set | None = None,
) -> ef.RunParams:
    """
    Convert Evaluator MS metric parameters to EvalFactory job parameters
    """
    if not exclude:
        exclude = set()
    exclude.add("inference")
    params = job.params or RunConfig()

    inference_params = {}
    if isinstance(params, RunConfigOnlineModel) and params.inference:
        inference_params = params.inference.model_dump(
            exclude_none=True, exclude_defaults=True, exclude={"max_tokens", "max_completion_tokens"}
        )
        # Use "max_tokens" key because RunParams.max_new_tokens has alias="max_tokens"
        # and Value.model_config has extra="ignore", so max_new_tokens gets silently dropped
        inference_params["max_tokens"] = params.inference.max_tokens or params.inference.max_completion_tokens

    # Build extra params from metric_params
    if isinstance(job, SystemBenchmarkJob):
        extra_params = dict(job.benchmark_params)
    else:
        extra_params = dict(job.metric_params)

    # For offline jobs, add the dataset_path pointing to where the download step writes the file
    if isinstance(job, MetricOfflineJob):
        extra_params["dataset_path"] = get_local_dataset_path(job.dataset, settings.jobs.dataset_dir)

    return ef.RunParams(
        # exclude_unset=True preserves user-specified values even if they match defaults,
        # while still excluding fields the user never set
        **params.model_dump(exclude_none=True, exclude_unset=True, exclude=exclude),
        **inference_params,
        extra=extra_params,
    )


def _setup_adapter_config(
    job: MetricOfflineJob | MetricOnlineJob | SystemBenchmarkJob,
    output_dir: str,
    system_prompt: str | None,
    reasoning_params: ReasoningParams | None,
) -> ef.AdapterConfig:
    """
    Configure all appropriate EvalFactory adapter config for the job
    """
    adapter = ef.AdapterConfig()
    # Configure 25.07+
    # Order matters: request interceptors must occur before response interceptors
    request_interceptors = [
        ef.InterceptorConfig(
            name="request_logging",
            config={
                "output_dir": output_dir,
                "log_failed_requests": True,
            },
        ),
    ]
    response_interceptors = [
        ef.InterceptorConfig(
            name="caching",
            config={
                "cache_dir": output_dir,
                "reuse_cached_responses": True,
                "save_requests": True,
                "save_responses": True,
            },
        ),
        ef.InterceptorConfig(
            name="endpoint",
            config={},
        ),
        ef.InterceptorConfig(
            name="response_logging",
            config={"output_dir": output_dir},
        ),
        ef.InterceptorConfig(
            name="raise_client_errors",
        ),
    ]
    adapter.post_eval_hooks = [
        ef.PostEvalHookConfig(
            name="post_eval_report",
            config={"report_types": ["json"]},
        ),
    ]

    # Configure callback for progress tracking
    if get_platform_config().get_service_url("jobs"):
        request_method = "PATCH"
        params = job.params or RunConfig()
        num_samples = params.limit_samples
        callback_interval = get_progress_tracking_interval(num_samples)
        callback_url = get_progress_tracking_url()

        response_interceptors.append(
            ef.InterceptorConfig(
                name="progress_tracking",
                config={
                    "progress_tracking_interval_seconds": 60,
                    "progress_tracking_interval": callback_interval,
                    "progress_tracking_url": callback_url,
                    "request_method": request_method,
                },
            )
        )
        adapter.post_eval_hooks.append(
            ef.PostEvalHookConfig(
                name="progress_tracking",
                config={
                    "progress_tracking_interval_seconds": 60,
                    "progress_tracking_interval": callback_interval,
                    "progress_tracking_url": callback_url,
                    "request_method": request_method,
                },
            )
        )

    # Configure reasoning context handling and system message
    if reasoning_params:
        reasoning = ef.InterceptorConfig(
            name="reasoning",
            config={},
        )
        if reasoning_params.end_token:
            reasoning.config["end_reasoning_token"] = reasoning_params.end_token
        if reasoning_params.include_if_not_finished is not None:
            reasoning.config["include_if_not_finished"] = reasoning_params.include_if_not_finished
        response_interceptors.append(reasoning)

    if system_prompt:
        # Must be added to beginning of list organized request -> response
        request_interceptors.append(
            ef.InterceptorConfig(
                name="system_message",
                config={"system_message": system_prompt},
            )
        )

    adapter.interceptors = request_interceptors
    adapter.interceptors.extend(response_interceptors)

    return adapter
