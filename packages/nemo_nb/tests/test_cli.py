# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Tests for the Typer-based CLI."""

import json

import pytest
from nemo_nb.cli import app
from typer.testing import CliRunner

# Create a test runner
runner = CliRunner()


@pytest.fixture
def sample_notebook(tmp_path):
    """Create a simple test notebook."""
    notebook = {
        "cells": [
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": ["# Test Notebook\n", "\n", "This is a test."],
            },
            {
                "cell_type": "code",
                "execution_count": 1,
                "metadata": {},
                "outputs": [{"name": "stdout", "output_type": "stream", "text": ["Hello, World!\n"]}],
                "source": ['print("Hello, World!")'],
            },
        ],
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
            "language_info": {"name": "python", "version": "3.11.0"},
        },
        "nbformat": 4,
        "nbformat_minor": 4,
    }

    notebook_path = tmp_path / "test_notebook.ipynb"
    notebook_path.write_text(json.dumps(notebook, indent=2), encoding="utf-8")
    return notebook_path


@pytest.fixture
def sample_markdown(tmp_path):
    """Create a simple test markdown file."""
    markdown_content = """# Test Markdown

This is a test markdown file.

```python
print("Hello, World!")
```

<!-- @nemo-nb: output -->
Hello, World!
"""

    markdown_path = tmp_path / "test_markdown.md"
    markdown_path.write_text(markdown_content, encoding="utf-8")
    return markdown_path


class TestCLIHelp:
    """Test CLI help commands."""

    def test_main_help(self):
        """Test main help output."""
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "Convert between Jupyter notebooks and Markdown files" in result.stdout
        assert "md-to-nb" in result.stdout
        assert "nb-to-md" in result.stdout
        assert "to-sphinx-md" in result.stdout

    def test_md_to_nb_help(self):
        """Test md-to-nb help output."""
        result = runner.invoke(app, ["md-to-nb", "--help"])
        assert result.exit_code == 0
        assert "Convert Markdown (notebook format) to Jupyter Notebook" in result.stdout
        assert "INPUT_FILE" in result.stdout or "input_file" in result.stdout
        assert "overwrite" in result.stdout.lower()
        assert "dry" in result.stdout.lower()

    def test_nb_to_md_help(self):
        """Test nb-to-md help output."""
        result = runner.invoke(app, ["nb-to-md", "--help"])
        assert result.exit_code == 0
        assert "Convert Jupyter Notebook to Markdown (notebook format)" in result.stdout
        assert "INPUT_FILE" in result.stdout or "input_file" in result.stdout
        assert "overwrite" in result.stdout.lower()
        assert "dry" in result.stdout.lower()

    def test_to_sphinx_md_help(self):
        """Test to-sphinx-md help output."""
        result = runner.invoke(app, ["to-sphinx-md", "--help"])
        assert result.exit_code == 0
        assert "Convert notebook or markdown to Sphinx docs format" in result.stdout
        assert "INPUT_FILE" in result.stdout or "input_file" in result.stdout
        assert "overwrite" in result.stdout.lower()
        assert "dry" in result.stdout.lower()


class TestNbToMd:
    """Test nb-to-md command."""

    def test_basic_conversion(self, sample_notebook, tmp_path):
        """Test basic notebook to markdown conversion."""
        output_path = tmp_path / "output.md"
        result = runner.invoke(app, ["nb-to-md", str(sample_notebook), str(output_path)])

        assert result.exit_code == 0
        assert "Converted:" in result.stdout
        assert output_path.exists()

        # Verify output content
        content = output_path.read_text(encoding="utf-8")
        assert "# Test Notebook" in content
        assert "```python" in content
        assert 'print("Hello, World!")' in content

    def test_default_output_path(self, sample_notebook):
        """Test conversion with default output path."""
        result = runner.invoke(app, ["nb-to-md", str(sample_notebook)])

        assert result.exit_code == 0
        expected_output = sample_notebook.with_suffix(".md")
        assert expected_output.exists()

        # Clean up
        expected_output.unlink()

    def test_overwrite_flag(self, sample_notebook, tmp_path):
        """Test overwrite flag."""
        output_path = tmp_path / "output.md"
        output_path.write_text("existing content", encoding="utf-8")

        # Without overwrite, should fail
        result = runner.invoke(app, ["nb-to-md", str(sample_notebook), str(output_path)])
        assert result.exit_code == 1
        output = result.stdout + result.stderr
        assert "Output file exists" in output or "exists" in output.lower()

        # With overwrite, should succeed
        result = runner.invoke(app, ["nb-to-md", str(sample_notebook), str(output_path), "--overwrite"])
        assert result.exit_code == 0
        assert output_path.read_text(encoding="utf-8") != "existing content"

    def test_dry_run(self, sample_notebook, tmp_path):
        """Test dry-run flag."""
        output_path = tmp_path / "output.md"
        result = runner.invoke(app, ["nb-to-md", str(sample_notebook), str(output_path), "--dry-run"])

        assert result.exit_code == 0
        assert "Would convert:" in result.stdout
        assert not output_path.exists()  # File should not be created

    def test_nonexistent_input(self, tmp_path):
        """Test error handling for nonexistent input file."""
        nonexistent = tmp_path / "nonexistent.ipynb"
        result = runner.invoke(app, ["nb-to-md", str(nonexistent)])

        assert result.exit_code == 1
        output = result.stdout + result.stderr
        assert "Input file does not exist" in output or "does not exist" in output.lower()

    def test_wrong_file_extension(self, tmp_path):
        """Test error handling for wrong file extension."""
        wrong_file = tmp_path / "test.md"
        wrong_file.write_text("test", encoding="utf-8")

        result = runner.invoke(app, ["nb-to-md", str(wrong_file)])
        assert result.exit_code == 1
        output = result.stdout + result.stderr
        assert "Expected .ipynb file" in output or ".ipynb" in output


