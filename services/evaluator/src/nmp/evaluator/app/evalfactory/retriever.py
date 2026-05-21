# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import nmp.evaluator.app.evalfactory.labels as ef_labels
import nmp.evaluator.app.jobs.evalfactory.models as ef
import nmp.evaluator.constants as constants
from nemo_evaluator_sdk.enums import MetricType
from nemo_evaluator_sdk.values import SecretRef, SupportedJobTypes
from nmp.evaluator.app.evalfactory.convert import get_dataset_config
from nmp.evaluator.app.evalfactory.handler import BaseSystemHandler
from nmp.evaluator.app.values import (
    MetricJob,
    MetricRetrieverJob,
    Parameter,
    RetrieverPipeline,
    SystemMetric,
)
from nmp.evaluator.config import settings
from nmp.evaluator.utils import milvus

# Mapping from registered retriever metric names to EvalFactory metric names
# EvalFactory uses pytrec_eval metric names (without retriever_ prefix, with mixed case)
RETRIEVER_METRIC_MAPPING: dict[str, str] = {
    # Fixed metrics (no cutoff)
    "retriever-map": "map",
    "retriever-gm-map": "gm_map",
    "retriever-gm-bpref": "gm_bpref",
    "retriever-rprec": "Rprec",
    "retriever-bpref": "bpref",
    "retriever-recip-rank": "recip_rank",
    "retriever-infap": "infAP",
    "retriever-ndcg": "ndcg",
    "retriever-ndcg-rel": "ndcg_rel",
    "retriever-bing": "binG",
    "retriever-g": "G",
    "retriever-rndcg": "Rndcg",
    "retriever-11pt-avg": "11pt_avg",
    "retriever-set-p": "set_P",
    "retriever-set-map": "set_map",
    "retriever-set-recall": "set_recall",
    "retriever-set-relative-p": "set_relative_P",
    "retriever-set-f": "set_F",
    # Cutoff-based metrics (P@k)
    "retriever-p-5": "P_5",
    "retriever-p-10": "P_10",
    "retriever-p-20": "P_20",
    "retriever-p-100": "P_100",
    # Cutoff-based metrics (recall@k)
    "retriever-recall-5": "recall_5",
    "retriever-recall-10": "recall_10",
    "retriever-recall-20": "recall_20",
    "retriever-recall-100": "recall_100",
    # Cutoff-based metrics (ndcg_cut@k)
    "retriever-ndcg-cut-5": "ndcg_cut_5",
    "retriever-ndcg-cut-10": "ndcg_cut_10",
    "retriever-ndcg-cut-20": "ndcg_cut_20",
    "retriever-ndcg-cut-100": "ndcg_cut_100",
    # Cutoff-based metrics (map_cut@k)
    "retriever-map-cut-5": "map_cut_5",
    "retriever-map-cut-10": "map_cut_10",
    "retriever-map-cut-20": "map_cut_20",
    "retriever-map-cut-100": "map_cut_100",
    # Cutoff-based metrics (success@k)
    "retriever-success-5": "success_5",
    "retriever-success-10": "success_10",
    "retriever-success-20": "success_20",
    "retriever-success-100": "success_100",
}


def get_retriever_evalfactory_metric_name(metric_name: str) -> str:
    """Get the EvalFactory metric name for a retriever metric."""
    if metric_name not in RETRIEVER_METRIC_MAPPING:
        raise ValueError(f"Unknown retriever metric: {metric_name}")
    return RETRIEVER_METRIC_MAPPING[metric_name]


