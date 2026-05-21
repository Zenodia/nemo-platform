# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Tests for MyST include directive expansion."""

import tempfile
from pathlib import Path

from nemo_nb.md_to_notebook import MarkdownToNotebookConverter, expand_includes


def test_expand_includes_basic():
    """Test that include directives are expanded."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        # Create an include file
        include_file = tmpdir / "include.md"
        include_file.write_text("# Included Content\n\nThis is included.")

        # Create main file with include directive
        main_content = """# Main File

```{include} include.md
```

More content."""

        result = expand_includes(main_content, tmpdir)

        # Check that the include was expanded
        assert "# Included Content" in result
        assert "This is included." in result
        assert "```{include}" not in result


def test_expand_includes_nested():
    """Test that nested includes work."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        # Create nested include files
        inner_file = tmpdir / "inner.md"
        inner_file.write_text("Inner content")

        middle_file = tmpdir / "middle.md"
        middle_file.write_text(
            """Middle content

```{include} inner.md
```
"""
        )

        # Create main file
        main_content = """Main content

```{include} middle.md
```
"""

        result = expand_includes(main_content, tmpdir)

        # Check that all includes were expanded
        assert "Main content" in result
        assert "Middle content" in result
        assert "Inner content" in result
        assert "```{include}" not in result


def test_expand_includes_missing_file():
    """Test that missing include files are left as-is."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        main_content = """# Main File

```{include} nonexistent.md
```
"""

        result = expand_includes(main_content, tmpdir)

        # Check that the directive is left unchanged
        assert "```{include} nonexistent.md" in result


def test_converter_expands_includes():
    """Test that the converter expands includes during conversion."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        # Create an include file with code
        include_file = tmpdir / "setup.md"
        include_file.write_text(
            """```python
import os
x = 1
```
"""
        )

        # Create main file with process marker and include
        main_file = tmpdir / "main.md"
        main_file.write_text(
            """<!-- @nemo-nb: process -->

# Main

```{include} setup.md
```

```python
y = x + 1
```
"""
        )

        # Convert to notebook
        converter = MarkdownToNotebookConverter()
        notebook = converter.convert(main_file)

        # Check that we have code cells from both files
        code_cells = [c for c in notebook["cells"] if c["cell_type"] == "code"]
        assert len(code_cells) == 2

        # Check that the first cell is from the included file
        first_cell_source = "".join(code_cells[0]["source"])
        assert "import os" in first_cell_source
        assert "x = 1" in first_cell_source

        # Check that the second cell is from the main file
        second_cell_source = "".join(code_cells[1]["source"])
        assert "y = x + 1" in second_cell_source
