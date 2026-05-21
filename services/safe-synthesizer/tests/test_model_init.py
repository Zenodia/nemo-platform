# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Unit tests for model_init module.

Tests the model weight downloading functionality from Files API to HuggingFace cache.
Mocks at the list_fileset_files/download_file level per testing guidelines.
"""

import os
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from nmp.safe_synthesizer.tasks.safe_synthesizer.model_init import (
    DEFAULT_MODEL_FILESETS,
    ModelFileset,
    download_model_fileset,
    generate_snapshot_hash,
    get_hf_cache_dir,
    get_model_cache_path,
    init_models,
    init_models_sync,
    is_model_cached,
)


class TestCachePathHelpers:
    """Tests for HuggingFace cache path helper functions."""

    def test_get_hf_cache_dir_default(self):
        """Test default HF cache directory."""
        with patch.dict(os.environ, {}, clear=True):
            # Remove HF_HOME if set
            os.environ.pop("HF_HOME", None)
            cache_dir = get_hf_cache_dir()
            assert cache_dir == Path("/app/.cache/huggingface/hub")

    def test_get_hf_cache_dir_from_env(self):
        """Test HF cache directory from environment variable."""
        with patch.dict(os.environ, {"HF_HOME": "/custom/cache"}):
            cache_dir = get_hf_cache_dir()
            assert cache_dir == Path("/custom/cache/hub")

    def test_get_hf_cache_dir_explicit(self):
        """Test HF cache directory with explicit parameter."""
        cache_dir = get_hf_cache_dir("/explicit/path")
        assert cache_dir == Path("/explicit/path/hub")

    def test_get_model_cache_path(self):
        """Test model cache path generation follows HF convention."""
        model_path = get_model_cache_path("gretelai/gretel-gliner-bi-large-v1.0", "/test/cache")
        expected = Path("/test/cache/hub/models--gretelai--gretel-gliner-bi-large-v1.0")
        assert model_path == expected

    def test_get_model_cache_path_org_model_format(self):
        """Test model cache path handles org/model format correctly."""
        model_path = get_model_cache_path("TinyLlama/TinyLlama-1.1B-Chat-v1.0", "/cache")
        assert "models--TinyLlama--TinyLlama-1.1B-Chat-v1.0" in str(model_path)

    def test_generate_snapshot_hash(self):
        """Test snapshot hash generation is deterministic."""
        hash1 = generate_snapshot_hash("test-fileset")
        hash2 = generate_snapshot_hash("test-fileset")
        assert hash1 == hash2
        assert len(hash1) == 40  # SHA1 hex length

    def test_generate_snapshot_hash_different_inputs(self):
        """Test different inputs produce different hashes."""
        hash1 = generate_snapshot_hash("fileset-a")
        hash2 = generate_snapshot_hash("fileset-b")
        assert hash1 != hash2


class TestIsCached:
    """Tests for is_model_cached function."""

    def test_model_not_cached_no_directory(self, tmp_path):
        """Test returns False when model directory doesn't exist."""
        assert is_model_cached("org/model", str(tmp_path)) is False

    def test_model_not_cached_empty_snapshots(self, tmp_path):
        """Test returns False when snapshots directory is empty."""
        model_dir = tmp_path / "hub" / "models--org--model" / "snapshots"
        model_dir.mkdir(parents=True)
        assert is_model_cached("org/model", str(tmp_path)) is False

    def test_model_cached_with_files(self, tmp_path):
        """Test returns True when snapshot contains files."""
        snapshot_dir = tmp_path / "hub" / "models--org--model" / "snapshots" / "abc123"
        snapshot_dir.mkdir(parents=True)
        (snapshot_dir / "config.json").write_text("{}")
        assert is_model_cached("org/model", str(tmp_path)) is True


