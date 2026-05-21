# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
# property and proprietary rights in and to this material, related
# documentation and any modifications thereto. Any use, reproduction,
# disclosure or distribution of this material and related documentation
# without an express license agreement from NVIDIA CORPORATION or
# its affiliates is strictly prohibited.

"""Unit tests for the dataset loader module.

Tests the loading of datasets from downloaded filesets using PyArrow.
Supports multiple file formats (JSON, JSONL, CSV, Parquet, ORC, Feather)
and pattern matching for file selection.
"""

import gzip
import json
from pathlib import Path

import pyarrow as pa
import pyarrow.feather as pa_feather
import pyarrow.parquet as pa_parquet
import pytest
from nemo_evaluator_sdk.datasets.loader import (
    DatasetLoadError,
    load_dataset,
    load_dataset_as_dicts,
)
from nemo_evaluator_sdk.datasets.loader import (
    discover_files as _discover_files,
)
from nemo_evaluator_sdk.datasets.loader import (
    is_glob_pattern as _is_glob_pattern,
)
from nemo_evaluator_sdk.datasets.loader import (
    load_file as _load_file,
)
from nmp.evaluator.app.datasets.loader import (
    _parse_dataset_ref,
    load_dataset_from_ref,
    load_dataset_from_ref_as_dicts,
)

# =============================================================================
# Test Fixtures
# =============================================================================


@pytest.fixture
def sample_data() -> list[dict]:
    """Sample dataset rows for testing."""
    return [
        {"prompt": "What is Python?", "response": "A programming language"},
        {"prompt": "Explain AI", "response": "Artificial intelligence"},
        {"prompt": "What is ML?", "response": "Machine learning"},
    ]


@pytest.fixture
def dataset_dir(tmp_path: Path, sample_data: list[dict]) -> Path:
    """Create a temporary dataset directory structure.

    Structure:
        tmp_path/
            workspace/
                fileset/
                    data.json
                    train.jsonl
                    test.csv
                    embeddings.parquet
                    features.feather
                    subdir/
                        nested.json
    """
    fileset_dir = tmp_path / "workspace" / "fileset"
    fileset_dir.mkdir(parents=True)

    # JSON file (array of objects)
    with open(fileset_dir / "data.json", "w") as f:
        json.dump(sample_data, f)

    # JSONL file (one object per line)
    with open(fileset_dir / "train.jsonl", "w") as f:
        for row in sample_data:
            f.write(json.dumps(row) + "\n")

    # CSV file
    csv_content = "prompt,response\n"
    for row in sample_data:
        csv_content += f'"{row["prompt"]}","{row["response"]}"\n'
    (fileset_dir / "test.csv").write_text(csv_content)

    # Parquet file
    table = pa.Table.from_pylist(sample_data)
    pa_parquet.write_table(table, fileset_dir / "embeddings.parquet")

    # Feather/Arrow IPC file
    pa_feather.write_feather(table, fileset_dir / "features.feather")

    # Nested directory with JSON
    subdir = fileset_dir / "subdir"
    subdir.mkdir()
    with open(subdir / "nested.json", "w") as f:
        json.dump(sample_data[:1], f)  # Just first row

    return tmp_path


@pytest.fixture
def compressed_dataset_dir(tmp_path: Path, sample_data: list[dict]) -> Path:
    """Create a dataset directory with compressed files."""
    fileset_dir = tmp_path / "workspace" / "compressed-fileset"
    fileset_dir.mkdir(parents=True)

    # Gzipped JSONL (common for HuggingFace datasets)
    with gzip.open(fileset_dir / "train.jsonl.gz", "wt", encoding="utf-8") as f:
        for row in sample_data:
            f.write(json.dumps(row) + "\n")

    return tmp_path


# =============================================================================
# Test: parse_dataset_ref
# =============================================================================


