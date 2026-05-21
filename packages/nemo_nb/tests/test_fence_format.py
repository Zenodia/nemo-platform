# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Tests for triple backtick fence format support.

This test suite covers:
1. Parsing fenced code blocks as code cells (MD ? NB)
2. Converting code cells to fenced blocks (NB ? MD)
3. Output markers with fences
4. Mixed format (fences + markers)
5. Fences inside explicit markdown cells
6. Round-trip conversion (MD ? NB ? MD)
7. Disable fence conversion with explicit cell markers
8. Auto-disable fence conversion when cells contain triple backticks (NB ? MD)
"""

from nemo_nb.converter import NotebookToMarkdownConverter
from nemo_nb.md_to_notebook import MarkdownToNotebookConverter


def test_parse_basic_fence():
    """Test parsing basic fenced code block."""
    md_content = """# Title

```python
x = 1
y = 2
```

More text
"""

    converter = MarkdownToNotebookConverter()
    converter._parse_markdown_with_context(md_content)
    notebook = converter._create_notebook_dict()

    assert len(notebook["cells"]) == 3
    assert notebook["cells"][0]["cell_type"] == "markdown"
    assert "# Title" in "".join(notebook["cells"][0]["source"])

    assert notebook["cells"][1]["cell_type"] == "code"
    assert "x = 1" in "".join(notebook["cells"][1]["source"])
    assert "y = 2" in "".join(notebook["cells"][1]["source"])

    assert notebook["cells"][2]["cell_type"] == "markdown"
    assert "More text" in "".join(notebook["cells"][2]["source"])


def test_fence_with_output():
    """Test fenced code block with output marker."""
    md_content = """```python
print("Hello")
```
<!-- @nemo-nb: output -->
Hello
"""

    converter = MarkdownToNotebookConverter()
    converter._parse_markdown_with_context(md_content)
    notebook = converter._create_notebook_dict()

    assert len(notebook["cells"]) == 1
    assert notebook["cells"][0]["cell_type"] == "code"
    assert len(notebook["cells"][0]["outputs"]) == 1
    assert notebook["cells"][0]["outputs"][0]["output_type"] == "stream"
    assert "Hello" in "".join(notebook["cells"][0]["outputs"][0]["text"])


def test_mixed_fence_and_markers():
    """Test mixing fenced code blocks and markers."""
    md_content = """```python
x = 1
```

<!-- @nemo-nb: cell python -->
y = 2

```bash
echo "test"
```
"""

    converter = MarkdownToNotebookConverter()
    converter._parse_markdown_with_context(md_content)
    notebook = converter._create_notebook_dict()

    assert len(notebook["cells"]) == 3
    assert notebook["cells"][0]["cell_type"] == "code"  # fence
    assert "x = 1" in "".join(notebook["cells"][0]["source"])

    assert notebook["cells"][1]["cell_type"] == "code"  # marker
    assert "y = 2" in "".join(notebook["cells"][1]["source"])

    assert notebook["cells"][2]["cell_type"] == "code"  # fence
    assert 'echo "test"' in "".join(notebook["cells"][2]["source"])


def test_fence_inside_explicit_markdown():
    """Test that fences inside explicit markdown cells are literal."""
    md_content = """<!-- @nemo-nb: cell markdown -->
Here's example code:

```python
x = 1  # This is literal text, not a code cell
```

