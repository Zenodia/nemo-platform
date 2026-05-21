# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Unit tests for FilesConfig (allowed_external_hosts and related)."""

import pytest
from nmp.common.config import Configuration
from nmp.core.files.config import FilesConfig


class TestFilesConfigAllowedExternalHosts:
    """Tests for FilesConfig.allowed_external_hosts and get_allowed_external_hosts()."""

    def test_allowed_external_hosts_default(self) -> None:
        """Test allowed_external_hosts default value and get_allowed_external_hosts() parsing."""
        config = FilesConfig()
        assert config.allowed_external_hosts == "https://api.ngc.nvidia.com,https://huggingface.co"
        assert config.get_allowed_external_hosts() == [
            "https://api.ngc.nvidia.com",
            "https://huggingface.co",
        ]

    def test_allowed_external_hosts_from_env_var(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test NMP_FILES_ALLOWED_EXTERNAL_HOSTS env var sets allowed_external_hosts."""
        monkeypatch.setenv(
            "NMP_FILES_ALLOWED_EXTERNAL_HOSTS",
            "https://proxy.corp.example.com,https://api.ngc.nvidia.com",
        )
        config = FilesConfig()
        assert config.allowed_external_hosts == ("https://proxy.corp.example.com,https://api.ngc.nvidia.com")
        assert config.get_allowed_external_hosts() == [
            "https://proxy.corp.example.com",
            "https://api.ngc.nvidia.com",
        ]

    def test_allowed_external_hosts_from_yaml(self) -> None:
        """Test files.allowed_external_hosts loaded from YAML via global_settings_to_service_config."""
        settings = {
            "files": {
                "allowed_external_hosts": "https://hf.example.com,https://ngc.example.com",
            },
        }
        config = Configuration.global_settings_to_service_config(settings, FilesConfig)
        assert config.allowed_external_hosts == "https://hf.example.com,https://ngc.example.com"
        assert config.get_allowed_external_hosts() == [
            "https://hf.example.com",
            "https://ngc.example.com",
        ]

    def test_get_allowed_external_hosts_strips_whitespace(self) -> None:
        """Test get_allowed_external_hosts() strips whitespace and skips empty segments."""
        config = FilesConfig(allowed_external_hosts="  https://a.com , https://b.com  , , https://c.com  ")
        assert config.get_allowed_external_hosts() == [
            "https://a.com",
            "https://b.com",
            "https://c.com",
        ]

    def test_allowed_external_hosts_invalid_url_raises(self) -> None:
        """Test that invalid URL in allowed_external_hosts raises during validation."""
        from pydantic import ValidationError

        with pytest.raises(ValidationError, match="IPv4 or IPv6"):
            FilesConfig(allowed_external_hosts="https://valid.com,http://[zzz]")

    def test_allowed_external_hosts_missing_netloc_raises(self) -> None:
        """Test that URL without scheme/netloc raises ValueError from model validator."""
        with pytest.raises(ValueError, match="must be a valid URL"):
            FilesConfig(allowed_external_hosts="https://valid.com,not-a-url")
