# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Unit tests for notebook converter with marker-based commands.

Tests conversion with marker commands:
1. Markdown cells pass through unchanged (after marker removal)
2. Code cells convert to code fences (after marker removal)
3. Outputs are ignored
4. Hide markers work
5. Language detection works
6. Directives are preserved
7. Marker commands are processed correctly
"""

from nemo_nb.converter import NotebookConverter


def test_basic_conversion():
    """Test markdown and code cell conversion."""
    notebook = {
        "cells": [
            {"cell_type": "markdown", "source": ["# Title\n", "Text"]},
            {
                "cell_type": "code",
                "metadata": {"language": "python"},
                "source": ["x = 1"],
                "outputs": [{"text": "1\n"}],
            },
        ]
    }

    converter = NotebookConverter({})
    md = converter.convert_notebook_dict(notebook)

    assert "# Title" in md
    assert "Text" in md
    assert "```python" in md
    assert "x = 1" in md


def test_markdown_cell_passthrough():
    """Test that markdown cells pass through exactly as-is."""
    notebook = {"cells": [{"cell_type": "markdown", "source": ["# Title\n", "\n", "Paragraph with **bold**\n"]}]}

    converter = NotebookConverter({})
    md = converter.convert_notebook_dict(notebook)

    assert md == "# Title\n\nParagraph with **bold**"


def test_code_cell_conversion():
    """Test code cell converts to code fence."""
    notebook = {"cells": [{"cell_type": "code", "source": ["x = 1\n", "y = 2\n"]}]}

    converter = NotebookConverter({})
    md = converter.convert_notebook_dict(notebook)

    # Jupyter/MyST format removed blank line after fence opening
    assert md == "```python\nx = 1\ny = 2\n\n```"


def test_output_cells_stripped():
    """Test that output cells are automatically stripped during conversion."""
    notebook = {
        "cells": [
            {
                "cell_type": "code",
                "source": ["x = 1 + 1"],
                "execution_count": 1,
                "metadata": {"execution": {"iopub.execute_input": "2025-11-14T19:54:49.359454Z"}},
                "outputs": [
                    {"output_type": "stream", "name": "stdout", "text": ["Output text that should be stripped\n"]},
                    {
                        "output_type": "execute_result",
                        "execution_count": 1,
                        "data": {"text/plain": ["42"]},
                        "metadata": {},
                    },
                ],
            }
        ]
    }

    converter = NotebookConverter({})
    md = converter.convert_notebook_dict(notebook)

    # Verify the code is present
    assert "x = 1 + 1" in md
    assert "```python" in md

    # Verify outputs are NOT present in the markdown
    assert "Output text that should be stripped" not in md  # stdout output should be stripped
    assert "42" not in md  # execute_result output should be stripped
    assert "output_type" not in md
    assert "stream" not in md


def test_hide_cell_via_marker():
    """Test cell hiding via marker command."""
    notebook = {
        "cells": [
            {"cell_type": "code", "source": ["# @nemo-nb: hide\n", "secret = 'hidden'"]},
            {"cell_type": "code", "source": ["visible = 'shown'"]},
        ]
    }

    converter = NotebookConverter({})
    md = converter.convert_notebook_dict(notebook)

    assert "secret" not in md
    assert "hidden" not in md
    assert "visible" in md
    assert "shown" in md


def test_hide_cell_via_metadata():
    """Test cell hiding via metadata (backward compatibility)."""
    notebook = {
        "cells": [
            {"cell_type": "code", "metadata": {"nemo_nb": {"hide": True}}, "source": ["secret = 'hidden'"]},
            {"cell_type": "code", "source": ["visible = 'shown'"]},
        ]
    }

    converter = NotebookConverter({})
    md = converter.convert_notebook_dict(notebook)

    assert "secret" not in md
    assert "visible" in md


def test_hide_cell_via_tags():
    """Test cell hiding via tags (backward compatibility)."""
    notebook = {
        "cells": [
            {"cell_type": "code", "metadata": {"tags": ["hide-cell"]}, "source": ["secret = 'hidden'"]},
            {"cell_type": "markdown", "metadata": {"tags": ["hide-cell", "other-tag"]}, "source": ["Hidden markdown"]},
        ]
    }

    converter = NotebookConverter({})
    md = converter.convert_notebook_dict(notebook)

    assert "secret" not in md
    assert "Hidden markdown" not in md


def test_language_detection():
    """Test language metadata for syntax highlighting."""
    notebook = {
        "cells": [
            {"cell_type": "code", "metadata": {"language": "bash"}, "source": ["echo 'hello'"]},
            {"cell_type": "code", "metadata": {"language": "javascript"}, "source": ["console.log('hello')"]},
        ]
    }

    converter = NotebookConverter({})
    md = converter.convert_notebook_dict(notebook)

    # bash should be preserved
    assert "```bash" in md
    assert "echo 'hello'" in md
    assert "```javascript" in md
    assert "console.log('hello')" in md


def test_directive_preservation():
    """CRITICAL: Directives in markdown cells must pass through exactly."""
    notebook = {
        "cells": [
            {
                "cell_type": "markdown",
                "source": ["::::{tab-set}\n", ":::{tab-item} Example\n", "Content here\n", ":::\n", "::::\n"],
            }
        ]
    }

    converter = NotebookConverter({})
    md = converter.convert_notebook_dict(notebook)

    assert "::::{tab-set}" in md
    assert ":::{tab-item} Example" in md
    assert "Content here" in md


def test_marker_removed_from_output():
    """Test that marker lines are removed from output."""
    notebook = {"cells": [{"cell_type": "code", "source": ["# @nemo-nb: tab Python\n", "x = 1"]}]}

    converter = NotebookConverter({})
    md = converter.convert_notebook_dict(notebook)

    assert "@nemo-nb" not in md
    assert "x = 1" in md


def test_wrap_directive_marker():
    """Test wrap directive via wrap-cell-start and wrap-cell-end markers."""
    notebook = {
        "cells": [
            {
                "cell_type": "code",
                "source": [
                    "# @nemo-nb: wrap-cell-start :::{dropdown} Click to expand\n",
                    "# @nemo-nb: wrap-cell-end :::   \n",
                    "x = 1",
                ],
            }
        ]
    }

    converter = NotebookConverter({})
    md = converter.convert_notebook_dict(notebook)

    assert ":::{dropdown} Click to expand" in md
    assert "x = 1" in md
    assert ":::" in md


def test_group_indent_space_start_end():
    """Test multi-cell grouping with indentation.

    When marker is at the start of a cell, the entire cell
    and all subsequent cells are indented.
    """
    notebook = {
        "cells": [
            {
                "cell_type": "markdown",
                "source": ["<!-- @nemo-nb: multi-cell-indent-space-start my-group 3 -->\n", "# Step 1"],
            },
            {"cell_type": "code", "source": ["x = 1"]},
            {"cell_type": "code", "source": ["# @nemo-nb: multi-cell-indent-space-end my-group\n", "y = 2"]},
        ]
    }

    converter = NotebookConverter({})
    md = converter.convert_notebook_dict(notebook)

    # Marker at start: entire cell IS indented
    assert "   # Step 1" in md
    # Subsequent cells ARE indented
    assert "   ```python" in md
    assert "   x = 1" in md
    # End marker at start of cell: content after it is NOT indented
    assert "y = 2" in md
    assert "   y = 2" not in md
    assert "@nemo-nb" not in md


def test_group_indent_space_marker_in_middle():
    """Test multi-cell grouping when marker is in middle of cell.

    When marker is in the middle of a cell, only content AFTER the marker
    and subsequent cells are indented.
    """
    notebook = {
        "cells": [
            {
                "cell_type": "markdown",
                "source": [
                    "1. To deploy:\n",
                    "<!-- @nemo-nb: multi-cell-indent-space-start indent-a 3 -->\n",
                    "<!-- @nemo-nb: insert ::::{tab-set} -->",
                ],
            },
            {"cell_type": "code", "source": ["x = 1"]},
            {"cell_type": "code", "source": ["# @nemo-nb: multi-cell-indent-space-end indent-a\n", "y = 2"]},
        ]
    }

    converter = NotebookConverter({})
    md = converter.convert_notebook_dict(notebook)

    # Content BEFORE marker is NOT indented
    assert "1. To deploy:" in md
    assert md.index("1. To deploy:") < md.index("::::{tab-set}")
    # Content AFTER marker in same cell IS indented
    assert "   ::::{tab-set}" in md
    # Subsequent cells ARE indented
    assert "   ```python" in md
    assert "   x = 1" in md
    # End marker at start of cell: content after it is NOT indented
    assert "y = 2" in md
    assert "   y = 2" not in md
    assert "@nemo-nb" not in md


def test_group_indent_tab_start_end():
    """Test multi-cell grouping with tab indentation.

    When marker is at the start of a cell, the entire cell
    and all subsequent cells are indented with tabs.
    """
    notebook = {
        "cells": [
            {
                "cell_type": "markdown",
                "source": ["<!-- @nemo-nb: multi-cell-indent-tab-start my-group 2 -->\n", "# Step 1"],
            },
            {"cell_type": "code", "source": ["x = 1"]},
            {"cell_type": "code", "source": ["# @nemo-nb: multi-cell-indent-tab-end my-group\n", "y = 2"]},
        ]
    }

    converter = NotebookConverter({})
    md = converter.convert_notebook_dict(notebook)

    # Marker at start: entire cell IS indented with tabs
    assert "\t\t# Step 1" in md
    assert "\t\t```python" in md
    assert "\t\tx = 1" in md
    # End marker at start of cell: content after it is NOT indented
    assert "y = 2" in md
    assert "\t\ty = 2" not in md
    assert "@nemo-nb" not in md


def test_multiple_markers_in_cell():
    """Test handling multiple markers in a single cell."""
    notebook = {
        "cells": [
            {
                "cell_type": "code",
                "source": [
                    "# @nemo-nb: wrap-cell-start :::{dropdown} Example\n",
                    "# @nemo-nb: wrap-cell-end :::   \n",
                    "# @nemo-nb: indent-space 4\n",
                    "x = 1",
                ],
            }
        ]
    }

    converter = NotebookConverter({})
    md = converter.convert_notebook_dict(notebook)

    # Should have both wrapping and indentation
    assert ":::{dropdown} Example" in md
    assert "    x = 1" in md  # Indented
    assert "    :::" in md  # Closing also indented


def test_empty_notebook():
    """Test conversion of empty notebook."""
    notebook = {"cells": []}

    converter = NotebookConverter({})
    md = converter.convert_notebook_dict(notebook)

    assert md == ""


def test_html_comment_marker_in_markdown():
    """Test HTML comment marker in markdown cells."""
    notebook = {
        "cells": [
            {
                "cell_type": "markdown",
                "source": [
                    "<!-- @nemo-nb: wrap-cell-start :::{note} Important -->\n",
                    "<!-- @nemo-nb: wrap-cell-end ::: -->\n",
                    "This is a note.",
                ],
            }
        ]
    }

    converter = NotebookConverter({})
    md = converter.convert_notebook_dict(notebook)

    assert ":::{note} Important" in md
    assert "This is a note." in md
    assert "@nemo-nb" not in md
    assert "<!--" not in md


def test_indent_spaces():
    """Test indent with spaces on code cell."""
    notebook = {"cells": [{"cell_type": "code", "source": ["# @nemo-nb: indent-space 4\n", "x = 1\n", "y = 2"]}]}

    converter = NotebookConverter({})
    md = converter.convert_notebook_dict(notebook)

    assert "    ```python" in md
    assert "    x = 1" in md
    assert "    y = 2" in md
    assert "    ```" in md
    assert "@nemo-nb" not in md


def test_indent_tabs():
    """Test indent with tabs on code cell."""
    notebook = {"cells": [{"cell_type": "code", "source": ["# @nemo-nb: indent-tab 2\n", "x = 1\n", "y = 2"]}]}

    converter = NotebookConverter({})
    md = converter.convert_notebook_dict(notebook)

    assert "\t\t```python" in md
    assert "\t\tx = 1" in md
    assert "\t\ty = 2" in md
    assert "\t\t```" in md
    assert "@nemo-nb" not in md


def test_indent_with_wrap():
    """Test indent combined with wrap directive."""
    notebook = {
        "cells": [
            {
                "cell_type": "code",
                "source": [
                    "# @nemo-nb: wrap-cell-start :::{dropdown} Example\n",
                    "# @nemo-nb: wrap-cell-end :::   \n",
                    "# @nemo-nb: indent-space 3\n",
                    "print('indented dropdown')",
                ],
            }
        ]
    }

    converter = NotebookConverter({})
    md = converter.convert_notebook_dict(notebook)

    assert "   :::{dropdown} Example" in md
    assert "   ```python" in md
    assert "   print('indented dropdown')" in md
    assert "   ```" in md
    assert "   :::" in md
    assert "@nemo-nb" not in md


def test_indent_with_group():
    """Test indent with multi-cell group.

    When marker is at the start of a cell, the entire cell
    and subsequent cells are indented.
    """
    notebook = {
        "cells": [
            {
                "cell_type": "markdown",
                "source": [
                    "<!-- @nemo-nb: multi-cell-indent-space-start my-group 4 -->\n",
                    "# Step 1",
                ],
            },
            {"cell_type": "code", "source": ["x = 1"]},
            {"cell_type": "code", "source": ["# @nemo-nb: multi-cell-indent-space-end my-group\n", "y = 2"]},
        ]
    }

    converter = NotebookConverter({})
    md = converter.convert_notebook_dict(notebook)

    # Marker at start: entire cell IS indented
    assert "    # Step 1" in md
    assert "    ```python" in md
    assert "    x = 1" in md
    # End marker at start of cell: content after it is NOT indented
    assert "y = 2" in md
    assert "    y = 2" not in md


def test_indent_spaces_and_tabs_combined():
    """Test that both indent types can be used (tabs applied after spaces)."""
    notebook = {
        "cells": [
            {"cell_type": "code", "source": ["# @nemo-nb: indent-space 2\n", "# @nemo-nb: indent-tab 1\n", "x = 1"]}
        ]
    }

    converter = NotebookConverter({})
    md = converter.convert_notebook_dict(notebook)

    # Should have both spaces and tabs
    assert "\t  ```python" in md or "  \t```python" in md
    assert "x = 1" in md


def test_insert_marker():
    """Test insert marker adds literal lines."""
    notebook = {
        "cells": [
            {
                "cell_type": "code",
                "source": ["# @nemo-nb: insert :sync: sdk\n", "print('hello')"],
            }
        ]
    }

    converter = NotebookConverter({})
    md = converter.convert_notebook_dict(notebook)

    assert ":sync: sdk" in md
    assert "print('hello')" in md


def test_insert_marker_with_wrap():
    """Test insert marker inside wrapped content."""
    notebook = {
        "cells": [
            {
                "cell_type": "code",
                "source": [
                    "# @nemo-nb: wrap-cell-start :::{tab-item} Python SDK\n",
                    "# @nemo-nb: wrap-cell-end :::   \n",
                    "# @nemo-nb: insert :sync: sdk\n",
                    "print('hello')",
                ],
            }
        ]
    }

    converter = NotebookConverter({})
    md = converter.convert_notebook_dict(notebook)

    assert ":::{tab-item} Python SDK" in md
    assert ":sync: sdk" in md
    assert "print('hello')" in md
    assert ":::" in md
    # Verify order: directive opening, then insert, then content
    assert md.index(":::{tab-item}") < md.index(":sync:") < md.index("print")


def test_multiple_insert_markers():
    """Test multiple insert markers maintain their positions."""
    notebook = {
        "cells": [
            {
                "cell_type": "code",
                "source": [
                    "# @nemo-nb: wrap-cell-start ```{code-block}\n",
                    "# @nemo-nb: wrap-cell-end ```   \n",
                    "# @nemo-nb: insert :emphasize-lines: 2-3\n",
                    "# @nemo-nb: insert :linenos:\n",
                    "x = 1\n",
                    "y = 2\n",
                    "# @nemo-nb: wrap-cell-end ```",
                ],
            }
        ]
    }

    converter = NotebookConverter({})
    md = converter.convert_notebook_dict(notebook)

    assert "```{code-block}" in md
    assert ":emphasize-lines: 2-3" in md
    assert ":linenos:" in md
    assert "x = 1" in md


def test_wrap_with_four_colons():
    """Test wrapping with four colons for nested directives."""
    notebook = {
        "cells": [
            {
                "cell_type": "code",
                "source": [
                    "# @nemo-nb: wrap-cell-start ::::{tab-set}\n",
                    "# @nemo-nb: wrap-cell-end ::::   \n",
                    "print('hello')",
                ],
            }
        ]
    }

    converter = NotebookConverter({})
    md = converter.convert_notebook_dict(notebook)

    assert "::::{tab-set}" in md
    assert "::::" in md
    assert md.count("::::") == 2  # Opening and closing


def test_language_override():
    """Test language marker overrides the language in code fence."""
    notebook = {
        "cells": [
            {
                "cell_type": "code",
                "metadata": {"language": "python"},
                "source": [
                    "# @nemo-nb: language {code-block}\n",
                    "{\n",
                    '  "key": "value"\n',
                    "}",
                ],
            }
        ]
    }

    converter = NotebookConverter({})
    md = converter.convert_notebook_dict(notebook)

    # Should use {code-block} instead of python
    assert "```{code-block}" in md
    assert "```python" not in md
    assert '"key": "value"' in md


def test_language_override_with_wrap():
    """Test language marker combined with wrap directive."""
    notebook = {
        "cells": [
            {
                "cell_type": "code",
                "source": [
                    "# @nemo-nb: wrap-cell-start ```{code-block}\n",
                    "# @nemo-nb: wrap-cell-end ```\n",
                    "# @nemo-nb: language {code-block}\n",
                    "# @nemo-nb: insert :emphasize-lines: 2-3\n",
                    "line1\n",
                    "line2\n",
                    "line3",
                ],
            }
        ]
    }

    converter = NotebookConverter({})
    md = converter.convert_notebook_dict(notebook)

    assert "```{code-block}" in md
    assert ":emphasize-lines: 2-3" in md
    assert "line1" in md
    # Check that we get the code-block wrapper and inner code-block
    assert md.count("{code-block}") == 2


def test_wrap_and_insert_inside_group():
    """Test that wrap and insert work correctly inside a group.

    When marker is at the start of a cell, the entire cell
    and subsequent cells are indented.
    """
    notebook = {
        "cells": [
            {
                "cell_type": "markdown",
                "source": ["<!-- @nemo-nb: multi-cell-indent-space-start my-group 3 -->\n", "Start of group"],
            },
            {
                "cell_type": "code",
                "source": [
                    "# @nemo-nb: wrap-cell-start :::{tab-item} Python\n",
                    "# @nemo-nb: wrap-cell-end :::\n",
                    "# @nemo-nb: insert :sync: tab1\n",
                    "print('hello')",
                ],
            },
            {
                "cell_type": "code",
                "source": ["# @nemo-nb: multi-cell-indent-space-end my-group\n", "print('end')"],
            },
        ]
    }

    converter = NotebookConverter({})
    md = converter.convert_notebook_dict(notebook)

    # Verify group indentation is applied (marker at start)
    assert "   Start of group" in md
    assert "   :::{tab-item} Python" in md
    assert "   :sync: tab1" in md
    assert "   print('hello')" in md
    assert "   :::" in md
    # End marker at start of cell: content after it is NOT indented
    assert "print('end')" in md
    assert "   print('end')" not in md


def test_multiple_nested_wraps_defer_pattern():
    """Test multiple wrap directives work like defer/stack (LIFO order).

    Multiple wrap directives should nest like:
    wrap-cell-start A -> wrap-cell-start B -> content -> wrap-cell-end B -> wrap-cell-end A

    This creates:
    A_open
    B_open
    content
    B_close
    A_close
    """
    notebook = {
        "cells": [
            {
                "cell_type": "code",
                "source": [
                    "# @nemo-nb: wrap-cell-start :::{dropdown} Outer Dropdown\n",
                    "# @nemo-nb: wrap-cell-end :::\n",
                    "# @nemo-nb: wrap-cell-start :::{note} Inner Note\n",
                    "# @nemo-nb: wrap-cell-end :::\n",
                    "print('nested content')",
                ],
            }
        ]
    }

    converter = NotebookConverter({})
    md = converter.convert_notebook_dict(notebook)

    # Expected structure:
    # :::{dropdown} Outer Dropdown
    # :::{note} Inner Note
    # ```python
    # print('nested content')
    # ```
    # :::
    # :::

    assert ":::{dropdown} Outer Dropdown" in md
    assert ":::{note} Inner Note" in md
    assert "print('nested content')" in md

    # Verify nesting order: dropdown should come before note
    dropdown_idx = md.index(":::{dropdown}")
    note_idx = md.index(":::{note}")
    assert dropdown_idx < note_idx, "Outer directive should come before inner directive"

    # Verify closing order: first ::: closes note, second ::: closes dropdown
    # The closings should be in reverse order (LIFO)
    lines = md.strip().split("\n")

    # Find indices of the closing :::
    closing_indices = [i for i, line in enumerate(lines) if line.strip() == ":::"]
    assert len(closing_indices) == 2, "Should have exactly 2 closing :::"

    # The content should be between openings and closings
    content_idx = next(i for i, line in enumerate(lines) if "print('nested content')" in line)
    assert dropdown_idx < content_idx < closing_indices[0], "Content should be inside both directives"


def test_notebook_convert_4_space_to_tab_basic():
    """Test notebook-convert-4-space-to-tab converts 4 spaces to tabs."""
    notebook = {
        "cells": [
            {
                "cell_type": "code",
                "metadata": {},
                "source": ["# @nemo-nb: notebook-convert-4-space-to-tab\n", "# This enables tab conversion"],
            },
            {
                "cell_type": "code",
                "metadata": {},
                "source": ["# @nemo-nb: indent-space 4\n", "print('indented')"],
            },
        ]
    }

    converter = NotebookConverter({})
    md = converter.convert_notebook_dict(notebook)

    # The 4-space indent should be converted to a tab
    assert "\tprint('indented')" in md
    assert "    print('indented')" not in md


def test_notebook_convert_4_space_to_tab_with_group():
    """Test notebook-convert-4-space-to-tab with group indentation."""
    notebook = {
        "cells": [
            {
                "cell_type": "markdown",
                "source": ["# @nemo-nb: notebook-convert-4-space-to-tab"],
            },
            {
                "cell_type": "markdown",
                "source": ["# @nemo-nb: multi-cell-indent-space-start mygroup 8\n", "Content in group"],
            },
            {
                "cell_type": "markdown",
                "source": ["# @nemo-nb: multi-cell-indent-space-end mygroup\n", "More content"],
            },
        ]
    }

    converter = NotebookConverter({})
    md = converter.convert_notebook_dict(notebook)

    # 8 spaces should convert to 2 tabs
    assert "\t\tContent in group" in md
    assert "        Content in group" not in md


def test_notebook_convert_4_space_to_tab_not_enabled():
    """Test that spaces remain when notebook-convert-4-space-to-tab is not enabled."""
    notebook = {
        "cells": [
            {
                "cell_type": "code",
                "metadata": {},
                "source": ["# @nemo-nb: indent-space 4\n", "print('indented')"],
            },
        ]
    }

    converter = NotebookConverter({})
    md = converter.convert_notebook_dict(notebook)

    # Spaces should remain as-is
    assert "    print('indented')" in md
    assert "\tprint('indented')" not in md


def test_notebook_convert_4_space_to_tab_partial_spaces():
    """Test notebook-convert-4-space-to-tab with non-multiple of 4 spaces."""
    notebook = {
        "cells": [
            {
                "cell_type": "code",
                "metadata": {},
                "source": ["# @nemo-nb: notebook-convert-4-space-to-tab"],
            },
            {
                "cell_type": "code",
                "metadata": {},
                "source": ["# @nemo-nb: indent-space 6\n", "print('indented')"],
            },
        ]
    }

    converter = NotebookConverter({})
    md = converter.convert_notebook_dict(notebook)

    # 6 spaces = 1 tab + 2 spaces
    assert "\t  print('indented')" in md


def test_notebook_convert_4_space_to_tab_multiple_cells():
    """Test notebook-convert-4-space-to-tab works across multiple cells."""
    notebook = {
        "cells": [
            {
                "cell_type": "code",
                "metadata": {},
                "source": ["// @nemo-nb: notebook-convert-4-space-to-tab"],
            },
            {
                "cell_type": "code",
                "metadata": {},
                "source": ["# @nemo-nb: indent-space 4\n", "x = 1"],
            },
            {
                "cell_type": "code",
                "metadata": {},
                "source": ["# @nemo-nb: indent-space 8\n", "y = 2"],
            },
        ]
    }

    converter = NotebookConverter({})
    md = converter.convert_notebook_dict(notebook)

    # First cell: 4 spaces -> 1 tab
    assert "\tx = 1" in md
    # Second cell: 8 spaces -> 2 tabs
    assert "\t\ty = 2" in md


def test_notebook_convert_4_space_to_tab_slash_marker():
    """Test notebook-convert-4-space-to-tab with slash marker syntax."""
    notebook = {
        "cells": [
            {
                "cell_type": "code",
                "metadata": {},
                "source": ["// @nemo-nb: notebook-convert-4-space-to-tab\n", "x = 1"],
            },
            {
                "cell_type": "code",
                "metadata": {},
                "source": ["# @nemo-nb: indent-space 4\n", "print('test')"],
            },
        ]
    }

    converter = NotebookConverter({})
    md = converter.convert_notebook_dict(notebook)

    # 4 spaces should convert to tab
    assert "\tprint('test')" in md


def test_insert_before_multi_cell_marker():
    """Test that insert markers before multi-cell-indent markers work correctly."""
    notebook = {
        "cells": [
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "<!-- @nemo-nb: insert (my-reference)= -->\n",
                    "# Title\n",
                    "\n",
                    "Some intro text.\n",
                    "<!-- @nemo-nb: multi-cell-indent-space-start mygroup 3 -->\n",
                    "<!-- @nemo-nb: insert ::::{tab-set} -->",
                ],
            }
        ]
    }

    converter = NotebookConverter({})
    md = converter.convert_notebook_dict(notebook)

    # The reference insert should appear at the beginning
    assert "(my-reference)=" in md
    assert md.startswith("(my-reference)=")

    # The tab-set insert should appear later, indented
    assert "::::{tab-set}" in md

    # Verify order: reference before title before tab-set
    ref_pos = md.find("(my-reference)=")
    title_pos = md.find("# Title")
    tabset_pos = md.find("::::{tab-set}")
    assert ref_pos < title_pos < tabset_pos


def test_multiple_inserts_before_multi_cell_marker():
    """Test that multiple insert markers before multi-cell-indent markers all appear."""
    notebook = {
        "cells": [
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "<!-- @nemo-nb: insert (ref1)= -->\n",
                    "<!-- @nemo-nb: insert (ref2)= -->\n",
                    "# Title\n",
                    "<!-- @nemo-nb: multi-cell-indent-space-start g 3 -->\n",
                    "Content",
                ],
            }
        ]
    }

    converter = NotebookConverter({})
    md = converter.convert_notebook_dict(notebook)

    # Both references should appear
    assert "(ref1)=" in md
    assert "(ref2)=" in md

    # Verify order
    assert md.find("(ref1)=") < md.find("(ref2)=") < md.find("# Title")


def test_insert_code_block_start_basic():
    """Test insert-code-block-start marker inserts options after fence."""
    notebook = {
        "cells": [
            {
                "cell_type": "code",
                "source": [
                    "# @nemo-nb: insert-code-block-start :emphasize-lines: 18-21\n",
                    "# @nemo-nb: language {code-block}\n",
                    "x = 1\n",
                    "y = 2",
                ],
            }
        ]
    }

    converter = NotebookConverter({})
    md = converter.convert_notebook_dict(notebook)

    assert "```{code-block}" in md
    assert ":emphasize-lines: 18-21" in md
    assert "x = 1" in md
    assert "y = 2" in md


def test_insert_code_block_start_with_linenos():
    """Test insert-code-block-start with :linenos: option."""
    notebook = {
        "cells": [
            {
                "cell_type": "code",
                "source": [
                    "# @nemo-nb: insert-code-block-start :linenos:\n",
                    "# @nemo-nb: language {code-block}\n",
                    "print('hello')",
                ],
            }
        ]
    }

    converter = NotebookConverter({})
    md = converter.convert_notebook_dict(notebook)

    assert "```{code-block}" in md
    assert ":linenos:" in md
    assert "print('hello')" in md


def test_insert_code_block_start_with_wrap():
    """Test insert-code-block-start combined with wrap directive."""
    notebook = {
        "cells": [
            {
                "cell_type": "code",
                "source": [
                    "# @nemo-nb: wrap-cell-start :::{dropdown} Click to expand\n",
                    "# @nemo-nb: wrap-cell-end :::\n",
                    "# @nemo-nb: insert-code-block-start :emphasize-lines: 1-2\n",
                    "# @nemo-nb: language {code-block}\n",
                    "x = 1\n",
                    "y = 2",
                ],
            }
        ]
    }

    converter = NotebookConverter({})
    md = converter.convert_notebook_dict(notebook)

    assert ":::{dropdown} Click to expand" in md
    assert "```{code-block}" in md
    assert ":emphasize-lines: 1-2" in md
    assert "x = 1" in md
    assert ":::" in md
    # Verify order
    assert md.index(":::{dropdown}") < md.index("```{code-block}") < md.index("x = 1")


def test_insert_code_block_start_with_indent():
    """Test insert-code-block-start with indentation."""
    notebook = {
        "cells": [
            {
                "cell_type": "code",
                "source": [
                    "# @nemo-nb: insert-code-block-start :emphasize-lines: 2\n",
                    "# @nemo-nb: language {code-block}\n",
                    "# @nemo-nb: indent-space 4\n",
                    "x = 1\n",
                    "y = 2",
                ],
            }
        ]
    }

    converter = NotebookConverter({})
    md = converter.convert_notebook_dict(notebook)

    assert "    ```{code-block}" in md
    assert "    :emphasize-lines: 2" in md
    assert "    x = 1" in md
    assert "    ```" in md


def test_insert_code_block_start_with_language():
    """Test that insert-code-block-start works with language marker."""
    notebook = {
        "cells": [
            {
                "cell_type": "code",
                "metadata": {"language": "python"},
                "source": [
                    "# @nemo-nb: language {code-block}\n",
                    "# @nemo-nb: insert-code-block-start :emphasize-lines: 1\n",
                    "echo 'test'",
                ],
            }
        ]
    }

    converter = NotebookConverter({})
    md = converter.convert_notebook_dict(notebook)

    # Should use {code-block} from language marker
    assert "```{code-block}" in md
    assert "```python" not in md
    assert ":emphasize-lines: 1" in md
    assert "echo 'test'" in md


def test_insert_code_block_start_in_group():
    """Test insert-code-block-start inside a multi-cell group."""
    notebook = {
        "cells": [
            {
                "cell_type": "markdown",
                "source": ["<!-- @nemo-nb: multi-cell-indent-space-start mygroup 3 -->\n", "# Start"],
            },
            {
                "cell_type": "code",
                "source": [
                    "# @nemo-nb: insert-code-block-start :linenos:\n",
                    "# @nemo-nb: language {code-block}\n",
                    "x = 1",
                ],
            },
            {
                "cell_type": "markdown",
                "source": ["<!-- @nemo-nb: multi-cell-indent-space-end mygroup -->\n", "End"],
            },
        ]
    }

    converter = NotebookConverter({})
    md = converter.convert_notebook_dict(notebook)

    # Content in group should be indented including code-block
    assert "   # Start" in md
    assert "   ```{code-block}" in md
    assert "   :linenos:" in md
    assert "   x = 1" in md
    # End marker at start of cell: content after it is NOT indented
    assert "End" in md
    assert "   End" not in md


def test_multi_cell_end_then_start_with_insert():
    """Test that insert after multi-cell-end then multi-cell-start gets indented correctly."""
    notebook = {
        "cells": [
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": ["1. First item\n", "<!-- @nemo-nb: multi-cell-indent-space-start indent-a 3 -->"],
            },
            {"cell_type": "code", "metadata": {}, "source": ['print("hello")']},
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "<!-- @nemo-nb: multi-cell-indent-space-end indent-a -->\n",
                    "2. Second item\n",
                    "<!-- @nemo-nb: multi-cell-indent-space-start indent-b 3 -->\n",
                    "<!-- @nemo-nb: insert ::::{tab-set} -->",
                ],
            },
            {"cell_type": "code", "metadata": {}, "source": ['print("world")']},
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": ["<!-- @nemo-nb: multi-cell-indent-space-end indent-b -->"],
            },
        ]
    }

    converter = NotebookConverter({})
    md = converter.convert_notebook_dict(notebook)

    # First group should be indented
    assert '   print("hello")' in md

    # Second item should NOT be indented (it's before the new group start)
    assert "2. Second item" in md
    assert "   2. Second item" not in md

    # Insert after the new group start should be indented
    assert "   ::::{tab-set}" in md
    assert "::::{tab-set}" in md  # Should exist (even if indented)

    # Content in the new group should be indented
    assert '   print("world")' in md

    # Verify the insert is not at the root level
    lines = md.split("\n")
    for i, line in enumerate(lines):
        if "::::{tab-set}" in line:
            # The line should start with spaces
            assert line.startswith("   "), "Expected '   ::::" + "{tab-set}' but got {repr(line)}"


def test_insert_only_cell():
    """Test that a cell with only an insert marker works correctly."""
    notebook = {
        "cells": [
            {"cell_type": "markdown", "metadata": {}, "source": ["Content before"]},
            {"cell_type": "markdown", "metadata": {}, "source": ["<!-- @nemo-nb: insert :::: -->"]},
            {"cell_type": "markdown", "metadata": {}, "source": ["Content after"]},
        ]
    }

    converter = NotebookConverter({})
    md = converter.convert_notebook_dict(notebook)

    # The insert should appear between the two content cells
    assert "Content before" in md
    assert "::::" in md
    assert "Content after" in md

    # Verify order
    assert md.index("Content before") < md.index("::::") < md.index("Content after")


def test_insert_only_cell_in_group():
    """Test that an insert-only cell inside a group gets indented."""
    notebook = {
        "cells": [
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": ["Start\n", "<!-- @nemo-nb: multi-cell-indent-space-start grp 3 -->"],
            },
            {"cell_type": "markdown", "metadata": {}, "source": ["<!-- @nemo-nb: insert :::: -->"]},
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": ["<!-- @nemo-nb: multi-cell-indent-space-end grp -->\n", "End"],
            },
        ]
    }

    converter = NotebookConverter({})
    md = converter.convert_notebook_dict(notebook)

    # The insert should be indented
    assert "   ::::" in md

    # The content after group end should not be indented
    assert "End" in md
    assert "   End" not in md


def test_download_marker(tmp_path):
    """Test download marker generates download link."""

    # Create a test notebook file
    notebook_path = tmp_path / "my-tutorial.ipynb"
    notebook = {
        "cells": [
            {"cell_type": "markdown", "source": ["<!-- @nemo-nb: download -->\n", "Tutorial content"]},
        ]
    }

    converter = NotebookConverter({})
    converter.current_notebook_path = notebook_path
    md = converter.convert_notebook_dict(notebook)

    # Verify download link is generated as HTML with download attribute
    assert (
        '<a href="my-tutorial.ipynb" download="my-tutorial.ipynb">Download this tutorial as a Jupyter notebook</a>'
        in md
    )
    assert "Tutorial content" in md


def test_download_marker_index_file(tmp_path):
    """Test download marker uses parent directory name for index.md."""

    # Create a test notebook file with index name
    notebook_path = tmp_path / "tutorials" / "index.ipynb"
    notebook_path.parent.mkdir(parents=True, exist_ok=True)

    notebook = {
        "cells": [
            {"cell_type": "markdown", "source": ["<!-- @nemo-nb: download -->"]},
        ]
    }

    converter = NotebookConverter({})
    converter.current_notebook_path = notebook_path
    md = converter.convert_notebook_dict(notebook)

    # Verify download link uses parent directory name with HTML download attribute
    assert '<a href="tutorials.ipynb" download="tutorials.ipynb">Download this tutorial as a Jupyter notebook</a>' in md


def test_download_marker_in_separate_cell(tmp_path):
    """Test download marker works when in its own cell (common pattern)."""

    # Create a test notebook file
    notebook_path = tmp_path / "my-tutorial.ipynb"
    notebook = {
        "cells": [
            {"cell_type": "markdown", "source": ["<!-- @nemo-nb: process -->"]},
            {"cell_type": "markdown", "source": ["<!-- @nemo-nb: download -->"]},
            {"cell_type": "markdown", "source": ["# Tutorial Title\n", "\n", "Content here"]},
        ]
    }

    converter = NotebookConverter({})
    converter.current_notebook_path = notebook_path
    md = converter.convert_notebook_dict(notebook)

    # Verify download link is generated even when in separate cell with HTML download attribute
    assert (
        '<a href="my-tutorial.ipynb" download="my-tutorial.ipynb">Download this tutorial as a Jupyter notebook</a>'
        in md
    )
    assert "# Tutorial Title" in md
    assert "Content here" in md


def test_download_marker_same_cell_with_blank_line(tmp_path):
    """Test download marker works when in same cell as content with blank line after marker."""
    # This matches the user's scenario: download marker followed by blank line, then content
    notebook_path = tmp_path / "dpo-customization-job.ipynb"
    notebook = {
        "cells": [
            {
                "cell_type": "markdown",
                "source": [
                    "<!-- @nemo-nb: process -->\n",
                    "<!-- @nemo-nb: download -->\n",
                    "\n",
                    "# DPO Customization\n",
                    "\n",
                    "Content here",
                ],
            },
        ]
    }

    converter = NotebookConverter({})
    converter.current_notebook_path = notebook_path
    md = converter.convert_notebook_dict(notebook)

    # Verify download link is generated
    assert (
        '<a href="dpo-customization-job.ipynb" download="dpo-customization-job.ipynb">Download this tutorial as a Jupyter notebook</a>'
        in md
    )
    assert "# DPO Customization" in md
    assert "Content here" in md


def test_download_split_marker(tmp_path):
    """Test download split marker generates separate Python and CLI links."""
    notebook_path = tmp_path / "my-tutorial.ipynb"
    notebook = {
        "cells": [{"cell_type": "markdown", "source": ["<!-- @nemo-nb: download split -->\n", "Tutorial content"]}]
    }

    converter = NotebookConverter({})
    converter.current_notebook_path = notebook_path
    md = converter.convert_notebook_dict(notebook)

    # Verify both download links are generated with separator
    assert '<a href="my-tutorial-python.ipynb" download="my-tutorial-python.ipynb">Download Python notebook</a>' in md
    assert '<a href="my-tutorial-cli.ipynb" download="my-tutorial-cli.ipynb">Download CLI notebook</a>' in md
    assert " | " in md  # Separator between links
    assert "Tutorial content" in md


def test_download_split_marker_index_file(tmp_path):
    """Test download split marker uses parent directory name for index.md."""
    notebook_path = tmp_path / "tutorials" / "index.ipynb"
    notebook_path.parent.mkdir(parents=True, exist_ok=True)

    notebook = {"cells": [{"cell_type": "markdown", "source": ["<!-- @nemo-nb: download split -->"]}]}

    converter = NotebookConverter({})
    converter.current_notebook_path = notebook_path
    md = converter.convert_notebook_dict(notebook)

    # Verify both links use parent directory name
    assert '<a href="tutorials-python.ipynb" download="tutorials-python.ipynb">Download Python notebook</a>' in md
    assert '<a href="tutorials-cli.ipynb" download="tutorials-cli.ipynb">Download CLI notebook</a>' in md


def test_download_split_marker_multiple_cells(tmp_path):
    """Test download split marker in separate cell from content."""
    notebook_path = tmp_path / "my-tutorial.ipynb"
    notebook = {
        "cells": [
            {"cell_type": "markdown", "source": ["<!-- @nemo-nb: process -->"]},
            {"cell_type": "markdown", "source": ["<!-- @nemo-nb: download split -->"]},
            {"cell_type": "markdown", "source": ["# Tutorial Title\n", "\n", "Content here"]},
        ]
    }

    converter = NotebookConverter({})
    converter.current_notebook_path = notebook_path
    md = converter.convert_notebook_dict(notebook)

    # Verify both download links are generated
    assert '<a href="my-tutorial-python.ipynb" download="my-tutorial-python.ipynb">Download Python notebook</a>' in md
    assert '<a href="my-tutorial-cli.ipynb" download="my-tutorial-cli.ipynb">Download CLI notebook</a>' in md
    assert "# Tutorial Title" in md
    assert "Content here" in md


def test_strip_hidden_cells_from_notebook():
    """Test that hidden cells are removed from notebooks for download (security)."""
    from nemo_nb.sphinx import strip_hidden_cells_from_notebook

    notebook = {
        "cells": [
            # Cell with hide marker - should be removed
            {"cell_type": "code", "source": ["# @nemo-nb: hide\n", "SECRET_KEY = 'secret123'"]},
            # Cell with hide metadata - should be removed
            {
                "cell_type": "code",
                "source": ["API_KEY = 'internal-key'"],
                "metadata": {"nemo_nb": {"hide": True}},
            },
            # Cell with hide-cell tag - should be removed
            {
                "cell_type": "code",
                "source": ["INTERNAL_ENDPOINT = 'http://internal'"],
                "metadata": {"tags": ["hide-cell"]},
            },
            # Visible cell - should be kept
            {"cell_type": "code", "source": ["print('Hello, world!')"]},
            # Another visible cell - should be kept
            {"cell_type": "markdown", "source": ["# Tutorial"]},
        ]
    }

    # Strip hidden cells
    filtered_notebook = strip_hidden_cells_from_notebook(notebook)

    # Should have only 2 cells (the visible ones)
    assert len(filtered_notebook["cells"]) == 2

    # Verify the kept cells
    sources = [" ".join(cell["source"]) for cell in filtered_notebook["cells"]]
    assert "print('Hello, world!')" in sources[0]
    assert "# Tutorial" in sources[1]

    # Verify secrets are NOT in the filtered notebook
    all_content = " ".join(sources)
    assert "SECRET_KEY" not in all_content
    assert "secret123" not in all_content
    assert "API_KEY" not in all_content
    assert "internal-key" not in all_content
    assert "INTERNAL_ENDPOINT" not in all_content
    assert "http://internal" not in all_content


def test_strip_hidden_cells_preserves_visible_cells():
    """Test that stripping hidden cells doesn't affect visible cells."""
    from nemo_nb.sphinx import strip_hidden_cells_from_notebook

    notebook = {
        "cells": [
            {"cell_type": "markdown", "source": ["# Introduction"], "metadata": {}},
            {"cell_type": "code", "source": ["x = 1\n", "y = 2"], "metadata": {}},
            {
                "cell_type": "code",
                "source": ["# This cell has metadata but is not hidden"],
                "metadata": {"some_other_field": "value"},
            },
        ]
    }

    # Strip hidden cells
    filtered_notebook = strip_hidden_cells_from_notebook(notebook)

    # All cells should be preserved
    assert len(filtered_notebook["cells"]) == 3
    assert filtered_notebook["cells"] == notebook["cells"]


def test_strip_hidden_cells_with_mixed_markers():
    """Test that cells with hide + other markers are still removed."""
    from nemo_nb.sphinx import strip_hidden_cells_from_notebook

    notebook = {
        "cells": [
            # Cell with hide + indent markers - should still be removed
            {
                "cell_type": "code",
                "source": ["# @nemo-nb: hide\n", "# @nemo-nb: indent-space 4\n", "secret = 'hidden'"],
            },
            # Visible cell with indent marker - should be kept
            {"cell_type": "code", "source": ["# @nemo-nb: indent-space 4\n", "visible = 'shown'"]},
        ]
    }

    # Strip hidden cells
    filtered_notebook = strip_hidden_cells_from_notebook(notebook)

    # Should have only 1 cell
    assert len(filtered_notebook["cells"]) == 1
    assert "visible" in filtered_notebook["cells"][0]["source"][1]
    assert "secret" not in str(filtered_notebook)