End of markdown.
<!-- @nemo-nb: cell python -->
y = 2
"""

    converter = MarkdownToNotebookConverter()
    converter._parse_markdown_with_context(md_content)
    notebook = converter._create_notebook_dict()

    # Should have 2 cells (markdown + code), not 3
    assert len(notebook["cells"]) == 2
    assert notebook["cells"][0]["cell_type"] == "markdown"
    assert "```python" in "".join(notebook["cells"][0]["source"])
    assert notebook["cells"][1]["cell_type"] == "code"


def test_notebook_to_markdown_uses_fences():
    """Test that notebook ? markdown conversion uses fences by default."""
    notebook = {
        "cells": [
            {"cell_type": "markdown", "source": ["# Title"], "metadata": {}},
            {"cell_type": "code", "source": ["x = 1"], "outputs": [], "metadata": {}},
            {"cell_type": "markdown", "source": ["More text"], "metadata": {}},
        ],
        "metadata": {},
        "nbformat": 4,
        "nbformat_minor": 4,
    }

    converter = NotebookToMarkdownConverter()
    md = converter.convert_notebook_dict(notebook)

    # Should use fences, not markers
    assert "```python" in md
    assert "x = 1" in md
    assert "```" in md
    assert "<!-- @nemo-nb: cell python -->" not in md
    assert "<!-- @nemo-nb: cell markdown -->" not in md


def test_notebook_to_markdown_with_outputs():
    """Test that notebook ? markdown preserves outputs with markers."""
    notebook = {
        "cells": [
            {
                "cell_type": "code",
                "source": ['print("Hello")'],
                "outputs": [
                    {
                        "output_type": "stream",
                        "name": "stdout",
                        "text": ["Hello\n"],
                    }
                ],
                "metadata": {},
            },
        ],
        "metadata": {},
        "nbformat": 4,
        "nbformat_minor": 4,
    }

    converter = NotebookToMarkdownConverter()
    md = converter.convert_notebook_dict(notebook)

    # Should have fence and output marker
    assert "```python" in md
    assert 'print("Hello")' in md
    assert "```" in md
    assert "<!-- @nemo-nb: output -->" in md
    assert "Hello" in md


def test_roundtrip_md_to_ipynb_to_md():
    """Test that MD ? IPYNB ? MD preserves structure."""
    original_md = """# My Notebook

```python
x = 1
y = 2
```

Some analysis text.

```bash
echo "test"
```
<!-- @nemo-nb: output -->
test
"""

    # Convert to notebook
    md_to_nb = MarkdownToNotebookConverter()
    md_to_nb._parse_markdown_with_context(original_md)
    notebook = md_to_nb._create_notebook_dict()

    # Convert back to markdown
    nb_to_md = NotebookToMarkdownConverter()
    result_md = nb_to_md.convert_notebook_dict(notebook)

    # Should have same structure
    assert "```python" in result_md
    assert "```bash" in result_md or "```sh" in result_md  # bash may be normalized to sh
    assert "x = 1" in result_md
    assert 'echo "test"' in result_md
    assert "<!-- @nemo-nb: output -->" in result_md


def test_multiple_code_cells_with_fences():
    """Test multiple consecutive code cells with fences."""
    md_content = """```python
x = 1
```

```python
y = 2
```

```bash
echo "done"
```
"""

    converter = MarkdownToNotebookConverter()
    converter._parse_markdown_with_context(md_content)
    notebook = converter._create_notebook_dict()

    assert len(notebook["cells"]) == 3
    assert all(cell["cell_type"] == "code" for cell in notebook["cells"])
    assert "x = 1" in "".join(notebook["cells"][0]["source"])
    assert "y = 2" in "".join(notebook["cells"][1]["source"])
    assert 'echo "done"' in "".join(notebook["cells"][2]["source"])


def test_empty_fence():
    """Test empty fenced code block."""
    md_content = """```python
```

More text
"""

    converter = MarkdownToNotebookConverter()
    converter._parse_markdown_with_context(md_content)
    notebook = converter._create_notebook_dict()

    # Empty fences are skipped by _add_code_cell (no lines), so we get just markdown
    # This is acceptable behavior - empty code cells are rare in practice
    assert len(notebook["cells"]) >= 1
    # The markdown cell should exist
    has_markdown = any(
        cell["cell_type"] == "markdown" and "More text" in "".join(cell["source"]) for cell in notebook["cells"]
    )
    assert has_markdown


def test_fence_with_different_languages():
    """Test fenced code blocks with different languages."""
    md_content = """```python
x = 1
```

```bash
echo "test"
```

```javascript
console.log("hello");
```
"""

    converter = MarkdownToNotebookConverter()
    converter._parse_markdown_with_context(md_content)
    notebook = converter._create_notebook_dict()

    assert len(notebook["cells"]) == 3
    assert notebook["cells"][0]["metadata"].get("language") is None  # Python is default
    assert notebook["cells"][1]["metadata"].get("language") == "bash"
    assert notebook["cells"][2]["metadata"].get("language") == "javascript"


def test_bash_cell_no_magic_during_conversion():
    """Test that bash/shell cells do NOT get %%bash magic during md-to-notebook conversion.

    The %%bash magic is added later during copy_notebooks_to_output, not during
    the initial conversion. This keeps the HTML rendering clean.
    """
    md_content = """```bash
echo "hello"
```

