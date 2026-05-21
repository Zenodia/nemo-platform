# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import pytest
from nemo_nb.cli import app
from nemo_nb.md_to_notebook import MarkdownToNotebookConverter
from typer.testing import CliRunner

runner = CliRunner()


class TestTabbedCodeBlock:
    def test_tabbed_fence_raises_error(self, tmp_path):
        converter = MarkdownToNotebookConverter()
        md_file = tmp_path / "test_tabbed_fence.md"
        md_file.write_text("\t```python\nprint('hi')\n```", encoding="utf-8")

        with pytest.raises(ValueError, match="Code block start fence contains tabs"):
            converter.convert(md_file)

    def test_tabbed_first_line_raises_error(self, tmp_path):
        converter = MarkdownToNotebookConverter()
        md_file = tmp_path / "test_tabbed_content.md"
        md_file.write_text("```python\n\tprint('hi')\n```", encoding="utf-8")

        with pytest.raises(ValueError, match="First line of code block contains tabs"):
            converter.convert(md_file)

    def test_valid_code_block(self, tmp_path):
        converter = MarkdownToNotebookConverter()
        md_file = tmp_path / "test_valid.md"
        md_file.write_text("```python\nprint('hi')\n```", encoding="utf-8")
        converter.convert(md_file)


class TestCLIConflict:
    def test_md_to_nb_conflict(self, tmp_path):
        md_file = tmp_path / "conflict.md"
        nb_file = tmp_path / "conflict.ipynb"

        # Create marked md file
        md_file.write_text("<!-- @nemo-nb: process -->\n# Test", encoding="utf-8")
        # Create nb file (content doesn't matter for existence check, but valid json to be safe)
        nb_file.write_text("{}", encoding="utf-8")

        result = runner.invoke(app, ["md-to-nb", str(md_file)])
        assert result.exit_code == 1
        assert "Conflict detected" in result.stderr

    def test_nb_to_md_conflict(self, tmp_path):
        md_file = tmp_path / "conflict.md"
        nb_file = tmp_path / "conflict.ipynb"

        # Create marked nb file (as json with marker in cell)
        nb_content = '{"cells": [{"source": ["# @nemo-nb: process"], "cell_type": "code"}]}'
        nb_file.write_text(nb_content, encoding="utf-8")

        # Create md file
        md_file.write_text("# Test", encoding="utf-8")

        result = runner.invoke(app, ["nb-to-md", str(nb_file)])
        assert result.exit_code == 1
        assert "Conflict detected" in result.stderr

    def test_md_to_nb_no_conflict_unmarked(self, tmp_path):
        md_file = tmp_path / "clean.md"
        nb_file = tmp_path / "clean.ipynb"

        # Create UNmarked md file
        md_file.write_text("# Test", encoding="utf-8")
        # Create UNmarked nb file
        nb_file.write_text("{}", encoding="utf-8")

        # Should fail because output exists (but NOT conflict)
        result = runner.invoke(app, ["md-to-nb", str(md_file)])
        assert result.exit_code == 1
        assert "Conflict detected" not in result.stderr
        assert "Output file exists" in result.stderr

        # With overwrite, should succeed
        result = runner.invoke(app, ["md-to-nb", str(md_file), "--overwrite"])
        assert result.exit_code == 0
