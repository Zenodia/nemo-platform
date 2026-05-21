# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Unit tests for cell metadata handling."""

from nemo_nb.structures import CellMetadata


def test_should_hide_with_nemo_config():
    """Test hide detection via nemo_nb.hide."""
    cell = {"metadata": {"nemo_nb": {"hide": True}}}

    meta = CellMetadata(cell)
    assert meta.should_hide() is True


def test_should_hide_with_false():
    """Test that hide=false doesn't hide."""
    cell = {"metadata": {"nemo_nb": {"hide": False}}}

    meta = CellMetadata(cell)
    assert meta.should_hide() is False


def test_should_hide_with_tags():
    """Test hide detection via tags."""
    cell = {"metadata": {"tags": ["hide-cell", "other-tag"]}}

    meta = CellMetadata(cell)
    assert meta.should_hide() is True


def test_should_not_hide_without_metadata():
    """Test that cells without hide metadata are not hidden."""
    cell = {"metadata": {}}

    meta = CellMetadata(cell)
    assert meta.should_hide() is False


def test_should_not_hide_with_other_tags():
    """Test that other tags don't cause hiding."""
    cell = {"metadata": {"tags": ["some-tag", "another-tag"]}}

    meta = CellMetadata(cell)
    assert meta.should_hide() is False


def test_get_language_from_metadata():
    """Test language extraction from metadata - bash stays bash."""
    cell = {"metadata": {"language": "bash"}}

    meta = CellMetadata(cell)
    # bash should be preserved
    assert meta.get_language() == "bash"


def test_get_language_default():
    """Test default language is python."""
    cell = {"metadata": {}}

    meta = CellMetadata(cell)
    assert meta.get_language() == "python"


def test_get_language_with_other_metadata():
    """Test language extraction with other metadata present."""
    cell = {"metadata": {"language": "javascript", "other_field": "value", "nemo_nb": {"some_config": True}}}

    meta = CellMetadata(cell)
    assert meta.get_language() == "javascript"


def test_cell_without_metadata():
    """Test handling cell with no metadata key."""
    cell = {}

    meta = CellMetadata(cell)
    assert meta.should_hide() is False
    assert meta.get_language() == "python"


def test_combined_hide_and_language():
    """Test that hide and language can be used together."""
    cell = {"metadata": {"language": "rust", "nemo_nb": {"hide": True}}}

    meta = CellMetadata(cell)
    assert meta.should_hide() is True
    assert meta.get_language() == "rust"


def test_bash_normalized_to_sh():
    """Test that bash is NOT normalized to sh."""
    cell_bash = {"metadata": {"language": "bash"}}
    cell_sh = {"metadata": {"language": "sh"}}

    meta_bash = CellMetadata(cell_bash)
    meta_sh = CellMetadata(cell_sh)

    # bash should return "bash", sh should return "sh"
    assert meta_bash.get_language() == "bash"
    assert meta_sh.get_language() == "sh"


def test_shellscript_normalized_to_sh():
    """Test that VSCode's shellscript languageId is normalized to sh."""
    cell = {"metadata": {"vscode": {"languageId": "shellscript"}}}

    meta = CellMetadata(cell)
    assert meta.get_language() == "sh"
