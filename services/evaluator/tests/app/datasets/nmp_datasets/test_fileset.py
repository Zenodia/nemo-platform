# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import asyncio
import json
import sys
from pathlib import Path
from typing import cast
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from nemo_evaluator_sdk.values import DatasetRows
from nmp.common.files.storage_config import HuggingfaceStorageConfig
from nmp.evaluator.app.datasets.nmp_datasets.fileset import (
    _download_fileset_ref,
    _download_fileset_ref_sync,
    _download_inline_dataset,
    _download_inline_fileset,
    _download_inline_fileset_sync,
    _generate_fileset_name,
    create_fileset,
    dataset_exists,
    download_dataset,
    download_dataset_sync,
    get_local_dataset_path,
    normalize_fileset_path,
)
from nmp.evaluator.app.values import Fileset, FilesetRef

# Mock fileset_filesystem before importing the module under test
mock_fileset_filesystem = MagicMock()
sys.modules["fileset_filesystem"] = mock_fileset_filesystem


def make_hf_storage_config() -> HuggingfaceStorageConfig:
    """Create a test HuggingfaceStorageConfig."""
    return HuggingfaceStorageConfig(
        repo_id="test-org/test-repo",
        repo_type="dataset",
    )


class TestNormalizeFilesetPath:
    @pytest.mark.parametrize(
        ("path", "expected"),
        [
            # `#` as a separator
            ("workspace#fileset-name", "workspace/fileset-name"),
            # No fragment
            ("workspace/fileset-name", "workspace/fileset-name"),
            # Glob fragments should not become local paths with wildcards
            ("workspace/fileset-name#*.jsonl", "workspace/fileset-name"),
            ("workspace/fileset-name#**/*.jsonl", "workspace/fileset-name"),
            # Glob fragment keeps stable prefix directory, if any
            ("workspace/fileset-name#data/*.jsonl", "workspace/fileset-name/data"),
            # Specific file fragments are appended normally
            ("workspace/fileset-name#data/train.jsonl", "workspace/fileset-name/data/train.jsonl"),
            # Empty string
            ("", ""),
        ],
    )
    def test_normalize_fileset_path(self, path: str, expected: str):
        assert normalize_fileset_path(path) == expected


class TestGetLocalDatasetPath:
    def test_inline_dataset_returns_output_dir_with_default_filename(self):
        """Test that DatasetRows returns output_dir/dataset.json."""
        dataset = DatasetRows(rows=[{"a": 1}])
        result = get_local_dataset_path(dataset, "/data/output")
        assert result == "/data/output/dataset.json"

    def test_inline_dataset_with_custom_filename(self):
        """Test that DatasetRows uses custom inline_filename."""
        dataset = DatasetRows(rows=[{"a": 1}])
        result = get_local_dataset_path(dataset, "/data/output", inline_filename="custom.json")
        assert result == "/data/output/custom.json"

    def test_fileset_ref_normalizes_hash_separator(self):
        """Test that FilesetRef path with # is normalized to /."""
        dataset = FilesetRef(root="workspace#fileset-name")
        result = get_local_dataset_path(dataset, "/data/output")
        assert result == "/data/output/workspace/fileset-name"

    def test_fileset_ref_with_slash_separator(self):
        """Test that FilesetRef with / separator works correctly."""
        dataset = FilesetRef(root="workspace/fileset-name")
        result = get_local_dataset_path(dataset, "/data/output")
        assert result == "/data/output/workspace/fileset-name"

    def test_fileset_ref_with_subpath(self):
        """Test that FilesetRef with subpath works correctly."""
        dataset = FilesetRef(root="workspace/fileset-name/subdir/file.json")
        result = get_local_dataset_path(dataset, "/data/output")
        assert result == "/data/output/workspace/fileset-name/subdir/file.json"

    def test_fileset_ref_with_glob_fragment_drops_pattern(self):
        """Glob fragments should resolve to a stable directory path."""
        dataset = FilesetRef(root="workspace/fileset-name#*.jsonl")
        result = get_local_dataset_path(dataset, "/data/output")
        assert result == "/data/output/workspace/fileset-name"

    def test_fileset_ref_with_glob_fragment_keeps_prefix_dir(self):
        """Glob fragments with a stable dir prefix keep that prefix."""
        dataset = FilesetRef(root="workspace/fileset-name#data/*.jsonl")
        result = get_local_dataset_path(dataset, "/data/output")
        assert result == "/data/output/workspace/fileset-name/data"

    def test_inline_fileset_with_path(self):
        """Test that Fileset with path joins correctly."""
        dataset = Fileset(storage=make_hf_storage_config(), path="data/file.json")
        result = get_local_dataset_path(dataset, "/data/output")
        assert result == "/data/output/data/file.json"

    def test_inline_fileset_with_none_path(self):
        """Test that Fileset with None path returns output_dir."""
        dataset = Fileset(storage=make_hf_storage_config(), path=None)
        result = get_local_dataset_path(dataset, "/data/output")
        assert result == "/data/output"

    def test_raises_error_when_output_dir_is_none(self):
        """Test that ValueError is raised when output_dir is None."""
        dataset = DatasetRows(rows=[{"a": 1}])
        with pytest.raises(ValueError, match="output_dir is required"):
            get_local_dataset_path(dataset, None)

    def test_raises_error_when_output_dir_is_empty(self):
        """Test that ValueError is raised when output_dir is empty string."""
        dataset = DatasetRows(rows=[{"a": 1}])
        with pytest.raises(ValueError, match="output_dir is required"):
            get_local_dataset_path(dataset, "")

    def test_raises_error_for_unsupported_dataset_type(self):
        """Test that ValueError is raised for unsupported dataset type."""
        unsupported_dataset = cast(FilesetRef | Fileset | DatasetRows, "not-a-dataset")
        with pytest.raises(ValueError, match="Unsupported dataset type"):
            get_local_dataset_path(unsupported_dataset, "/data/output")


class TestGenerateFilesetName:
    def test_generates_unique_names(self):
        """Test that _generate_fileset_name generates unique names."""
        names = {_generate_fileset_name() for _ in range(100)}
        assert len(names) == 100

    def test_name_format(self):
        """Test that _generate_fileset_name follows expected format."""
        name = _generate_fileset_name()
        assert name.startswith("fileset-")
        assert len(name) == len("fileset-") + 8


