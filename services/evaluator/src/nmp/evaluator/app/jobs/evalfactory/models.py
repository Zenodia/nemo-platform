# SPDX-FileCopyrightText: Copyright (c) 2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
# property and proprietary rights in and to this material, related
# documentation and any modifications thereto. Any use, reproduction,
# disclosure or distribution of this material and related documentation
# without an express license agreement from NVIDIA CORPORATION or
# its affiliates is strictly prohibited.

from typing import Any, Dict

from nmp.evaluator.app.jobs.evalfactory.constants import ModelFormat
from pydantic import BaseModel, Field


class Value(BaseModel):
    """The base class for all value types.

    This also helps avoid confusion since Model and BaseModel in Pydantic
    mean something different.
    """

    model_config = {"arbitrary_types_allowed": True, "protected_namespaces": (), "extra": "ignore"}


class CachedOutputs(Value):
    path: str = Field()


class InterceptorConfig(Value):
    """Configuration for a single interceptor"""

    name: str = Field(description="Name of the interceptor to use")
    enabled: bool = Field(description="Whether this interceptor is enabled", default=True)
    config: dict[str, Any] = Field(description="Configuration for the interceptor", default_factory=dict)


class PostEvalHookConfig(Value):
    """Configuration for a single post-evaluation hook"""

    name: str = Field(description="Name of the post-evaluation hook to use")
    enabled: bool = Field(description="Whether this post-evaluation hook is enabled", default=True)
    config: dict[str, Any] = Field(description="Configuration for the post-evaluation hook", default_factory=dict)


class AdapterConfig(Value):
    interceptors: list[InterceptorConfig] = Field(
        description="List of interceptors to use with their configurations",
        default_factory=list,
    )
    post_eval_hooks: list[PostEvalHookConfig] = Field(
        description="List of post-evaluation hooks to use with their configurations",
        default_factory=list,
    )


class APIEndpoint(Value):
    url: str | None = Field(default=None)
    model_id: str | None = Field(default=None)
    # This field is REQUIRED for LM Eval Harness. We make sure it gets set in that handler's augment_config
    # method. If the user does not supply a value we do our best/safest guess but the ultimate
    # underlying default is 'completions', which is used in the total absence of anything better.
    type: str | None = Field(default=None)
    api_key: str | None = Field(
        default=None,
        description="Contains env var name pointing to secret, not the raw secret itself. Deprecated field used for EvalFactory 25.11 and earlier, still used by agentic_eval:26.01. Will be removed 26.03",
    )
    api_key_name: str | None = Field(
        default=None, description="Contains env var name pointing to secret, not the raw secret itself (25.12+)."
    )
    # If absent, underlying default is False
    stream: bool | None = Field(default=None)
    # Evaluator reasoning options are mapped from Config to EvalFactory target.api_endpoint.adapter_config
    adapter_config: AdapterConfig | None = Field(default=None)
    format: str | None = Field(default=None)


class EvaluationTarget(Value):
    api_endpoint: APIEndpoint | None = Field(default=None)
    cached_outputs: CachedOutputs | None = Field(default=None)


class Dataset(Value):
    format: str | None = Field(default=None)
    namespace: str | None = Field(default=None)
    dataset_name: str | None = Field(default=None)
    path: str = Field()
    split: str | None = Field(default=None)
    limit: int | None = Field(default=None)


class MetricConfig(Value):
    """A metric that is computed as part of the evaluation."""

    type: str = Field(
        description="The type of the metric.",
    )

    # NOTE: we can spec this in detail as well, but not for the initial implementation
    params: dict[str, Any] | None = Field(default=None, description="Specific parameters for the metric.")


class TaskConfig(Value):
    """Configuration object for a task which is part of an evaluation."""

    type: str = Field(
        description="The type of the task within a benchmark. Example 'mmlu_high_school', etc.",
    )

    params: dict[str, Any] | None = Field(default=None, description="Additional parameters related to the task.")

    metrics: dict[str, MetricConfig] | None = Field(default=None, description="Metrics to be computed for the task.")

    dataset: Dataset | None = Field(
        None,
        description="Optional dataset reference."
        "Typically, if not specified, means that the type of task has an implicit dataset.",
    )


