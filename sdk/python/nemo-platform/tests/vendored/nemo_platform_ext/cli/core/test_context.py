# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

from nemo_platform.cli.core.context import CLIContext


def test_context_instances_are_independent():
    """Test that CLIContext instances don't share state."""
    ctx1 = CLIContext(overrides={"base_url": "http://ctx1.example.com"})
    ctx2 = CLIContext(overrides={"base_url": "http://ctx2.example.com"})

    assert ctx1.overrides["base_url"] == "http://ctx1.example.com"
    assert ctx2.overrides["base_url"] == "http://ctx2.example.com"


def test_verbosity_default():
    """Test that verbosity defaults to 0."""
    ctx = CLIContext()
    assert ctx.verbosity == 0


def test_verbosity_can_be_set():
    """Test that verbosity can be set."""
    ctx = CLIContext(verbosity=1)
    assert ctx.verbosity == 1


def test_overrides_default_to_empty():
    """Test that overrides default to empty dict."""
    ctx = CLIContext()
    assert ctx.overrides == {}


def test_get_output_format_with_override():
    """Test get_output_format returns override when provided."""
    ctx = CLIContext()
    # Override should be returned directly without loading config
    result = ctx.get_output_format(override="yaml")
    assert result == "yaml"


def test_get_timestamp_format_with_override():
    """Test get_timestamp_format returns override when provided."""
    ctx = CLIContext()
    result = ctx.get_timestamp_format(override="relative")
    assert result == "relative"


def test_get_no_truncate_with_override():
    """Test get_no_truncate returns override when provided."""
    ctx = CLIContext()
    result = ctx.get_no_truncate(override=True)
    assert result is True


def test_get_no_truncate_default():
    """Test get_no_truncate returns False by default."""
    ctx = CLIContext()
    result = ctx.get_no_truncate(override=None)
    assert result is False


def test_get_client_passes_user_config_and_is_cached():
    """Test that get_client passes user's client config to the SDK client and caches it."""
    ctx = CLIContext(overrides={"base_url": "http://test.example.com", "access_token": "token-123"})

    client = ctx.get_client()

    # Verify the client has the expected headers from get_client_config()
    assert "Authorization" in client.default_headers
    assert client.default_headers["Authorization"] == "Bearer token-123"

    # Verify the client is cached
    client2 = ctx.get_client()
    assert client is client2