```shell
ls -la
```

```sh
pwd
```
"""

    converter = MarkdownToNotebookConverter()
    converter._parse_markdown_with_context(md_content)
    notebook = converter._create_notebook_dict()

    assert len(notebook["cells"]) == 3

    # Shell cells should NOT have %%bash magic during conversion
    for cell in notebook["cells"]:
        source = "".join(cell["source"])
        assert not source.startswith("%%bash"), f"Cell should NOT start with %%bash during conversion: {source}"
        # But should have shell language in metadata
        assert cell["metadata"].get("language") in ("bash", "shell", "sh")


def test_bash_cell_with_existing_magic_preserved():
    """Test that existing %%bash magic is preserved if author included it."""
    md_content = """```bash
%%bash
echo "hello"
```
"""

    converter = MarkdownToNotebookConverter()
    converter._parse_markdown_with_context(md_content)
    notebook = converter._create_notebook_dict()

    assert len(notebook["cells"]) == 1
    source = "".join(notebook["cells"][0]["source"])

    # Should have exactly one %%bash (the one author wrote)
    assert source.count("%%bash") == 1
    assert source.startswith("%%bash")


def test_python_cell_no_magic_added():
    """Test that Python cells don't get %%bash magic."""
    md_content = """```python
print("hello")
```
"""

    converter = MarkdownToNotebookConverter()
    converter._parse_markdown_with_context(md_content)
    notebook = converter._create_notebook_dict()

    assert len(notebook["cells"]) == 1
    source = "".join(notebook["cells"][0]["source"])
    assert "%%bash" not in source


def test_add_bash_magic_to_shell_cells():
    """Test that add_bash_magic_to_shell_cells adds %%bash to shell cells."""
    from nemo_nb.sphinx import add_bash_magic_to_shell_cells

    notebook = {
        "cells": [
            {
                "cell_type": "code",
                "source": ["echo 'hello'\n", "echo 'world'"],
                "metadata": {"language": "bash"},
                "outputs": [],
            },
            {
                "cell_type": "code",
                "source": ["ls -la"],
                "metadata": {"language": "shell"},
                "outputs": [],
            },
            {
                "cell_type": "code",
                "source": ["pwd"],
                "metadata": {"language": "sh"},
                "outputs": [],
            },
            {
                "cell_type": "code",
                "source": ["print('hello')"],
                "metadata": {},  # Python (no language metadata)
                "outputs": [],
            },
        ],
        "metadata": {},
        "nbformat": 4,
        "nbformat_minor": 4,
    }

    result = add_bash_magic_to_shell_cells(notebook)

    # Shell cells should have %%bash magic added
    assert result["cells"][0]["source"][0] == "%%bash\n"
    assert result["cells"][1]["source"][0] == "%%bash\n"
    assert result["cells"][2]["source"][0] == "%%bash\n"

    # Python cell should NOT have %%bash magic
    assert "%%bash" not in result["cells"][3]["source"][0]


def test_add_bash_magic_not_duplicated():
    """Test that add_bash_magic_to_shell_cells doesn't duplicate existing magic."""
    from nemo_nb.sphinx import add_bash_magic_to_shell_cells

    notebook = {
        "cells": [
            {
                "cell_type": "code",
                "source": ["%%bash\n", "echo 'hello'"],
                "metadata": {"language": "bash"},
                "outputs": [],
            },
        ],
        "metadata": {},
        "nbformat": 4,
        "nbformat_minor": 4,
    }

    result = add_bash_magic_to_shell_cells(notebook)

    # Should still have exactly one %%bash
    source = "".join(result["cells"][0]["source"])
    assert source.count("%%bash") == 1


def test_fence_with_execute_result_output():
    """Test fenced code block with execute_result output."""
    md_content = """```python
21 * 2
```
<!-- @nemo-nb: output execute_result -->
42
"""

    converter = MarkdownToNotebookConverter()
    converter._parse_markdown_with_context(md_content)
    notebook = converter._create_notebook_dict()

    assert len(notebook["cells"]) == 1
    assert notebook["cells"][0]["cell_type"] == "code"
    assert len(notebook["cells"][0]["outputs"]) == 1
    assert notebook["cells"][0]["outputs"][0]["output_type"] == "execute_result"
    assert "42" in "".join(notebook["cells"][0]["outputs"][0]["data"]["text/plain"])