def build_retriever_pipeline(
    retriever_pipeline: RetrieverPipeline,
    metric_params: dict,
    collection_name: str = "metric_eval",
) -> ef.RetrieverPipeline:
    """Build the retriever pipeline config from a retriever pipeline definition.

    This is a shared utility used by both Retriever and RAG metrics handlers.

    Args:
        retriever_pipeline: The pipeline configuration with embedding model.
        metric_params: Additional parameters including top_k and truncate_long_documents.
        collection_name: Milvus collection name for the evaluation.

    Returns:
        Configured RetrieverPipeline for eval factory.
    """
    embedding_model = retriever_pipeline.embeddings_model

    # Use host_url (direct NIM endpoint) when available, falling back to the model URL.
    # EvalFactory's Haystack NvidiaDocumentEmbedder only accepts http://host:port format
    # and rejects URLs with path components (like IGW-proxied URLs).
    # host_url is populated when the model was resolved from a ModelRef.
    embedding_url = embedding_model.host_url or embedding_model.url

    # Build embedding model endpoint
    embedding_endpoint = ef.APIEndpoint(
        url=embedding_url,
        model_id=embedding_model.name,
        format=embedding_model.format,
    )
    # Keep api_key explicit for EvalFactory/Haystack embedders:
    # if omitted, some versions require NVIDIA_API_KEY env and fail hard.
    # api_key_name is not supported in 26.01
    embedding_endpoint.api_key = (
        "$QUERY_API_KEY"
        if embedding_model.api_key_secret
        else (embedding_model.api_key or constants.PLACEHOLDER_INFERENCE_API_KEY)
    )

    # Both query and index use the same embedding model
    query_model = ef.RetrieverModel(api_endpoint=embedding_endpoint)
    index_model = ef.RetrieverModel(
        api_endpoint=ef.APIEndpoint(
            url=embedding_url,
            model_id=embedding_model.name,
            format=embedding_model.format,
            # api_key_name is not supported in 26.01
            api_key=(
                "$INDEX_API_KEY"
                if embedding_model.api_key_secret
                else (embedding_model.api_key or constants.PLACEHOLDER_INFERENCE_API_KEY)
            ),
        )
    )

    # Build retriever pipeline
    pipeline = ef.RetrieverPipeline(
        query_embedding_model=query_model,
        index_embedding_model=index_model,
        top_k=metric_params.get("top_k", 10),
    )

    # Build pipeline params (milvus config, yaml files, etc.)
    pipeline.params = {
        "index_pipeline_yaml_file": "/workspace/tests/retriever/templates/dense_only/milvus_index_nim.yaml",
        "query_pipeline_yaml_file": "/workspace/tests/retriever/templates/dense_only/milvus_query_nim.yaml",
        "component_inputs_template": '{"embedder": {"text": "${query}"} }',
        "milvus_collection_name": collection_name,
        "retriever_name": "nim-retriever",
        "retriever_type": "nvidia-nemo-nim",
    }

    # Handle truncate_long_documents param
    if metric_params.get("truncate_long_documents"):
        pipeline.params["truncate_long_documents"] = metric_params["truncate_long_documents"]

    # Configure milvus
    if settings.evalfactory.milvus_url:
        milvus_config = milvus.get_milvus_configs(
            milvus_url=settings.evalfactory.milvus_url, collection_name=collection_name
        )
        pipeline.params.update(milvus_config)
    else:
        # Use file based local milvus if milvus server is not specified
        pipeline.params["milvus_uri"] = "/workspace/milvus.db"

    return pipeline


top_k_param = Parameter(
    name="top_k",
    type="integer",
    default=10,
    description="Number of top results to retrieve for evaluation.",
)
truncate_long_documents_param = Parameter(
    name="truncate_long_documents",
    type="string",
    description="Handle documents exceeding 65k characters. 'start': keep last 65k chars, 'end': keep first 65k chars.",
)

dataset_format_param = Parameter(
    name="dataset_format",
    type="string",
    default="beir",
    description="The dataset format for retriever evaluation. Supported format: beir.",
)

# Common optional params for retriever metrics
retriever_common_optional_params = [
    dataset_format_param,
    top_k_param,
    truncate_long_documents_param,
]


