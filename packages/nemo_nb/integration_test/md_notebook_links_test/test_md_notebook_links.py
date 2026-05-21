# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Integration test for MD notebook files with cross-page links.

Tests that:
1. MD (notebook format) files with frontmatter are converted to .ipynb
2. The .ipynb files are then converted to .sphinx.md for Sphinx
3. Links between pages are preserved
4. Code cells and output cells are properly processed
"""

import json
import subprocess
from pathlib import Path

import pytest


@pytest.fixture
def test_dir():
    """Return the test directory path."""
    return Path(__file__).parent


@pytest.fixture
def generated_dir(test_dir):
    """Return the nemo-nb _generated output directory.

    The nemo_nb extension now writes intermediate .ipynb and .sphinx.md files
    to ``_generated/nemo-nb`` instead of ``_build/nemo-nb``. This fixture
    reflects the new behavior and keeps the tests aligned with the current
    output layout.
    """

    gen_dir = test_dir / "_generated" / "nemo-nb"
    gen_dir.mkdir(parents=True, exist_ok=True)
    return gen_dir


def test_md_files_exist(test_dir):
    """Test that the source MD files exist."""
    expected_files = ["index.md", "getting-started.md", "configuration.md"]
    for filename in expected_files:
        filepath = test_dir / filename
        assert filepath.exists(), f"Source file {filename} should exist"


def test_sphinx_build(test_dir):
    """Test that Sphinx build completes successfully."""
    build_dir = test_dir / "_build"

    # Clean previous build
    if build_dir.exists():
        subprocess.run(["rm", "-rf", str(build_dir)], check=True)

    # Run Sphinx build
    result = subprocess.run(
        ["sphinx-build", "-b", "html", str(test_dir), str(build_dir / "html")],
        cwd=test_dir,
        capture_output=True,
        text=True,
    )

    print("STDOUT:", result.stdout)
    print("STDERR:", result.stderr)

    assert result.returncode == 0, f"Sphinx build failed: {result.stderr}"


def test_intermediate_ipynb_generated(generated_dir):
    """Test that intermediate .ipynb files were generated from .md files."""
    expected_notebooks = ["index.ipynb", "getting-started.ipynb", "configuration.ipynb"]

    for notebook_name in expected_notebooks:
        notebook_path = generated_dir / notebook_name
        assert notebook_path.exists(), (
            f"Intermediate notebook {notebook_name} should be generated in _generated/nemo-nb/"
        )

        # Verify it's valid JSON
        with open(notebook_path) as f:
            notebook_data = json.load(f)

        # Check basic notebook structure
        assert "cells" in notebook_data, "Notebook should have cells"
        assert "metadata" in notebook_data, "Notebook should have metadata"
        assert "nbformat" in notebook_data, "Notebook should have nbformat"

        # Verify we have both markdown and code cells
        cell_types = [cell["cell_type"] for cell in notebook_data["cells"]]
        assert "markdown" in cell_types, f"{notebook_name} should have markdown cells"
        assert "code" in cell_types, f"{notebook_name} should have code cells"


def test_sphinx_md_generated(generated_dir):
    """Test that .sphinx.md files were generated for Sphinx processing."""
    expected_sphinx_files = ["index.sphinx.md", "getting-started.sphinx.md", "configuration.sphinx.md"]

    for sphinx_file in expected_sphinx_files:
        sphinx_path = generated_dir / sphinx_file
        assert sphinx_path.exists(), f"Sphinx MD file {sphinx_file} should be generated in _generated/nemo-nb/"

        # Read and verify content
        content = sphinx_path.read_text()

        # Check that code fences are present (converter produces plain markdown code fences)
        assert "```python" in content or "```json" in content, f"{sphinx_file} should contain code fences"


def test_links_in_index(generated_dir):
    """Test that links in index.md are preserved in the generated files."""
    index_sphinx = generated_dir / "index.sphinx.md"
    assert index_sphinx.exists(), "index.sphinx.md should exist in _generated/nemo-nb/"

    content = index_sphinx.read_text()

    # Check that links to other pages are present
    assert "getting-started" in content, "Link to getting-started should be preserved"
    assert "configuration" in content, "Link to configuration should be preserved"


def test_output_cells_in_notebooks(generated_dir):
    """Test that output cells are properly included in generated notebooks."""
    index_notebook = generated_dir / "index.ipynb"
    assert index_notebook.exists(), "index.ipynb should exist in _generated/nemo-nb/"

    with open(index_notebook) as f:
        notebook_data = json.load(f)

    # Find code cells with outputs
    code_cells_with_outputs = [
        cell for cell in notebook_data["cells"] if cell["cell_type"] == "code" and cell.get("outputs")
    ]

    assert len(code_cells_with_outputs) > 0, "Should have at least one code cell with outputs"


def test_frontmatter_preserved(generated_dir):
    """Test that frontmatter is preserved in the first markdown cell."""
    index_notebook = generated_dir / "index.ipynb"

    with open(index_notebook) as f:
        notebook_data = json.load(f)

    # Frontmatter should be in the first markdown cell
    assert len(notebook_data["cells"]) > 0, "Notebook should have cells"
    first_cell = notebook_data["cells"][0]
    assert first_cell["cell_type"] == "markdown", "First cell should be markdown"

    cell_source = "".join(first_cell["source"])
    assert "title:" in cell_source, "Frontmatter title should be in first markdown cell"
    assert "Integration Test Documentation" in cell_source or "integration" in cell_source.lower(), (
        "Frontmatter should contain expected content"
    )


def test_html_output_generated(test_dir):
    """Test that HTML files were generated by Sphinx."""
    html_dir = test_dir / "_build" / "html"
    expected_html = ["index.html", "getting-started.html", "configuration.html"]

    for html_file in expected_html:
        html_path = html_dir / html_file
        assert html_path.exists(), f"HTML file {html_file} should be generated"

        # Verify it's not empty
        content = html_path.read_text()
        assert len(content) > 0, f"{html_file} should not be empty"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
