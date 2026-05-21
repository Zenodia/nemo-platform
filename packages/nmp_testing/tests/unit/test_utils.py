# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Unit tests for testing utils (e.g. short_unique_name, add_mock_provider validation)."""

import re

from nmp.common.entities.constants import NAME_PATTERN
from nmp.testing.utils import short_unique_name

_ENTITY_NAME_PATTERN = re.compile(NAME_PATTERN)


class TestShortUniqueName:
    """Tests that short_unique_name produces valid entity names (NAME_PATTERN)."""

    def test_matches_entity_name_pattern(self):
        """Output matches NAME_PATTERN (lowercase, starts with letter, 2-63 chars, etc.)."""
        name = short_unique_name("provider")
        assert _ENTITY_NAME_PATTERN.match(name), f"{name!r} should match NAME_PATTERN"

    def test_lowercase_prefix(self):
        """Prefix is lowercased so result has no uppercase."""
        name = short_unique_name("Provider")
        assert name == name.lower()
        assert _ENTITY_NAME_PATTERN.match(name)

    def test_digit_prefix_becomes_letter(self):
        """Prefix that would start with a digit is fixed to start with 'a'."""
        name = short_unique_name("9invalid")
        assert name[0].isalpha() and name[0].islower()
        assert _ENTITY_NAME_PATTERN.match(name)

    def test_no_trailing_hyphen(self):
        """Result does not end with a hyphen."""
        name = short_unique_name("x")
        assert not name.endswith("-"), f"{name!r} must not end with hyphen"

    def test_consecutive_hyphens_collapsed(self):
        """Consecutive hyphens in prefix are collapsed."""
        name = short_unique_name("a--b")
        assert "--" not in name
        assert _ENTITY_NAME_PATTERN.match(name)