class TestMdToNb:
    """Test md-to-nb command."""

    def test_basic_conversion(self, sample_markdown, tmp_path):
        """Test basic markdown to notebook conversion."""
        output_path = tmp_path / "output.ipynb"
        result = runner.invoke(app, ["md-to-nb", str(sample_markdown), str(output_path)])

        assert result.exit_code == 0
        assert "Converted:" in result.stdout
        assert output_path.exists()

        # Verify output is valid JSON
        notebook = json.loads(output_path.read_text(encoding="utf-8"))
        assert notebook["nbformat"] == 4
        assert len(notebook["cells"]) >= 1

    def test_default_output_path(self, sample_markdown):
        """Test conversion with default output path."""
        result = runner.invoke(app, ["md-to-nb", str(sample_markdown)])

        assert result.exit_code == 0
        expected_output = sample_markdown.with_suffix(".ipynb")
        assert expected_output.exists()

        # Clean up
        expected_output.unlink()

    def test_overwrite_flag(self, sample_markdown, tmp_path):
        """Test overwrite flag."""
        output_path = tmp_path / "output.ipynb"
        output_path.write_text("{}", encoding="utf-8")

        # Without overwrite, should fail
        result = runner.invoke(app, ["md-to-nb", str(sample_markdown), str(output_path)])
        assert result.exit_code == 1
        output = result.stdout + result.stderr
        assert "Output file exists" in output or "exists" in output.lower()

        # With overwrite, should succeed
        result = runner.invoke(app, ["md-to-nb", str(sample_markdown), str(output_path), "--overwrite"])
        assert result.exit_code == 0

    def test_dry_run(self, sample_markdown, tmp_path):
        """Test dry-run flag."""
        output_path = tmp_path / "output.ipynb"
        result = runner.invoke(app, ["md-to-nb", str(sample_markdown), str(output_path), "--dry-run"])

        assert result.exit_code == 0
        assert "Would convert:" in result.stdout
        assert not output_path.exists()

    def test_wrong_file_extension(self, tmp_path):
        """Test error handling for wrong file extension."""
        wrong_file = tmp_path / "test.ipynb"
        wrong_file.write_text("{}", encoding="utf-8")

        result = runner.invoke(app, ["md-to-nb", str(wrong_file)])
        assert result.exit_code == 1
        output = result.stdout + result.stderr
        assert "Expected .md file" in output or ".md" in output