class TestCreateFileset:
    @pytest.mark.asyncio
    async def test_creates_and_deletes_fileset(self):
        """Test that create_fileset creates and then deletes the fileset."""
        mock_sdk = AsyncMock()
        mock_fileset = MagicMock()
        mock_fileset.name = "test-fileset"
        mock_fileset.workspace = "default"
        mock_sdk.files.filesets.create.return_value = mock_fileset

        async with create_fileset(mock_sdk, name="test-fileset", workspace="default") as fileset:
            assert fileset.name == "test-fileset"
            mock_sdk.files.filesets.create.assert_called_once_with(
                workspace="default",
                name="test-fileset",
                description="Test fileset",
            )

        mock_sdk.files.filesets.delete.assert_called_once_with("test-fileset", workspace="default")

    @pytest.mark.asyncio
    async def test_generates_name_if_not_provided(self):
        """Test that create_fileset generates a name if not provided."""
        mock_sdk = AsyncMock()
        mock_fileset = MagicMock()
        mock_sdk.files.filesets.create.return_value = mock_fileset

        async with create_fileset(mock_sdk, workspace="default"):
            call_args = mock_sdk.files.filesets.create.call_args
            assert call_args.kwargs["name"].startswith("fileset-")

    @pytest.mark.asyncio
    async def test_passes_kwargs_to_create(self):
        """Test that create_fileset passes additional kwargs to SDK create."""
        mock_sdk = AsyncMock()
        mock_fileset = MagicMock()
        mock_sdk.files.filesets.create.return_value = mock_fileset

        storage_config = {"type": "huggingface", "repo_id": "test/repo"}

        async with create_fileset(mock_sdk, name="test", storage=storage_config):
            call_args = mock_sdk.files.filesets.create.call_args
            assert call_args.kwargs["storage"] == storage_config

    @pytest.mark.asyncio
    async def test_cleanup_called_on_user_exception(self):
        """Test that cleanup is called even when user code raises an exception."""
        mock_sdk = AsyncMock()
        mock_fileset = MagicMock()
        mock_fileset.name = "test-fileset"
        mock_sdk.files.filesets.create.return_value = mock_fileset

        with pytest.raises(ValueError, match="User error"):
            async with create_fileset(mock_sdk, name="test-fileset", workspace="default"):
                raise ValueError("User error")

        # Cleanup should still be called despite the exception
        mock_sdk.files.filesets.delete.assert_called_once_with("test-fileset", workspace="default")

    @pytest.mark.asyncio
    async def test_cleanup_failure_logs_warning(self, caplog):
        """Test that cleanup failure is logged as warning and doesn't raise."""
        import logging

        caplog.set_level(logging.WARNING, logger="nmp.evaluator.app.datasets.nmp_datasets.fileset")

        mock_sdk = AsyncMock()
        mock_fileset = MagicMock()
        mock_fileset.name = "test-fileset"
        mock_sdk.files.filesets.create.return_value = mock_fileset
        mock_sdk.files.filesets.delete.side_effect = Exception("Delete failed")

        # Should not raise despite cleanup failure
        async with create_fileset(mock_sdk, name="test-fileset", workspace="default"):
            pass

        # Warning should be logged
        assert "Fileset cleanup failed" in caplog.text
        assert "Delete failed" in caplog.text

    @pytest.mark.asyncio
    async def test_cleanup_failure_on_user_exception_logs_warning(self, caplog):
        """Test that both user exception and cleanup failure are handled."""
        import logging

        caplog.set_level(logging.WARNING, logger="nmp.evaluator.app.datasets.nmp_datasets.fileset")

        mock_sdk = AsyncMock()
        mock_fileset = MagicMock()
        mock_fileset.name = "test-fileset"
        mock_sdk.files.filesets.create.return_value = mock_fileset
        mock_sdk.files.filesets.delete.side_effect = Exception("Delete failed")

        # User exception should still propagate
        with pytest.raises(ValueError, match="User error"):
            async with create_fileset(mock_sdk, name="test-fileset", workspace="default"):
                raise ValueError("User error")

        # Cleanup warning should still be logged
        assert "Fileset cleanup failed" in caplog.text
        assert "Delete failed" in caplog.text