class TestParseDatasetRef:
    """Tests for parsing dataset reference strings."""

    def test_parse_simple_ref(self):
        """Parse workspace/fileset without fragment."""
        workspace, fileset, pattern = _parse_dataset_ref("my-workspace/my-fileset")
        assert workspace == "my-workspace"
        assert fileset == "my-fileset"
        assert pattern is None

    def test_parse_ref_with_filename_fragment(self):
        """Parse workspace/fileset#filename."""
        workspace, fileset, pattern = _parse_dataset_ref("workspace/fileset#train.jsonl")
        assert workspace == "workspace"
        assert fileset == "fileset"
        assert pattern == "train.jsonl"

    def test_parse_ref_with_path_fragment(self):
        """Parse workspace/fileset#path/to/file.json."""
        workspace, fileset, pattern = _parse_dataset_ref("workspace/fileset#data/train.json")
        assert workspace == "workspace"
        assert fileset == "fileset"
        assert pattern == "data/train.json"

    def test_parse_ref_with_glob_pattern(self):
        """Parse workspace/fileset#*.json."""
        workspace, fileset, pattern = _parse_dataset_ref("workspace/fileset#*.json")
        assert workspace == "workspace"
        assert fileset == "fileset"
        assert pattern == "*.json"

    def test_parse_ref_with_recursive_glob(self):
        """Parse workspace/fileset#**/*.parquet."""
        workspace, fileset, pattern = _parse_dataset_ref("workspace/fileset#**/*.parquet")
        assert workspace == "workspace"
        assert fileset == "fileset"
        assert pattern == "**/*.parquet"

    def test_parse_ref_with_subdir_glob(self):
        """Parse workspace/fileset#subdir/*.csv."""
        workspace, fileset, pattern = _parse_dataset_ref("workspace/fileset#subdir/*.csv")
        assert workspace == "workspace"
        assert fileset == "fileset"
        assert pattern == "subdir/*.csv"

    def test_parse_ref_invalid_no_workspace(self):
        """Raise error for ref without workspace."""
        with pytest.raises(ValueError, match="workspace"):
            _parse_dataset_ref("just-fileset")

    def test_parse_ref_empty_string(self):
        """Raise error for empty string."""
        with pytest.raises(ValueError):
            _parse_dataset_ref("")


# =============================================================================
# Test: is_glob_pattern
# =============================================================================


class TestIsGlobPattern:
    """Tests for glob pattern detection."""

    @pytest.mark.parametrize(
        ("pattern", "expected"),
        [
            ("*.json", True),  # Single asterisk
            ("**/*.json", True),  # Double asterisk (recursive)
            ("file?.json", True),  # Question mark wildcard
            ("file[0-9].json", True),  # Bracket range
            ("train.jsonl", False),  # Plain filename
            ("data/train.json", False),  # Path without wildcards
        ],
    )
    def test_is_glob_pattern(self, pattern: str, expected: bool):
        """Detect glob patterns correctly."""
        assert _is_glob_pattern(pattern) is expected


# =============================================================================
# Test: discover_files
# =============================================================================


class TestDiscoverFiles:
    """Tests for file discovery in datasets."""

    def test_discover_all_files(self, dataset_dir: Path):
        """Discover all files when no pattern specified."""
        fileset_path = dataset_dir / "workspace" / "fileset"
        files = _discover_files(fileset_path, pattern=None)

        # Should find all data files (not directories)
        filenames = {f.name for f in files}
        assert "data.json" in filenames
        assert "train.jsonl" in filenames
        assert "test.csv" in filenames
        assert "embeddings.parquet" in filenames
        assert "features.feather" in filenames
        assert "nested.json" in filenames  # From subdir

    def test_discover_specific_file(self, dataset_dir: Path):
        """Discover a specific file by name."""
        fileset_path = dataset_dir / "workspace" / "fileset"
        files = _discover_files(fileset_path, pattern="data.json")

        assert len(files) == 1
        assert files[0].name == "data.json"

    def test_discover_file_in_subdir(self, dataset_dir: Path):
        """Discover a file in subdirectory by path."""
        fileset_path = dataset_dir / "workspace" / "fileset"
        files = _discover_files(fileset_path, pattern="subdir/nested.json")

        assert len(files) == 1
        assert files[0].name == "nested.json"

    def test_discover_glob_extension(self, dataset_dir: Path):
        """Discover files matching glob extension pattern."""
        fileset_path = dataset_dir / "workspace" / "fileset"
        files = _discover_files(fileset_path, pattern="*.json")

        # Should match data.json but not nested.json (different dir) or train.jsonl
        filenames = {f.name for f in files}
        assert "data.json" in filenames
        assert "train.jsonl" not in filenames

    def test_discover_recursive_glob(self, dataset_dir: Path):
        """Discover files matching recursive glob pattern."""
        fileset_path = dataset_dir / "workspace" / "fileset"
        files = _discover_files(fileset_path, pattern="**/*.json")

        # Should match both data.json and subdir/nested.json
        filenames = {f.name for f in files}
        assert "data.json" in filenames
        assert "nested.json" in filenames

    def test_discover_no_matches_raises(self, dataset_dir: Path):
        """Raise error when pattern matches no files."""
        fileset_path = dataset_dir / "workspace" / "fileset"

        with pytest.raises(DatasetLoadError, match="No files found"):
            _discover_files(fileset_path, pattern="*.nonexistent")

    def test_discover_specific_file_not_found_raises(self, dataset_dir: Path):
        """Raise error when specific file not found."""
        fileset_path = dataset_dir / "workspace" / "fileset"

        with pytest.raises(DatasetLoadError, match="not found"):
            _discover_files(fileset_path, pattern="missing.json")

    def test_discover_empty_directory_raises(self, tmp_path: Path):
        """Raise error when directory is empty."""
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()

        with pytest.raises(DatasetLoadError, match="No files found"):
            _discover_files(empty_dir, pattern=None)


