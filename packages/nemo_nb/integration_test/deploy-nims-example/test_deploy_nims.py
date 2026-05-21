# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Integration test for deploy-nims notebook conversion.

Tests that:
1. The .ipynb file is converted to .sphinx.md
2. The generated .sphinx.md matches the reference markdown file
"""

import json
from pathlib import Path

import pytest
from nemo_nb.converter import NotebookConverter, NotebookToMarkdownConverter


@pytest.fixture
def test_dir():
    """Return the test directory path."""
    return Path(__file__).parent


@pytest.fixture
def build_dir(test_dir):
    """Return the build directory."""
    return test_dir / "_build"


@pytest.fixture
def nemo_nb_dir(build_dir):
    """Return the nemo-nb output directory."""
    return build_dir / "nemo-nb"


@pytest.fixture
def input_notebook(test_dir):
    """Return the input notebook path."""
    return test_dir / "deploy-nims-test.ipynb"


@pytest.fixture
def reference_md(test_dir):
    """Return the reference markdown path."""
    return test_dir / "deploy-nims-original-doc-as-reference.md"


@pytest.fixture
def output_sphinx_md(nemo_nb_dir):
    """Return the output sphinx.md path."""
    return nemo_nb_dir / "deploy-nims-test.sphinx.md"


@pytest.fixture
def output_md_notebook(nemo_nb_dir):
    """Return the output markdown notebook path (for fun, not testing)."""
    return nemo_nb_dir / "deploy-nims-test.md"


def test_input_files_exist(input_notebook, reference_md):
    """Test that the input files exist."""
    assert input_notebook.exists(), f"Input notebook {input_notebook} should exist"
    assert reference_md.exists(), f"Reference markdown {reference_md} should exist"


def test_notebook_is_valid(input_notebook):
    """Test that the input notebook is valid JSON."""
    with open(input_notebook) as f:
        notebook_data = json.load(f)

    assert "cells" in notebook_data, "Notebook should have cells"
    assert "metadata" in notebook_data, "Notebook should have metadata"
    assert "nbformat" in notebook_data, "Notebook should have nbformat"


def test_convert_notebook_to_sphinx_md(input_notebook, nemo_nb_dir, output_sphinx_md, output_md_notebook):
    """Test converting the notebook to .sphinx.md format."""
    # Create build directory
    nemo_nb_dir.mkdir(parents=True, exist_ok=True)

    # Load the notebook
    with open(input_notebook) as f:
        notebook_data = json.load(f)

    # Convert notebook to sphinx markdown
    converter = NotebookConverter()
    markdown_content = converter.convert_notebook_dict(notebook_data)

    # Write to .sphinx.md file
    output_sphinx_md.write_text(markdown_content)

    # Also generate a markdown notebook for fun (not used in testing)
    md_converter = NotebookToMarkdownConverter()
    md_notebook_content = md_converter.convert_notebook_dict(notebook_data)
    output_md_notebook.write_text(md_notebook_content)

    assert output_sphinx_md.exists(), f"Output file {output_sphinx_md} should be created"
    assert len(markdown_content) > 0, "Generated markdown should not be empty"


def test_generated_md_matches_reference(output_sphinx_md, reference_md):
    """Test that the generated .sphinx.md matches the reference markdown."""
    assert output_sphinx_md.exists(), f"Output file {output_sphinx_md} should exist"

    generated_content = output_sphinx_md.read_text()
    reference_content = reference_md.read_text()

    # Normalize line endings
    generated_lines = [line.rstrip() for line in generated_content.splitlines()]
    reference_lines = [line.rstrip() for line in reference_content.splitlines()]

    # Compare line by line for better error messages
    max_lines = max(len(generated_lines), len(reference_lines))

    differences = []
    for i in range(max_lines):
        gen_line = generated_lines[i] if i < len(generated_lines) else "<MISSING>"
        ref_line = reference_lines[i] if i < len(reference_lines) else "<MISSING>"

        if gen_line != ref_line:
            differences.append(f"Line {i + 1}:\n  Generated: {gen_line}\n  Reference: {ref_line}")

    if differences:
        error_msg = "Generated markdown differs from reference:\n\n"
        error_msg += "\n\n".join(differences[:10])  # Show first 10 differences
        if len(differences) > 10:
            error_msg += f"\n\n... and {len(differences) - 10} more differences"
        pytest.fail(error_msg)


def test_tab_sets_present(output_sphinx_md):
    """Test that tab-sets are present in the generated markdown."""
    assert output_sphinx_md.exists(), "Output file should exist"

    content = output_sphinx_md.read_text()

    # Check for tab-set directives
    assert "::::{tab-set}" in content, "Should contain tab-set directive"
    assert ":::{tab-item}" in content, "Should contain tab-item directives"


def test_dropdowns_present(output_sphinx_md):
    """Test that dropdowns are present in the generated markdown."""
    assert output_sphinx_md.exists(), "Output file should exist"

    content = output_sphinx_md.read_text()

    # Check for dropdown directives
    assert ":::{dropdown}" in content, "Should contain dropdown directives"
    assert ":icon: code-square" in content, "Dropdown should have icon"


def test_code_blocks_present(output_sphinx_md):
    """Test that code blocks are present in the generated markdown."""
    assert output_sphinx_md.exists(), "Output file should exist"

    content = output_sphinx_md.read_text()

    # Check for code blocks
    assert "```python" in content, "Should contain Python code blocks"
    assert "```sh" in content or "```bash" in content, "Should contain shell code blocks"


def test_myst_label_present(output_sphinx_md):
    """Test that MyST label is present in the generated markdown."""
    assert output_sphinx_md.exists(), "Output file should exist"

    content = output_sphinx_md.read_text()

    # Check for MyST label
    assert "(nemo-nb-integration-test-1)=" in content, "Should contain MyST label"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