class TestDatasetExists:
    @pytest.mark.asyncio
    async def test_dataset_inline_always_returns_true(self):
        """Test that DatasetRows always returns True."""
        mock_sdk = AsyncMock()
        dataset = DatasetRows(rows=[{"a": 1}])

        result = await dataset_exists(mock_sdk, dataset)

        assert result is True
        # SDK should not be called for inline datasets
        mock_sdk.files.filesets.create.assert_not_called()

    @pytest.mark.asyncio
    async def test_fileset_urn_checks_exists(self):
        """Test that FilesetRef uses FilesetFileSystem._exists."""
        mock_sdk = AsyncMock()
        dataset = FilesetRef(root="default/my-fileset")

        with patch("nmp.evaluator.app.datasets.nmp_datasets.fileset.FilesetFileSystem") as mock_fs_class:
            mock_fs = AsyncMock()
            mock_fs._exists.return_value = True
            mock_fs_class.return_value = mock_fs

            result = await dataset_exists(mock_sdk, dataset)

            assert result is True
            mock_fs._exists.assert_called_once_with("default/my-fileset")

    @pytest.mark.asyncio
    async def test_fileset_urn_returns_false_when_not_exists(self):
        """Test that FilesetRef returns False when path doesn't exist."""
        mock_sdk = AsyncMock()
        dataset = FilesetRef(root="default/my-fileset")

        with patch("nmp.evaluator.app.datasets.nmp_datasets.fileset.FilesetFileSystem") as mock_fs_class:
            mock_fs = AsyncMock()
            mock_fs._exists.return_value = False
            mock_fs_class.return_value = mock_fs

            result = await dataset_exists(mock_sdk, dataset)

            assert result is False

    @pytest.mark.asyncio
    async def test_fileset_inline_with_path_checks_exists(self):
        """Test that Fileset with path uses FilesetFileSystem._exists."""
        mock_sdk = AsyncMock()
        mock_fileset = MagicMock()
        mock_fileset.name = "test-fileset"
        mock_fileset.workspace = "default"
        mock_sdk.files.filesets.create.return_value = mock_fileset

        dataset = Fileset(
            storage=make_hf_storage_config(),
            path="data/file.json",
        )

        with patch("nmp.evaluator.app.datasets.nmp_datasets.fileset.FilesetFileSystem") as mock_fs_class:
            mock_fs = AsyncMock()
            mock_fs._exists.return_value = True
            mock_fs_class.return_value = mock_fs

            result = await dataset_exists(mock_sdk, dataset)

            assert result is True
            mock_fs._exists.assert_called_once_with("default/test-fileset/data/file.json")

    @pytest.mark.asyncio
    async def test_fileset_inline_with_none_path_checks_list_files(self):
        """Test that Fileset with None path uses list."""
        mock_sdk = AsyncMock()
        mock_fileset = MagicMock()
        mock_fileset.name = "test-fileset"
        mock_fileset.workspace = "default"
        mock_sdk.files.filesets.create.return_value = mock_fileset

        # sdk.files.list() returns ListFilesResponse with .data attribute
        mock_response = MagicMock()
        mock_response.data = [MagicMock(), MagicMock()]
        mock_sdk.files.list.return_value = mock_response

        # Fileset with None path - treated as "no specific path"
        dataset = Fileset(storage=make_hf_storage_config(), path=None)

        result = await dataset_exists(mock_sdk, dataset)

        # None path uses list to check if fileset has any files
        assert result is True
        mock_sdk.files.list.assert_called_once()

    @pytest.mark.asyncio
    async def test_fileset_inline_with_none_path_returns_false_when_no_files(self):
        """Test that Fileset with None path returns False when no files exist."""
        mock_sdk = AsyncMock()
        mock_fileset = MagicMock()
        mock_fileset.name = "test-fileset"
        mock_fileset.workspace = "default"
        mock_sdk.files.filesets.create.return_value = mock_fileset

        # sdk.files.list() returns ListFilesResponse with empty .data
        mock_response = MagicMock()
        mock_response.data = []
        mock_sdk.files.list.return_value = mock_response

        # Fileset with None path
        dataset = Fileset(storage=make_hf_storage_config(), path=None)

        result = await dataset_exists(mock_sdk, dataset)

        assert result is False
        mock_sdk.files.list.assert_called_once()

    @pytest.mark.asyncio
    async def test_fileset_ref_with_fragment_specific_file_exists(self):
        """Test that FilesetRef with specific file fragment checks that file exists."""
        mock_sdk = AsyncMock()
        dataset = FilesetRef(root="default/my-fileset#train.json")

        with patch("nmp.evaluator.app.datasets.nmp_datasets.fileset.FilesetFileSystem") as mock_fs_class:
            mock_fs = AsyncMock()
            # First call checks base path, second checks specific file
            mock_fs._exists.side_effect = [True, True]
            mock_fs_class.return_value = mock_fs

            result = await dataset_exists(mock_sdk, dataset)

            assert result is True
            assert mock_fs._exists.call_count == 2
            mock_fs._exists.assert_any_call("default/my-fileset")
            mock_fs._exists.assert_any_call("default/my-fileset/train.json")

    @pytest.mark.asyncio
    async def test_fileset_ref_with_fragment_specific_file_not_exists(self):
        """Test that FilesetRef with specific file fragment returns False when file doesn't exist."""
        mock_sdk = AsyncMock()
        dataset = FilesetRef(root="default/my-fileset#train.json")

        with patch("nmp.evaluator.app.datasets.nmp_datasets.fileset.FilesetFileSystem") as mock_fs_class:
            mock_fs = AsyncMock()
            # Base path exists but file doesn't
            mock_fs._exists.side_effect = [True, False]
            mock_fs_class.return_value = mock_fs

            result = await dataset_exists(mock_sdk, dataset)

            assert result is False

    @pytest.mark.asyncio
    async def test_fileset_ref_with_fragment_base_not_exists(self):
        """Test that FilesetRef with fragment returns False when base fileset doesn't exist."""
        mock_sdk = AsyncMock()
        dataset = FilesetRef(root="default/my-fileset#train.json")

        with patch("nmp.evaluator.app.datasets.nmp_datasets.fileset.FilesetFileSystem") as mock_fs_class:
            mock_fs = AsyncMock()
            mock_fs._exists.return_value = False
            mock_fs_class.return_value = mock_fs

            result = await dataset_exists(mock_sdk, dataset)

            assert result is False
            # Should only check base path, not try to find files
            mock_fs._exists.assert_called_once_with("default/my-fileset")

    @pytest.mark.asyncio
    async def test_fileset_ref_with_glob_pattern_matches(self):
        """Glob precheck should only validate base exists (avoid listing)."""
        mock_sdk = AsyncMock()
        dataset = FilesetRef(root="default/my-fileset#*.json")

        with patch("nmp.evaluator.app.datasets.nmp_datasets.fileset.FilesetFileSystem") as mock_fs_class:
            mock_fs = AsyncMock()
            mock_fs._exists.return_value = True  # Base path exists
            mock_fs_class.return_value = mock_fs

            result = await dataset_exists(mock_sdk, dataset)

            assert result is True
            mock_fs._find.assert_not_called()

    @pytest.mark.asyncio
    async def test_fileset_ref_with_glob_pattern_checks_prefix_dir(self):
        """Glob precheck should validate stable prefix dir if present."""
        mock_sdk = AsyncMock()
        dataset = FilesetRef(root="default/my-fileset#data/*.json")

        with patch("nmp.evaluator.app.datasets.nmp_datasets.fileset.FilesetFileSystem") as mock_fs_class:
            mock_fs = AsyncMock()
            # base exists, then prefix dir exists
            mock_fs._exists.side_effect = [True, True]
            mock_fs_class.return_value = mock_fs

            result = await dataset_exists(mock_sdk, dataset)

            assert result is True
            assert mock_fs._exists.call_count == 2
            mock_fs._exists.assert_any_call("default/my-fileset")
            mock_fs._exists.assert_any_call("default/my-fileset/data")

    @pytest.mark.asyncio
    async def test_fileset_ref_with_glob_pattern_missing_prefix_dir_returns_false(self):
        """Glob precheck should fail if stable prefix directory is missing."""
        mock_sdk = AsyncMock()
        dataset = FilesetRef(root="default/my-fileset#data/*.json")

        with patch("nmp.evaluator.app.datasets.nmp_datasets.fileset.FilesetFileSystem") as mock_fs_class:
            mock_fs = AsyncMock()
            # base exists, but prefix dir does not
            mock_fs._exists.side_effect = [True, False]
            mock_fs_class.return_value = mock_fs

            result = await dataset_exists(mock_sdk, dataset)

            assert result is False

    @pytest.mark.asyncio
    async def test_fileset_ref_with_glob_pattern_no_matches(self):
        """Glob precheck no longer attempts to prove a match exists."""
        mock_sdk = AsyncMock()
        dataset = FilesetRef(root="default/my-fileset#*.json")

        with patch("nmp.evaluator.app.datasets.nmp_datasets.fileset.FilesetFileSystem") as mock_fs_class:
            mock_fs = AsyncMock()
            mock_fs._exists.return_value = True  # Base path exists
            mock_fs_class.return_value = mock_fs

            result = await dataset_exists(mock_sdk, dataset)

            assert result is True

    @pytest.mark.asyncio
    async def test_fileset_ref_with_glob_pattern_find_exception(self):
        """Glob precheck should not call find, so exceptions are irrelevant."""
        mock_sdk = AsyncMock()
        dataset = FilesetRef(root="default/my-fileset#*.json")

        with patch("nmp.evaluator.app.datasets.nmp_datasets.fileset.FilesetFileSystem") as mock_fs_class:
            mock_fs = AsyncMock()
            mock_fs._exists.return_value = True
            mock_fs_class.return_value = mock_fs

            result = await dataset_exists(mock_sdk, dataset)

            assert result is True


