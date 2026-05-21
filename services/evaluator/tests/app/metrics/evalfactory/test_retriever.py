# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import os
from typing import Literal
from unittest import mock

import pytest
from nemo_evaluator_sdk.values import SecretRef, SupportedJobTypes
from nmp.evaluator import constants
from nmp.evaluator.app.evalfactory.retriever import RetrieverHandler
from nmp.evaluator.app.values import MetricOfflineJob, MetricRetrieverJob
from nmp.evaluator.config import EvaluatorSettings, settings


class TestRetrieverHandler:
    handler = RetrieverHandler()

    def _fileset_dataset(self, path: str = "fiqa") -> dict:
        """Create an Fileset dataset configuration (external dataset)."""
        return {
            "path": path,
            "storage": {"type": "huggingface", "repo_id": "BeIR/fiqa", "repo_type": "dataset"},
        }

    def _inline_dataset(self, name: str = "fiqa") -> dict:
        """Create an DatasetRows dataset configuration (local/BEIR dataset)."""
        # rows is required by DatasetRows schema - provide dummy row for BEIR test cases
        return {"rows": [{"input": "placeholder"}]}

    def _test_job_basic(self) -> MetricRetrieverJob:
        """Job for basic retriever metric (no secrets)."""
        metric = next(m for m in RetrieverHandler._system_metrics if m.name == "retriever-map")
        return MetricRetrieverJob.model_validate(
            {
                "metric": metric,
                "retriever_pipeline": {
                    "embeddings_model": {"url": "http://embedding.test", "name": "my/embedding-model"},
                },
                "dataset": self._fileset_dataset(),
                "metric_params": {},
            }
        )

    def _test_job_with_secrets(self) -> MetricRetrieverJob:
        """Job for retriever metric with secrets."""
        metric = next(m for m in RetrieverHandler._system_metrics if m.name == "retriever-ndcg")
        return MetricRetrieverJob.model_validate(
            {
                "metric": metric,
                "retriever_pipeline": {
                    "embeddings_model": {
                        "url": "http://embedding.test",
                        "name": "my/embedding-model",
                        "api_key_secret": "embedding-api-secret",
                    },
                },
                "dataset": self._fileset_dataset(),
                "metric_params": {},
            }
        )

    @mock.patch.dict(
        os.environ,
        {
            "NMP_EVALUATOR_EVALFACTORY_RAG_RETRIEVER": "my-container",
        },
    )
    def test_docker_image(self):
        assert RetrieverHandler.docker_image() == settings.evalfactory.rag_retriever, (
            "settings is loaded before env override, expect loaded defaults"
        )
        assert EvaluatorSettings().evalfactory.rag_retriever == "my-container", "failed environment variable override"

    def test_system_metrics_count(self):
        # 38 total retriever metrics (18 fixed + 20 cutoff-based)
        assert len(RetrieverHandler.system_metrics()) == 38

    def test_all_metrics_are_retriever_only(self):
        for metric in RetrieverHandler.system_metrics():
            assert metric.labels.get("eval_harness") == "retriever"
            assert metric.supported_job_types == [SupportedJobTypes.RETRIEVER.value]

    def test_all_metrics_no_required_params(self):
        """Retriever metrics don't require API keys by default."""
        for metric in RetrieverHandler._system_metrics:
            assert len(metric.required_params) == 0, f"{metric.name} should not have required params"

    def test_all_metrics_have_optional_params(self):
        """All retriever metrics should have common optional params."""
        for metric in RetrieverHandler._system_metrics:
            param_names = [p.name for p in metric.optional_params]
            assert "dataset_format" in param_names, f"{metric.name} missing dataset_format param"
            assert "top_k" in param_names, f"{metric.name} missing top_k param"

    def test_secrets_no_api_keys(self):
        secrets = self.handler.metric_job_secrets(self._test_job_basic())
        assert len(secrets) == 0

    def test_secrets_with_api_keys(self):
        secrets = self.handler.metric_job_secrets(self._test_job_with_secrets())
        assert secrets == {
            "QUERY_API_KEY": SecretRef(root="embedding-api-secret"),
            "INDEX_API_KEY": SecretRef(root="embedding-api-secret"),
        }

    def test_unsupported_offline_job(self):
        """Retriever metrics don't support offline job type."""
        metric = next(m for m in RetrieverHandler._system_metrics if m.name == "retriever-map")
        job = MetricOfflineJob.model_validate(
            {
                "metric": metric,
                "dataset": {"rows": [{"input": "test"}]},
                "metric_params": {},
            }
        )
        with pytest.raises(ValueError, match="metric does not support offline evaluations"):
            self.handler.augment_metric_job(job, "output_dir")

    def test_augment_metric_job_basic_metric(self):
        ef_job = self.handler.augment_metric_job(self._test_job_basic(), "output_dir")
        assert ef_job.config is not None
        assert ef_job.target is not None
        assert ef_job.target.api_endpoint is not None
        assert ef_job.config.params is not None
        assert ef_job.config.params.extra is not None

        assert ef_job.config.type == "retriever"
        assert ef_job.target.api_endpoint.type == "embedding"
        assert ef_job.output_dir == "output_dir"
        # Metric is in the tasks config
        assert "map" in ef_job.config.params.extra["tasks"]["retriever"]["metrics"]

    def test_augment_metric_job_basic_metric_sets_placeholder_embedder_api_key(self):
        """Embedder API key must be explicit to avoid strict NVIDIA_API_KEY env lookup."""
        ef_job = self.handler.augment_metric_job(self._test_job_basic(), "output_dir")
        assert ef_job.config is not None
        assert ef_job.config.params is not None
        assert ef_job.config.params.extra is not None

        pipeline = ef_job.config.params.extra["pipeline"]
        # api_key_name is not supported by Retriever 26.01
        assert pipeline["query_embedding_model"]["api_endpoint"]["api_key"] == constants.PLACEHOLDER_INFERENCE_API_KEY
        # api_key_name is not supported by Retriever 26.01
        assert pipeline["index_embedding_model"]["api_endpoint"]["api_key"] == constants.PLACEHOLDER_INFERENCE_API_KEY

    def test_augment_metric_job_cutoff_metric(self):
        """Test cutoff-based metric name conversion."""
        metric = next(m for m in RetrieverHandler._system_metrics if m.name == "retriever-ndcg-cut-10")
        job = MetricRetrieverJob.model_validate(
            {
                "metric": metric,
                "retriever_pipeline": {
                    "embeddings_model": {"url": "http://embedding.test", "name": "my/embedding-model"},
                },
                "dataset": self._fileset_dataset(),
                "metric_params": {},
            }
        )
        ef_job = self.handler.augment_metric_job(job, "output_dir")
        assert ef_job.config is not None
        assert ef_job.config.params is not None
        assert ef_job.config.params.extra is not None

        assert ef_job.config.type == "retriever"
        # Metric is in the tasks config with underscore format
        assert "ndcg_cut_10" in ef_job.config.params.extra["tasks"]["retriever"]["metrics"]

    def test_metric_name_conversion(self):
        """Metric names use dashes which are converted to underscores during augment_metric_job."""
        # Note: Some metric names may have been mutated by previous tests that called augment_metric_job
        for metric in RetrieverHandler._system_metrics:
            # Names should contain either dashes or underscores (if already converted), not mixed
            has_dash = "-" in metric.name
            has_underscore = "_" in metric.name
            # Either all dashes, all underscores, or single word (no separator)
            assert not (has_dash and has_underscore), f"Metric {metric.name} has mixed separators"

    def test_fixed_metrics_exist(self):
        """Verify all expected fixed metrics exist."""
        fixed_metric_names = RetrieverHandler._fixed_metrics
        # Normalize names (handle both dashes and underscores due to potential mutation from augment_metric_job)
        system_metric_names = [m.name.replace("_", "-") for m in RetrieverHandler._system_metrics]
        for name in fixed_metric_names:
            assert name in system_metric_names, f"Fixed metric {name} not found in system metrics"

    def test_cutoff_metrics_exist(self):
        """Verify cutoff-based metrics exist for common cutoff values."""
        cutoff_values = [5, 10, 20, 100]
        cutoff_metric_prefixes = [
            "retriever-p-",
            "retriever-recall-",
            "retriever-ndcg-cut-",
            "retriever-map-cut-",
            "retriever-success-",
        ]

        # Normalize names (handle both dashes and underscores due to potential mutation from augment_metric_job)
        system_metric_names = [m.name.replace("_", "-") for m in RetrieverHandler._system_metrics]
        for prefix in cutoff_metric_prefixes:
            for cutoff in cutoff_values:
                expected_name = f"{prefix}{cutoff}"
                assert expected_name in system_metric_names, f"Cutoff metric {expected_name} not found"

    def test_augment_metric_job_generates_evalfactory_config_structure(self):
        """Verify the generated eval factory config matches expected structure."""
        metric = next(m for m in RetrieverHandler._system_metrics if m.name == "retriever-recall-5")
        job = MetricRetrieverJob.model_validate(
            {
                "metric": metric,
                "retriever_pipeline": {
                    "embeddings_model": {
                        "url": "https://integrate.api.nvidia.com/v1",
                        "name": "nvidia/nv-embedqa-e5-v5",
                        "api_key_secret": "query_embed_secret",
                    },
                },
                "dataset": self._fileset_dataset("fiqa"),
                "metric_params": {"top_k": 10, "dataset_format": "beir"},
            }
        )

        ef_job = self.handler.augment_metric_job(job, "/output")
        assert ef_job.config is not None

        # Validate target structure
        assert ef_job.target is not None
        assert ef_job.target.api_endpoint is not None
        assert ef_job.target.api_endpoint.type == "embedding"

        # Validate config structure
        assert ef_job.config.type == "retriever"
        assert ef_job.config.params is not None
        assert ef_job.config.params.extra is not None

        extra = ef_job.config.params.extra

        # Validate tasks structure
        assert "tasks" in extra
        assert "retriever" in extra["tasks"]
        task = extra["tasks"]["retriever"]
        assert task["type"] == "beir"
        assert "metrics" in task
        assert "recall_5" in task["metrics"]
        assert task["metrics"]["recall_5"]["type"] == "pytrec_eval"

        # Validate dataset in task config - Fileset uses output_dir + path
        assert "dataset" in task
        assert task["dataset"]["format"] == "beir"
        assert task["dataset"]["path"] == f"{settings.jobs.dataset_dir}/fiqa"

        # Validate pipeline structure
        assert "pipeline" in extra
        pipeline = extra["pipeline"]

        # Validate query_embedding_model
        assert "query_embedding_model" in pipeline
        query_model = pipeline["query_embedding_model"]
        assert query_model["api_endpoint"]["url"] == "https://integrate.api.nvidia.com/v1"
        assert query_model["api_endpoint"]["model_id"] == "nvidia/nv-embedqa-e5-v5"
        # api_key_name is not supported by Retriever 26.01
        assert query_model["api_endpoint"]["api_key"] == "$QUERY_API_KEY"

        # Validate index_embedding_model
        assert "index_embedding_model" in pipeline
        index_model = pipeline["index_embedding_model"]
        assert index_model["api_endpoint"]["url"] == "https://integrate.api.nvidia.com/v1"
        assert index_model["api_endpoint"]["model_id"] == "nvidia/nv-embedqa-e5-v5"
        # api_key_name is not supported by Retriever 26.01
        assert index_model["api_endpoint"]["api_key"] == "$INDEX_API_KEY"

        # Validate reranker_model is not present
        assert "reranker_model" not in pipeline or pipeline.get("reranker_model") is None

        # Validate top_k
        assert pipeline["top_k"] == 10

        # Validate pipeline params (milvus config, yaml files)
        assert "params" in pipeline
        params = pipeline["params"]
        assert "milvus_collection_name" in params
        assert "index_pipeline_yaml_file" in params
        assert "query_pipeline_yaml_file" in params
        assert "component_inputs_template" in params
        # Dense only yaml files should be used
        assert "dense_only" in params["index_pipeline_yaml_file"]
        assert "dense_only" in params["query_pipeline_yaml_file"]
        assert "ranker" not in params["component_inputs_template"]

    def test_augment_metric_job_without_reranker(self):
        """Verify config structure without reranker uses dense_only yaml files."""
        metric = next(m for m in RetrieverHandler._system_metrics if m.name == "retriever-map")
        job = MetricRetrieverJob.model_validate(
            {
                "metric": metric,
                "retriever_pipeline": {
                    "embeddings_model": {
                        "url": "https://integrate.api.nvidia.com/v1",
                        "name": "nvidia/nv-embedqa-e5-v5",
                    },
                },
                "dataset": self._fileset_dataset("fiqa"),
                "metric_params": {"top_k": 5},
            }
        )

        ef_job = self.handler.augment_metric_job(job, "/output")
        assert ef_job.config is not None
        assert ef_job.config.params is not None
        assert ef_job.config.params.extra is not None
        extra = ef_job.config.params.extra
        pipeline = extra["pipeline"]

        # No reranker_model in pipeline
        assert "reranker_model" not in pipeline or pipeline.get("reranker_model") is None

        # Dense only yaml files should be used
        assert "dense_only" in pipeline["params"]["index_pipeline_yaml_file"]
        assert "dense_only" in pipeline["params"]["query_pipeline_yaml_file"]
        assert "ranker" not in pipeline["params"]["component_inputs_template"]

        # top_k from metric_params
        assert pipeline["top_k"] == 5

    def test_builtin_dataset_invalid_rejected_by_type_system(self):
        """Verify that invalid BuiltInDataset identifiers are rejected by Pydantic validation."""
        from nmp.evaluator.app.values import BuiltInDataset
        from pydantic import ValidationError

        # Invalid dataset ID should be rejected by Pydantic's Literal validation
        with pytest.raises(ValidationError):
            BuiltInDataset(root="invalid-dataset-name")  # ty: ignore[invalid-argument-type]

    def test_builtin_dataset_all_known_datasets(self):
        """Verify that all known BEIR academic datasets work with BuiltInDataset."""
        from nmp.evaluator.app.values import BuiltInDataset

        metric = next(m for m in RetrieverHandler._system_metrics if m.name == "retriever-map")

        # Test a few representative BEIR datasets using BuiltInDataset
        test_datasets: list[Literal["beir/fiqa", "beir/nfcorpus", "beir/msmarco", "beir/hotpotqa"]] = [
            "beir/fiqa",
            "beir/nfcorpus",
            "beir/msmarco",
            "beir/hotpotqa",
        ]
        for dataset_id in test_datasets:
            builtin_dataset = BuiltInDataset(root=dataset_id)
            job = MetricRetrieverJob.model_validate(
                {
                    "metric": metric,
                    "retriever_pipeline": {
                        "embeddings_model": {"url": "http://embedding.test", "name": "my/embedding-model"},
                    },
                    "dataset": builtin_dataset,
                    "metric_params": {"dataset_format": "beir"},
                }
            )

            ef_job = self.handler.augment_metric_job(job, "/output")
            assert ef_job.config is not None
            assert ef_job.config.params is not None
            assert ef_job.config.params.extra is not None
            task = ef_job.config.params.extra["tasks"]["retriever"]
            # BuiltInDataset uses name directly (e.g., "fiqa" from "beir/fiqa")
            assert task["dataset"]["path"] == builtin_dataset.name
            assert task["dataset"]["format"] == "beir"

    def test_inline_dataset_uses_output_dir_json(self):
        """Verify that DatasetRows outputs to output_dir/dataset.json."""
        metric = next(m for m in RetrieverHandler._system_metrics if m.name == "retriever-map")
        job = MetricRetrieverJob.model_validate(
            {
                "metric": metric,
                "retriever_pipeline": {
                    "embeddings_model": {"url": "http://embedding.test", "name": "my/embedding-model"},
                },
                "dataset": self._inline_dataset("custom-dataset"),
                "metric_params": {"dataset_format": "custom"},
            }
        )

        ef_job = self.handler.augment_metric_job(job, "/output")
        assert ef_job.config is not None
        assert ef_job.config.params is not None
        assert ef_job.config.params.extra is not None
        task = ef_job.config.params.extra["tasks"]["retriever"]
        # DatasetRows is written to output_dir/dataset.json
        assert task["dataset"]["path"] == f"{settings.jobs.dataset_dir}/dataset.json"
        assert task["dataset"]["format"] == "custom"

    def test_fileset_dataset_uses_output_dir(self):
        """Verify that Fileset datasets use output_dir + path."""
        metric = next(m for m in RetrieverHandler._system_metrics if m.name == "retriever-map")
        job = MetricRetrieverJob.model_validate(
            {
                "metric": metric,
                "retriever_pipeline": {
                    "embeddings_model": {"url": "http://embedding.test", "name": "my/embedding-model"},
                },
                "dataset": self._fileset_dataset("my-external-dataset"),
                "metric_params": {"dataset_format": "beir"},
            }
        )

        ef_job = self.handler.augment_metric_job(job, "/output")
        assert ef_job.config is not None
        assert ef_job.config.params is not None
        assert ef_job.config.params.extra is not None
        task = ef_job.config.params.extra["tasks"]["retriever"]
        assert task["dataset"]["path"] == f"{settings.jobs.dataset_dir}/my-external-dataset"  # JOB_DATASET_DIR + path
        assert task["dataset"]["format"] == "beir"