def test_markdown_after_fence():
    """Test that markdown resumes after fence closes."""
    md_content = """Some text

```python
x = 1
```

More markdown here

```python
y = 2
```

Final markdown
"""

    converter = MarkdownToNotebookConverter()
    converter._parse_markdown_with_context(md_content)
    notebook = converter._create_notebook_dict()

    assert len(notebook["cells"]) == 5
    assert notebook["cells"][0]["cell_type"] == "markdown"
    assert notebook["cells"][1]["cell_type"] == "code"
    assert notebook["cells"][2]["cell_type"] == "markdown"
    assert "More markdown here" in "".join(notebook["cells"][2]["source"])
    assert notebook["cells"][3]["cell_type"] == "code"
    assert notebook["cells"][4]["cell_type"] == "markdown"
    assert "Final markdown" in "".join(notebook["cells"][4]["source"])


def test_fence_starting_document():
    """Test document starting with a code fence."""
    md_content = """```python
# File starts with code
x = 1
```

Text after code
"""

    converter = MarkdownToNotebookConverter()
    converter._parse_markdown_with_context(md_content)
    notebook = converter._create_notebook_dict()

    # First cell should be code (not markdown)
    assert len(notebook["cells"]) == 2
    assert notebook["cells"][0]["cell_type"] == "code"
    assert "x = 1" in "".join(notebook["cells"][0]["source"])
    assert notebook["cells"][1]["cell_type"] == "markdown"


def test_multiple_outputs_with_fence():
    """Test multiple outputs attached to a fenced code cell."""
    md_content = """```python
print("first")
print("second")
42
```
<!-- @nemo-nb: output -->
first
second
<!-- @nemo-nb: output execute_result -->
42
"""

    converter = MarkdownToNotebookConverter()
    converter._parse_markdown_with_context(md_content)
    notebook = converter._create_notebook_dict()

    assert len(notebook["cells"]) == 1
    assert notebook["cells"][0]["cell_type"] == "code"
    assert len(notebook["cells"][0]["outputs"]) == 2
    assert notebook["cells"][0]["outputs"][0]["output_type"] == "stream"
    assert notebook["cells"][0]["outputs"][1]["output_type"] == "execute_result"


def test_four_backticks_for_nested_fences():
    """Test using four backticks to fence code containing triple backticks."""
    md_content = """# Documentation

````python
# This code contains triple backticks
markdown = '''
```python
x = 1
```
'''
print(markdown)
````

More text
"""

    converter = MarkdownToNotebookConverter()
    converter._parse_markdown_with_context(md_content)
    notebook = converter._create_notebook_dict()

    assert len(notebook["cells"]) == 3
    assert notebook["cells"][0]["cell_type"] == "markdown"

    assert notebook["cells"][1]["cell_type"] == "code"
    code_content = "".join(notebook["cells"][1]["source"])
    assert "```python" in code_content
    assert "x = 1" in code_content

    assert notebook["cells"][2]["cell_type"] == "markdown"


def test_notebook_with_triple_backticks_uses_explicit_markers():
    """Test that notebook to markdown uses explicit markers when code contains ```."""
    notebook = {
        "cells": [
            {
                "cell_type": "code",
                "source": ['markdown = """\n```python\nx = 1\n```\n"""'],
                "outputs": [],
                "metadata": {},
            },
        ],
        "metadata": {},
        "nbformat": 4,
        "nbformat_minor": 4,
    }

    converter = NotebookToMarkdownConverter()
    md = converter.convert_notebook_dict(notebook)

    # Should automatically add disable-fence-conversion marker and use explicit cell markers
    assert "<!-- @nemo-nb: disable-fence-conversion -->" in md
    assert "<!-- @nemo-nb: cell python -->" in md
    # Should NOT use fence delimiters for the code cell
    # The ``` inside the string should be preserved as literal text
    assert 'markdown = """' in md
    assert "```python" in md  # This is the literal string inside the code, not a fence
    assert "x = 1" in md