class TestToSphinxMd:
    """Test to-sphinx-md command."""

    def test_from_notebook(self, sample_notebook, tmp_path):
        """Test conversion from notebook to Sphinx markdown."""
        output_path = tmp_path / "output.sphinx.md"
        result = runner.invoke(app, ["to-sphinx-md", str(sample_notebook), str(output_path)])

        assert result.exit_code == 0
        assert "Converted:" in result.stdout
        assert "Sphinx docs format" in result.stdout
        assert output_path.exists()

    def test_from_markdown(self, sample_markdown, tmp_path):
        """Test conversion from markdown to Sphinx markdown."""
        output_path = tmp_path / "output.sphinx.md"
        result = runner.invoke(app, ["to-sphinx-md", str(sample_markdown), str(output_path)])

        assert result.exit_code == 0
        assert "Converted:" in result.stdout
        assert output_path.exists()

    def test_default_output_path(self, sample_notebook):
        """Test conversion with default output path."""
        result = runner.invoke(app, ["to-sphinx-md", str(sample_notebook)])

        assert result.exit_code == 0
        expected_output = sample_notebook.with_suffix(".sphinx.md")
        assert expected_output.exists()

        # Clean up
        expected_output.unlink()

    def test_overwrite_flag(self, sample_notebook, tmp_path):
        """Test overwrite flag."""
        output_path = tmp_path / "output.sphinx.md"
        output_path.write_text("existing content", encoding="utf-8")

        # Without overwrite, should fail
        result = runner.invoke(app, ["to-sphinx-md", str(sample_notebook), str(output_path)])
        assert result.exit_code == 1
        output = result.stdout + result.stderr
        assert "Output file exists" in output or "exists" in output.lower()

        # With overwrite, should succeed
        result = runner.invoke(app, ["to-sphinx-md", str(sample_notebook), str(output_path), "--overwrite"])
        assert result.exit_code == 0

    def test_dry_run_notebook(self, sample_notebook, tmp_path):
        """Test dry-run with notebook input."""
        output_path = tmp_path / "output.sphinx.md"
        result = runner.invoke(app, ["to-sphinx-md", str(sample_notebook), str(output_path), "--dry-run"])

        assert result.exit_code == 0
        assert "Would convert:" in result.stdout
        assert not output_path.exists()

    def test_dry_run_markdown(self, sample_markdown, tmp_path):
        """Test dry-run with markdown input."""
        output_path = tmp_path / "output.sphinx.md"
        result = runner.invoke(app, ["to-sphinx-md", str(sample_markdown), str(output_path), "--dry-run"])

        assert result.exit_code == 0
        assert "Would convert:" in result.stdout
        assert not output_path.exists()


class TestErrorHandling:
    """Test error handling and edge cases."""

    def test_no_command(self):
        """Test invoking CLI with no command shows help."""
        result = runner.invoke(app, [])
        # With no_args_is_help=True, this should show help
        # Typer may use exit code 0 or 2 depending on version
        assert result.exit_code in (0, 2)
        assert "Convert between Jupyter notebooks and Markdown files" in result.stdout

    def test_invalid_command(self):
        """Test invoking CLI with invalid command."""
        result = runner.invoke(app, ["invalid-command"])
        assert result.exit_code != 0

    def test_missing_required_argument(self):
        """Test missing required argument."""
        result = runner.invoke(app, ["nb-to-md"])
        assert result.exit_code != 0
        # Typer will show an error about missing argument

    def test_nonexistent_file(self, tmp_path):
        """Test with nonexistent file."""
        nonexistent = tmp_path / "nonexistent.ipynb"
        result = runner.invoke(app, ["nb-to-md", str(nonexistent)])
        assert result.exit_code == 1
        output = result.stdout + result.stderr
        assert "Input file does not exist" in output or "does not exist" in output.lower()


class TestRoundtrip:
    """Test roundtrip conversions."""

    def test_ipynb_to_md_to_ipynb(self, sample_notebook, tmp_path):
        """Test roundtrip: notebook -> markdown -> notebook."""
        md_path = tmp_path / "intermediate.md"
        final_ipynb = tmp_path / "final.ipynb"

        # Convert to markdown
        result = runner.invoke(app, ["nb-to-md", str(sample_notebook), str(md_path)])
        assert result.exit_code == 0

        # Convert back to notebook
        result = runner.invoke(app, ["md-to-nb", str(md_path), str(final_ipynb)])
        assert result.exit_code == 0

        # Verify final notebook is valid
        notebook = json.loads(final_ipynb.read_text(encoding="utf-8"))
        assert notebook["nbformat"] == 4
        assert len(notebook["cells"]) >= 1

    def test_md_to_ipynb_to_md(self, sample_markdown, tmp_path):
        """Test roundtrip: markdown -> notebook -> markdown."""
        ipynb_path = tmp_path / "intermediate.ipynb"
        final_md = tmp_path / "final.md"

        # Convert to notebook
        result = runner.invoke(app, ["md-to-nb", str(sample_markdown), str(ipynb_path)])
        assert result.exit_code == 0

        # Convert back to markdown
        result = runner.invoke(app, ["nb-to-md", str(ipynb_path), str(final_md)])
        assert result.exit_code == 0

        # Verify final markdown exists and has content
        content = final_md.read_text(encoding="utf-8")
        assert "# Test Markdown" in content
        assert "```python" in content