# =============================================================================
# Test: load_file
# =============================================================================


class TestLoadFile:
    """Tests for loading individual files."""

    def test_load_json_array(self, dataset_dir: Path):
        """Load JSON file containing array of objects."""
        file_path = dataset_dir / "workspace" / "fileset" / "data.json"
        table = _load_file(file_path)

        assert table is not None
        assert table.num_rows == 3
        assert "prompt" in table.column_names
        assert "response" in table.column_names

    def test_load_jsonl(self, dataset_dir: Path):
        """Load JSONL file (newline-delimited JSON)."""
        file_path = dataset_dir / "workspace" / "fileset" / "train.jsonl"
        table = _load_file(file_path)

        assert table is not None
        assert table.num_rows == 3

    def test_load_csv(self, dataset_dir: Path):
        """Load CSV file."""
        file_path = dataset_dir / "workspace" / "fileset" / "test.csv"
        table = _load_file(file_path)

        assert table is not None
        assert table.num_rows == 3

    def test_load_parquet(self, dataset_dir: Path):
        """Load Parquet file."""
        file_path = dataset_dir / "workspace" / "fileset" / "embeddings.parquet"
        table = _load_file(file_path)

        assert table is not None
        assert table.num_rows == 3

    def test_load_feather(self, dataset_dir: Path):
        """Load Feather/Arrow IPC file."""
        file_path = dataset_dir / "workspace" / "fileset" / "features.feather"
        table = _load_file(file_path)

        assert table is not None
        assert table.num_rows == 3

    def test_load_gzipped_jsonl(self, compressed_dataset_dir: Path):
        """Load gzip-compressed JSONL file."""
        file_path = compressed_dataset_dir / "workspace" / "compressed-fileset" / "train.jsonl.gz"
        table = _load_file(file_path)

        assert table is not None
        assert table.num_rows == 3

    def test_load_unsupported_format_returns_none(self, tmp_path: Path):
        """Return None for unsupported file formats."""
        # Create a text file (not a supported data format)
        text_file = tmp_path / "readme.txt"
        text_file.write_text("This is not a data file")

        result = _load_file(text_file)
        assert result is None

    def test_load_corrupted_file_returns_none(self, tmp_path: Path):
        """Return None for corrupted/invalid files."""
        # Create a file with invalid JSON
        bad_json = tmp_path / "bad.json"
        bad_json.write_text("this is not valid json {{{")

        result = _load_file(bad_json)
        assert result is None


# =============================================================================
# Test: load_dataset
# =============================================================================


class TestLoadDataset:
    """Tests for the main dataset loading function."""

    def test_load_all_files_concatenated(self, dataset_dir: Path, sample_data: list[dict]):
        """Load all files and concatenate into single table."""
        fileset_path = dataset_dir / "workspace" / "fileset"
        table = load_dataset(fileset_path, pattern=None)

        # Multiple files loaded, each with 3 rows (except nested.json with 1)
        # data.json (3) + train.jsonl (3) + test.csv (3) + embeddings.parquet (3)
        # + features.feather (3) + nested.json (1) = 16 rows
        assert table.num_rows == 16
        assert "prompt" in table.column_names
        assert "response" in table.column_names

    def test_load_specific_file(self, dataset_dir: Path):
        """Load a specific file by name."""
        fileset_path = dataset_dir / "workspace" / "fileset"
        table = load_dataset(fileset_path, pattern="data.json")

        assert table.num_rows == 3

    def test_load_glob_pattern(self, dataset_dir: Path):
        """Load files matching glob pattern."""
        fileset_path = dataset_dir / "workspace" / "fileset"
        table = load_dataset(fileset_path, pattern="*.parquet")

        assert table.num_rows == 3  # Only embeddings.parquet

    def test_load_skips_unparseable_files(self, dataset_dir: Path):
        """Skip files that cannot be parsed."""
        fileset_path = dataset_dir / "workspace" / "fileset"

        # Add an unparseable file
        (fileset_path / "readme.md").write_text("# This is markdown")

        # Should still load successfully, skipping the markdown file
        table = load_dataset(fileset_path, pattern=None)
        assert table.num_rows > 0

    def test_load_no_parseable_files_raises(self, tmp_path: Path):
        """Raise error when no files can be parsed."""
        fileset_path = tmp_path / "workspace" / "bad-fileset"
        fileset_path.mkdir(parents=True)

        # Only unparseable files
        (fileset_path / "readme.md").write_text("# Readme")
        (fileset_path / "notes.txt").write_text("Notes")

        with pytest.raises(DatasetLoadError, match="No data could be loaded"):
            load_dataset(fileset_path, pattern=None)