def test_five_backticks():
    """Test using five backticks (edge case)."""
    md_content = """# Test

`````python
code = "test"
`````

Text
"""

    converter = MarkdownToNotebookConverter()
    converter._parse_markdown_with_context(md_content)
    notebook = converter._create_notebook_dict()

    assert len(notebook["cells"]) == 3
    assert notebook["cells"][1]["cell_type"] == "code"
    assert 'code = "test"' in "".join(notebook["cells"][1]["source"])


def test_disable_fence_conversion_basic():
    """Test disable-fence-conversion keeps fences in markdown cells."""
    md_content = """<!-- @nemo-nb: disable-fence-conversion -->
# Title

Here's some example code:

```python
x = 1
y = 2
```

More text
"""

    converter = MarkdownToNotebookConverter()
    converter._check_disable_fence_conversion(md_content)
    converter._parse_markdown_with_context(md_content)
    notebook = converter._create_notebook_dict()

    # Should have only 1 cell (all markdown, no code cell created)
    assert len(notebook["cells"]) == 1
    assert notebook["cells"][0]["cell_type"] == "markdown"

    # The markdown cell should contain the fence markers
    content = "".join(notebook["cells"][0]["source"])
    assert "```python" in content
    assert "x = 1" in content
    assert "y = 2" in content
    assert "```" in content


def test_disable_fence_conversion_with_explicit_cell_markers():
    """Test disable-fence-conversion with explicit cell markers for code cells."""
    md_content = """<!-- @nemo-nb: disable-fence-conversion -->
# Title

Here's documentation with code examples:

```python
# This stays as markdown
example = "not executable"
```

<!-- @nemo-nb: cell python -->
# This is an actual code cell
actual_code = "executable"

<!-- @nemo-nb: cell markdown -->
More text with another example:

```bash
echo "This also stays as markdown"
```
"""

    converter = MarkdownToNotebookConverter()
    converter._check_disable_fence_conversion(md_content)
    converter._parse_markdown_with_context(md_content)
    notebook = converter._create_notebook_dict()

    # Should have 3 cells: markdown with fence, code cell, markdown with fence
    assert len(notebook["cells"]) == 3

    # First cell: markdown with fence
    assert notebook["cells"][0]["cell_type"] == "markdown"
    content0 = "".join(notebook["cells"][0]["source"])
    assert "```python" in content0
    assert 'example = "not executable"' in content0

    # Second cell: actual code cell (from explicit marker)
    assert notebook["cells"][1]["cell_type"] == "code"
    content1 = "".join(notebook["cells"][1]["source"])
    assert 'actual_code = "executable"' in content1
    # Should NOT contain the markdown after it
    assert "More text" not in content1

    # Third cell: markdown with fence (from explicit markdown marker)
    assert notebook["cells"][2]["cell_type"] == "markdown"
    content2 = "".join(notebook["cells"][2]["source"])
    assert "```bash" in content2
    assert 'echo "This also stays as markdown"' in content2


def test_disable_fence_conversion_multiple_fences():
    """Test disable-fence-conversion with multiple fences in same cell."""
    md_content = """<!-- @nemo-nb: disable-fence-conversion -->
# API Examples

Python example:

```python
import requests
response = requests.get("https://api.example.com")
```

Curl example:

```bash
curl https://api.example.com
```

Both stay in the same markdown cell.
"""

    converter = MarkdownToNotebookConverter()
    converter._check_disable_fence_conversion(md_content)
    converter._parse_markdown_with_context(md_content)
    notebook = converter._create_notebook_dict()

    # Should have only 1 markdown cell
    assert len(notebook["cells"]) == 1
    assert notebook["cells"][0]["cell_type"] == "markdown"

    content = "".join(notebook["cells"][0]["source"])
    assert "```python" in content
    assert "import requests" in content
    assert "```bash" in content
    assert "curl https://api.example.com" in content


def test_auto_disable_fence_conversion_when_cell_contains_backticks():
    """Test that disable-fence-conversion is auto-added when notebook contains triple backticks."""
    notebook = {
        "cells": [
            {"cell_type": "markdown", "source": ["# Documentation"], "metadata": {}},
            {
                "cell_type": "code",
                "source": ['markdown_text = """\n```python\nx = 1\n```\n"""'],
                "outputs": [],
                "metadata": {},
            },
            {"cell_type": "markdown", "source": ["More text"], "metadata": {}},
        ],
        "metadata": {},
        "nbformat": 4,
        "nbformat_minor": 4,
    }

    converter = NotebookToMarkdownConverter()
    md = converter.convert_notebook_dict(notebook)

    # Should automatically add disable-fence-conversion marker at the start
    assert "<!-- @nemo-nb: disable-fence-conversion -->" in md
    # Marker should be at the very beginning
    lines = md.strip().split("\n")
    assert lines[0] == "<!-- @nemo-nb: disable-fence-conversion -->"


