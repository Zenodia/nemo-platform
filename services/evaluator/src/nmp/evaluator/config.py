# SPDX-FileCopyrightText: Copyright (c) 2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
# property and proprietary rights in and to this material, related
# documentation and any modifications thereto. Any use, reproduction,
# disclosure or distribution of this material and related documentation
# without an express license agreement from NVIDIA CORPORATION or
# its affiliates is strictly prohibited.
"""Configuration for the Evaluator service."""

import logging
from pathlib import Path
from urllib.parse import urlparse

from nmp.common.config import create_service_config_class, get_service_config
from pydantic import BaseModel, Field, model_validator
from pydantic_settings import SettingsConfigDict

log = logging.getLogger(__name__)


class JobsConfig(BaseModel):
    configs_dir: str = Field(
        default="/configs", description="Directory path in job container for evaluation configuration."
    )
    volume_path: str = Field(
        default="/jobs",
        description="Directory path of the shared volume mount for job steps to persist artifacts for a job.",
    )
    results_dir: str = Field(
        default="/jobs/results", description="Directory path in the job container for results to be output."
    )
    dataset_dir: str = Field(
        default="/jobs/datasets",
        description="Directory path in the job container for dataset files to be downloaded to and loaded from.",
    )

    @model_validator(mode="after")
    def validate_directories(self):
        """Validate that all provider names are unique across types."""
        if not Path(self.results_dir).is_relative_to(Path(self.volume_path)):
            raise ValueError(
                f"job.results_dir {self.results_dir} is not a subpath of job.volume_path {self.volume_path}"
            )
        if not Path(self.dataset_dir).is_relative_to(Path(self.volume_path)):
            raise ValueError(
                f"job.dataset_dir {self.dataset_dir} is not a subpath of job.volume_path {self.volume_path}"
            )
        return self


class EvalFactoryConfig(BaseModel):
    """
    Configuration for EvalFactory integration with NeMo Platform.
    """

    agentic_eval: str = Field(default="nvcr.io/nvidia/eval-factory/agentic_eval:26.01")
    bfcl: str = Field(default="nvcr.io/nvidia/eval-factory/bfcl:26.01")
    lm_eval_harness: str = Field(default="nvcr.io/nvidia/eval-factory/lm-evaluation-harness:26.01")
    bigcode_evaluation_harness: str = Field(default="nvcr.io/nvidia/eval-factory/bigcode-evaluation-harness:26.01")
    rag_retriever: str = Field(default="nvcr.io/nvidia/eval-factory/rag_retriever_eval:26.01")
    safety_harness: str = Field(default="nvcr.io/nvidia/eval-factory/safety-harness:26.01")
    simple_evals: str = Field(default="nvcr.io/nvidia/eval-factory/simple-evals:26.01")

    milvus_url: str | None = Field(
        default=None, description="Connect to a hosted Milvus server for retrieval evaluations"
    )

    @model_validator(mode="after")
    def validate_milvus_url(self):
        if not self.milvus_url:
            return self

        parsed_url = urlparse(self.milvus_url)
        if not parsed_url.hostname:
            raise ValueError(
                f"milvus_url is not properly configured, URL {self.milvus_url} is in incorrect format and missing the hostname."
            )

        return self


class EvaluatorSettings(create_service_config_class("evaluator")):  # type: ignore[unsupported-base]
    """
    Configuration for the Evaluator service.

    Environment variables use the NMP_EVALUATOR_ prefix.
    """

    jobs: JobsConfig = Field(
        default_factory=JobsConfig, description="Configuration for jobs created with Evaluator service."
    )
    evalfactory: EvalFactoryConfig = Field(
        default_factory=EvalFactoryConfig, description="Configuration for EvalFactory integration with NeMo Platform."
    )
    recreate_existing_system_entities: bool = Field(
        default=False, description="Upsert system metrics and benchmarks on app startup"
    )

    # model_config is merged with inherited class
    # Without env_nested_max_split=1 set, NMP_EVALUATOR_EVALFACTORY_AGENTIC_EVAL would be parsed as
    # nemo_platform_evaluator.evaluator.agentic.eval instead of nemo_platform_evaluator.evaluator.agentic_eval
    model_config = SettingsConfigDict(env_nested_max_split=1)


settings = get_service_config(EvaluatorSettings)