# =============================================================================
# Test: load_dataset_as_dicts
# =============================================================================


class TestLoadDatasetAsDicts:
    """Tests for loading datasets as list of dicts."""

    def test_load_as_dicts(self, dataset_dir: Path, sample_data: list[dict]):
        """Load dataset and convert to list of dicts."""
        fileset_path = dataset_dir / "workspace" / "fileset"
        rows = load_dataset_as_dicts(fileset_path, pattern="data.json")

        assert len(rows) == 3
        assert rows[0] == sample_data[0]
        assert rows[1] == sample_data[1]
        assert rows[2] == sample_data[2]

    def test_load_preserves_types(self, tmp_path: Path):
        """Preserve data types when converting to dicts."""
        fileset_path = tmp_path / "workspace" / "typed-fileset"
        fileset_path.mkdir(parents=True)

        # Create data with various types
        data = [
            {"int_col": 42, "float_col": 3.14, "bool_col": True, "str_col": "hello"},
            {"int_col": -1, "float_col": 2.718, "bool_col": False, "str_col": "world"},
        ]
        with open(fileset_path / "data.json", "w") as f:
            json.dump(data, f)

        rows = load_dataset_as_dicts(fileset_path, pattern="data.json")

        assert rows[0]["int_col"] == 42
        assert abs(rows[0]["float_col"] - 3.14) < 0.001
        assert rows[0]["bool_col"] is True
        assert rows[0]["str_col"] == "hello"

    def test_load_as_dicts_falls_back_for_mixed_nested_jsonl(self, tmp_path: Path):
        """Fallback should load mixed nested JSONL rows without pyarrow schema inference."""
        fileset_path = tmp_path / "workspace" / "mixed-base-fileset"
        fileset_path.mkdir(parents=True)

        rows = [
            {
                "messages": [{"role": "user", "content": "q1"}],
                "tools": [
                    {
                        "type": "function",
                        "function": {
                            "name": "search",
                            "parameters": {
                                "type": "object",
                                "properties": {"page": {"type": "integer", "default": 1}},
                            },
                        },
                    }
                ],
            },
            {
                "messages": [{"role": "user", "content": "q2"}],
                "tools": [
                    {
                        "type": "function",
                        "function": {
                            "name": "search",
                            "parameters": {
                                "type": "object",
                                "properties": {"page": {"type": "string", "default": "1"}},
                            },
                        },
                    }
                ],
            },
        ]
        with open(fileset_path / "mixed.jsonl", "w", encoding="utf-8") as f:
            for row in rows:
                f.write(json.dumps(row) + "\n")

        loaded = load_dataset_as_dicts(fileset_path, pattern="mixed.jsonl")
        assert len(loaded) == 2
        assert loaded[0]["tools"][0]["function"]["parameters"]["properties"]["page"]["default"] == 1
        assert loaded[1]["tools"][0]["function"]["parameters"]["properties"]["page"]["default"] == "1"


# =============================================================================
# Test: Integration with FilesetRef
# =============================================================================