def test_auto_disable_fence_conversion_markdown_cell_with_backticks():
    """Test that disable-fence-conversion is auto-added for markdown cells with backticks."""
    notebook = {
        "cells": [
            {
                "cell_type": "markdown",
                "source": ["# Example\n\n```python\nx = 1\n```"],
                "metadata": {},
            },
        ],
        "metadata": {},
        "nbformat": 4,
        "nbformat_minor": 4,
    }

    converter = NotebookToMarkdownConverter()
    md = converter.convert_notebook_dict(notebook)

    # Should automatically add disable-fence-conversion marker
    assert "<!-- @nemo-nb: disable-fence-conversion -->" in md
    assert md.startswith("<!-- @nemo-nb: disable-fence-conversion -->")


def test_no_auto_disable_fence_conversion_without_backticks():
    """Test that disable-fence-conversion is NOT added when no triple backticks present."""
    notebook = {
        "cells": [
            {"cell_type": "markdown", "source": ["# Title"], "metadata": {}},
            {
                "cell_type": "code",
                "source": ["x = 1\ny = 2"],
                "outputs": [],
                "metadata": {},
            },
        ],
        "metadata": {},
        "nbformat": 4,
        "nbformat_minor": 4,
    }

    converter = NotebookToMarkdownConverter()
    md = converter.convert_notebook_dict(notebook)

    # Should NOT have disable-fence-conversion marker
    assert "<!-- @nemo-nb: disable-fence-conversion -->" not in md
    # Should use normal fences
    assert "```python" in md


def test_auto_disable_roundtrip_preserves_structure():
    """Test that auto-disable marker allows proper roundtrip conversion."""
    # Original notebook with triple backticks in code
    notebook = {
        "cells": [
            {"cell_type": "markdown", "source": ["# Markdown Tutorial"], "metadata": {}},
            {
                "cell_type": "code",
                "source": ['example = """\n```markdown\n# Example\n```\n"""'],
                "outputs": [],
                "metadata": {},
            },
        ],
        "metadata": {},
        "nbformat": 4,
        "nbformat_minor": 4,
    }

    # Convert to markdown
    nb_to_md = NotebookToMarkdownConverter()
    md = nb_to_md.convert_notebook_dict(notebook)

    # Should have disable-fence-conversion marker
    assert "<!-- @nemo-nb: disable-fence-conversion -->" in md
    # Should use explicit cell markers instead of fences
    assert "<!-- @nemo-nb: cell python -->" in md
    assert "<!-- @nemo-nb: cell markdown -->" in md

    # Convert back to notebook
    md_to_nb = MarkdownToNotebookConverter()
    md_to_nb._check_disable_fence_conversion(md)
    md_to_nb._parse_markdown_with_context(md)
    result_notebook = md_to_nb._create_notebook_dict()

    # Should preserve cells (may have extra cell for the marker itself, that's ok)
    # Find the markdown cell with "Markdown Tutorial" and code cell with triple backticks
    markdown_cells = [c for c in result_notebook["cells"] if c["cell_type"] == "markdown"]
    code_cells = [c for c in result_notebook["cells"] if c["cell_type"] == "code"]

    # Should have at least 1 markdown cell and 1 code cell
    assert len(markdown_cells) >= 1
    assert len(code_cells) == 1

    # Find the markdown cell with content
    tutorial_cell = next((c for c in markdown_cells if "Markdown Tutorial" in "".join(c["source"])), None)
    assert tutorial_cell is not None

    # Code cell should still contain the triple backticks
    code_content = "".join(code_cells[0]["source"])
    assert "```markdown" in code_content


