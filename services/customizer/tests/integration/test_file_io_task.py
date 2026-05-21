# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Integration tests for the file I/O task."""

import json
import os
import tempfile

import nmp.customizer.tasks.file_io as file_io
import pytest
from nmp.core.files.service import FilesService
from nmp.core.jobs.service import JobsService
from nmp.testing import task_harness


class TestFileDownloadTask:
    """Integration tests for the file download task module."""

    @pytest.mark.asyncio
    async def test_task_downloads_files(self):
        """Test that task downloads files from a fileset to local storage."""
        workspace = "default"
        fileset_name = "test-download-fileset"
        dest_dir = "download_files"
        nested_1_dir_name = "nested_1"
        nested_2_dir_name = "nested_2"
        file1_name = "file1.txt"
        file2_name = "file2.txt"
        file1_content = "Content of file 1 for download"
        file2_content = "Content of file 2 for download"

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create download_config.json
            download_config = {
                "download": [
                    {
                        "src": f"{workspace}/{fileset_name}",
                        "dest": dest_dir,
                    }
                ],
                "upload": [],
            }
            download_config_path = os.path.join(tmpdir, "download_config.json")
            with open(download_config_path, "w") as f:
                json.dump(download_config, f)

            env = {
                "NEMO_JOB_ID": "test-download-file-job-123",
                "NEMO_JOB_STEP_CONFIG_FILE_PATH": download_config_path,
                "NEMO_JOB_STEP": "FileDownload",
                "NEMO_JOB_TASK": "download-task",
                "NEMO_JOB_PERSISTENT_JOB_STORAGE_PATH": tmpdir,
            }
            async with task_harness(
                file_io,
                FilesService,
                config={},
                env=env,
            ) as ctx:
                # Setup: Create fileset and upload files before running download task
                ctx.sdk.files.filesets.create(workspace=workspace, name=fileset_name)

                # Upload test files to the fileset
                ctx.sdk.files.upload_content(
                    content=file1_content.encode("utf-8"),
                    remote_path=f"{nested_1_dir_name}/{file1_name}",
                    fileset=fileset_name,
                    workspace=workspace,
                )
                ctx.sdk.files.upload_content(
                    content=file2_content.encode("utf-8"),
                    remote_path=f"{nested_2_dir_name}/{file2_name}",
                    fileset=fileset_name,
                    workspace=workspace,
                )

                result = ctx.run_task()

                assert result.exit_code == 0, f"Task failed: stdout={result.stdout}, stderr={result.stderr}"
                assert result.exception is None

                download_dir = os.path.join(tmpdir, dest_dir)
                file1_path = os.path.join(download_dir, nested_1_dir_name, file1_name)
                file2_path = os.path.join(download_dir, nested_2_dir_name, file2_name)

                assert os.path.exists(file1_path), f"File not downloaded: {file1_path}"
                assert os.path.exists(file2_path), f"File not downloaded: {file2_path}"

                with open(file1_path) as f:
                    assert f.read() == file1_content

                with open(file2_path) as f:
                    assert f.read() == file2_content

    @pytest.mark.asyncio
    async def test_task_downloads_empty_fileset(self):
        """Test that task handles empty fileset gracefully."""
        workspace = "default"
        fileset_name = "test-empty-fileset"
        dest_dir = "download_empty"

        with tempfile.TemporaryDirectory() as tmpdir:
            download_config = {
                "download": [
                    {
                        "src": f"{workspace}/{fileset_name}",
                        "dest": dest_dir,
                    }
                ],
                "upload": [],
            }
            download_config_path = os.path.join(tmpdir, "download_config.json")
            with open(download_config_path, "w") as f:
                json.dump(download_config, f)

            env = {
                "NEMO_JOB_ID": "test-download-empty-job-123",
                "NEMO_JOB_STEP_CONFIG_FILE_PATH": download_config_path,
                "NEMO_JOB_STEP": "FileDownload",
                "NEMO_JOB_TASK": "download-task",
                "NEMO_JOB_PERSISTENT_JOB_STORAGE_PATH": tmpdir,
            }
            async with task_harness(
                file_io,
                FilesService,
                config={},
                env=env,
            ) as ctx:
                # Create empty fileset
                ctx.sdk.files.filesets.create(workspace=workspace, name=fileset_name)

                result = ctx.run_task()

                assert result.exit_code == 0, f"Task failed: stdout={result.stdout}, stderr={result.stderr}"
                assert result.exception is None

    @pytest.mark.asyncio
    async def test_task_fails_for_nonexistent_fileset(self):
        """Test that task fails when fileset does not exist."""
        workspace = "default"
        fileset_name = "nonexistent-fileset"
        dest_dir = "download_nonexistent"

        with tempfile.TemporaryDirectory() as tmpdir:
            download_config = {
                "download": [
                    {
                        "src": f"{workspace}/{fileset_name}",
                        "dest": dest_dir,
                    }
                ],
                "upload": [],
            }
            download_config_path = os.path.join(tmpdir, "download_config.json")
            with open(download_config_path, "w") as f:
                json.dump(download_config, f)

            env = {
                "NEMO_JOB_ID": "test-download-nonexistent-job-123",
                "NEMO_JOB_STEP_CONFIG_FILE_PATH": download_config_path,
                "NEMO_JOB_STEP": "FileDownload",
                "NEMO_JOB_TASK": "download-task",
                "NEMO_JOB_PERSISTENT_JOB_STORAGE_PATH": tmpdir,
            }
            async with task_harness(
                file_io,
                FilesService,
                config={},
                env=env,
            ) as ctx:
                # Do NOT create the fileset - it should not exist

                result = ctx.run_task()

                # Task should fail because fileset doesn't exist
                assert result.exit_code == 1, f"Task should have failed: stdout={result.stdout}, stderr={result.stderr}"


