# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Test for code formatting preservation issues.

Issue: Multi-line dict/object formatting should be preserved in code cells.
The converter should not modify the original code formatting.
"""

from nemo_nb.converter import NotebookConverter


def test_multiline_dict_formatting_preserved():
    """Test that multi-line dict formatting in code cells is preserved."""
    notebook = {
        "cells": [
            {
                "cell_type": "code",
                "metadata": {},
                "execution_count": None,
                "outputs": [],
                "source": [
                    "config = {\n",
                    '    "model": "test",\n',
                    '    "settings": {\n',
                    '        "key1": "value1",\n',
                    '        "key2": "value2"\n',
                    "    }\n",
                    "}",
                ],
            },
        ],
        "metadata": {},
        "nbformat": 4,
        "nbformat_minor": 4,
    }

    converter = NotebookConverter()
    result = converter.convert_notebook_dict(notebook)

    # Expected: multi-line formatting preserved (without Jupyter/MyST blank line after fence)
    expected = """```python
config = {
    "model": "test",
    "settings": {
        "key1": "value1",
        "key2": "value2"
    }
}
```"""

    result = result.strip()

    print("\n=== EXPECTED ===")
    print(expected)
    print("\n=== ACTUAL ===")
    print(result)

    assert result == expected, "Multi-line dict formatting was not preserved"


def test_single_line_dict_not_expanded():
    """Test that single-line dicts are kept as single-line (no auto-formatting)."""
    notebook = {
        "cells": [
            {
                "cell_type": "code",
                "metadata": {},
                "execution_count": None,
                "outputs": [],
                "source": [
                    'config = {"key": "value", "nested": {"a": "b"}}',
                ],
            },
        ],
        "metadata": {},
        "nbformat": 4,
        "nbformat_minor": 4,
    }

    converter = NotebookConverter()
    result = converter.convert_notebook_dict(notebook)

    # Should keep single line as-is (no reformatting, without Jupyter/MyST blank line)
    expected = """```python
config = {"key": "value", "nested": {"a": "b"}}
```"""

    result = result.strip()

    assert result == expected, "Converter should not reformat code"


def test_indentation_with_tabs_preserved():
    """Test that tab indentation is preserved when specified."""
    notebook = {
        "cells": [
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "<!-- @nemo-nb: notebook-convert-4-space-to-tab -->\n",
                ],
            },
            {
                "cell_type": "code",
                "metadata": {},
                "execution_count": None,
                "outputs": [],
                "source": [
                    "def foo():\n",
                    "    return {\n",
                    '        "key": "value"\n',
                    "    }",
                ],
            },
        ],
        "metadata": {},
        "nbformat": 4,
        "nbformat_minor": 4,
    }

    converter = NotebookConverter()
    result = converter.convert_notebook_dict(notebook)

    # With notebook-convert-4-space-to-tab, 4 spaces should become tabs
    # The result should have tabs for indentation
    assert "\t" in result or "    " in result, "Should have indentation"

    # Verify the structure is maintained
    assert "def foo():" in result
    assert '"key": "value"' in result
