# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Test edge cases for list manipulation in md_to_notebook.py."""

import tempfile
from pathlib import Path

import pytest
from nemo_nb.md_to_notebook import MarkdownToNotebookConverter, expand_includes_in_text


class TestListManipulationEdgeCases:
    """Test edge cases for list manipulation operations."""

    def test_strip_leading_empty_lines_empty_list(self):
        """Test stripping leading empty lines from empty list."""
        converter = MarkdownToNotebookConverter()
        result = converter._strip_leading_empty_lines([])
        assert result == []

    def test_strip_leading_empty_lines_single_element(self):
        """Test stripping leading empty lines from single element."""
        converter = MarkdownToNotebookConverter()
        result = converter._strip_leading_empty_lines(["content"])
        assert result == ["content"]

    def test_strip_leading_empty_lines_single_empty(self):
        """Test stripping leading empty lines when only empty string."""
        converter = MarkdownToNotebookConverter()
        result = converter._strip_leading_empty_lines([""])
        assert result == []

    def test_strip_leading_empty_lines_all_empty(self):
        """Test stripping leading empty lines when all are empty."""
        converter = MarkdownToNotebookConverter()
        result = converter._strip_leading_empty_lines(["", "  ", "\t", ""])
        assert result == []

    def test_strip_leading_empty_lines_some_empty(self):
        """Test stripping leading empty lines with some empty."""
        converter = MarkdownToNotebookConverter()
        result = converter._strip_leading_empty_lines(["", "content", "more"])
        assert result == ["content", "more"]

    def test_strip_leading_empty_lines_whitespace_only(self):
        """Test stripping leading whitespace-only lines."""
        converter = MarkdownToNotebookConverter()
        result = converter._strip_leading_empty_lines(["  ", "\t", "content"])
        assert result == ["content"]

    def test_strip_trailing_empty_lines_empty_list(self):
        """Test stripping trailing empty lines from empty list."""
        converter = MarkdownToNotebookConverter()
        result = converter._strip_trailing_empty_lines([])
        assert result == []

    def test_strip_trailing_empty_lines_single_element(self):
        """Test stripping trailing empty lines from single element."""
        converter = MarkdownToNotebookConverter()
        result = converter._strip_trailing_empty_lines(["content"])
        assert result == ["content"]

    def test_strip_trailing_empty_lines_single_empty(self):
        """Test stripping trailing empty lines when only empty string."""
        converter = MarkdownToNotebookConverter()
        result = converter._strip_trailing_empty_lines([""])
        assert result == []

    def test_strip_trailing_empty_lines_all_empty(self):
        """Test stripping trailing empty lines when all are empty."""
        converter = MarkdownToNotebookConverter()
        result = converter._strip_trailing_empty_lines(["", "  ", "\t", ""])
        assert result == []

    def test_strip_trailing_empty_lines_some_empty(self):
        """Test stripping trailing empty lines with some empty."""
        converter = MarkdownToNotebookConverter()
        result = converter._strip_trailing_empty_lines(["content", "more", ""])
        assert result == ["content", "more"]

    def test_strip_trailing_empty_lines_whitespace_only(self):
        """Test stripping trailing whitespace-only lines."""
        converter = MarkdownToNotebookConverter()
        result = converter._strip_trailing_empty_lines(["content", "  ", "\t"])
        assert result == ["content"]

    def test_strip_empty_lines_empty_list(self):
        """Test stripping both leading and trailing from empty list."""
        converter = MarkdownToNotebookConverter()
        result = converter._strip_empty_lines([])
        assert result == []

    def test_strip_empty_lines_single_element(self):
        """Test stripping both from single element."""
        converter = MarkdownToNotebookConverter()
        result = converter._strip_empty_lines(["content"])
        assert result == ["content"]

    def test_strip_empty_lines_all_empty(self):
        """Test stripping both when all are empty."""
        converter = MarkdownToNotebookConverter()
        result = converter._strip_empty_lines(["", "  ", "\t", ""])
        assert result == []

    def test_strip_empty_lines_leading_and_trailing(self):
        """Test stripping both leading and trailing empty lines."""
        converter = MarkdownToNotebookConverter()
        result = converter._strip_empty_lines(["", "content", "more", ""])
        assert result == ["content", "more"]

    def test_strip_empty_lines_preserves_middle(self):
        """Test that empty lines in the middle are preserved."""
        converter = MarkdownToNotebookConverter()
        result = converter._strip_empty_lines(["", "content", "", "more", ""])
        assert result == ["content", "", "more"]

    def test_strip_empty_lines_no_mutation(self):
        """Test that strip operations don't mutate original list."""
        converter = MarkdownToNotebookConverter()
        original = ["", "content", ""]
        original_copy = original.copy()
        result = converter._strip_empty_lines(original)
        # Original list should not be mutated
        assert original == original_copy
        # Result should be stripped
        assert result == ["content"]

    def test_save_current_cell_empty_list(self):
        """Test saving cell with empty list."""
        converter = MarkdownToNotebookConverter()
        converter._save_current_cell([], "markdown", "python", False)
        # Should not add any cells
        assert len(converter.cells) == 0

    def test_save_current_cell_all_empty_lines(self):
        """Test saving cell with all empty lines."""
        converter = MarkdownToNotebookConverter()
        converter._save_current_cell(["", "  ", ""], "markdown", "python", False)
        # Should not add any cells
        assert len(converter.cells) == 0

    def test_save_current_cell_with_skip(self):
        """Test saving cell with skip=True."""
        converter = MarkdownToNotebookConverter()
        converter._save_current_cell(["content"], "markdown", "python", True)
        # Should not add any cells
        assert len(converter.cells) == 0

    def test_save_current_cell_invalid_type_raises_error(self):
        """Test that invalid cell_type raises ValueError."""
        converter = MarkdownToNotebookConverter()
        with pytest.raises(ValueError, match="Invalid cell_type"):
            converter._save_current_cell(["content"], "invalid", "python", False)

    def test_save_current_cell_none_type_raises_error(self):
        """Test that None cell_type raises ValueError."""
        converter = MarkdownToNotebookConverter()
        with pytest.raises(ValueError, match="Invalid cell_type"):
            converter._save_current_cell(["content"], None, "python", False)

    def test_add_markdown_cell_empty_list(self):
        """Test adding markdown cell with empty list."""
        converter = MarkdownToNotebookConverter()
        converter._add_markdown_cell([])
        # Should not add any cells
        assert len(converter.cells) == 0

    def test_add_markdown_cell_all_empty_lines(self):
        """Test adding markdown cell with all empty lines."""
        converter = MarkdownToNotebookConverter()
        converter._add_markdown_cell(["", "  ", ""])
        # Should not add any cells
        assert len(converter.cells) == 0

    def test_add_markdown_cell_single_line(self):
        """Test adding markdown cell with single line."""
        converter = MarkdownToNotebookConverter()
        converter._add_markdown_cell(["# Title"])
        assert len(converter.cells) == 1
        assert converter.cells[0].cell_type == "markdown"
        assert converter.cells[0].source == ["# Title"]

    def test_add_code_cell_empty_list(self):
        """Test adding code cell with empty list."""
        converter = MarkdownToNotebookConverter()
        converter._add_code_cell([], "python")
        # Should not add any cells
        assert len(converter.cells) == 0

    def test_add_code_cell_single_line(self):
        """Test adding code cell with single line."""
        converter = MarkdownToNotebookConverter()
        converter._add_code_cell(["print('hello')"], "python")
        assert len(converter.cells) == 1
        assert converter.cells[0].cell_type == "code"
        assert converter.cells[0].source == ["print('hello')"]

    def test_large_list_performance(self):
        """Test that large lists don't cause performance issues."""
        converter = MarkdownToNotebookConverter()
        # Create a large list with empty lines at start and end
        large_list = [""] * 1000 + ["content"] * 100 + [""] * 1000
        result = converter._strip_empty_lines(large_list)
        assert len(result) == 100
        assert all(line == "content" for line in result)

    def test_nested_empty_content(self):
        """Test deeply nested structure with empty content."""
        converter = MarkdownToNotebookConverter()
        lines = ["", "", "content", "", "", "more", "", ""]
        result = converter._strip_empty_lines(lines)
        assert result == ["content", "", "", "more"]