class TestDownloadDatasetRows:
    def test_creates_directory_and_writes_json(self, tmp_path):
        """Test that _download_inline_dataset creates dir and writes JSON."""
        dataset = DatasetRows(rows=[{"a": 1}, {"b": 2}])
        destination = tmp_path / "output"

        result = _download_inline_dataset(dataset, str(destination))

        assert result == destination / "dataset.json"
        assert result.exists()

        with open(result) as f:
            data = json.load(f)
        assert data == [{"a": 1}, {"b": 2}]

    def test_custom_filename(self, tmp_path):
        """Test that _download_inline_dataset uses custom filename."""
        dataset = DatasetRows(rows=[{"a": 1}])
        destination = tmp_path / "output"

        result = _download_inline_dataset(dataset, str(destination), filename="custom.json")

        assert result == destination / "custom.json"
        assert result.exists()

    def test_creates_nested_directories(self, tmp_path):
        """Test that _download_inline_dataset creates nested directories."""
        dataset = DatasetRows(rows=[{"a": 1}])
        destination = tmp_path / "deep" / "nested" / "path"

        result = _download_inline_dataset(dataset, str(destination))

        assert result.exists()
        assert destination.exists()

    def test_unwraps_columnar_format_for_ragas(self, tmp_path):
        """Test that _download_inline_dataset unwraps columnar format for RAGAS/HuggingFace compatibility.

        When rows contains a single dict with list values (columnar format),
        the dict is unwrapped so Dataset.from_dict() can consume it directly.
        """
        # RAGAS/HF columnar format: single dict with list values, wrapped in a list
        columnar_data = {
            "question": ["Q1", "Q2", "Q3"],
            "contexts": [["ctx1"], ["ctx2"], ["ctx3"]],
            "ground_truth": ["gt1", "gt2", "gt3"],
            "answer": ["A1", "A2", "A3"],
        }
        dataset = DatasetRows(rows=[columnar_data])
        destination = tmp_path / "output"

        result = _download_inline_dataset(dataset, str(destination))

        assert result.exists()

        with open(result) as f:
            data = json.load(f)

        # Should be unwrapped to just the dict, not a list containing a dict
        assert isinstance(data, dict), "Columnar format should be unwrapped to a dict"
        assert data == columnar_data
        assert "question" in data
        assert data["question"] == ["Q1", "Q2", "Q3"]

    def test_preserves_row_format_multiple_dicts(self, tmp_path):
        """Test that _download_inline_dataset preserves row format when multiple dicts present."""
        # Standard row format: list of dicts
        row_data = [{"a": 1}, {"a": 2}, {"a": 3}]
        dataset = DatasetRows(rows=row_data)
        destination = tmp_path / "output"

        result = _download_inline_dataset(dataset, str(destination))

        with open(result) as f:
            data = json.load(f)

        # Should remain as a list of dicts
        assert isinstance(data, list)
        assert data == row_data

    def test_preserves_single_row_with_non_list_values(self, tmp_path):
        """Test that single row with non-list values is not unwrapped."""
        # Single row with scalar values (not columnar format)
        row_data = [{"name": "test", "value": 42}]
        dataset = DatasetRows(rows=row_data)
        destination = tmp_path / "output"

        result = _download_inline_dataset(dataset, str(destination))

        with open(result) as f:
            data = json.load(f)

        # Should remain as a list since values are not lists
        assert isinstance(data, list)
        assert data == row_data


