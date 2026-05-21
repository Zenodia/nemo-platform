# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

from unittest.mock import patch

import pytest
from nemo_evaluator_sdk.values import DatasetRows
from nmp.common.files.storage_config import HuggingfaceStorageConfig
from nmp.evaluator.app.evalfactory.convert import _convert_config_params, get_dataset_config
from nmp.evaluator.app.values import BuiltInDataset, Fileset, FilesetRef, MetricOfflineJob


def make_hf_storage_config() -> HuggingfaceStorageConfig:
    """Create a test HuggingfaceStorageConfig."""
    return HuggingfaceStorageConfig(
        repo_id="test-org/test-repo",
        repo_type="dataset",
    )


class TestGetDatasetConfig:
    def test_builtin_ragas_amnesty_qa_returns_special_config(self):
        """Test that ragas/amnesty_qa returns the special HuggingFace config."""
        dataset = BuiltInDataset(root="ragas/amnesty_qa")
        result = get_dataset_config(dataset)

        assert result.format == "ragas"
        assert result.path == "explodinggradients/amnesty_qa"
        assert result.dataset_name == "english_v2"
        assert result.split == "eval"

    def test_builtin_beir_dataset_returns_format_and_name(self):
        """Test that BEIR datasets return format and name from the dataset."""
        dataset = BuiltInDataset(root="beir/fiqa")
        result = get_dataset_config(dataset)

        assert result.format == "beir"
        assert result.path == "fiqa"

    def test_inline_dataset_uses_local_path(self):
        """Test that DatasetRows resolves to local path with default filename."""
        dataset = DatasetRows(rows=[{"a": 1}])
        result = get_dataset_config(dataset, output_dir="/data/output")

        assert result.path == "/data/output/dataset.json"
        assert result.format is None

    def test_inline_dataset_with_format(self):
        """Test that DatasetRows with dataset_format sets format."""
        dataset = DatasetRows(rows=[{"a": 1}])
        result = get_dataset_config(dataset, dataset_format="ragas", output_dir="/data/output")

        assert result.path == "/data/output/dataset.json"
        assert result.format == "ragas"

    def test_fileset_ref_uses_local_path(self):
        """Test that FilesetRef resolves to local path."""
        dataset = FilesetRef(root="workspace/fileset-name")
        result = get_dataset_config(dataset, output_dir="/data/output")

        assert result.path == "/data/output/workspace/fileset-name"
        assert result.format is None

    def test_fileset_ref_with_format(self):
        """Test that FilesetRef with dataset_format sets format."""
        dataset = FilesetRef(root="workspace/fileset-name")
        result = get_dataset_config(dataset, dataset_format="beir", output_dir="/data/output")

        assert result.path == "/data/output/workspace/fileset-name"
        assert result.format == "beir"

    def test_inline_fileset_uses_local_path(self):
        """Test that Fileset resolves to local path."""
        dataset = Fileset(storage=make_hf_storage_config(), path="data/file.json")
        result = get_dataset_config(dataset, output_dir="/data/output")

        assert result.path == "/data/output/data/file.json"
        assert result.format is None

    def test_inline_fileset_with_none_path(self):
        """Test that Fileset with None path returns output_dir."""
        dataset = Fileset(storage=make_hf_storage_config(), path=None)
        result = get_dataset_config(dataset, output_dir="/data/output")

        assert result.path == "/data/output"

    def test_inline_fileset_with_format(self):
        """Test that Fileset with dataset_format sets format."""
        dataset = Fileset(storage=make_hf_storage_config(), path="data/file.json")
        result = get_dataset_config(dataset, dataset_format="ragas", output_dir="/data/output")

        assert result.path == "/data/output/data/file.json"
        assert result.format == "ragas"

    def test_non_builtin_requires_output_dir(self):
        """Test that non-BuiltInDataset types raise when output_dir is missing."""
        dataset = DatasetRows(rows=[{"a": 1}])

        with pytest.raises(ValueError, match="output_dir is required"):
            get_dataset_config(dataset, output_dir=None)

    def test_builtin_does_not_require_output_dir(self):
        """Test that BuiltInDataset does not require output_dir."""
        dataset = BuiltInDataset(root="beir/fiqa")
        # Should not raise
        result = get_dataset_config(dataset, output_dir=None)

        assert result.format == "beir"
        assert result.path == "fiqa"


class TestConvertConfigParams:
    """Tests for _convert_config_params function."""

    def _make_offline_job(self, dataset) -> MetricOfflineJob:
        """Create a minimal MetricOfflineJob for testing."""
        return MetricOfflineJob.model_validate(
            {
                "metric": {
                    "name": "test-metric",
                    "type": "system",
                },
                "dataset": dataset,
            }
        )

    @patch("nmp.evaluator.app.evalfactory.convert.settings")
    def test_offline_job_with_inline_dataset_sets_dataset_path(self, mock_settings):
        """Test that extra_params['dataset_path'] is set for DatasetRows."""
        mock_settings.jobs.dataset_dir = "/jobs/datasets"

        dataset = DatasetRows(rows=[{"a": 1}])
        job = self._make_offline_job(dataset.model_dump())

        result = _convert_config_params(job)

        assert result.extra is not None
        assert "dataset_path" in result.extra
        assert result.extra["dataset_path"] == "/jobs/datasets/dataset.json"

    @patch("nmp.evaluator.app.evalfactory.convert.settings")
    def test_offline_job_with_fileset_ref_sets_dataset_path(self, mock_settings):
        """Test that extra_params['dataset_path'] is set for FilesetRef with full path."""
        mock_settings.jobs.dataset_dir = "/jobs/datasets"

        dataset = FilesetRef(root="default/my-fileset/data.jsonl")
        job = self._make_offline_job(dataset.root)

        result = _convert_config_params(job)

        assert result.extra is not None
        assert "dataset_path" in result.extra
        assert result.extra["dataset_path"] == "/jobs/datasets/default/my-fileset/data.jsonl"

    @patch("nmp.evaluator.app.evalfactory.convert.settings")
    def test_offline_job_with_fileset_ref_directory_sets_dataset_path(self, mock_settings):
        """Test that extra_params['dataset_path'] is set for FilesetRef directory."""
        mock_settings.jobs.dataset_dir = "/jobs/datasets"

        dataset = FilesetRef(root="workspace/fileset-name")
        job = self._make_offline_job(dataset.root)

        result = _convert_config_params(job)

        assert result.extra is not None
        assert "dataset_path" in result.extra
        assert result.extra["dataset_path"] == "/jobs/datasets/workspace/fileset-name"

    @patch("nmp.evaluator.app.evalfactory.convert.settings")
    def test_metric_params_included_in_extra(self, mock_settings):
        """Test that metric_params are included in extra_params."""
        mock_settings.jobs.dataset_dir = "/jobs/datasets"

        dataset = DatasetRows(rows=[{"a": 1}])
        job = self._make_offline_job(dataset.model_dump())
        job.metric_params["custom_param"] = "custom_value"

        result = _convert_config_params(job)

        assert result.extra is not None
        assert "custom_param" in result.extra
        assert result.extra["custom_param"] == "custom_value"
        assert "dataset_path" in result.extra