class TestFilesetRefIntegration:
    """Tests for integration with FilesetRef dataset references."""

    def test_load_from_fileset_ref_path(self, dataset_dir: Path):
        """Load dataset using FilesetRef-style path structure."""
        # Simulate the path structure after download:
        # {base_dir}/{workspace}/{fileset}/
        base_dir = dataset_dir
        ref = "workspace/fileset"

        table = load_dataset_from_ref(ref, base_dir=base_dir, pattern=None)
        assert table.num_rows > 0

    def test_load_from_fileset_ref_with_fragment(self, dataset_dir: Path):
        """Load dataset using FilesetRef with # fragment."""
        base_dir = dataset_dir
        # ref includes fragment for specific file
        ref = "workspace/fileset#data.json"

        table = load_dataset_from_ref(ref, base_dir=base_dir)
        assert table.num_rows == 3

    def test_load_from_fileset_ref_with_glob_fragment(self, dataset_dir: Path):
        """Load dataset using FilesetRef with glob fragment."""
        base_dir = dataset_dir
        ref = "workspace/fileset#*.json"

        table = load_dataset_from_ref(ref, base_dir=base_dir)
        # data.json has 3 rows
        assert table.num_rows == 3

    def test_load_from_fileset_ref_dir_not_found(self, tmp_path: Path):
        """Raise error when fileset directory doesn't exist."""
        with pytest.raises(DatasetLoadError, match="not found"):
            load_dataset_from_ref("workspace/missing-fileset", base_dir=tmp_path)


class TestFilesetRefFallbackLoading:
    """Tests for JSON fallback path when PyArrow cannot infer nested schema."""

    def test_load_from_ref_as_dicts_falls_back_for_mixed_nested_jsonl(self, tmp_path: Path):
        """Fallback loader should parse mixed-type nested JSONL rows as dicts."""
        fileset_path = tmp_path / "workspace" / "mixed-fileset"
        fileset_path.mkdir(parents=True)
        ref = "workspace/mixed-fileset#evaluation.jsonl"

        rows = [
            {
                "messages": [{"role": "user", "content": "q1"}],
                "tools": [
                    {
                        "type": "function",
                        "function": {
                            "name": "search",
                            "parameters": {
                                "type": "object",
                                "properties": {"page": {"type": "integer", "default": 1}},
                            },
                        },
                    }
                ],
                "tool_calls": [{"type": "function", "function": {"name": "search", "arguments": {"page": 1}}}],
            },
            {
                "messages": [{"role": "user", "content": "q2"}],
                "tools": [
                    {
                        "type": "function",
                        "function": {
                            "name": "search",
                            "parameters": {
                                "type": "object",
                                "properties": {"page": {"type": "string", "default": "1"}},
                            },
                        },
                    }
                ],
                "tool_calls": [{"type": "function", "function": {"name": "search", "arguments": {"page": "1"}}}],
            },
        ]

        with open(fileset_path / "evaluation.jsonl", "w", encoding="utf-8") as f:
            for row in rows:
                f.write(json.dumps(row) + "\n")

        loaded = load_dataset_from_ref_as_dicts(ref, base_dir=tmp_path)
        assert len(loaded) == 2
        assert loaded[0]["tools"][0]["function"]["parameters"]["properties"]["page"]["default"] == 1
        assert loaded[1]["tools"][0]["function"]["parameters"]["properties"]["page"]["default"] == "1"

    def test_load_from_ref_as_dicts_falls_back_for_gzipped_jsonl(self, tmp_path: Path):
        """Fallback loader should parse gzipped JSONL rows when PyArrow path fails."""
        fileset_path = tmp_path / "workspace" / "mixed-gz-fileset"
        fileset_path.mkdir(parents=True)
        ref = "workspace/mixed-gz-fileset#evaluation.jsonl.gz"

        rows = [
            {
                "messages": [{"role": "user", "content": "q1"}],
                "tools": [
                    {
                        "type": "function",
                        "function": {
                            "name": "lookup",
                            "parameters": {
                                "type": "object",
                                "properties": {"date": {"type": "string", "default": "2022-10-08"}},
                            },
                        },
                    }
                ],
                "tool_calls": [{"type": "function", "function": {"name": "lookup", "arguments": {"id": 123}}}],
            },
            {
                "messages": [{"role": "user", "content": "q2"}],
                "tools": [
                    {
                        "type": "function",
                        "function": {
                            "name": "lookup",
                            "parameters": {
                                "type": "object",
                                "properties": {"date": {"type": "string", "default": "2022-10-08"}},
                            },
                        },
                    }
                ],
                "tool_calls": [{"type": "function", "function": {"name": "lookup", "arguments": {"id": "123"}}}],
            },
        ]

        with gzip.open(fileset_path / "evaluation.jsonl.gz", "wt", encoding="utf-8") as f:
            for row in rows:
                f.write(json.dumps(row) + "\n")

        loaded = load_dataset_from_ref_as_dicts(ref, base_dir=tmp_path)
        assert len(loaded) == 2
        assert loaded[0]["tool_calls"][0]["function"]["arguments"]["id"] == 123
        assert loaded[1]["tool_calls"][0]["function"]["arguments"]["id"] == "123"