class TestFileUploadTask:
    """Integration tests for the file upload task module."""

    @pytest.mark.asyncio
    async def test_task_uploads_files(self):
        """Test that task writes default message to file API."""
        workspace = "default"
        file_entity_name = "test-upload-fileset"
        src_dir = "upload_files"
        nested_1_dir_name = "nested_1"
        nested_2_dir_name = "nested_2"
        file1_name = "file1.txt"
        file2_name = "file2.txt"
        file2_content = "Content of file 2"
        file1_content = "Content of file 1"
        job_id = "test-upload-file-job-123"
        task_name = "upload-task"

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create upload_config.json
            upload_config = {
                "download": [],
                "upload": [
                    {
                        "src": src_dir,
                        "dest": f"{workspace}/{file_entity_name}",
                    }
                ],
            }
            upload_config_path = os.path.join(tmpdir, "upload_config.json")
            with open(upload_config_path, "w") as f:
                json.dump(upload_config, f)

            # Create upload_files directory structure with test files
            upload_files_dir = os.path.join(tmpdir, src_dir)
            nested_1_dir = os.path.join(upload_files_dir, nested_1_dir_name)
            nested_2_dir = os.path.join(upload_files_dir, nested_2_dir_name)
            os.makedirs(nested_1_dir)
            os.makedirs(nested_2_dir)

            with open(os.path.join(nested_1_dir, file1_name), "w") as f:
                f.write(file1_content)
            with open(os.path.join(nested_2_dir, file2_name), "w") as f:
                f.write(file2_content)

            env = {
                "NEMO_JOB_ID": job_id,
                "NEMO_JOB_WORKSPACE": workspace,
                "NEMO_JOB_STEP_CONFIG_FILE_PATH": upload_config_path,
                "NEMO_JOB_STEP": "FileUpload",
                "NEMO_JOB_TASK": task_name,
                "NEMO_JOB_PERSISTENT_JOB_STORAGE_PATH": tmpdir,
            }
            async with task_harness(
                file_io,
                FilesService,
                JobsService,
                config={},
                env=env,
            ) as ctx:
                result = ctx.run_task()

                assert result.exit_code == 0, f"Task failed: stdout={result.stdout}, stderr={result.stderr}"
                assert result.exception is None

                # Verify the file was uploaded to the auto-created fileset
                # Note: When uploading a directory, we upload its CONTENTS (not the directory itself)
                # so files are at nested_1/file1.txt, not upload_files/nested_1/file1.txt
                content = ctx.sdk.files.download_content(
                    remote_path=f"{nested_1_dir_name}/{file1_name}",
                    fileset=file_entity_name,
                    workspace=workspace,
                ).decode("utf-8")
                assert content == file1_content

                content = ctx.sdk.files.download_content(
                    remote_path=f"{nested_2_dir_name}/{file2_name}",
                    fileset=file_entity_name,
                    workspace=workspace,
                ).decode("utf-8")
                assert content == file2_content

    @pytest.mark.asyncio
    async def test_task_fails_for_nonexistent_source_directory(self):
        """Test that task fails when source directory does not exist."""
        workspace = "default"
        file_entity_name = "test-upload-nonexistent-src"
        src_dir = "nonexistent_directory"

        with tempfile.TemporaryDirectory() as tmpdir:
            upload_config = {
                "download": [],
                "upload": [
                    {
                        "src": src_dir,
                        "dest": f"{workspace}/{file_entity_name}",
                    }
                ],
            }
            upload_config_path = os.path.join(tmpdir, "upload_config.json")
            with open(upload_config_path, "w") as f:
                json.dump(upload_config, f)

            # Do NOT create the source directory - it should not exist

            env = {
                "NEMO_JOB_ID": "test-upload-nonexistent-src-job-123",
                "NEMO_JOB_STEP_CONFIG_FILE_PATH": upload_config_path,
                "NEMO_JOB_STEP": "FileUpload",
                "NEMO_JOB_TASK": "upload-task",
                "NEMO_JOB_PERSISTENT_JOB_STORAGE_PATH": tmpdir,
            }
            async with task_harness(
                file_io,
                FilesService,
                config={},
                env=env,
            ) as ctx:
                result = ctx.run_task()

                # Task should fail because source directory doesn't exist
                assert result.exit_code == 1, f"Task should have failed: stdout={result.stdout}, stderr={result.stderr}"

    @pytest.mark.asyncio
    async def test_task_uploads_single_file(self):
        """Test that task successfully uploads a single file as source."""
        workspace = "default"
        file_entity_name = "test-upload-single-file"
        src_file_name = "source_file.txt"
        file_content = "This is a single file upload"

        with tempfile.TemporaryDirectory() as tmpdir:
            upload_config = {
                "download": [],
                "upload": [
                    {
                        "src": src_file_name,
                        "dest": f"{workspace}/{file_entity_name}",
                    }
                ],
            }
            upload_config_path = os.path.join(tmpdir, "upload_config.json")
            with open(upload_config_path, "w") as f:
                json.dump(upload_config, f)

            # Create a single file to upload
            file_path = os.path.join(tmpdir, src_file_name)
            with open(file_path, "w") as f:
                f.write(file_content)

            env = {
                "NEMO_JOB_ID": "test-upload-single-file-job-123",
                "NEMO_JOB_STEP_CONFIG_FILE_PATH": upload_config_path,
                "NEMO_JOB_STEP": "FileUpload",
                "NEMO_JOB_TASK": "upload-task",
                "NEMO_JOB_PERSISTENT_JOB_STORAGE_PATH": tmpdir,
            }
            async with task_harness(
                file_io,
                FilesService,
                config={},
                env=env,
            ) as ctx:
                result = ctx.run_task()

                # Task should succeed when uploading a single file
                assert result.exit_code == 0, f"Task failed: stdout={result.stdout}, stderr={result.stderr}"
                assert result.exception is None

                # Verify the file was uploaded to the fileset
                content = ctx.sdk.files.download_content(
                    remote_path=src_file_name,
                    fileset=file_entity_name,
                    workspace=workspace,
                ).decode("utf-8")
                assert content == file_content

    @pytest.mark.asyncio
    async def test_task_uploads_empty_directory(self):
        """Test that task handles empty source directory gracefully."""
        workspace = "default"
        file_entity_name = "test-upload-empty-dir"
        src_dir = "empty_directory"

        with tempfile.TemporaryDirectory() as tmpdir:
            upload_config = {
                "download": [],
                "upload": [
                    {
                        "src": src_dir,
                        "dest": f"{workspace}/{file_entity_name}",
                    }
                ],
            }
            upload_config_path = os.path.join(tmpdir, "upload_config.json")
            with open(upload_config_path, "w") as f:
                json.dump(upload_config, f)

            # Create an empty directory
            empty_dir_path = os.path.join(tmpdir, src_dir)
            os.makedirs(empty_dir_path)

            env = {
                "NEMO_JOB_ID": "test-upload-empty-dir-job-123",
                "NEMO_JOB_STEP_CONFIG_FILE_PATH": upload_config_path,
                "NEMO_JOB_STEP": "FileUpload",
                "NEMO_JOB_TASK": "upload-task",
                "NEMO_JOB_PERSISTENT_JOB_STORAGE_PATH": tmpdir,
            }
            async with task_harness(
                file_io,
                FilesService,
                config={},
                env=env,
            ) as ctx:
                result = ctx.run_task()

                # Task should succeed but upload nothing
                assert result.exit_code == 0, f"Task failed: stdout={result.stdout}, stderr={result.stderr}"
                assert result.exception is None
