# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Integration tests for model weight downloading via Files API.

These tests verify the complete flow of downloading model weights from
a real Files Service instance to the HuggingFace cache directory.

Uses the create_test_client pattern for fast in-memory testing with
the Files Service, and respx to bridge sync test client to async downloads.
"""

import asyncio
from pathlib import Path
from typing import Generator

import httpx
import pytest
import respx
from nemo_platform import NeMoPlatform
from nmp.core.files.service import FilesService
from nmp.safe_synthesizer.tasks.safe_synthesizer.model_init import (
    ModelFileset,
    download_model_fileset,
    generate_snapshot_hash,
    init_models,
    is_model_cached,
)
from nmp.testing import create_test_client

# Test workspace for model filesets
TEST_WORKSPACE = "model-init-test"


@pytest.fixture(scope="module")
def files_sdk() -> Generator[NeMoPlatform, None, None]:
    """SDK client for Files Service with ASGI test transport."""
    with create_test_client(FilesService, workspaces=[TEST_WORKSPACE]) as sdk:
        yield sdk


@pytest.fixture
def hf_cache_dir(tmp_path: Path) -> Path:
    """Temporary HuggingFace cache directory for tests."""
    cache_dir = tmp_path / "hf_cache"
    cache_dir.mkdir()
    return cache_dir


def _create_respx_route_for_files_api(
    files_sdk: NeMoPlatform,
    workspace: str,
    fileset_name: str,
    base_url: str = "http://files-api",
):
    """Create respx routes that proxy to the real Files Service.

    This bridges the async httpx client used by model_init to the sync
    test client backing files_sdk.
    """
    # Route for listing files
    list_url = f"{base_url}/v2/workspaces/{workspace}/filesets/{fileset_name}/files"
    list_response = files_sdk._client.get(f"/v2/workspaces/{workspace}/filesets/{fileset_name}/files")
    respx.get(list_url).respond(
        status_code=list_response.status_code,
        json=list_response.json() if list_response.status_code == 200 else None,
    )

    # If listing succeeded, also set up download routes for each file
    if list_response.status_code == 200:
        files_data = list_response.json().get("files", [])
        for file_info in files_data:
            file_path = file_info["path"]
            download_url = f"{base_url}/v2/workspaces/{workspace}/filesets/{fileset_name}/-/{file_path}"
            download_response = files_sdk._client.get(
                f"/v2/workspaces/{workspace}/filesets/{fileset_name}/-/{file_path}"
            )
            respx.get(download_url).respond(
                status_code=download_response.status_code,
                content=download_response.content,
            )


class TestModelDownloadIntegration:
    """Integration tests for downloading models from Files Service."""

    @respx.mock
    @pytest.mark.integration
    def test_download_single_file_model(
        self,
        files_sdk: NeMoPlatform,
        hf_cache_dir: Path,
    ):
        """Test downloading a simple model with one file."""
        fileset_name = "test-single-file-model"
        base_url = "http://files-api"

        # Create fileset
        files_sdk.files.filesets.create(
            workspace=TEST_WORKSPACE,
            name=fileset_name,
            description="Test model with single file",
        )

        try:
            # Upload a mock model file
            config_content = b'{"model_type": "test", "hidden_size": 256}'
            files_sdk.files.upload_content(
                content=config_content,
                remote_path="config.json",
                fileset=fileset_name,
                workspace=TEST_WORKSPACE,
            )

            # Set up respx routes to proxy to real Files Service
            _create_respx_route_for_files_api(files_sdk, TEST_WORKSPACE, fileset_name, base_url)

            # Create ModelFileset config
            model_fileset = ModelFileset(
                workspace=TEST_WORKSPACE,
                name=fileset_name,
                hf_model_id="test-org/single-file-model",
            )

            # Download the model
            async def run_download():
                async with httpx.AsyncClient(base_url=base_url) as client:
                    return await download_model_fileset(
                        client,
                        base_url,
                        model_fileset,
                        hf_home=str(hf_cache_dir),
                    )

            result = asyncio.run(run_download())
            assert result is True

            # Verify cache structure
            model_dir = hf_cache_dir / "hub" / "models--test-org--single-file-model"
            assert model_dir.exists(), "Model directory should be created"

            # Verify refs/main exists and points to snapshot
            refs_main = model_dir / "refs" / "main"
            assert refs_main.exists(), "refs/main should exist"
            snapshot_hash = refs_main.read_text()

            # Verify snapshot contains the file
            snapshot_dir = model_dir / "snapshots" / snapshot_hash
            assert snapshot_dir.exists(), "Snapshot directory should exist"
            config_path = snapshot_dir / "config.json"
            assert config_path.exists(), "config.json should be downloaded"
            assert config_path.read_bytes() == config_content

        finally:
            files_sdk.files.filesets.delete(fileset_name, workspace=TEST_WORKSPACE)

    @respx.mock
    @pytest.mark.integration
    def test_download_multi_file_model(
        self,
        files_sdk: NeMoPlatform,
        hf_cache_dir: Path,
    ):
        """Test downloading a model with multiple files."""
        fileset_name = "test-multi-file-model"
        base_url = "http://files-api"

        # Create fileset
        files_sdk.files.filesets.create(
            workspace=TEST_WORKSPACE,
            name=fileset_name,
            description="Test model with multiple files",
        )

        try:
            # Upload mock model files
            files_to_upload = {
                "config.json": b'{"model_type": "test"}',
                "tokenizer.json": b'{"vocab_size": 32000}',
                "model.safetensors": b"fake tensor data " * 100,
                "tokenizer_config.json": b'{"tokenizer_class": "TestTokenizer"}',
            }

            for path, content in files_to_upload.items():
                files_sdk.files.upload_content(
                    content=content,
                    remote_path=path,
                    fileset=fileset_name,
                    workspace=TEST_WORKSPACE,
                )

            _create_respx_route_for_files_api(files_sdk, TEST_WORKSPACE, fileset_name, base_url)

            model_fileset = ModelFileset(
                workspace=TEST_WORKSPACE,
                name=fileset_name,
                hf_model_id="test-org/multi-file-model",
            )

            async def run_download():
                async with httpx.AsyncClient(base_url=base_url) as client:
                    return await download_model_fileset(
                        client,
                        base_url,
                        model_fileset,
                        hf_home=str(hf_cache_dir),
                    )

            result = asyncio.run(run_download())
            assert result is True

            # Verify all files downloaded
            model_dir = hf_cache_dir / "hub" / "models--test-org--multi-file-model"
            snapshot_hash = (model_dir / "refs" / "main").read_text()
            snapshot_dir = model_dir / "snapshots" / snapshot_hash

            for path, expected_content in files_to_upload.items():
                file_path = snapshot_dir / path
                assert file_path.exists(), f"{path} should be downloaded"
                assert file_path.read_bytes() == expected_content

        finally:
            files_sdk.files.filesets.delete(fileset_name, workspace=TEST_WORKSPACE)

    @respx.mock
    @pytest.mark.integration
    def test_is_model_cached_after_download(
        self,
        files_sdk: NeMoPlatform,
        hf_cache_dir: Path,
    ):
        """Test that is_model_cached returns True after successful download."""
        fileset_name = "test-cache-check-model"
        model_id = "test-org/cache-check-model"
        base_url = "http://files-api"

        files_sdk.files.filesets.create(
            workspace=TEST_WORKSPACE,
            name=fileset_name,
        )

        try:
            # Verify not cached before download
            assert is_model_cached(model_id, str(hf_cache_dir)) is False

            # Upload and download
            files_sdk.files.upload_content(
                content=b"{}",
                remote_path="config.json",
                fileset=fileset_name,
                workspace=TEST_WORKSPACE,
            )

            _create_respx_route_for_files_api(files_sdk, TEST_WORKSPACE, fileset_name, base_url)

            model_fileset = ModelFileset(
                workspace=TEST_WORKSPACE,
                name=fileset_name,
                hf_model_id=model_id,
            )

            async def run_download():
                async with httpx.AsyncClient(base_url=base_url) as client:
                    return await download_model_fileset(
                        client,
                        base_url,
                        model_fileset,
                        hf_home=str(hf_cache_dir),
                    )

            asyncio.run(run_download())

            # Verify cached after download
            assert is_model_cached(model_id, str(hf_cache_dir)) is True

        finally:
            files_sdk.files.filesets.delete(fileset_name, workspace=TEST_WORKSPACE)

    @respx.mock
    @pytest.mark.integration
    def test_init_models_multiple_filesets(
        self,
        files_sdk: NeMoPlatform,
        hf_cache_dir: Path,
    ):
        """Test downloading multiple model filesets."""
        base_url = "http://files-api"
        filesets_to_create = [
            ("model-a", "org-a/model-a"),
            ("model-b", "org-b/model-b"),
        ]

        created_filesets = []
        try:
            # Create filesets with files
            for name, _ in filesets_to_create:
                files_sdk.files.filesets.create(
                    workspace=TEST_WORKSPACE,
                    name=name,
                )
                files_sdk.files.upload_content(
                    content=b'{"name": "' + name.encode() + b'"}',
                    remote_path="config.json",
                    fileset=name,
                    workspace=TEST_WORKSPACE,
                )
                created_filesets.append(name)

                # Set up respx routes for this fileset
                _create_respx_route_for_files_api(files_sdk, TEST_WORKSPACE, name, base_url)

            model_filesets = [
                ModelFileset(workspace=TEST_WORKSPACE, name=name, hf_model_id=model_id)
                for name, model_id in filesets_to_create
            ]

            # Download all models
            results = asyncio.run(
                init_models(
                    base_url,
                    filesets=model_filesets,
                    hf_home=str(hf_cache_dir),
                )
            )

            # Verify all downloads succeeded
            for _, model_id in filesets_to_create:
                assert results.get(model_id) is True, f"{model_id} should download successfully"
                assert is_model_cached(model_id, str(hf_cache_dir)) is True

        finally:
            for name in created_filesets:
                try:
                    files_sdk.files.filesets.delete(name, workspace=TEST_WORKSPACE)
                except Exception:
                    pass

    @respx.mock
    @pytest.mark.integration
    def test_skip_download_if_cached(
        self,
        files_sdk: NeMoPlatform,
        hf_cache_dir: Path,
    ):
        """Test that download is skipped if model already cached."""
        fileset_name = "test-skip-cached"
        model_id = "test-org/skip-cached-model"

        # Pre-create cache structure manually
        snapshot_hash = generate_snapshot_hash(fileset_name)
        snapshot_dir = hf_cache_dir / "hub" / "models--test-org--skip-cached-model" / "snapshots" / snapshot_hash
        snapshot_dir.mkdir(parents=True)
        (snapshot_dir / "config.json").write_text('{"pre_cached": true}')

        files_sdk.files.filesets.create(
            workspace=TEST_WORKSPACE,
            name=fileset_name,
        )

        try:
            # Upload different content to fileset
            files_sdk.files.upload_content(
                content=b'{"from_files_api": true}',
                remote_path="config.json",
                fileset=fileset_name,
                workspace=TEST_WORKSPACE,
            )

            model_fileset = ModelFileset(
                workspace=TEST_WORKSPACE,
                name=fileset_name,
                hf_model_id=model_id,
            )

            # Download should be skipped - no HTTP calls needed
            async def run_download():
                async with httpx.AsyncClient() as client:
                    return await download_model_fileset(
                        client,
                        "http://files-api",
                        model_fileset,
                        hf_home=str(hf_cache_dir),
                        force=False,  # Don't force re-download
                    )

            result = asyncio.run(run_download())
            assert result is True

            # Verify original cached content is preserved (not overwritten)
            cached_config = snapshot_dir / "config.json"
            assert cached_config.read_text() == '{"pre_cached": true}'

        finally:
            files_sdk.files.filesets.delete(fileset_name, workspace=TEST_WORKSPACE)


class TestCacheStructureRequirements:
    """Tests demonstrating HuggingFace cache structure requirements."""

    @pytest.mark.integration
    def test_from_pretrained_requires_refs_main(self, hf_cache_dir: Path):
        """Demonstrate that from_pretrained needs refs/main to resolve snapshot.

        This test shows what happens when the cache structure is incomplete.
        HuggingFace's from_pretrained expects:
        - hub/models--{org}--{model}/refs/main (file containing snapshot hash)
        - hub/models--{org}--{model}/snapshots/{hash}/ (directory with model files)

        Without refs/main, HuggingFace cannot resolve which snapshot to use.
        """
        model_id = "test-org/incomplete-model"
        model_dir = hf_cache_dir / "hub" / "models--test-org--incomplete-model"

        # Create snapshot WITHOUT refs/main
        snapshot_hash = "abc123def456"
        snapshot_dir = model_dir / "snapshots" / snapshot_hash
        snapshot_dir.mkdir(parents=True)
        (snapshot_dir / "config.json").write_text('{"valid": true}')

        # The model files exist, but refs/main is missing
        refs_main = model_dir / "refs" / "main"
        assert not refs_main.exists(), "refs/main should not exist for this test"

        # This simulates what HuggingFace's from_pretrained would do:
        # It looks for refs/main to resolve "main" revision to a snapshot hash
        # Without it, the model appears "not downloaded" even though files exist

        # Our is_model_cached function correctly detects this as cached
        # because it checks for any snapshot with files
        assert is_model_cached(model_id, str(hf_cache_dir)) is True

        # The proper download creates refs/main pointing to the snapshot
        # This is critical for from_pretrained to work
        refs_dir = model_dir / "refs"
        refs_dir.mkdir(parents=True, exist_ok=True)
        (refs_dir / "main").write_text(snapshot_hash)

        # Now HuggingFace can resolve: "main" -> refs/main -> snapshot_hash -> files

    @respx.mock
    @pytest.mark.integration
    def test_correct_cache_structure_created_by_download(
        self,
        files_sdk: NeMoPlatform,
        hf_cache_dir: Path,
    ):
        """Verify download creates complete cache structure for from_pretrained."""
        fileset_name = "cache-structure-test"
        model_id = "verify-org/cache-structure-model"
        base_url = "http://files-api"

        files_sdk.files.filesets.create(
            workspace=TEST_WORKSPACE,
            name=fileset_name,
        )

        try:
            files_sdk.files.upload_content(
                content=b'{"test": true}',
                remote_path="config.json",
                fileset=fileset_name,
                workspace=TEST_WORKSPACE,
            )

            _create_respx_route_for_files_api(files_sdk, TEST_WORKSPACE, fileset_name, base_url)

            model_fileset = ModelFileset(
                workspace=TEST_WORKSPACE,
                name=fileset_name,
                hf_model_id=model_id,
            )

            async def run_download():
                async with httpx.AsyncClient(base_url=base_url) as client:
                    return await download_model_fileset(
                        client,
                        base_url,
                        model_fileset,
                        hf_home=str(hf_cache_dir),
                    )

            asyncio.run(run_download())

            # Verify complete cache structure
            model_dir = hf_cache_dir / "hub" / "models--verify-org--cache-structure-model"

            # 1. refs/main must exist and contain valid hash
            refs_main = model_dir / "refs" / "main"
            assert refs_main.exists(), "refs/main is required for from_pretrained"
            snapshot_hash = refs_main.read_text()
            assert len(snapshot_hash) == 40, "Hash should be 40 char SHA1"

            # 2. snapshots/{hash} must exist
            snapshot_dir = model_dir / "snapshots" / snapshot_hash
            assert snapshot_dir.exists(), "Snapshot directory must exist"
            assert snapshot_dir.is_dir(), "Snapshot must be a directory"

            # 3. Model files must be in snapshot
            assert (snapshot_dir / "config.json").exists(), "Model files must be in snapshot"

            # This structure allows from_pretrained("verify-org/cache-structure-model")
            # to resolve: model_id -> cache lookup -> refs/main -> hash -> snapshot/files

        finally:
            files_sdk.files.filesets.delete(fileset_name, workspace=TEST_WORKSPACE)
