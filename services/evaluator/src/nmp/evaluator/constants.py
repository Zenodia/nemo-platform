# SPDX-FileCopyrightText: Copyright (c) 2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
# property and proprietary rights in and to this material, related
# documentation and any modifications thereto. Any use, reproduction,
# disclosure or distribution of this material and related documentation
# without an express license agreement from NVIDIA CORPORATION or
# its affiliates is strictly prohibited.
import os

PROJECT_HOME_DIR = os.getcwd()
DEFAULT_ENTITY_NAMESPACE = "default"  # default namespace will be "default"
DEFAULT_PROGRESS_TRACKING_INTERVAL = 50

PLACEHOLDER_INFERENCE_API_KEY = "XXX"

# secret keys
SECRET_KEY_TARGET_MODEL_API_TOKEN = "target.model.api_endpoint.api_key"
SECRET_KEY_ACADEMIC_BENCHMARK_HF_TOKEN = "config.params.extra.hf_token"
SECRET_KEY_RAG_JUDGE_API_KEY = "config.tasks.beir.params.judge_llm.api_endpoint.api_key"
SECRET_KEY_RAG_JUDGE_EMBEDDING_API_KEY = "config.tasks.beir.params.judge_embeddings.api_endpoint.api_key"
SECRET_KEY_LLM_AS_A_JUDGE_API_KEY = "config.tasks.metrics.params.model.api_endpoint.api_key"
SECRET_KEY_AGENTIC_EVAL_JUDGE_API_KEY = "config.tasks.judge.model.api_key"
SECRET_KEY_BFCL_RAPID_API_KEY = "config.params.extra.rapid_api_key"
SECRET_KEY_BFCL_EXCHANGERATE_API_KEY = "config.params.extra.exchangerate_api_key"
SECRET_KEY_BFCL_OMDB_API_KEY = "config.params.extra.omdb_api_key"
SECRET_KEY_BFCL_GEOCODE_API_KEY = "config.params.extra.geocode_api_key"
SECRET_KEY_SAFETY_HARNESS_JUDGE_API_KEY = "config.params.extra.judge.model.api_endpoint.api_key"
SECRET_KEY_TARGET_RETRIEVER_QUERY_API_TOKEN = "target.retriever.pipeline.query_embedding_model.api_endpoint.api_key"
SECRET_KEY_TARGET_RETRIEVER_INDEX_API_TOKEN = "target.retriever.pipeline.index_embedding_model.api_endpoint.api_key"
SECRET_KEY_TARGET_RAG_QUERY_API_TOKEN = (
    "target.rag.pipeline.retriever.pipeline.query_embedding_model.api_endpoint.api_key"
)
SECRET_KEY_TARGET_RAG_INDEX_API_TOKEN = (
    "target.rag.pipeline.retriever.pipeline.index_embedding_model.api_endpoint.api_key"
)
SECRET_KEY_TARGET_RAG_MODEL_API_TOKEN = "target.rag.pipeline.model.api_endpoint.api_key"
SECRET_KEY_SIMPLE_EVALS_JUDGE_API_KEY = "config.params.extra.judge.api_key"
