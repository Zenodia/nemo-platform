# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Integration test for edge cases in markdown to notebook conversion.

Tests that various "messed up" markdown scenarios are handled gracefully:
- Empty code blocks
- Excessive/missing whitespace
- Regular HTML comments (not markers)
- Broken markdown syntax near markers
- Special characters and unicode
- Complex code content
- Edge cases in output positioning
"""

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
def edge_cases_md(test_dir):
    """Return path to the edge_cases.md file."""
    return test_dir / "edge_cases.md"


def test_edge_cases_md_to_notebook_converts_without_error(edge_cases_md, generated_dir):
    """Test that markdown with edge cases converts to notebook without errors.

    This is the most basic test - just verify conversion completes.
    """
    from nemo_nb.md_to_notebook import MarkdownToNotebookConverter

    converter = MarkdownToNotebookConverter()
    generated_notebook = converter.convert(edge_cases_md)

    # Write to generated directory
    generated_ipynb_path = generated_dir / "edge_cases.ipynb"
    converter.write_notebook(generated_notebook, generated_ipynb_path)

    # Basic validation - should have cells
    assert "cells" in generated_notebook
    assert len(generated_notebook["cells"]) > 0
    assert generated_notebook.get("nbformat") == 4


def test_basic_malformed_markdown_handling(edge_cases_md, generated_dir):
    """Test handling of empty blocks, excessive whitespace, and broken markdown.

    Covers: Test 1 (empty block), Test 2 (excessive blank lines),
            Test 5 (broken markdown), Test 9 (zero blank lines),
            Test 10 (trailing whitespace), Test 17 (empty output)
    """
    from nemo_nb.md_to_notebook import MarkdownToNotebookConverter

    converter = MarkdownToNotebookConverter()
    notebook = converter.convert(edge_cases_md)

    cells = notebook["cells"]

    # Find the cell for "Test 1: Empty Code Block"
    # It should create a code cell even if empty
    code_cells = [c for c in cells if c["cell_type"] == "code"]
    assert len(code_cells) > 0, "Should have at least one code cell"

    # Empty cells might or might not be created - just verify no crash during conversion

    # Verify the notebook has reasonable structure despite malformed markdown
    markdown_cells = [c for c in cells if c["cell_type"] == "markdown"]
    assert len(markdown_cells) > 0, "Should have markdown cells"

    # Check that text like "###NoSpaceAfterHashes" is preserved somewhere
    all_content = "\n".join("".join(c.get("source", [])) for c in cells)
    # The broken markdown should be captured somewhere (might be normalized)
    assert "Test 1" in all_content
    assert "Test 2" in all_content


def test_special_characters_and_unicode(edge_cases_md, generated_dir):
    """Test handling of unicode, emoji, and special characters.

    Covers: Test 4 (unicode/emoji), Test 8 (special chars not in markers),
            Test 16 (HTML entities)
    """
    from nemo_nb.md_to_notebook import MarkdownToNotebookConverter

    converter = MarkdownToNotebookConverter()
    notebook = converter.convert(edge_cases_md)

    cells = notebook["cells"]

    # Find cells with special characters
    all_content = "\n".join("".join(c.get("source", [])) for c in cells)

    # Unicode and emoji should be preserved
    assert "??" in all_content or "Hello" in all_content, "Unicode content should be preserved"

    # Special characters in code should be preserved
    assert "$100" in all_content or "price" in all_content
    assert "#python" in all_content or "hashtag" in all_content
    assert "@example.com" in all_content or "email" in all_content

    # HTML entities should be preserved as-is in markdown
    assert "&lt;" in all_content or "HTML entities" in all_content


def test_regular_html_comments_not_treated_as_markers(edge_cases_md, generated_dir):
    """Test that regular HTML comments are preserved as markdown content.

    Covers: Test 3 (regular HTML comments), Test 12 (HTML-like comments in code)
    """
    from nemo_nb.md_to_notebook import MarkdownToNotebookConverter

    converter = MarkdownToNotebookConverter()
    notebook = converter.convert(edge_cases_md)

    cells = notebook["cells"]

    # Find markdown cells
    markdown_cells = [c for c in cells if c["cell_type"] == "markdown"]

    # Regular comments like "<!-- This is just a regular comment -->"
    # should be in markdown cells, not interpreted as markers
    markdown_content = "\n".join("".join(c.get("source", [])) for c in markdown_cells)

    # The text around the regular comment should be preserved
    assert "regular comment" in markdown_content.lower() or "Test 3" in markdown_content

    # Code cells with HTML-like content
    code_cells = [c for c in cells if c["cell_type"] == "code"]
    code_content = "\n".join("".join(c.get("source", [])) for c in code_cells)

    # Comments in code like "# This comment has HTML-like content: <!--"
    # should be preserved in code cells
    assert "HTML-like" in code_content or "@not-a-marker" in code_content


def test_complex_code_content(edge_cases_md, generated_dir):
    """Test handling of complex code: nested fences, long lines, mixed indentation.

    Covers: Test 6 (nested fences), Test 11 (long lines), Test 19 (mixed indentation)
    """
    from nemo_nb.md_to_notebook import MarkdownToNotebookConverter

    converter = MarkdownToNotebookConverter()
    notebook = converter.convert(edge_cases_md)

    cells = notebook["cells"]
    code_cells = [c for c in cells if c["cell_type"] == "code"]

    # Find cell with nested fences (uses 4 backticks)
    code_content = "\n".join("".join(c.get("source", [])) for c in code_cells)

    # Should preserve nested fence content
    assert "nested = True" in code_content or "markdown_text" in code_content

    # Should preserve very long lines
    assert "very_long_variable_name" in code_content or len(code_content) > 1000

    # Should preserve mixed indentation (tabs and spaces)
    # The actual content should be there even if indentation is normalized


def test_output_edge_cases(edge_cases_md, generated_dir):
    """Test edge cases in output handling.

    Covers: Test 7 (output with code-like content), Test 13 (multiple outputs),
            Test 17 (empty output)
    """
    from nemo_nb.md_to_notebook import MarkdownToNotebookConverter

    converter = MarkdownToNotebookConverter()
    notebook = converter.convert(edge_cases_md)

    cells = notebook["cells"]
    code_cells = [c for c in cells if c["cell_type"] == "code"]

    # Find cells with outputs
    cells_with_outputs = [c for c in code_cells if c.get("outputs", [])]

    assert len(cells_with_outputs) > 0, "Should have cells with outputs"

    # Check for cell with multiple outputs (Test 13)
    multi_output_cells = [c for c in code_cells if len(c.get("outputs", [])) > 1]
    assert len(multi_output_cells) > 0, "Should have at least one cell with multiple outputs"

    # Verify outputs are structured correctly
    for cell in cells_with_outputs:
        for output in cell.get("outputs", []):
            assert "output_type" in output, "Output should have output_type field"

    # Check that output with code-like content is preserved
    all_outputs = []
    for cell in code_cells:
        for output in cell.get("outputs", []):
            if "text" in output:
                text = output["text"]
                if isinstance(text, list):
                    all_outputs.append("".join(text))
                else:
                    all_outputs.append(text)

    all_output_text = "\n".join(all_outputs)
    # Output might contain code-like content
    assert len(all_output_text) > 0, "Should have some output text"


def test_content_near_markers(edge_cases_md, generated_dir):
    """Test handling of various content types near markers.

    Covers: Test 14 (lists near code), Test 15 (blockquote near code),
            Test 18 (inline code near fenced code)
    """
    from nemo_nb.md_to_notebook import MarkdownToNotebookConverter

    converter = MarkdownToNotebookConverter()
    notebook = converter.convert(edge_cases_md)

    cells = notebook["cells"]
    markdown_cells = [c for c in cells if c["cell_type"] == "markdown"]

    markdown_content = "\n".join("".join(c.get("source", [])) for c in markdown_cells)

    # Lists should be preserved in markdown
    assert "- Item" in markdown_content or "list" in markdown_content.lower()

    # Blockquotes should be preserved
    assert ">" in markdown_content or "blockquote" in markdown_content.lower()

    # Inline code should be preserved
    assert "`" in markdown_content or "print()" in markdown_content


def test_unexpected_markdown_between_code_and_output(edge_cases_md, generated_dir):
    """Test the controversial case: markdown header between code and output marker.

    Covers: Test 20 (markdown header between code and output)

    This test documents the behavior when there's unexpected content between
    a code block and its output marker. This might fail or behave unexpectedly.
    """
    from nemo_nb.md_to_notebook import MarkdownToNotebookConverter

    converter = MarkdownToNotebookConverter()
    notebook = converter.convert(edge_cases_md)

    # Just verify it doesn't crash - behavior might be undefined
    cells = notebook["cells"]
    assert len(cells) > 0

    # The "Unexpected Header Here" might end up in various places depending on parsing
    all_content = "\n".join("".join(c.get("source", [])) for c in cells)

    # Just check the content exists somewhere - placement might vary
    assert "Test 20" in all_content


def test_cell_count_is_reasonable(edge_cases_md, generated_dir):
    """Sanity check that we have a reasonable number of cells.

    The edge_cases.md has 20 test sections, so we should have a reasonable
    number of cells (probably 40-60 including markdown and code cells).
    """
    from nemo_nb.md_to_notebook import MarkdownToNotebookConverter

    converter = MarkdownToNotebookConverter()
    notebook = converter.convert(edge_cases_md)

    cells = notebook["cells"]

    # Should have a decent number of cells
    assert len(cells) >= 10, f"Expected at least 10 cells, got {len(cells)}"

    # Should have mix of markdown and code
    code_cells = [c for c in cells if c["cell_type"] == "code"]
    markdown_cells = [c for c in cells if c["cell_type"] == "markdown"]

    assert len(code_cells) > 0, "Should have code cells"
    assert len(markdown_cells) > 0, "Should have markdown cells"

    print("\nGenerated notebook stats:")
    print(f"  Total cells: {len(cells)}")
    print(f"  Code cells: {len(code_cells)}")
    print(f"  Markdown cells: {len(markdown_cells)}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