class RetrieverHandler(BaseSystemHandler):
    @classmethod
    def docker_image(cls) -> str:
        return settings.evalfactory.rag_retriever

    @classmethod
    def system_metrics(cls) -> list[SystemMetric]:
        return cls._system_metrics

    def metric_job_secrets(self, job: MetricJob) -> dict[str, SecretRef]:
        """Job secrets for the metric. Returns a dictionary of environment variables to the secret reference.

        The env var names must match what's used in the pipeline config:
        - QUERY_API_KEY: for query embedding model
        - INDEX_API_KEY: for index embedding model
        """
        assert isinstance(job, MetricRetrieverJob), (
            f"{getattr(job.metric, 'name', '<inline-metric>')} is not supported with {type(job).__name__}, expected MetricRetrieverJob"
        )
        secrets: dict[str, SecretRef] = {}
        if job.retriever_pipeline.embeddings_model.api_key_secret:
            # Both query and index use the same embedding model/secret
            secrets["QUERY_API_KEY"] = job.retriever_pipeline.embeddings_model.api_key_secret
            secrets["INDEX_API_KEY"] = job.retriever_pipeline.embeddings_model.api_key_secret
        return secrets

    def augment_metric_job(self, job: MetricJob, output_dir: str) -> ef.EvaluationJob:
        self.validate_supported_metric_job_types(job)
        assert isinstance(job, MetricRetrieverJob)
        assert isinstance(job.metric, SystemMetric)
        metric = job.metric
        self.validate_params(job.metric_params, metric.required_params, metric.optional_params)

        # Build retriever pipeline config
        pipeline = self._build_retriever_pipeline(job)

        # Build task config with the metric
        # Get EvalFactory metric name from mapping
        metric_name = get_retriever_evalfactory_metric_name(metric.name)
        dataset_format = job.metric_params.get("dataset_format", "beir")
        task_config = ef.TaskConfig(
            type=dataset_format,
            metrics={metric_name: ef.MetricConfig(type="pytrec_eval", params={})},
            dataset=get_dataset_config(job.dataset, dataset_format, settings.jobs.dataset_dir),
        )

        # Build RetrieverConfig with task and pipeline
        retriever_config = ef.RetrieverConfig(
            tasks={"retriever": task_config},
            pipeline=pipeline,
        )

        return ef.EvaluationJob(
            target=ef.EvaluationTarget(
                api_endpoint=ef.APIEndpoint(
                    url="",  # Retriever doesn't evaluate a target model directly
                    model_id="",
                    type="embedding",
                )
            ),
            config=ef.RunConfig(
                type="retriever",
                params=ef.RunParams(
                    extra=retriever_config.model_dump(mode="json", exclude_none=True, exclude_unset=True)
                ),
            ),
            output_dir=output_dir,
        )

    def _build_retriever_pipeline(self, job: MetricRetrieverJob) -> ef.RetrieverPipeline:
        """Build the retriever pipeline config from the metric job."""
        return build_retriever_pipeline(
            retriever_pipeline=job.retriever_pipeline,
            metric_params=job.metric_params,
            collection_name="metric_eval",
        )

    # Fixed pytrec_eval metrics (no cutoff parameter)
    _fixed_metrics = [
        "retriever-map",
        "retriever-gm-map",
        "retriever-gm-bpref",
        "retriever-rprec",
        "retriever-bpref",
        "retriever-recip-rank",
        "retriever-infap",
        "retriever-ndcg",
        "retriever-ndcg-rel",
        "retriever-bing",
        "retriever-g",
        "retriever-rndcg",
        "retriever-11pt-avg",
        "retriever-set-p",
        "retriever-set-map",
        "retriever-set-recall",
        "retriever-set-relative-p",
        "retriever-set-f",
    ]

    _system_metrics = [
        # Fixed metrics (no cutoff)
        SystemMetric(
            type=MetricType.SYSTEM_RETRIEVER,
            name="retriever-map",
            description="Mean Average Precision (MAP) - measures the mean of average precision scores across all queries.",
            labels=ef_labels.new_labels("retriever", ef_labels.LABEL_RETRIEVAL),
            supported_job_types=[SupportedJobTypes.RETRIEVER],
            optional_params=retriever_common_optional_params,
        ),
        SystemMetric(
            type=MetricType.SYSTEM_RETRIEVER,
            name="retriever-gm-map",
            description="Geometric Mean of Average Precision - geometric mean variant of MAP.",
            labels=ef_labels.new_labels("retriever", ef_labels.LABEL_RETRIEVAL),
            supported_job_types=[SupportedJobTypes.RETRIEVER],
            optional_params=retriever_common_optional_params,
        ),
        SystemMetric(
            type=MetricType.SYSTEM_RETRIEVER,
            name="retriever-gm-bpref",
            description="Geometric Mean of Binary Preference - geometric mean variant of bpref.",
            labels=ef_labels.new_labels("retriever", ef_labels.LABEL_RETRIEVAL),
            supported_job_types=[SupportedJobTypes.RETRIEVER],
            optional_params=retriever_common_optional_params,
        ),
        SystemMetric(
            type=MetricType.SYSTEM_RETRIEVER,
            name="retriever-rprec",
            description="R-Precision - precision at R, where R is the number of relevant documents for a query.",
            labels=ef_labels.new_labels("retriever", ef_labels.LABEL_RETRIEVAL),
            supported_job_types=[SupportedJobTypes.RETRIEVER],
            optional_params=retriever_common_optional_params,
        ),
        SystemMetric(
            type=MetricType.SYSTEM_RETRIEVER,
            name="retriever-bpref",
            description="Binary Preference - measures preference of relevant documents over non-relevant ones.",
            labels=ef_labels.new_labels("retriever", ef_labels.LABEL_RETRIEVAL),
            supported_job_types=[SupportedJobTypes.RETRIEVER],
            optional_params=retriever_common_optional_params,
        ),
        SystemMetric(
            type=MetricType.SYSTEM_RETRIEVER,
            name="retriever-recip-rank",
            description="Reciprocal Rank - the multiplicative inverse of the rank of the first relevant document.",
            labels=ef_labels.new_labels("retriever", ef_labels.LABEL_RETRIEVAL),
            supported_job_types=[SupportedJobTypes.RETRIEVER],
            optional_params=retriever_common_optional_params,
        ),
        SystemMetric(
            type=MetricType.SYSTEM_RETRIEVER,
            name="retriever-infap",
            description="Inferred Average Precision - average precision adjusted for incomplete relevance judgments.",
            labels=ef_labels.new_labels("retriever", ef_labels.LABEL_RETRIEVAL),
            supported_job_types=[SupportedJobTypes.RETRIEVER],
            optional_params=retriever_common_optional_params,
        ),
        SystemMetric(
            type=MetricType.SYSTEM_RETRIEVER,
            name="retriever-ndcg",
            description="Normalized Discounted Cumulative Gain - measures ranking quality with graded relevance.",
            labels=ef_labels.new_labels("retriever", ef_labels.LABEL_RETRIEVAL),
            supported_job_types=[SupportedJobTypes.RETRIEVER],
            optional_params=retriever_common_optional_params,
        ),
        SystemMetric(
            type=MetricType.SYSTEM_RETRIEVER,
            name="retriever-ndcg-rel",
            description="NDCG with relevance - NDCG variant that considers relevance levels.",
            labels=ef_labels.new_labels("retriever", ef_labels.LABEL_RETRIEVAL),
            supported_job_types=[SupportedJobTypes.RETRIEVER],
            optional_params=retriever_common_optional_params,
        ),
        SystemMetric(
            type=MetricType.SYSTEM_RETRIEVER,
            name="retriever-bing",
            description="Binary Gain - cumulative gain using binary relevance.",
            labels=ef_labels.new_labels("retriever", ef_labels.LABEL_RETRIEVAL),
            supported_job_types=[SupportedJobTypes.RETRIEVER],
            optional_params=retriever_common_optional_params,
        ),
        SystemMetric(
            type=MetricType.SYSTEM_RETRIEVER,
            name="retriever-g",
            description="Gain - cumulative gain using graded relevance.",
            labels=ef_labels.new_labels("retriever", ef_labels.LABEL_RETRIEVAL),
            supported_job_types=[SupportedJobTypes.RETRIEVER],
            optional_params=retriever_common_optional_params,
        ),
        SystemMetric(
            type=MetricType.SYSTEM_RETRIEVER,
            name="retriever-rndcg",
            description="Rank-biased NDCG - NDCG variant with rank-based weighting.",
            labels=ef_labels.new_labels("retriever", ef_labels.LABEL_RETRIEVAL),
            supported_job_types=[SupportedJobTypes.RETRIEVER],
            optional_params=retriever_common_optional_params,
        ),
        SystemMetric(
            type=MetricType.SYSTEM_RETRIEVER,
            name="retriever-11pt-avg",
            description="11-point interpolated average precision - precision averaged at 11 recall levels.",
            labels=ef_labels.new_labels("retriever", ef_labels.LABEL_RETRIEVAL),
            supported_job_types=[SupportedJobTypes.RETRIEVER],
            optional_params=retriever_common_optional_params,
        ),
        SystemMetric(
            type=MetricType.SYSTEM_RETRIEVER,
            name="retriever-set-p",
            description="Set-based Precision - precision calculated over unique documents.",
            labels=ef_labels.new_labels("retriever", ef_labels.LABEL_RETRIEVAL),
            supported_job_types=[SupportedJobTypes.RETRIEVER],
            optional_params=retriever_common_optional_params,
        ),
        SystemMetric(
            type=MetricType.SYSTEM_RETRIEVER,
            name="retriever-set-map",
            description="Set-based Mean Average Precision - MAP calculated over unique documents.",
            labels=ef_labels.new_labels("retriever", ef_labels.LABEL_RETRIEVAL),
            supported_job_types=[SupportedJobTypes.RETRIEVER],
            optional_params=retriever_common_optional_params,
        ),
        SystemMetric(
            type=MetricType.SYSTEM_RETRIEVER,
            name="retriever-set-recall",
            description="Set-based Recall - recall calculated over unique documents.",
            labels=ef_labels.new_labels("retriever", ef_labels.LABEL_RETRIEVAL),
            supported_job_types=[SupportedJobTypes.RETRIEVER],
            optional_params=retriever_common_optional_params,
        ),
        SystemMetric(
            type=MetricType.SYSTEM_RETRIEVER,
            name="retriever-set-relative-p",
            description="Set-based Relative Precision - relative precision over unique documents.",
            labels=ef_labels.new_labels("retriever", ef_labels.LABEL_RETRIEVAL),
            supported_job_types=[SupportedJobTypes.RETRIEVER],
            optional_params=retriever_common_optional_params,
        ),
        SystemMetric(
            type=MetricType.SYSTEM_RETRIEVER,
            name="retriever-set-f",
            description="Set-based F-measure - harmonic mean of precision and recall over unique documents.",
            labels=ef_labels.new_labels("retriever", ef_labels.LABEL_RETRIEVAL),
            supported_job_types=[SupportedJobTypes.RETRIEVER],
            optional_params=retriever_common_optional_params,
        ),
        # Cutoff-based metrics - common cutoff values (5, 10, 20, 100)
        SystemMetric(
            type=MetricType.SYSTEM_RETRIEVER,
            name="retriever-p-5",
            description="Precision at 5 - the fraction of the top 5 retrieved documents that are relevant.",
            labels=ef_labels.new_labels("retriever", ef_labels.LABEL_RETRIEVAL),
            supported_job_types=[SupportedJobTypes.RETRIEVER],
            optional_params=retriever_common_optional_params,
        ),
        SystemMetric(
            type=MetricType.SYSTEM_RETRIEVER,
            name="retriever-p-10",
            description="Precision at 10 - the fraction of the top 10 retrieved documents that are relevant.",
            labels=ef_labels.new_labels("retriever", ef_labels.LABEL_RETRIEVAL),
            supported_job_types=[SupportedJobTypes.RETRIEVER],
            optional_params=retriever_common_optional_params,
        ),
        SystemMetric(
            type=MetricType.SYSTEM_RETRIEVER,
            name="retriever-p-20",
            description="Precision at 20 - the fraction of the top 20 retrieved documents that are relevant.",
            labels=ef_labels.new_labels("retriever", ef_labels.LABEL_RETRIEVAL),
            supported_job_types=[SupportedJobTypes.RETRIEVER],
            optional_params=retriever_common_optional_params,
        ),
        SystemMetric(
            type=MetricType.SYSTEM_RETRIEVER,
            name="retriever-p-100",
            description="Precision at 100 - the fraction of the top 100 retrieved documents that are relevant.",
            labels=ef_labels.new_labels("retriever", ef_labels.LABEL_RETRIEVAL),
            supported_job_types=[SupportedJobTypes.RETRIEVER],
            optional_params=retriever_common_optional_params,
        ),
        SystemMetric(
            type=MetricType.SYSTEM_RETRIEVER,
            name="retriever-recall-5",
            description="Recall at 5 - the fraction of relevant documents retrieved in the top 5 results.",
            labels=ef_labels.new_labels("retriever", ef_labels.LABEL_RETRIEVAL),
            supported_job_types=[SupportedJobTypes.RETRIEVER],
            optional_params=retriever_common_optional_params,
        ),
        SystemMetric(
            type=MetricType.SYSTEM_RETRIEVER,
            name="retriever-recall-10",
            description="Recall at 10 - the fraction of relevant documents retrieved in the top 10 results.",
            labels=ef_labels.new_labels("retriever", ef_labels.LABEL_RETRIEVAL),
            supported_job_types=[SupportedJobTypes.RETRIEVER],
            optional_params=retriever_common_optional_params,
        ),
        SystemMetric(
            type=MetricType.SYSTEM_RETRIEVER,
            name="retriever-recall-20",
            description="Recall at 20 - the fraction of relevant documents retrieved in the top 20 results.",
            labels=ef_labels.new_labels("retriever", ef_labels.LABEL_RETRIEVAL),
            supported_job_types=[SupportedJobTypes.RETRIEVER],
            optional_params=retriever_common_optional_params,
        ),
        SystemMetric(
            type=MetricType.SYSTEM_RETRIEVER,
            name="retriever-recall-100",
            description="Recall at 100 - the fraction of relevant documents retrieved in the top 100 results.",
            labels=ef_labels.new_labels("retriever", ef_labels.LABEL_RETRIEVAL),
            supported_job_types=[SupportedJobTypes.RETRIEVER],
            optional_params=retriever_common_optional_params,
        ),
        SystemMetric(
            type=MetricType.SYSTEM_RETRIEVER,
            name="retriever-ndcg-cut-5",
            description="NDCG at cutoff 5 - Normalized Discounted Cumulative Gain for top 5 results.",
            labels=ef_labels.new_labels("retriever", ef_labels.LABEL_RETRIEVAL),
            supported_job_types=[SupportedJobTypes.RETRIEVER],
            optional_params=retriever_common_optional_params,
        ),
        SystemMetric(
            type=MetricType.SYSTEM_RETRIEVER,
            name="retriever-ndcg-cut-10",
            description="NDCG at cutoff 10 - Normalized Discounted Cumulative Gain for top 10 results.",
            labels=ef_labels.new_labels("retriever", ef_labels.LABEL_RETRIEVAL),
            supported_job_types=[SupportedJobTypes.RETRIEVER],
            optional_params=retriever_common_optional_params,
        ),
        SystemMetric(
            type=MetricType.SYSTEM_RETRIEVER,
            name="retriever-ndcg-cut-20",
            description="NDCG at cutoff 20 - Normalized Discounted Cumulative Gain for top 20 results.",
            labels=ef_labels.new_labels("retriever", ef_labels.LABEL_RETRIEVAL),
            supported_job_types=[SupportedJobTypes.RETRIEVER],
            optional_params=retriever_common_optional_params,
        ),
        SystemMetric(
            type=MetricType.SYSTEM_RETRIEVER,
            name="retriever-ndcg-cut-100",
            description="NDCG at cutoff 100 - Normalized Discounted Cumulative Gain for top 100 results.",
            labels=ef_labels.new_labels("retriever", ef_labels.LABEL_RETRIEVAL),
            supported_job_types=[SupportedJobTypes.RETRIEVER],
            optional_params=retriever_common_optional_params,
        ),
        SystemMetric(
            type=MetricType.SYSTEM_RETRIEVER,
            name="retriever-map-cut-5",
            description="Mean Average Precision at cutoff 5 - MAP calculated for top 5 results.",
            labels=ef_labels.new_labels("retriever", ef_labels.LABEL_RETRIEVAL),
            supported_job_types=[SupportedJobTypes.RETRIEVER],
            optional_params=retriever_common_optional_params,
        ),
        SystemMetric(
            type=MetricType.SYSTEM_RETRIEVER,
            name="retriever-map-cut-10",
            description="Mean Average Precision at cutoff 10 - MAP calculated for top 10 results.",
            labels=ef_labels.new_labels("retriever", ef_labels.LABEL_RETRIEVAL),
            supported_job_types=[SupportedJobTypes.RETRIEVER],
            optional_params=retriever_common_optional_params,
        ),
        SystemMetric(
            type=MetricType.SYSTEM_RETRIEVER,
            name="retriever-map-cut-20",
            description="Mean Average Precision at cutoff 20 - MAP calculated for top 20 results.",
            labels=ef_labels.new_labels("retriever", ef_labels.LABEL_RETRIEVAL),
            supported_job_types=[SupportedJobTypes.RETRIEVER],
            optional_params=retriever_common_optional_params,
        ),
        SystemMetric(
            type=MetricType.SYSTEM_RETRIEVER,
            name="retriever-map-cut-100",
            description="Mean Average Precision at cutoff 100 - MAP calculated for top 100 results.",
            labels=ef_labels.new_labels("retriever", ef_labels.LABEL_RETRIEVAL),
            supported_job_types=[SupportedJobTypes.RETRIEVER],
            optional_params=retriever_common_optional_params,
        ),
        SystemMetric(
            type=MetricType.SYSTEM_RETRIEVER,
            name="retriever-success-5",
            description="Success at 5 - whether at least one relevant document is in the top 5 results.",
            labels=ef_labels.new_labels("retriever", ef_labels.LABEL_RETRIEVAL),
            supported_job_types=[SupportedJobTypes.RETRIEVER],
            optional_params=retriever_common_optional_params,
        ),
        SystemMetric(
            type=MetricType.SYSTEM_RETRIEVER,
            name="retriever-success-10",
            description="Success at 10 - whether at least one relevant document is in the top 10 results.",
            labels=ef_labels.new_labels("retriever", ef_labels.LABEL_RETRIEVAL),
            supported_job_types=[SupportedJobTypes.RETRIEVER],
            optional_params=retriever_common_optional_params,
        ),
        SystemMetric(
            type=MetricType.SYSTEM_RETRIEVER,
            name="retriever-success-20",
            description="Success at 20 - whether at least one relevant document is in the top 20 results.",
            labels=ef_labels.new_labels("retriever", ef_labels.LABEL_RETRIEVAL),
            supported_job_types=[SupportedJobTypes.RETRIEVER],
            optional_params=retriever_common_optional_params,
        ),
        SystemMetric(
            type=MetricType.SYSTEM_RETRIEVER,
            name="retriever-success-100",
            description="Success at 100 - whether at least one relevant document is in the top 100 results.",
            labels=ef_labels.new_labels("retriever", ef_labels.LABEL_RETRIEVAL),
            supported_job_types=[SupportedJobTypes.RETRIEVER],
            optional_params=retriever_common_optional_params,
        ),
    ]