class TestModelFileset:
    """Tests for ModelFileset dataclass."""

    def test_fileset_ref_property(self):
        """Test fileset_ref combines workspace and name."""
        fileset = ModelFileset(
            workspace="safe-synthesizer",
            name="gliner-model",
            hf_model_id="gretelai/gretel-gliner-bi-large-v1.0",
        )
        assert fileset.fileset_ref == "safe-synthesizer/gliner-model"

    def test_default_model_filesets_defined(self):
        """Test default model filesets are defined."""
        assert len(DEFAULT_MODEL_FILESETS) > 0
        # Check expected models are present
        model_ids = [f.hf_model_id for f in DEFAULT_MODEL_FILESETS]
        assert "gretelai/gretel-gliner-bi-large-v1.0" in model_ids
        assert "HuggingFaceTB/SmolLM3-3B" in model_ids


class TestDownloadModelFileset:
    """Tests for download_model_fileset function."""

    @pytest.mark.asyncio
    async def test_skip_if_already_cached(self, tmp_path):
        """Test skips download if model already cached."""
        # Set up cached model
        snapshot_dir = tmp_path / "hub" / "models--org--model" / "snapshots" / "abc123"
        snapshot_dir.mkdir(parents=True)
        (snapshot_dir / "config.json").write_text("{}")

        fileset = ModelFileset(
            workspace="test",
            name="test-model",
            hf_model_id="org/model",
        )

        client = AsyncMock()
        result = await download_model_fileset(
            client,
            "http://files-api",
            fileset,
            hf_home=str(tmp_path),
            force=False,
        )

        assert result is True
        # Verify no HTTP calls were made
        client.get.assert_not_called()
        client.stream.assert_not_called()

    @pytest.mark.asyncio
    async def test_force_redownload(self, tmp_path):
        """Test force=True triggers download even if cached."""
        # Set up cached model
        snapshot_dir = tmp_path / "hub" / "models--org--model" / "snapshots" / "abc123"
        snapshot_dir.mkdir(parents=True)
        (snapshot_dir / "config.json").write_text("{}")

        fileset = ModelFileset(
            workspace="test",
            name="test-model",
            hf_model_id="org/model",
        )

        # Mock the API calls
        with patch("nmp.safe_synthesizer.tasks.safe_synthesizer.model_init.list_fileset_files") as mock_list:
            mock_list.return_value = [{"path": "config.json", "size": 100}]

            with patch("nmp.safe_synthesizer.tasks.safe_synthesizer.model_init.download_file") as mock_download:
                mock_download.return_value = None

                client = AsyncMock()
                result = await download_model_fileset(
                    client,
                    "http://files-api",
                    fileset,
                    hf_home=str(tmp_path),
                    force=True,
                )

                assert result is True
                mock_list.assert_called_once()

    @pytest.mark.asyncio
    async def test_download_creates_cache_structure(self, tmp_path):
        """Test download creates correct HF cache directory structure."""
        fileset = ModelFileset(
            workspace="safe-synthesizer",
            name="test-model",
            hf_model_id="org/my-model",
        )

        mock_files = [
            {"path": "config.json", "size": 100},
            {"path": "model.safetensors", "size": 1000},
        ]

        with patch("nmp.safe_synthesizer.tasks.safe_synthesizer.model_init.list_fileset_files") as mock_list:
            mock_list.return_value = mock_files

            with patch("nmp.safe_synthesizer.tasks.safe_synthesizer.model_init.download_file") as mock_download:
                # Simulate file creation
                async def fake_download(client, url, ws, name, path, dest):
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    dest.write_bytes(b"fake content")

                mock_download.side_effect = fake_download

                client = AsyncMock()
                result = await download_model_fileset(
                    client,
                    "http://files-api",
                    fileset,
                    hf_home=str(tmp_path),
                )

                assert result is True

                # Verify cache structure
                model_dir = tmp_path / "hub" / "models--org--my-model"
                assert model_dir.exists()

                # Verify refs/main points to snapshot
                refs_main = model_dir / "refs" / "main"
                assert refs_main.exists()
                snapshot_hash = refs_main.read_text()
                assert len(snapshot_hash) == 40

                # Verify snapshot directory has files
                snapshot_dir = model_dir / "snapshots" / snapshot_hash
                assert snapshot_dir.exists()
                assert (snapshot_dir / "config.json").exists()
                assert (snapshot_dir / "model.safetensors").exists()

    @pytest.mark.asyncio
    async def test_download_empty_fileset(self, tmp_path):
        """Test returns False for empty fileset."""
        fileset = ModelFileset(
            workspace="test",
            name="empty-model",
            hf_model_id="org/empty",
        )

        with patch("nmp.safe_synthesizer.tasks.safe_synthesizer.model_init.list_fileset_files") as mock_list:
            mock_list.return_value = []

            client = AsyncMock()
            result = await download_model_fileset(
                client,
                "http://files-api",
                fileset,
                hf_home=str(tmp_path),
            )

            assert result is False

    @pytest.mark.asyncio
    async def test_download_handles_http_error(self, tmp_path):
        """Test handles HTTP errors gracefully."""
        import httpx

        fileset = ModelFileset(
            workspace="test",
            name="error-model",
            hf_model_id="org/error",
        )

        with patch("nmp.safe_synthesizer.tasks.safe_synthesizer.model_init.list_fileset_files") as mock_list:
            mock_list.side_effect = httpx.HTTPStatusError(
                "Not found",
                request=MagicMock(),
                response=MagicMock(status_code=404),
            )

            client = AsyncMock()
            result = await download_model_fileset(
                client,
                "http://files-api",
                fileset,
                hf_home=str(tmp_path),
            )

            assert result is False


