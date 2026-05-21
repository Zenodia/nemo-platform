# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Unit tests for the SPAStaticFiles handler."""

from nmp.studio.static_files import SPAStaticFiles


class TestHasFileExtension:
    """Tests for the _has_file_extension method."""

    def test_nested_path_with_extension(self):
        assert SPAStaticFiles._has_file_extension("assets/main.12345.js") is True

    def test_nested_path_without_extension(self):
        assert SPAStaticFiles._has_file_extension("workspaces/123/models") is False

    def test_path_with_trailing_slash(self):
        assert SPAStaticFiles._has_file_extension("dashboard/") is False

    def test_hidden_file_has_extension(self):
        # .gitignore should be considered as having an extension
        assert SPAStaticFiles._has_file_extension(".gitignore") is True

    def test_empty_path(self):
        assert SPAStaticFiles._has_file_extension("") is False

    def test_root_path(self):
        assert SPAStaticFiles._has_file_extension("/") is False