class TestAssertionCoverage:
    """Test that assertions are working correctly."""

    def test_strip_leading_assertion_valid(self):
        """Test that strip leading assertion doesn't fire on valid input."""
        converter = MarkdownToNotebookConverter()
        # This should not raise an assertion error
        result = converter._strip_leading_empty_lines(["content"])
        assert result == ["content"]

    def test_strip_trailing_assertion_valid(self):
        """Test that strip trailing assertion doesn't fire on valid input."""
        converter = MarkdownToNotebookConverter()
        # This should not raise an assertion error
        result = converter._strip_trailing_empty_lines(["content"])
        assert result == ["content"]

    def test_strip_both_assertion_valid(self):
        """Test that strip both assertion doesn't fire on valid input."""
        converter = MarkdownToNotebookConverter()
        # This should not raise an assertion error
        result = converter._strip_empty_lines(["", "content", ""])
        assert result == ["content"]


class TestNestedDirectiveFences:
    """Test proper handling of nested fences in directive blocks."""

    def test_admonition_with_code_block(self):
        """Test that code blocks inside directive fences don't prematurely close the directive.

        This was a bug where a ```bash code block (3 backticks) inside a ````{admonition}
        directive (4 backticks) would incorrectly close the directive when its closing ```
        was encountered, causing subsequent content to be misparsed as a code cell.
        """
        markdown = """<!-- @nemo-nb: process -->
# Test

Some text before.

````{admonition} Optional Configuration
---
class: tip
---
Here's a command inside the admonition:
```bash
echo "hello"
```
````

## After Admonition

Regular text after the admonition should be markdown, not code.

```python
print("This is actual Python code")
```

More text.
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(markdown)
            f.flush()
            temp_path = Path(f.name)

        try:
            converter = MarkdownToNotebookConverter()
            notebook = converter.convert(temp_path)
            cells = notebook["cells"]

            # Should have multiple cells, not everything lumped into one code cell
            assert len(cells) >= 3, f"Expected at least 3 cells, got {len(cells)}"

            # First cell should be markdown with the title
            assert cells[0]["cell_type"] == "markdown"
            assert "# Test" in "".join(cells[0]["source"])

            # Find the python code cell
            python_cells = [
                c
                for c in cells
                if c.get("cell_type") == "code" and c.get("metadata", {}).get("language", "python") == "python"
            ]
            assert len(python_cells) == 1, f"Expected 1 Python code cell, got {len(python_cells)}"

            # Python code cell should contain the actual Python code
            python_cell_source = "".join(python_cells[0]["source"])
            assert 'print("This is actual Python code")' in python_cell_source

            # "After Admonition" text should be in a markdown cell, not a code cell
            markdown_cells = [c for c in cells if c.get("cell_type") == "markdown"]
            all_markdown = "".join("".join(c["source"]) for c in markdown_cells)
            assert "After Admonition" in all_markdown
            assert "Regular text after the admonition" in all_markdown

        finally:
            temp_path.unlink(missing_ok=True)

    def test_nested_directive_fences_different_lengths(self):
        """Test that directive fences with different lengths are tracked separately."""

        markdown = """<!-- @nemo-nb: process -->