class TestAddSugarCommand:
    """Test the add-sugar command."""

    @pytest.fixture
    def notebook_with_marker(self, tmp_path):
        """Create a notebook with the process marker."""
        notebook = {
            "cells": [
                {
                    "cell_type": "markdown",
                    "metadata": {},
                    "source": ["<!-- @nemo-nb: process -->\n", "# Test Notebook"],
                },
                {
                    "cell_type": "code",
                    "execution_count": None,
                    "metadata": {},
                    "outputs": [],
                    "source": ['print("Hello")'],
                },
            ],
            "metadata": {},
            "nbformat": 4,
            "nbformat_minor": 4,
        }
        path = tmp_path / "with_marker.ipynb"
        path.write_text(json.dumps(notebook, indent=2), encoding="utf-8")
        return path

    @pytest.fixture
    def notebook_without_marker(self, tmp_path):
        """Create a notebook without the process marker."""
        notebook = {
            "cells": [
                {
                    "cell_type": "markdown",
                    "metadata": {},
                    "source": ["# Test Notebook"],
                },
            ],
            "metadata": {},
            "nbformat": 4,
            "nbformat_minor": 4,
        }
        path = tmp_path / "no_marker.ipynb"
        path.write_text(json.dumps(notebook, indent=2), encoding="utf-8")
        return path

    @pytest.fixture
    def md_with_marker(self, tmp_path):
        """Create a markdown file with the process marker."""
        content = """<!-- @nemo-nb: process -->
# Test Document

```python
print("hello")
```
"""
        path = tmp_path / "with_marker.md"
        path.write_text(content, encoding="utf-8")
        return path

    @pytest.fixture
    def md_without_marker(self, tmp_path):
        """Create a markdown file without the process marker."""
        content = """# Test Document

```python
print("hello")
```
"""
        path = tmp_path / "no_marker.md"
        path.write_text(content, encoding="utf-8")
        return path

    def test_add_sugar_help(self):
        """Test add-sugar command help."""
        result = runner.invoke(app, ["add-sugar", "--help"])
        assert result.exit_code == 0
        assert "Apply syntax sugar markers" in result.stdout
        assert "@nemo-nb: process" in result.stdout

    def test_add_sugar_ipynb_requires_process_marker(self, notebook_without_marker):
        """Test that .ipynb without process marker is rejected."""
        result = runner.invoke(app, ["add-sugar", str(notebook_without_marker), "--check"])
        assert result.exit_code == 1
        output = result.stdout + (result.stderr or "")
        assert "does not contain the @nemo-nb: process marker" in output

    def test_add_sugar_md_requires_process_marker(self, md_without_marker):
        """Test that .md without process marker is rejected."""
        result = runner.invoke(app, ["add-sugar", str(md_without_marker), "--check"])
        assert result.exit_code == 1
        output = result.stdout + (result.stderr or "")
        assert "does not contain the @nemo-nb: process marker" in output

    def test_add_sugar_ipynb_with_marker_succeeds(self, notebook_with_marker):
        """Test that .ipynb with process marker is processed."""
        result = runner.invoke(app, ["add-sugar", str(notebook_with_marker), "--check"])
        # Exit code 0 means no changes needed, 1 means would modify
        assert result.exit_code in [0, 1]
        output = result.stdout
        assert "Error" not in output or "would modify" in output.lower()

    def test_add_sugar_md_with_marker_succeeds(self, md_with_marker):
        """Test that .md with process marker is processed."""
        result = runner.invoke(app, ["add-sugar", str(md_with_marker), "--check"])
        assert result.exit_code in [0, 1]
        output = result.stdout
        assert "Error" not in output or "would modify" in output.lower()

    def test_add_sugar_verbose_shows_passes(self, notebook_with_marker):
        """Test that --verbose shows pass names."""
        result = runner.invoke(app, ["add-sugar", str(notebook_with_marker), "--verbose", "--check"])
        output = result.stdout
        assert "TabSet" in output
        assert "TabItem" in output
        assert "Dropdown" in output
        assert "LabelInsert" in output

    def test_add_sugar_wrong_extension_rejected(self, tmp_path):
        """Test that wrong file extensions are rejected."""
        txt_file = tmp_path / "test.txt"
        txt_file.write_text("content", encoding="utf-8")

        result = runner.invoke(app, ["add-sugar", str(txt_file)])
        assert result.exit_code == 1
        output = result.stdout + (result.stderr or "")
        assert ".ipynb or .md" in output

    def test_add_sugar_nonexistent_file(self, tmp_path):
        """Test error for nonexistent file."""
        result = runner.invoke(app, ["add-sugar", str(tmp_path / "nonexistent.ipynb")])
        assert result.exit_code == 1
        output = result.stdout + (result.stderr or "")
        assert "does not exist" in output
