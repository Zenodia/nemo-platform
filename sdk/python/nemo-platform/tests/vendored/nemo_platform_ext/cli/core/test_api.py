# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Tests for core CLI utilities."""

from unittest.mock import patch

import pytest
import typer
from nemo_platform.cli.core.api import (
    build_kwargs,
    is_tty,
    merge_filter_dict,
    parse_resource_id,
)
from nemo_platform.cli.core.errors import InvalidSearchPatternError


def test_build_kwargs_filters_none_values():
    """Test that build_kwargs filters out None values."""
    result = build_kwargs(a=1, b=None, c="test", d=None)
    assert result == {"a": 1, "c": "test"}


def test_build_kwargs_empty():
    """Test build_kwargs with all None values."""
    result = build_kwargs(a=None, b=None)
    assert result == {}


def test_build_kwargs_no_none():
    """Test build_kwargs with no None values."""
    result = build_kwargs(a=1, b=2, c=3)
    assert result == {"a": 1, "b": 2, "c": 3}


@patch("sys.stdout.isatty")
def test_is_tty_true(mock_isatty):
    """Test is_tty when stdout is a TTY."""
    mock_isatty.return_value = True
    assert is_tty() is True


@patch("sys.stdout.isatty")
def test_is_tty_false(mock_isatty):
    """Test is_tty when stdout is not a TTY."""
    mock_isatty.return_value = False
    assert is_tty() is False


def test_parse_resource_id_with_slash():
    """Test parsing resource ID with namespace/name format."""
    name, namespace = parse_resource_id("default/my-model", None, None)
    assert name == "my-model"
    assert namespace == "default"


def test_parse_resource_id_with_options():
    """Test parsing resource ID with separate options."""
    name, namespace = parse_resource_id(None, "production", "my-dataset")
    assert name == "my-dataset"
    assert namespace == "production"


def test_parse_resource_id_with_name_and_namespace_option():
    """Test parsing with just name and namespace option."""
    name, namespace = parse_resource_id("my-config", "staging", None)
    assert name == "my-config"
    assert namespace == "staging"


def test_parse_resource_id_missing_namespace():
    """Test that parse_resource_id raises error when namespace is missing."""
    with pytest.raises(typer.Exit) as exc_info:
        parse_resource_id("my-model", None, None)

    assert exc_info.value.exit_code == 1


def test_parse_resource_id_no_arguments():
    """Test that parse_resource_id raises error when no arguments provided."""
    with pytest.raises(typer.Exit) as exc_info:
        parse_resource_id(None, None, None)

    assert exc_info.value.exit_code == 1


def test_merge_filter_dict_whitespace_only_raises():
    """Whitespace-only value raises InvalidSearchPatternError."""
    with pytest.raises(InvalidSearchPatternError):
        merge_filter_dict("   ")


def test_merge_filter_dict_invalid_json_raises_invalid_search_pattern():
    """Invalid JSON in --search raises InvalidSearchPatternError with parse_error set."""
    invalid_json = '{"name": ["nemo", "djs]}'  # missing closing quote
    with pytest.raises(InvalidSearchPatternError) as exc_info:
        merge_filter_dict(invalid_json)
    assert exc_info.value.value == invalid_json
    assert exc_info.value.parse_error is not None
    assert "Unterminated string" in exc_info.value.parse_error


def test_merge_filter_dict_json_object_parsed():
    """Valid JSON object string is parsed and returned (with optional kwargs)."""
    result = merge_filter_dict('{"name": "nemo"}')
    assert result == {"name": "nemo"}


def test_merge_filter_dict_bare_value_raises():
    """Single bare value (e.g. --search meta) is not valid; must be JSON."""
    with pytest.raises(InvalidSearchPatternError):
        merge_filter_dict("meta")


def test_merge_filter_dict_key_value_raises():
    """key=value string is not valid; must be JSON."""
    with pytest.raises(InvalidSearchPatternError):
        merge_filter_dict("name=myvalue")


def test_merge_filter_dict_none_with_kwargs():
    """None json_str with kwargs returns only the kwargs."""
    result = merge_filter_dict(None, name=["nemo"])
    assert result == {"name": ["nemo"]}
