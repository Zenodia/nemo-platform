# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import re

import pytest
from nmp.customizer.entities.validators import (
    validate_fileset_uri,
    validate_optional_fileset_uri,
)


class TestValidateFilesetUri:
    """Unit tests for validate_fileset_uri function.

    Tests the fileset URI validation including:
    - Protocol validation (only fileset:// is supported)
    - URI format validation (fileset://workspace/name)
    - Dataset name validation (REGEX_WORD_CHARACTER_DOT_DASH pattern)
    """

    @pytest.mark.parametrize(
        "uri",
        [
            "fileset://workspace/valid-name",
            "fileset://default/my-dataset",
            "fileset://ws/Dataset_v1.0",
            "fileset://workspace/My.Dataset_v2",
            # Edge cases valid per REGEX_WORD_CHARACTER_DOT_DASH (^[\w\-.]+$)
            "fileset://ws/a",  # single char name
            "fileset://ws/123",  # all digits
            "fileset://ws/_underscore_name",  # starts with underscore
            "fileset://ws/.dot-start",  # starts with dot
            "fileset://ws/-hyphen-start",  # starts with hyphen
            "fileset://ws/name--with--consecutive--hyphens",
            "fileset://ws/name..with..dots",
            "fileset://ws/___",  # all underscores
            "fileset://ws/...",  # all dots
            "fileset://ws/---",  # all hyphens
            "fileset://ws/MixedCase123",
            "fileset://ws/ALLCAPS",
            "fileset://ws/under_score_name",
        ],
        ids=[
            "hyphenated",
            "simple",
            "mixed-chars",
            "dots-underscores",
            "single-char-name",
            "all-digits",
            "starts-with-underscore",
            "starts-with-dot",
            "starts-with-hyphen",
            "consecutive-hyphens",
            "consecutive-dots",
            "all-underscores",
            "all-dots",
            "all-hyphens",
            "mixed-case-digits",
            "all-caps",
            "underscores",
        ],
    )
    def test_valid_fileset_uri_accepted(self, uri: str):
        """Valid fileset URIs should pass validation and return unchanged."""
        result = validate_fileset_uri(uri)
        assert result == uri

    @pytest.mark.parametrize(
        ("uri", "invalid_name"),
        [
            # Special characters not allowed by REGEX_WORD_CHARACTER_DOT_DASH
            ("fileset://workspace/bad name", "bad name"),
            ("fileset://workspace/bad@name", "bad@name"),
            ("fileset://workspace/bad+name", "bad+name"),
            ("fileset://workspace/bad*name", "bad*name"),
            ("fileset://workspace/bad!name", "bad!name"),
            ("fileset://workspace/bad#name", "bad#name"),
            ("fileset://workspace/bad$name", "bad$name"),
            ("fileset://workspace/bad%name", "bad%name"),
            ("fileset://workspace/bad^name", "bad^name"),
            ("fileset://workspace/bad&name", "bad&name"),
            ("fileset://workspace/bad=name", "bad=name"),
            ("fileset://workspace/bad~name", "bad~name"),
            ("fileset://workspace/bad`name", "bad`name"),
            ("fileset://workspace/bad(name)", "bad(name)"),
            ("fileset://workspace/bad[name]", "bad[name]"),
            ("fileset://workspace/bad{name}", "bad{name}"),
            ("fileset://workspace/bad<name>", "bad<name>"),
            ("fileset://workspace/bad|name", "bad|name"),
            ("fileset://workspace/bad\\name", "bad\\name"),
            ("fileset://workspace/bad;name", "bad;name"),
            ("fileset://workspace/bad:name", "bad:name"),
            ("fileset://workspace/bad'name", "bad'name"),
            ('fileset://workspace/bad"name', 'bad"name'),
            ("fileset://workspace/bad,name", "bad,name"),
            ("fileset://workspace/bad?name", "bad?name"),
        ],
        ids=[
            "space",
            "at-sign",
            "plus",
            "star",
            "exclamation",
            "hash",
            "dollar",
            "percent",
            "caret",
            "ampersand",
            "equals",
            "tilde",
            "backtick",
            "parentheses",
            "brackets",
            "braces",
            "angle-brackets",
            "pipe",
            "backslash",
            "semicolon",
            "colon",
            "single-quote",
            "double-quote",
            "comma",
            "question-mark",
        ],
    )
    def test_invalid_dataset_name_rejected(self, uri: str, invalid_name: str):
        """Dataset names with invalid characters should be rejected.

        The name must match REGEX_WORD_CHARACTER_DOT_DASH (^[\\w\\-.]+$).
        """
        with pytest.raises(ValueError, match=f"Invalid dataset name: '{re.escape(invalid_name)}'"):
            validate_fileset_uri(uri)

    @pytest.mark.parametrize(
        "uri",
        [
            # Unsupported protocols
            "hf://workspace/name",
            "ngc://workspace/name",
            "s3://bucket/name",
            "http://example.com/file",
            "https://example.com/file",
            # Missing protocol
            "workspace/name",
            "name-only",
            "/absolute/path",
        ],
        ids=[
            "hf-protocol",
            "ngc-protocol",
            "s3-protocol",
            "http-protocol",
            "https-protocol",
            "workspace-name-no-protocol",
            "name-only",
            "absolute-path",
        ],
    )
    def test_unsupported_protocol_rejected(self, uri: str):
        """Only fileset:// protocol is supported."""
        with pytest.raises(ValueError, match="Only 'fileset://' protocol is currently supported"):
            validate_fileset_uri(uri)

    @pytest.mark.parametrize(
        "uri",
        [
            # Invalid fileset:// formats
            "fileset://",
            "fileset://workspace",
            "fileset://workspace/",
            "fileset:///name",
            "fileset://workspace/name/extra",
            "fileset://workspace/name/extra/path",
        ],
        ids=[
            "empty-after-protocol",
            "workspace-only",
            "trailing-slash",
            "missing-workspace",
            "extra-path-segment",
            "multiple-extra-segments",
        ],
    )
    def test_invalid_fileset_uri_format_rejected(self, uri: str):
        """Invalid fileset:// URI formats should be rejected."""
        with pytest.raises(ValueError, match="Invalid fileset URI format"):
            validate_fileset_uri(uri)


class TestValidateOptionalFilesetUri:
    """Tests for validate_optional_fileset_uri function."""

    def test_none_returns_none(self):
        """None input should return None."""
        result = validate_optional_fileset_uri(None)
        assert result is None

    def test_valid_uri_returns_uri(self):
        """Valid URI should return the URI unchanged."""
        uri = "fileset://workspace/name"
        result = validate_optional_fileset_uri(uri)
        assert result == uri

    def test_invalid_uri_raises(self):
        """Invalid URI should raise ValueError."""
        with pytest.raises(ValueError):
            validate_optional_fileset_uri("invalid-uri")

    def test_invalid_name_raises(self):
        """URI with invalid name should raise ValueError."""
        with pytest.raises(ValueError, match="Invalid dataset name"):
            validate_optional_fileset_uri("fileset://workspace/bad name")