class TestDownloadFilesetRef:
    @pytest.mark.asyncio
    async def test_downloads_using_fs_get(self, tmp_path):
        """Test that _download_fileset_ref uses FilesetFileSystem._get to download to destination/root."""
        mock_sdk = AsyncMock()
        dataset = FilesetRef(root="default/my-fileset")
        destination = tmp_path / "output"

        # Mock _get to simulate download
        async def mock_get(path, dest, recursive=True):
            # dest is now destination/default/my-fileset
            dest_path = Path(dest)
            dest_path.mkdir(parents=True, exist_ok=True)
            (dest_path / "file.json").write_text('{"test": 1}')

        with patch("nmp.evaluator.app.datasets.nmp_datasets.fileset.FilesetFileSystem") as mock_fs_class:
            mock_fs = AsyncMock()
            mock_fs._get = mock_get
            mock_fs_class.return_value = mock_fs

            result = await _download_fileset_ref(mock_sdk, dataset, str(destination))

            # Files are downloaded to destination / dataset.root
            expected_dest = destination / "default" / "my-fileset"
            assert result == expected_dest
            assert (expected_dest / "file.json").exists()

    @pytest.mark.asyncio
    async def test_respects_recursive_flag(self, tmp_path):
        """Test that _download_fileset_ref respects recursive flag."""
        mock_sdk = AsyncMock()
        dataset = FilesetRef(root="default/my-fileset")
        destination = tmp_path / "output"
        get_calls = []

        async def mock_get(path, dest, recursive=True):
            get_calls.append({"path": path, "recursive": recursive})
            fileset_dir = Path(dest) / "my-fileset"
            fileset_dir.mkdir(parents=True, exist_ok=True)
            (fileset_dir / "file.json").write_text('{"test": 1}')

        with patch("nmp.evaluator.app.datasets.nmp_datasets.fileset.FilesetFileSystem") as mock_fs_class:
            mock_fs = AsyncMock()
            mock_fs._get = mock_get
            mock_fs_class.return_value = mock_fs

            await _download_fileset_ref(mock_sdk, dataset, str(destination), recursive=False)

            assert len(get_calls) == 1
            assert get_calls[0]["recursive"] is False

    @pytest.mark.asyncio
    async def test_downloads_specific_file_with_fragment(self, tmp_path):
        """Test that _download_fileset_ref downloads specific file when fragment is used."""
        mock_sdk = AsyncMock()
        dataset = FilesetRef(root="default/my-fileset#train.json")
        destination = tmp_path / "output"
        get_file_calls = []

        async def mock_get_file(remote_path, local_path):
            get_file_calls.append({"remote": remote_path, "local": local_path})
            Path(local_path).parent.mkdir(parents=True, exist_ok=True)
            Path(local_path).write_text('{"data": "train"}')

        with patch("nmp.evaluator.app.datasets.nmp_datasets.fileset.FilesetFileSystem") as mock_fs_class:
            mock_fs = AsyncMock()
            mock_fs._get_file = mock_get_file
            mock_fs_class.return_value = mock_fs

            result = await _download_fileset_ref(mock_sdk, dataset, str(destination))

            assert len(get_file_calls) == 1
            assert get_file_calls[0]["remote"] == "default/my-fileset/train.json"
            # File is downloaded to destination/base_path/filename
            expected_file = destination / "default" / "my-fileset" / "train.json"
            assert result == expected_file
            assert expected_file.exists()

    @pytest.mark.asyncio
    async def test_downloads_matching_files_with_glob_pattern(self, tmp_path):
        """Test that _download_fileset_ref downloads all files matching glob pattern."""
        mock_sdk = AsyncMock()
        dataset = FilesetRef(root="default/my-fileset#*.json")
        destination = tmp_path / "output"
        get_file_calls = []

        async def mock_get_file(remote_path, local_path):
            get_file_calls.append({"remote": remote_path, "local": local_path})
            Path(local_path).parent.mkdir(parents=True, exist_ok=True)
            Path(local_path).write_text('{"data": "test"}')

        with patch("nmp.evaluator.app.datasets.nmp_datasets.fileset.FilesetFileSystem") as mock_fs_class:
            mock_fs = AsyncMock()
            # _find returns paths in format "workspace/fileset#relative_path"
            mock_fs._find.return_value = [
                "default/my-fileset#train.json",
                "default/my-fileset#test.json",
                "default/my-fileset#data.csv",  # Should not be downloaded
            ]
            mock_fs._get_file = mock_get_file
            mock_fs_class.return_value = mock_fs

            result = await _download_fileset_ref(mock_sdk, dataset, str(destination))

            # Should download only .json files
            assert len(get_file_calls) == 2
            remote_paths = {call["remote"] for call in get_file_calls}
            assert "default/my-fileset#train.json" in remote_paths
            assert "default/my-fileset#test.json" in remote_paths
            assert "default/my-fileset#data.csv" not in remote_paths

            # Result should be the base directory
            expected_base = destination / "default" / "my-fileset"
            assert result == expected_base

    @pytest.mark.asyncio
    async def test_simple_glob_matches_only_top_level_files(self, tmp_path):
        """Test that *.json only matches top-level files, not nested ones."""
        mock_sdk = AsyncMock()
        dataset = FilesetRef(root="default/my-fileset#*.json")
        destination = tmp_path / "output"
        get_file_calls = []

        async def mock_get_file(remote_path, local_path):
            get_file_calls.append({"remote": remote_path, "local": local_path})
            Path(local_path).parent.mkdir(parents=True, exist_ok=True)
            Path(local_path).write_text("{}")

        with patch("nmp.evaluator.app.datasets.nmp_datasets.fileset.FilesetFileSystem") as mock_fs_class:
            mock_fs = AsyncMock()
            # _find returns paths in format "workspace/fileset#relative_path"
            mock_fs._find.return_value = [
                "default/my-fileset#train.json",
                "default/my-fileset#subdir/nested.json",  # Should NOT match *.json
            ]
            mock_fs._get_file = mock_get_file
            mock_fs_class.return_value = mock_fs

            await _download_fileset_ref(mock_sdk, dataset, str(destination))

            # *.json matches only top-level .json files (simple pattern)
            assert len(get_file_calls) == 1
            assert get_file_calls[0]["remote"] == "default/my-fileset#train.json"

    @pytest.mark.asyncio
    async def test_path_pattern_matches_subdir_files(self, tmp_path):
        """Test that */*.json matches files in any single subdirectory."""
        mock_sdk = AsyncMock()
        dataset = FilesetRef(root="default/my-fileset#*/*.json")
        destination = tmp_path / "output"
        get_file_calls = []

        async def mock_get_file(remote_path, local_path):
            get_file_calls.append({"remote": remote_path, "local": local_path})
            Path(local_path).parent.mkdir(parents=True, exist_ok=True)
            Path(local_path).write_text("{}")

        with patch("nmp.evaluator.app.datasets.nmp_datasets.fileset.FilesetFileSystem") as mock_fs_class:
            mock_fs = AsyncMock()
            # _find returns paths in format "workspace/fileset#relative_path"
            mock_fs._find.return_value = [
                "default/my-fileset#train.json",  # Won't match */*.json (no subdir)
                "default/my-fileset#subdir/nested.json",  # Matches
                "default/my-fileset#data/file.json",  # Matches
            ]
            mock_fs._get_file = mock_get_file
            mock_fs_class.return_value = mock_fs

            await _download_fileset_ref(mock_sdk, dataset, str(destination))

            # */*.json matches files in single-level subdirectories
            assert len(get_file_calls) == 2
            remote_paths = {call["remote"] for call in get_file_calls}
            assert "default/my-fileset#subdir/nested.json" in remote_paths
            assert "default/my-fileset#data/file.json" in remote_paths

    @pytest.mark.asyncio
    async def test_path_pattern_does_not_match_from_right(self, tmp_path):
        """Test that data/*.json is anchored at the fileset root."""
        mock_sdk = AsyncMock()
        dataset = FilesetRef(root="default/my-fileset#data/*.json")
        destination = tmp_path / "output"
        get_file_calls = []

        async def mock_get_file(remote_path, local_path):
            get_file_calls.append({"remote": remote_path, "local": local_path})
            Path(local_path).parent.mkdir(parents=True, exist_ok=True)
            Path(local_path).write_text("{}")

        with patch("nmp.evaluator.app.datasets.nmp_datasets.fileset.FilesetFileSystem") as mock_fs_class:
            mock_fs = AsyncMock()
            mock_fs._find.return_value = [
                "default/my-fileset#data/root.json",
                "default/my-fileset#nested/data/right-anchored.json",
            ]
            mock_fs._get_file = mock_get_file
            mock_fs_class.return_value = mock_fs

            await _download_fileset_ref(mock_sdk, dataset, str(destination))

            assert len(get_file_calls) == 1
            assert get_file_calls[0]["remote"] == "default/my-fileset#data/root.json"

    @pytest.mark.asyncio
    async def test_fragment_with_subdirectory_path(self, tmp_path):
        """Test that _download_fileset_ref handles fragment with subdirectory path."""
        mock_sdk = AsyncMock()
        dataset = FilesetRef(root="default/my-fileset#data/train.json")
        destination = tmp_path / "output"
        get_file_calls = []

        async def mock_get_file(remote_path, local_path):
            get_file_calls.append({"remote": remote_path, "local": local_path})
            Path(local_path).parent.mkdir(parents=True, exist_ok=True)
            Path(local_path).write_text('{"data": "nested"}')

        with patch("nmp.evaluator.app.datasets.nmp_datasets.fileset.FilesetFileSystem") as mock_fs_class:
            mock_fs = AsyncMock()
            mock_fs._get_file = mock_get_file
            mock_fs_class.return_value = mock_fs

            result = await _download_fileset_ref(mock_sdk, dataset, str(destination))

            assert len(get_file_calls) == 1
            assert get_file_calls[0]["remote"] == "default/my-fileset/data/train.json"
            # File is downloaded to destination/base_path/fragment_path
            expected_file = destination / "default" / "my-fileset" / "data" / "train.json"
            assert result == expected_file

    @pytest.mark.asyncio
    async def test_fragment_with_leading_slash_stays_relative(self, tmp_path):
        """Test that leading slash fragments do not escape the fileset destination."""
        mock_sdk = AsyncMock()
        dataset = FilesetRef(root="default/my-fileset#/data/train.json")
        destination = tmp_path / "output"
        get_file_calls = []

        async def mock_get_file(remote_path, local_path):
            get_file_calls.append({"remote": remote_path, "local": local_path})
            Path(local_path).parent.mkdir(parents=True, exist_ok=True)
            Path(local_path).write_text('{"data": "nested"}')

        with patch("nmp.evaluator.app.datasets.nmp_datasets.fileset.FilesetFileSystem") as mock_fs_class:
            mock_fs = AsyncMock()
            mock_fs._get_file = mock_get_file
            mock_fs_class.return_value = mock_fs

            result = await _download_fileset_ref(mock_sdk, dataset, str(destination))

            assert len(get_file_calls) == 1
            assert get_file_calls[0]["remote"] == "default/my-fileset/data/train.json"
            assert result == destination / "default" / "my-fileset" / "data" / "train.json"

    @pytest.mark.asyncio
    @pytest.mark.parametrize("root", ["default/my-fileset#", "default/my-fileset#/"])
    async def test_empty_fragment_downloads_fileset_root(self, root, tmp_path):
        """Test that empty fragments behave like no fragment."""
        mock_sdk = AsyncMock()
        dataset = FilesetRef(root=root)
        destination = tmp_path / "output"

        with patch("nmp.evaluator.app.datasets.nmp_datasets.fileset.FilesetFileSystem") as mock_fs_class:
            mock_fs = AsyncMock()
            mock_fs_class.return_value = mock_fs

            result = await _download_fileset_ref(mock_sdk, dataset, str(destination))

            expected_dest = destination / "default" / "my-fileset"
            assert result == expected_dest
            mock_fs._get.assert_awaited_once_with(
                "default/my-fileset/",
                str(expected_dest),
                recursive=True,
            )