def test_text_fence_becomes_raw_cell():
    """Test that a ```text fence is converted to a raw cell, not a code cell."""
    md_content = """# Title

```text
 ┌──────────────┐
 │  ASCII art   │
 └──────────────┘
```

More text.
"""

    converter = MarkdownToNotebookConverter()
    converter._parse_markdown_with_context(md_content)
    notebook = converter._create_notebook_dict()

    assert len(notebook["cells"]) == 3
    assert notebook["cells"][0]["cell_type"] == "markdown"
    assert notebook["cells"][1]["cell_type"] == "raw"
    assert "ASCII art" in "".join(notebook["cells"][1]["source"])
    # Raw cells must not have outputs or execution_count fields
    assert "outputs" not in notebook["cells"][1]
    assert "execution_count" not in notebook["cells"][1]
    assert notebook["cells"][2]["cell_type"] == "markdown"


def test_yaml_fence_becomes_raw_cell():
    """Test that a ```yaml fence is converted to a raw cell, not a code cell."""
    md_content = """# Config example

```yaml
key: value
nested:
  foo: bar
```
"""

    converter = MarkdownToNotebookConverter()
    converter._parse_markdown_with_context(md_content)
    notebook = converter._create_notebook_dict()

    raw_cells = [c for c in notebook["cells"] if c["cell_type"] == "raw"]
    assert len(raw_cells) == 1
    assert "key: value" in "".join(raw_cells[0]["source"])
    assert "outputs" not in raw_cells[0]


def test_python_fence_still_becomes_code_cell():
    """Sanity-check: ```python fences are unaffected by the raw-cell override."""
    md_content = """```python
x = 1
```
"""

    converter = MarkdownToNotebookConverter()
    converter._parse_markdown_with_context(md_content)
    notebook = converter._create_notebook_dict()

    code_cells = [c for c in notebook["cells"] if c["cell_type"] == "code"]
    assert len(code_cells) == 1
    assert "x = 1" in "".join(code_cells[0]["source"])


def test_raw_cell_roundtrip_to_markdown():
    """Test that text/yaml raw cells survive the full md→nb→md roundtrip.

    This is the key regression test: raw cells must be converted back to the
    correct code fence (not dropped) when the notebook is rendered to markdown
    for Sphinx HTML output.
    """
    md_content = """# Title

```text
 ┌──────────┐
 │ diagram  │
 └──────────┘
```

```yaml
key: value
```

```python
x = 1
```
"""

    # Stage 1: md → notebook
    md_to_nb = MarkdownToNotebookConverter()
    md_to_nb._parse_markdown_with_context(md_content)
    notebook = md_to_nb._create_notebook_dict()

    raw_cells = [c for c in notebook["cells"] if c["cell_type"] == "raw"]
    assert len(raw_cells) == 2

    # Stage 2: notebook → markdown (for Sphinx HTML)
    nb_to_md = NotebookToMarkdownConverter()
    result_md = nb_to_md.convert_notebook_dict(notebook)

    # Both fences must appear in the rendered markdown
    assert "```text" in result_md
    assert "diagram" in result_md
    assert "```yaml" in result_md
    assert "key: value" in result_md
    assert "```python" in result_md
    assert "x = 1" in result_md


def test_no_language_fence_becomes_raw_cell():
    """Test that a fence with no language tag becomes a raw cell, not a Python cell."""
    md_content = """# Title

```
some plain text
no language specified
```

```python
x = 1
```
"""

    converter = MarkdownToNotebookConverter()
    converter._parse_markdown_with_context(md_content)
    notebook = converter._create_notebook_dict()

    raw_cells = [c for c in notebook["cells"] if c["cell_type"] == "raw"]
    code_cells = [c for c in notebook["cells"] if c["cell_type"] == "code"]

    assert len(raw_cells) == 1
    assert "plain text" in "".join(raw_cells[0]["source"])

    assert len(code_cells) == 1
    assert "x = 1" in "".join(code_cells[0]["source"])


def test_no_language_fence_roundtrip():
    """Test that a no-language fence roundtrips without a language tag."""
    md_content = """```
plain text block
```
"""

    md_to_nb = MarkdownToNotebookConverter()
    md_to_nb._parse_markdown_with_context(md_content)
    notebook = md_to_nb._create_notebook_dict()

    nb_to_md = NotebookToMarkdownConverter()
    result_md = nb_to_md.convert_notebook_dict(notebook)

    # Should reconstruct as a no-language fence (``` with no language)
    assert "plain text block" in result_md
    # No language identifier between the backticks and the newline
    assert "```\n" in result_md or result_md.startswith("```\n")