class TestInitModels:
    """Tests for init_models and init_models_sync functions."""

    @pytest.mark.asyncio
    async def test_init_models_downloads_all(self, tmp_path):
        """Test init_models downloads all specified filesets."""
        filesets = [
            ModelFileset(workspace="test", name="model-a", hf_model_id="org/model-a"),
            ModelFileset(workspace="test", name="model-b", hf_model_id="org/model-b"),
        ]

        with patch("nmp.safe_synthesizer.tasks.safe_synthesizer.model_init.download_model_fileset") as mock_download:
            mock_download.return_value = True

            results = await init_models(
                "http://files-api",
                filesets=filesets,
                hf_home=str(tmp_path),
            )

            assert results == {"org/model-a": True, "org/model-b": True}
            assert mock_download.call_count == 2

    @pytest.mark.asyncio
    async def test_init_models_partial_failure(self, tmp_path):
        """Test init_models reports partial failures."""
        filesets = [
            ModelFileset(workspace="test", name="model-a", hf_model_id="org/model-a"),
            ModelFileset(workspace="test", name="model-b", hf_model_id="org/model-b"),
        ]

        with patch("nmp.safe_synthesizer.tasks.safe_synthesizer.model_init.download_model_fileset") as mock_download:
            # First succeeds, second fails
            mock_download.side_effect = [True, False]

            results = await init_models(
                "http://files-api",
                filesets=filesets,
                hf_home=str(tmp_path),
            )

            assert results == {"org/model-a": True, "org/model-b": False}

    def test_init_models_sync_no_url(self):
        """Test init_models_sync returns empty dict if no URL configured."""
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("NMP_FILES_URL", None)
            os.environ.pop("NMP_FILES_API_URL", None)

            results = init_models_sync(files_api_url=None)
            assert results == {}

    def test_init_models_sync_with_url(self, tmp_path):
        """Test init_models_sync calls init_models with URL."""
        with patch("nmp.safe_synthesizer.tasks.safe_synthesizer.model_init.init_models") as mock_init:
            mock_init.return_value = {"org/model": True}

            results = init_models_sync(
                files_api_url="http://test-api",
                filesets=[],
                hf_home=str(tmp_path),
            )

            mock_init.assert_called_once()
            assert results == {"org/model": True}

    def test_init_models_sync_uses_env_var(self, tmp_path):
        """Test init_models_sync reads URL from environment."""
        with patch.dict(os.environ, {"NMP_FILES_URL": "http://env-api"}):
            with patch("nmp.safe_synthesizer.tasks.safe_synthesizer.model_init.init_models") as mock_init:
                mock_init.return_value = {}

                init_models_sync(filesets=[], hf_home=str(tmp_path))

                # Verify the URL from env was used
                call_args = mock_init.call_args
                assert call_args.kwargs["files_api_url"] == "http://env-api"