class TestDownloadFileset:
    @pytest.mark.asyncio
    async def test_creates_fileset_and_downloads(self):
        """Test that _download_inline_fileset creates fileset and downloads."""
        mock_sdk = AsyncMock()
        mock_fileset = MagicMock()
        mock_fileset.name = "test-fileset"
        mock_fileset.workspace = "default"
        mock_sdk.files.filesets.create.return_value = mock_fileset

        dataset = Fileset(
            storage=make_hf_storage_config(),
            path="checkpoints/",
        )

        with patch("nmp.evaluator.app.datasets.nmp_datasets.fileset.FilesetFileSystem") as mock_fs_class:
            mock_fs = AsyncMock()
            mock_fs_class.return_value = mock_fs

            result = await _download_inline_fileset(mock_sdk, dataset, "/local/destination")

            # dest = destination / dataset.path (Path strips trailing slash)
            mock_fs._get.assert_called_once_with(
                "default/test-fileset/checkpoints/", "/local/destination/checkpoints", recursive=True
            )
            assert result == Path("/local/destination/checkpoints")

        # Verify fileset was deleted after download
        mock_sdk.files.filesets.delete.assert_called_once()

    @pytest.mark.asyncio
    async def test_downloads_root_when_none_path(self):
        """Test that _download_inline_fileset downloads root when path is None."""
        mock_sdk = AsyncMock()
        mock_fileset = MagicMock()
        mock_fileset.name = "test-fileset"
        mock_fileset.workspace = "default"
        mock_sdk.files.filesets.create.return_value = mock_fileset

        # Fileset with None path - downloads from root
        dataset = Fileset(storage=make_hf_storage_config(), path=None)

        with patch("nmp.evaluator.app.datasets.nmp_datasets.fileset.FilesetFileSystem") as mock_fs_class:
            mock_fs = AsyncMock()
            mock_fs_class.return_value = mock_fs

            result = await _download_inline_fileset(mock_sdk, dataset, "/local/destination")

            # When path is None, dest = destination (unchanged)
            mock_fs._get.assert_called_once_with("default/test-fileset/", "/local/destination", recursive=True)
            assert result == Path("/local/destination")