# Test

`````{outer}
Outer directive with 5 backticks

````{inner}
Inner directive with 4 backticks

```python
print("code inside inner")
```
````

Text between directives

```bash
echo "bash inside outer"
```
`````

Text after all directives.
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(markdown)
            f.flush()
            temp_path = Path(f.name)

        try:
            converter = MarkdownToNotebookConverter()
            notebook = converter.convert(temp_path)
            cells = notebook["cells"]

            # Should successfully parse without errors
            assert len(cells) >= 1

            # The text after all directives should be in a markdown cell
            markdown_cells = [c for c in cells if c.get("cell_type") == "markdown"]
            all_markdown = "".join("".join(c["source"]) for c in markdown_cells)
            assert "Text after all directives" in all_markdown

        finally:
            temp_path.unlink(missing_ok=True)


class TestExpandIncludesInText:
    """Test text-level {include} directive expansion."""

    def test_expands_include_as_code_cell(self, tmp_path):
        """Code blocks in included files become proper code cells, not markdown."""
        snippet = tmp_path / "setup.md"
        snippet.write_text("# Setup\n\n```bash\nnemo install\n```\n")

        md_file = tmp_path / "tutorial.md"
        md_file.write_text("<!-- @nemo-nb: process -->\n# Tutorial\n\n```{include} setup.md\n```\n\n## Next\n")

        converter = MarkdownToNotebookConverter()
        notebook = converter.convert(md_file)

        cell_types = [c["cell_type"] for c in notebook["cells"]]
        sources = ["".join(c["source"]) for c in notebook["cells"]]

        # The bash block from the snippet must be a code cell, not markdown
        assert "code" in cell_types, "Expected at least one code cell from included snippet"
        bash_cell = next(c for c in notebook["cells"] if c["cell_type"] == "code")
        assert "nemo install" in "".join(bash_cell["source"])
        # Trailing prose must still appear
        assert any("Next" in s for s in sources)
        # No raw {include} directive should remain
        assert not any("{include}" in s for s in sources)

    def test_expand_includes_in_text_missing_file(self, tmp_path):
        """Missing includes are left as-is with a warning."""
        md_file = tmp_path / "tutorial.md"
        content = "# Title\n\n```{include} nonexistent.md\n```\n\nAfter\n"
        result = expand_includes_in_text(content, md_file)
        assert "{include}" in result  # directive preserved
        assert "After" in result

    def test_expand_includes_in_text_no_includes(self, tmp_path):
        """Content without {include} is returned unchanged."""
        md_file = tmp_path / "tutorial.md"
        content = "# Title\n\n```python\nprint('hello')\n```\n"
        result = expand_includes_in_text(content, md_file)
        assert result == content
