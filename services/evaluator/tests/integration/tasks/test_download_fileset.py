# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Integration tests for the download_fileset task.

These tests verify that the download_fileset task correctly:
- Downloads files from filesets via URN paths
- Handles inline dataset data
- Properly interfaces with the Files API
- Handles edge cases (empty filesets, special characters, nested dirs)
- Reports clear errors for invalid inputs

Uses task_harness for in-memory service testing.
"""

import json
from pathlib import Path

import pytest
from nmp.core.files.service import FilesService
from nmp.evaluator.tasks import download_fileset
from nmp.testing import task_harness

# Test workspace
TEST_WORKSPACE = "test-workspace"


# =============================================================================
# Integration Tests
# =============================================================================


@pytest.mark.integration
class TestDownloadFilesetTask:
    """Integration tests for the download_fileset task."""

    @pytest.mark.asyncio
    async def test_download_inline_dataset(self, tmp_path: Path):
        """Test downloading inline dataset writes rows to JSON file."""
        dataset = {
            "rows": [
                {"input": "What is Python?", "expected": "A programming language"},
                {"input": "What is 2+2?", "expected": "4"},
            ]
        }

        async with task_harness(
            download_fileset,
            FilesService,
            config={},
            env={
                "NEMO_JOB_WORKSPACE": TEST_WORKSPACE,
            },
        ) as ctx:
            # Run task with inline dataset
            result = ctx.run_task(args=["--dataset", json.dumps(dataset), "--local-dir", str(tmp_path)])

            assert result.exit_code == 0, f"Task failed: {result.stderr}, exception={result.exception}"

        # Verify file was created
        output_file = tmp_path / "dataset.json"
        assert output_file.exists()

        # Verify content
        with open(output_file) as f:
            content = json.load(f)

        assert len(content) == 2
        assert content[0]["input"] == "What is Python?"
        assert content[1]["expected"] == "4"

    @pytest.mark.asyncio
    async def test_download_urn_dataset_directory(self, tmp_path: Path):
        """Test downloading a directory from a fileset via URN."""
        fileset_name = "test-download-dir-fileset"

        async with task_harness(
            download_fileset,
            FilesService,
            config={},
            env={
                "NEMO_JOB_WORKSPACE": TEST_WORKSPACE,
            },
        ) as ctx:
            # Setup: Create fileset with files
            ctx.sdk.files.filesets.create(
                workspace=TEST_WORKSPACE,
                name=fileset_name,
                description="Test fileset for directory download",
            )

            ctx.sdk.files.upload_content(
                content=b'{"file": 1}',
                remote_path="subdir/file1.json",
                fileset=fileset_name,
                workspace=TEST_WORKSPACE,
            )
            ctx.sdk.files.upload_content(
                content=b'{"file": 2}',
                remote_path="subdir/file2.json",
                fileset=fileset_name,
                workspace=TEST_WORKSPACE,
            )

            # Run task with URN pointing to directory
            dataset = f"{TEST_WORKSPACE}/{fileset_name}/subdir/"
            result = ctx.run_task(args=["--dataset", json.dumps(dataset), "--local-dir", str(tmp_path)])

            assert result.exit_code == 0, f"Task failed: {result.stderr}, exception={result.exception}"

            # Verify files were downloaded
            files = list(tmp_path.rglob("*.json"))
            assert len(files) >= 2

    @pytest.mark.asyncio
    async def test_download_creates_destination_directory(self, tmp_path: Path):
        """Test that download creates nested destination directories."""
        nested_dest = tmp_path / "nested" / "path" / "to" / "data"
        dataset = {"rows": [{"key": "value"}]}

        async with task_harness(
            download_fileset,
            FilesService,
            config={},
            env={
                "NEMO_JOB_WORKSPACE": TEST_WORKSPACE,
            },
        ) as ctx:
            result = ctx.run_task(args=["--dataset", json.dumps(dataset), "--local-dir", str(nested_dest)])

            assert result.exit_code == 0, f"Task failed: {result.stderr}, exception={result.exception}"

        assert nested_dest.exists()
        assert (nested_dest / "dataset.json").exists()

    @pytest.mark.asyncio
    async def test_download_urn_fileset_root(self, tmp_path: Path):
        """Test downloading from fileset root (no trailing path)."""
        fileset_name = "test-root-download"

        async with task_harness(
            download_fileset,
            FilesService,
            config={},
            env={
                "NEMO_JOB_WORKSPACE": TEST_WORKSPACE,
            },
        ) as ctx:
            # Setup
            ctx.sdk.files.filesets.create(
                workspace=TEST_WORKSPACE,
                name=fileset_name,
                description="Test fileset",
            )
            ctx.sdk.files.upload_content(
                content=json.dumps([{"id": 1}, {"id": 2}]).encode(),
                remote_path="dataset.json",
                fileset=fileset_name,
                workspace=TEST_WORKSPACE,
            )
            ctx.sdk.files.upload_content(
                content=b'{"setting": true}',
                remote_path="config.json",
                fileset=fileset_name,
                workspace=TEST_WORKSPACE,
            )

            # Run task
            dataset = f"{TEST_WORKSPACE}/{fileset_name}"
            result = ctx.run_task(args=["--dataset", json.dumps(dataset), "--local-dir", str(tmp_path)])

            assert result.exit_code == 0, f"Task failed: {result.stderr}, exception={result.exception}"

            # Verify both files downloaded
            files = list(tmp_path.rglob("*.json"))
            assert len(files) == 2

    @pytest.mark.asyncio
    async def test_download_urn_nested_subdirectories(self, tmp_path: Path):
        """Test downloading nested subdirectories recursively."""
        fileset_name = "test-nested-dirs"

        async with task_harness(
            download_fileset,
            FilesService,
            config={},
            env={
                "NEMO_JOB_WORKSPACE": TEST_WORKSPACE,
            },
        ) as ctx:
            # Setup
            ctx.sdk.files.filesets.create(
                workspace=TEST_WORKSPACE,
                name=fileset_name,
                description="Test fileset",
            )
            ctx.sdk.files.upload_content(
                content=b'{"level": 1}',
                remote_path="level1/file1.json",
                fileset=fileset_name,
                workspace=TEST_WORKSPACE,
            )
            ctx.sdk.files.upload_content(
                content=b'{"level": 2}',
                remote_path="level1/level2/file2.json",
                fileset=fileset_name,
                workspace=TEST_WORKSPACE,
            )
            ctx.sdk.files.upload_content(
                content=b'{"level": 3}',
                remote_path="level1/level2/level3/file3.json",
                fileset=fileset_name,
                workspace=TEST_WORKSPACE,
            )

            # Run task
            dataset = f"{TEST_WORKSPACE}/{fileset_name}/"
            result = ctx.run_task(args=["--dataset", json.dumps(dataset), "--local-dir", str(tmp_path)])

            assert result.exit_code == 0, f"Task failed: {result.stderr}, exception={result.exception}"

            # Verify all files downloaded
            files = list(tmp_path.rglob("*.json"))
            assert len(files) == 3

    @pytest.mark.asyncio
    async def test_download_urn_nonexistent_fileset_raises(self, tmp_path: Path):
        """Test that downloading from non-existent fileset fails."""
        async with task_harness(
            download_fileset,
            FilesService,
            config={},
            env={
                "NEMO_JOB_WORKSPACE": TEST_WORKSPACE,
            },
        ) as ctx:
            dataset = f"{TEST_WORKSPACE}/nonexistent-fileset-12345"
            result = ctx.run_task(args=["--dataset", json.dumps(dataset), "--local-dir", str(tmp_path)])

            # Task should fail
            assert result.exit_code != 0

    @pytest.mark.asyncio
    async def test_download_urn_empty_fileset(self, tmp_path: Path):
        """Test downloading from an empty fileset (no files uploaded)."""
        fileset_name = "test-empty-fileset"

        async with task_harness(
            download_fileset,
            FilesService,
            config={},
            env={
                "NEMO_JOB_WORKSPACE": TEST_WORKSPACE,
            },
        ) as ctx:
            # Setup: empty fileset
            ctx.sdk.files.filesets.create(
                workspace=TEST_WORKSPACE,
                name=fileset_name,
                description="Empty fileset",
            )

            dataset = f"{TEST_WORKSPACE}/{fileset_name}/"
            result = ctx.run_task(args=["--dataset", json.dumps(dataset), "--local-dir", str(tmp_path)])

            # Should complete without error
            assert result.exit_code == 0, f"Task failed: {result.stderr}, exception={result.exception}"
            assert tmp_path.exists()

    @pytest.mark.asyncio
    async def test_download_inline_dataset_preserves_data_types(self, tmp_path: Path):
        """Test that inline dataset preserves various JSON data types."""
        dataset = {
            "rows": [
                {
                    "string": "hello",
                    "number": 42,
                    "float": 3.14159,
                    "boolean": True,
                    "null": None,
                    "array": [1, 2, 3],
                    "nested": {"a": {"b": "c"}},
                },
            ]
        }

        async with task_harness(
            download_fileset,
            FilesService,
            config={},
            env={
                "NEMO_JOB_WORKSPACE": TEST_WORKSPACE,
            },
        ) as ctx:
            result = ctx.run_task(args=["--dataset", json.dumps(dataset), "--local-dir", str(tmp_path)])

            assert result.exit_code == 0, f"Task failed: {result.stderr}, exception={result.exception}"

        with open(tmp_path / "dataset.json") as f:
            content = json.load(f)

        row = content[0]
        assert row["string"] == "hello"
        assert row["number"] == 42
        assert abs(row["float"] - 3.14159) < 0.0001
        assert row["boolean"] is True
        assert row["null"] is None
        assert row["array"] == [1, 2, 3]
        assert row["nested"]["a"]["b"] == "c"

    @pytest.mark.asyncio
    async def test_download_urn_with_special_characters_in_path(self, tmp_path: Path):
        """Test downloading files with special characters in filenames."""
        fileset_name = "test-special-chars"

        async with task_harness(
            download_fileset,
            FilesService,
            config={},
            env={
                "NEMO_JOB_WORKSPACE": TEST_WORKSPACE,
            },
        ) as ctx:
            # Setup
            ctx.sdk.files.filesets.create(
                workspace=TEST_WORKSPACE,
                name=fileset_name,
                description="Test fileset",
            )
            ctx.sdk.files.upload_content(
                content=b'{"type": "dashes"}',
                remote_path="data-with-dashes.json",
                fileset=fileset_name,
                workspace=TEST_WORKSPACE,
            )
            ctx.sdk.files.upload_content(
                content=b'{"type": "underscores"}',
                remote_path="data_with_underscores.json",
                fileset=fileset_name,
                workspace=TEST_WORKSPACE,
            )
            ctx.sdk.files.upload_content(
                content=b'{"type": "dots"}',
                remote_path="data.multiple.dots.json",
                fileset=fileset_name,
                workspace=TEST_WORKSPACE,
            )

            dataset = f"{TEST_WORKSPACE}/{fileset_name}/"
            result = ctx.run_task(args=["--dataset", json.dumps(dataset), "--local-dir", str(tmp_path)])

            assert result.exit_code == 0, f"Task failed: {result.stderr}, exception={result.exception}"

            files = list(tmp_path.rglob("*.json"))
            assert len(files) == 3

    @pytest.mark.asyncio
    async def test_download_inline_dataset_large_rows(self, tmp_path: Path):
        """Test downloading inline dataset with many rows."""
        rows = [{"id": i, "data": f"row-{i}" * 10} for i in range(100)]
        dataset = {"rows": rows}

        async with task_harness(
            download_fileset,
            FilesService,
            config={},
            env={
                "NEMO_JOB_WORKSPACE": TEST_WORKSPACE,
            },
        ) as ctx:
            result = ctx.run_task(args=["--dataset", json.dumps(dataset), "--local-dir", str(tmp_path)])

            assert result.exit_code == 0, f"Task failed: {result.stderr}, exception={result.exception}"

        with open(tmp_path / "dataset.json") as f:
            content = json.load(f)

        assert len(content) == 100
        assert content[0]["id"] == 0
        assert content[99]["id"] == 99