class RunParams(Value):
    """Global parameters for an evaluation."""

    # General parameters that control the execution of an evaluation

    parallelism: int | None = Field(
        description="Parallelism to be used for the evaluation job. "
        "Typically, this represents the maximum number of concurrent requests made to the model.",
        default=None,
    )
    request_timeout: int | None = Field(
        description="The timeout to be used for requests made to the model.",
        default=None,
    )
    max_retries: int | None = Field(description="Maximum number of retries for failed requests.", default=None)

    # Parameters related to the LLM request params

    limit_samples: int | None = Field(description="Limit number of evaluation samples", default=None)
    max_new_tokens: int | None = Field(description="Max tokens to generate", default=None, alias="max_tokens")
    temperature: float | None = Field(
        description="Float value between 0 and 1. temp of 0 indicates greedy decoding, "
        "where the token with highest prob is chosen. Temperature can't be set to 0.0 currently",
        default=None,
    )
    top_p: float | None = Field(
        description="Float value between 0 and 1; limits to the top tokens within a certain "
        "probability. top_p=0 means the model will only consider the single most likely "
        "token for the next prediction",
        default=None,
    )
    extra: dict[str, Any] | None = Field(description="Any other custom parameters.", default_factory=dict)

    # BFCL
    task: str | None = Field(default=None)


class RunConfig(Value):
    type: str = Field()
    params: RunParams | None = Field()


class EvaluationJob(Value):
    id: str | None = Field(default=None)
    target: EvaluationTarget | None = Field(default=None)
    config: RunConfig | None = Field(default=None)
    output_dir: str | None = Field(default=None)


class AgenticParams(Value):
    dataset_path: str = Field(description="Path to the dataset file")
    metric_mode: str | None = Field(
        default=None, description="Specific mode for `topic_adherence` (precision, recall, f1. default f1)"
    )
    judge_model_type: ModelFormat | None = Field(
        default=None, description="The type of judge model to use (e.g., openai or nvidia-nim)"
    )
    judge_model_args: dict[str, Any] | None = Field(default=None, description="Configuration for judge model")
    judge_sanity_check: bool | None = Field(default=None, description="Enable/disable judge model sanity checks")
    trajectory_used_tools: str | None = Field(
        default=None, description="Comma-separated list of tools used in trajectory evaluation"
    )
    trajectory_custom_tools: dict[str, str] | None = Field(
        default=None,
        description="Dictionary mapping tool names to descriptions for trajectory evaluation",
    )


class RetrieverParams(Value):
    index_pipeline_yaml_file: str
    query_pipeline_yaml_file: str
    component_inputs_template: str
    milvus_uri: str | None = Field(None)
    milvus_host: str | None = Field(None)
    milvus_port: str | None = Field(None)
    milvus_password: str | None = Field(None)
    milvus_collection_name: str | None = Field(None)
    retriever_name: str | None
    retriever_type: str | None


class RetrieverModel(Value):
    api_endpoint: APIEndpoint | None = Field(default=None)


class RetrieverPipeline(Value):
    top_k: int | None = Field(default=None)
    query_embedding_model: RetrieverModel | None = Field(default=None)
    index_embedding_model: RetrieverModel | None = Field(default=None)
    reranker_model: RetrieverModel | None = Field(default=None)
    params: dict[str, Any] | None = Field(default=None)


class RAGPipeline(Value):
    context_ordering: str | None
    params: dict[str, Any] | None = Field(default=None)
    retriever: dict[str, RetrieverPipeline | None] | None


class JudgeTaskParams(Value):
    judge_llm: str
    judge_llm_url: str
    judge_llm_api_key: str | None
    judge_embeddings: str
    judge_embeddings_url: str
    judge_embeddings_api_key: str | None
    judge_request_timeout: int
    judge_max_retries: int
    judge_max_workers: int


class RAGConfig(Value):
    tasks: Dict[str, TaskConfig]
    pipeline: RAGPipeline


class RetrieverConfig(Value):
    tasks: Dict[str, TaskConfig]
    pipeline: RetrieverPipeline
