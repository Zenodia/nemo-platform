# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Integration test for bidirectional notebook conversion.

Tests that:
1. .ipynb files can be converted to .md format and match the expected .md file
2. .md files can be converted to .ipynb format and match the expected .ipynb file
3. The conversion is truly bidirectional and preserves all content
"""

import json
from pathlib import Path

import pytest


@pytest.fixture
def test_dir():
    """Return the test directory path."""
    return Path(__file__).parent


@pytest.fixture
def generated_dir(test_dir):
    """Return and create the _generated directory."""
    gen_dir = test_dir / "_generated"
    gen_dir.mkdir(exist_ok=True)
    return gen_dir


@pytest.fixture
def sample_ipynb(test_dir):
    """Return path to the sample .ipynb file."""
    return test_dir / "sample.ipynb"


@pytest.fixture
def sample_md(test_dir):
    """Return path to the sample .md file."""
    return test_dir / "sample.md"


def normalize_markdown(content: str) -> str:
    """Normalize markdown content for comparison.

    Args:
        content: Markdown content as string

    Returns:
        Normalized content
    """
    # Strip trailing whitespace from each line
    lines = [line.rstrip() for line in content.split("\n")]
    # Remove trailing empty lines
    while lines and not lines[-1]:
        lines.pop()
    return "\n".join(lines)


def normalize_notebook(notebook: dict) -> dict:
    """Normalize notebook content for comparison.

    Args:
        notebook: Notebook dictionary

    Returns:
        Normalized notebook dictionary
    """
    # Create a deep copy to avoid modifying original
    import copy

    nb = copy.deepcopy(notebook)

    # Normalize cells
    for cell in nb.get("cells", []):
        # Normalize source lines
        source = cell.get("source", [])
        if isinstance(source, list):
            # Remove trailing newlines from last line if present
            if source and source[-1].endswith("\n"):
                source[-1] = source[-1].rstrip("\n")
            cell["source"] = source

        # Normalize outputs
        if cell.get("cell_type") == "code":
            outputs = cell.get("outputs", [])
            for output in outputs:
                # Normalize text outputs
                if "text" in output:
                    text = output["text"]
                    if isinstance(text, list) and text:
                        # Ensure last line doesn't have trailing newline
                        if text[-1].endswith("\n"):
                            text[-1] = text[-1].rstrip("\n")
                        output["text"] = text

                # Normalize traceback in error outputs
                if output.get("output_type") == "error" and "traceback" in output:
                    traceback = output["traceback"]
                    if isinstance(traceback, list) and traceback:
                        if traceback[-1].endswith("\n"):
                            traceback[-1] = traceback[-1].rstrip("\n")
                        output["traceback"] = traceback

                # Normalize data outputs
                if "data" in output:
                    data = output["data"]
                    if "text/plain" in data:
                        text_plain = data["text/plain"]
                        if isinstance(text_plain, list) and text_plain:
                            if text_plain[-1].endswith("\n"):
                                text_plain[-1] = text_plain[-1].rstrip("\n")
                            data["text/plain"] = text_plain

    return nb


def test_ipynb_to_md_conversion(sample_ipynb, sample_md, generated_dir):
    """Test converting .ipynb to .md produces valid markdown with expected content."""
    from nemo_nb.converter import NotebookToMarkdownConverter

    # Convert the ipynb to md
    generated_md_path = generated_dir / "sample.ipynb.md"
    with open(sample_ipynb, "r", encoding="utf-8") as f:
        notebook_data = json.load(f)
    converter = NotebookToMarkdownConverter()
    md_content = converter.convert_notebook_dict(notebook_data)
    generated_md_path.write_text(md_content, encoding="utf-8")

    # Read generated and expected content
    generated_content = generated_md_path.read_text(encoding="utf-8")
    expected_content = sample_md.read_text(encoding="utf-8")

    # Verify key content is present (not exact match due to formatting differences)
    assert "# Bidirectional Conversion Test" in generated_content
    assert "## Output Type: stream (stdout)" in generated_content
    assert "## Output Type: stream (stderr)" in generated_content
    assert "## Output Type: execute_result" in generated_content
    assert "## Output Type: display_data" in generated_content
    assert "## Output Type: error" in generated_content
    assert "## Multiple Outputs" in generated_content
    assert "## Special Characters" in generated_content

    # Verify output markers are present
    assert "@nemo-nb: output" in generated_content
    # Verify fence format is used (not explicit markers)
    assert "```python" in generated_content
    assert "<!-- @nemo-nb: cell python -->" not in generated_content

    # Verify code blocks are present
    assert 'print("This is stdout output")' in generated_content
    assert 'print("This is stderr output", file=sys.stderr)' in generated_content
    assert "21 * 2" in generated_content

    # Compare content structure with expected
    # Both should now use the new format (<!-- @nemo-nb: cell/output -->)

    # Normalize both for comparison
    generated_normalized = normalize_markdown(generated_content)
    expected_normalized = normalize_markdown(expected_content)

    # Verify all section headings from expected are in generated
    expected_headings = [line.strip() for line in expected_normalized.split("\n") if line.strip().startswith("##")]
    for heading in expected_headings:
        assert heading in generated_normalized, f"Expected heading not found in generated: {heading}"

    # Verify key code snippets from expected are in generated
    # These are the actual snippets in sample.ipynb
    expected_code_snippets = [
        'print("This is stdout output")',
        'print("This is stderr output", file=sys.stderr)',
        "21 * 2",
        "display(data)",
        'raise ValueError("This is a test error")',
        "50 + 50",
        'print("Special: $ # @")',
    ]
    for snippet in expected_code_snippets:
        assert snippet in generated_normalized, f"Expected code snippet not found in generated: {snippet}"

    # Verify similar content length (within 50% tolerance due to format differences)
    gen_len = len(generated_normalized)
    exp_len = len(expected_normalized)
    length_ratio = gen_len / exp_len
    assert 0.5 < length_ratio < 1.5, (
        f"Content length differs significantly: {gen_len} generated vs {exp_len} expected (ratio: {length_ratio:.2f})"
    )


def test_md_to_ipynb_conversion(sample_md, sample_ipynb, generated_dir):
    """Test converting .md to .ipynb matches the expected .ipynb file."""
    from nemo_nb.md_to_notebook import MarkdownToNotebookConverter

    # Convert the md to ipynb
    converter = MarkdownToNotebookConverter()
    generated_notebook = converter.convert(sample_md)

    # Write to generated directory
    generated_ipynb_path = generated_dir / "sample.md.ipynb"
    converter.write_notebook(generated_notebook, generated_ipynb_path)

    # Read expected notebook
    with open(sample_ipynb, "r", encoding="utf-8") as f:
        expected_notebook = json.load(f)

    # Normalize both for comparison
    generated_normalized = normalize_notebook(generated_notebook)
    expected_normalized = normalize_notebook(expected_notebook)

    # Compare structure
    assert generated_normalized.get("nbformat") == expected_normalized.get("nbformat"), (
        "Notebook format versions don't match"
    )
    assert generated_normalized.get("nbformat_minor") == expected_normalized.get("nbformat_minor"), (
        "Notebook format minor versions don't match"
    )

    # Compare cell count
    gen_cells = generated_normalized.get("cells", [])
    exp_cells = expected_normalized.get("cells", [])
    assert len(gen_cells) == len(exp_cells), (
        f"Cell count mismatch: generated has {len(gen_cells)}, expected has {len(exp_cells)}"
    )

    # Compare each cell
    for i, (gen_cell, exp_cell) in enumerate(zip(gen_cells, exp_cells)):
        # Compare cell type
        assert gen_cell.get("cell_type") == exp_cell.get("cell_type"), f"Cell {i}: cell_type mismatch"

        # Compare source
        gen_source = gen_cell.get("source", [])
        exp_source = exp_cell.get("source", [])
        assert gen_source == exp_source, (
            f"Cell {i}: source content mismatch\nGenerated: {gen_source}\nExpected: {exp_source}"
        )

        # For code cells, compare outputs
        if gen_cell.get("cell_type") == "code":
            gen_outputs = gen_cell.get("outputs", [])
            exp_outputs = exp_cell.get("outputs", [])
            assert len(gen_outputs) == len(exp_outputs), f"Cell {i}: output count mismatch"

            for j, (gen_output, exp_output) in enumerate(zip(gen_outputs, exp_outputs)):
                assert gen_output.get("output_type") == exp_output.get("output_type"), (
                    f"Cell {i}, Output {j}: output_type mismatch"
                )

                # Compare output content based on type
                if gen_output.get("output_type") == "stream":
                    assert gen_output.get("name") == exp_output.get("name"), (
                        f"Cell {i}, Output {j}: stream name mismatch"
                    )
                    assert gen_output.get("text") == exp_output.get("text"), (
                        f"Cell {i}, Output {j}: text content mismatch"
                    )
                elif gen_output.get("output_type") in ["execute_result", "display_data"]:
                    assert gen_output.get("data") == exp_output.get("data"), f"Cell {i}, Output {j}: data mismatch"
                elif gen_output.get("output_type") == "error":
                    assert gen_output.get("traceback") == exp_output.get("traceback"), (
                        f"Cell {i}, Output {j}: traceback mismatch"
                    )


def test_roundtrip_ipynb_to_md_to_ipynb(sample_ipynb, generated_dir):
    """Test that converting ipynb->md->ipynb preserves the content."""
    from nemo_nb.converter import NotebookToMarkdownConverter
    from nemo_nb.md_to_notebook import MarkdownToNotebookConverter

    # Step 1: Convert ipynb to md
    intermediate_md_path = generated_dir / "roundtrip.md"
    with open(sample_ipynb, "r", encoding="utf-8") as f:
        notebook_data = json.load(f)
    md_converter = NotebookToMarkdownConverter()
    md_content = md_converter.convert_notebook_dict(notebook_data)
    intermediate_md_path.write_text(md_content, encoding="utf-8")

    # Step 2: Convert md back to ipynb
    converter = MarkdownToNotebookConverter()
    roundtrip_notebook = converter.convert(intermediate_md_path)
    roundtrip_ipynb_path = generated_dir / "roundtrip.ipynb"
    converter.write_notebook(roundtrip_notebook, roundtrip_ipynb_path)

    # Step 3: Compare with original
    with open(sample_ipynb, "r", encoding="utf-8") as f:
        original_notebook = json.load(f)

    # Normalize both
    roundtrip_normalized = normalize_notebook(roundtrip_notebook)
    original_normalized = normalize_notebook(original_notebook)

    # Compare cells
    rt_cells = roundtrip_normalized.get("cells", [])
    orig_cells = original_normalized.get("cells", [])

    assert len(rt_cells) == len(orig_cells), f"Roundtrip cell count mismatch: {len(rt_cells)} vs {len(orig_cells)}"

    for i, (rt_cell, orig_cell) in enumerate(zip(rt_cells, orig_cells)):
        assert rt_cell.get("cell_type") == orig_cell.get("cell_type"), f"Roundtrip cell {i}: cell_type mismatch"
        assert rt_cell.get("source") == orig_cell.get("source"), f"Roundtrip cell {i}: source mismatch"


def test_roundtrip_md_to_ipynb_to_md(sample_md, generated_dir):
    """Test that converting md->ipynb->md preserves the content."""
    from nemo_nb.converter import NotebookToMarkdownConverter
    from nemo_nb.md_to_notebook import MarkdownToNotebookConverter

    # Step 1: Convert md to ipynb
    converter = MarkdownToNotebookConverter()
    intermediate_notebook = converter.convert(sample_md)
    intermediate_ipynb_path = generated_dir / "roundtrip2.ipynb"
    converter.write_notebook(intermediate_notebook, intermediate_ipynb_path)

    # Step 2: Convert ipynb back to md
    roundtrip_md_path = generated_dir / "roundtrip2.md"
    md_converter = NotebookToMarkdownConverter()
    md_content = md_converter.convert_notebook_dict(intermediate_notebook)
    roundtrip_md_path.write_text(md_content, encoding="utf-8")

    # Step 3: Compare with original
    original_content = sample_md.read_text(encoding="utf-8")
    roundtrip_content = roundtrip_md_path.read_text(encoding="utf-8")

    # Normalize both
    original_normalized = normalize_markdown(original_content)
    roundtrip_normalized = normalize_markdown(roundtrip_content)

    assert roundtrip_normalized == original_normalized, (
        f"Roundtrip markdown mismatch.\nOriginal: {sample_md}\nRoundtrip: {roundtrip_md_path}"
    )


def test_md_with_tabbed_code_blocks_raises_error(generated_dir):
    """Test that markdown files with tabbed code blocks raise ValueError."""
    from nemo_nb.md_to_notebook import MarkdownToNotebookConverter

    converter = MarkdownToNotebookConverter()

    # Case 1: Tabbed fence
    tabbed_fence_md = generated_dir / "tabbed_fence.md"
    tabbed_fence_md.write_text("\t```python\nprint('hi')\n```", encoding="utf-8")

    with pytest.raises(ValueError, match="Code block start fence contains tabs"):
        converter.convert(tabbed_fence_md)

    # Case 2: Tabbed first line of content
    tabbed_content_md = generated_dir / "tabbed_content.md"
    tabbed_content_md.write_text("```python\n\tprint('hi')\n```", encoding="utf-8")

    with pytest.raises(ValueError, match="First line of code block contains tabs"):
        converter.convert(tabbed_content_md)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