class TestDownloadDataset:
    @pytest.mark.asyncio
    async def test_routes_to_inline_download(self, tmp_path):
        """Test that download_dataset routes DatasetRows correctly."""
        mock_sdk = AsyncMock()
        dataset = DatasetRows(rows=[{"a": 1}])

        await download_dataset(mock_sdk, dataset, str(tmp_path))

        # Verify file was created
        output_file = tmp_path / "dataset.json"
        assert output_file.exists()

    @pytest.mark.asyncio
    async def test_routes_to_fileset_urn_download(self, tmp_path):
        """Test that download_dataset routes FilesetRef correctly."""
        mock_sdk = AsyncMock()
        dataset = FilesetRef(root="default/my-fileset")
        destination = tmp_path / "output"

        async def mock_get(path, dest, recursive=True):
            # dest is now destination/default/my-fileset
            dest_path = Path(dest)
            dest_path.mkdir(parents=True, exist_ok=True)
            (dest_path / "file.json").write_text('{"test": 1}')

        with patch("nmp.evaluator.app.datasets.nmp_datasets.fileset.FilesetFileSystem") as mock_fs_class:
            mock_fs = AsyncMock()
            mock_fs._get = mock_get
            mock_fs_class.return_value = mock_fs

            result = await download_dataset(mock_sdk, dataset, str(destination))

            # Files are downloaded to destination / dataset.root
            expected_dest = destination / "default" / "my-fileset"
            assert result == expected_dest
            assert (expected_dest / "file.json").exists()

    @pytest.mark.asyncio
    async def test_routes_to_fileset_inline_download(self):
        """Test that download_dataset routes Fileset correctly."""
        mock_sdk = AsyncMock()
        mock_fileset = MagicMock()
        mock_fileset.name = "test-fileset"
        mock_fileset.workspace = "default"
        mock_sdk.files.filesets.create.return_value = mock_fileset

        dataset = Fileset(
            storage=make_hf_storage_config(),
            path="data/",
        )

        with patch("nmp.evaluator.app.datasets.nmp_datasets.fileset.FilesetFileSystem") as mock_fs_class:
            mock_fs = AsyncMock()
            mock_fs_class.return_value = mock_fs

            await download_dataset(mock_sdk, dataset, "/local/destination")

            mock_sdk.files.filesets.create.assert_called_once()
            mock_fs._get.assert_called_once()

    @pytest.mark.asyncio
    async def test_passes_workspace_to_fileset_inline(self):
        """Test that download_dataset passes workspace to Fileset download."""
        mock_sdk = AsyncMock()
        mock_fileset = MagicMock()
        mock_fileset.name = "test-fileset"
        mock_fileset.workspace = "custom-workspace"
        mock_sdk.files.filesets.create.return_value = mock_fileset

        dataset = Fileset(
            storage=make_hf_storage_config(),
            path="data/",
        )

        with patch("nmp.evaluator.app.datasets.nmp_datasets.fileset.FilesetFileSystem") as mock_fs_class:
            mock_fs = AsyncMock()
            mock_fs_class.return_value = mock_fs

            await download_dataset(mock_sdk, dataset, "/local/destination", workspace="custom-workspace")

            call_args = mock_sdk.files.filesets.create.call_args
            assert call_args.kwargs["workspace"] == "custom-workspace"

    @pytest.mark.asyncio
    async def test_passes_recursive_flag(self, tmp_path):
        """Test that download_dataset passes recursive flag."""
        mock_sdk = AsyncMock()
        dataset = FilesetRef(root="default/my-fileset")
        destination = tmp_path / "output"
        get_calls = []

        async def mock_get(path, dest, recursive=True):
            get_calls.append({"path": path, "recursive": recursive})
            fileset_dir = Path(dest) / "my-fileset"
            fileset_dir.mkdir(parents=True, exist_ok=True)
            (fileset_dir / "file.json").write_text('{"test": 1}')

        with patch("nmp.evaluator.app.datasets.nmp_datasets.fileset.FilesetFileSystem") as mock_fs_class:
            mock_fs = AsyncMock()
            mock_fs._get = mock_get
            mock_fs_class.return_value = mock_fs

            await download_dataset(mock_sdk, dataset, str(destination), recursive=False)

            assert len(get_calls) == 1
            assert get_calls[0]["recursive"] is False


class TestDownloadDatasetSync:
    def test_routes_to_inline_download(self, tmp_path):
        """Test that download_dataset_sync routes DatasetRows correctly."""
        mock_sdk = MagicMock()
        dataset = DatasetRows(rows=[{"a": 1}])

        with patch("nmp.evaluator.app.datasets.nmp_datasets.fileset._download_fileset_ref_sync") as mock_bridge:
            result = download_dataset_sync(mock_sdk, dataset, str(tmp_path))

        assert result == tmp_path / "dataset.json"
        assert json.loads(result.read_text(encoding="utf-8")) == [{"a": 1}]
        mock_bridge.assert_not_called()

    def test_routes_inline_fileset_to_sync_bridge(self, tmp_path):
        """Test that download_dataset_sync routes Fileset configs to the sync bridge."""
        mock_sdk = MagicMock()
        dataset = Fileset(storage=make_hf_storage_config(), path="data/")
        expected_path = tmp_path / "data"

        with patch(
            "nmp.evaluator.app.datasets.nmp_datasets.fileset._download_inline_fileset_sync",
            return_value=expected_path,
        ) as mock_bridge:
            result = download_dataset_sync(mock_sdk, dataset, str(tmp_path), workspace="custom")

        assert result == expected_path
        mock_bridge.assert_called_once_with(mock_sdk, dataset, str(tmp_path), workspace="custom", recursive=True)

    def test_bridges_filesetref_to_async_helper(self, tmp_path):
        """Test that the sync helper delegates to `_download_fileset_ref` via `fsspec.asyn.sync`."""
        mock_sdk = MagicMock()
        mock_async_sdk = MagicMock()
        mock_async_sdk.close = AsyncMock()
        dataset = FilesetRef(root="default/my-fileset#data/validation.jsonl")
        destination = tmp_path / "output"
        expected_path = destination / "default" / "my-fileset" / "data" / "validation.jsonl"

        with (
            patch("nmp.evaluator.app.datasets.nmp_datasets.fileset.FilesetFileSystem") as mock_fs_class,
            patch(
                "nmp.evaluator.app.datasets.nmp_datasets.fileset._download_fileset_ref",
                new_callable=AsyncMock,
            ) as mock_async_helper,
            patch(
                "nmp.evaluator.app.datasets.nmp_datasets.fileset.fsspec.asyn.sync",
                side_effect=lambda loop, fn, *a, **kw: asyncio.run(fn(*a, **kw)),
            ),
        ):
            mock_fs_class.return_value._sdk = mock_async_sdk
            mock_async_helper.return_value = expected_path

            result = _download_fileset_ref_sync(mock_sdk, dataset, str(destination))

        assert result == expected_path
        mock_fs_class.assert_called_once_with(sdk=mock_sdk)
        mock_async_helper.assert_awaited_once_with(mock_async_sdk, dataset, str(destination), recursive=True)
        mock_async_sdk.close.assert_awaited_once_with()

    def test_bridges_recursive_false(self, tmp_path):
        """Test that recursive=False propagates to the async helper through the bridge."""
        mock_sdk = MagicMock()
        mock_async_sdk = MagicMock()
        mock_async_sdk.close = AsyncMock()
        dataset = FilesetRef(root="default/my-fileset")
        destination = tmp_path / "output"
        expected_path = destination / "default" / "my-fileset"

        with (
            patch("nmp.evaluator.app.datasets.nmp_datasets.fileset.FilesetFileSystem") as mock_fs_class,
            patch(
                "nmp.evaluator.app.datasets.nmp_datasets.fileset._download_fileset_ref",
                new_callable=AsyncMock,
            ) as mock_async_helper,
            patch(
                "nmp.evaluator.app.datasets.nmp_datasets.fileset.fsspec.asyn.sync",
                side_effect=lambda loop, fn, *a, **kw: asyncio.run(fn(*a, **kw)),
            ),
        ):
            mock_fs_class.return_value._sdk = mock_async_sdk
            mock_async_helper.return_value = expected_path

            _download_fileset_ref_sync(mock_sdk, dataset, str(destination), recursive=False)

        mock_async_helper.assert_awaited_once_with(mock_async_sdk, dataset, str(destination), recursive=False)
        mock_async_sdk.close.assert_awaited_once_with()

    def test_closes_async_sdk_when_filesetref_download_fails(self, tmp_path):
        """Test that the sync bridge closes its converted async SDK when downloads fail."""
        mock_sdk = MagicMock()
        mock_async_sdk = MagicMock()
        mock_async_sdk.close = AsyncMock()
        dataset = FilesetRef(root="default/my-fileset")
        destination = tmp_path / "output"

        with (
            patch("nmp.evaluator.app.datasets.nmp_datasets.fileset.FilesetFileSystem") as mock_fs_class,
            patch(
                "nmp.evaluator.app.datasets.nmp_datasets.fileset._download_fileset_ref",
                new_callable=AsyncMock,
            ) as mock_async_helper,
            patch(
                "nmp.evaluator.app.datasets.nmp_datasets.fileset.fsspec.asyn.sync",
                side_effect=lambda loop, fn, *a, **kw: asyncio.run(fn(*a, **kw)),
            ),
        ):
            mock_fs_class.return_value._sdk = mock_async_sdk
            mock_async_helper.side_effect = RuntimeError("download failed")

            with pytest.raises(RuntimeError, match="download failed"):
                _download_fileset_ref_sync(mock_sdk, dataset, str(destination))

        mock_async_sdk.close.assert_awaited_once_with()

    def test_bridges_inline_fileset_to_async_helper(self, tmp_path):
        """Test that the inline Fileset sync helper delegates through the async SDK bridge."""
        mock_sdk = MagicMock()
        mock_async_sdk = MagicMock()
        mock_async_sdk.close = AsyncMock()
        dataset = Fileset(storage=make_hf_storage_config(), path="data/validation.jsonl")
        destination = tmp_path / "output"
        expected_path = destination / "data" / "validation.jsonl"

        with (
            patch("nmp.evaluator.app.datasets.nmp_datasets.fileset.FilesetFileSystem") as mock_fs_class,
            patch(
                "nmp.evaluator.app.datasets.nmp_datasets.fileset._download_inline_fileset",
                new_callable=AsyncMock,
            ) as mock_async_helper,
            patch(
                "nmp.evaluator.app.datasets.nmp_datasets.fileset.fsspec.asyn.sync",
                side_effect=lambda loop, fn, *a, **kw: asyncio.run(fn(*a, **kw)),
            ),
        ):
            mock_fs_class.return_value._sdk = mock_async_sdk
            mock_async_helper.return_value = expected_path

            result = _download_inline_fileset_sync(
                mock_sdk, dataset, str(destination), workspace="custom", recursive=False
            )

        assert result == expected_path
        mock_fs_class.assert_called_once_with(sdk=mock_sdk)
        mock_async_helper.assert_awaited_once_with(
            mock_async_sdk,
            dataset,
            str(destination),
            workspace="custom",
            recursive=False,
        )
        mock_async_sdk.close.assert_awaited_once_with()
