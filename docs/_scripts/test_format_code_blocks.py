# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

from pathlib import Path

from docs._scripts.format_code_blocks import display_path, format_markdown


def test_format_markdown_formats_json_fence() -> None:
    markdown = """Before
```json
{"b": [1,2], "a": true}
```
"""

    formatted, blocks_changed = format_markdown(markdown)

    assert blocks_changed == 1
    assert (
        formatted
        == """Before
```json
{
  "b": [
    1,
    2
  ],
  "a": true
}
```
"""
    )


def test_format_markdown_preserves_markdown_indent() -> None:
    markdown = """??? "Output"
    ```json
    {"a":1}
    ```
"""

    formatted, blocks_changed = format_markdown(markdown)

    assert blocks_changed == 1
    assert (
        formatted
        == """??? "Output"
    ```json
    {
      "a": 1
    }
    ```
"""
    )


def test_format_markdown_skips_invalid_json() -> None:
    markdown = """```json
{"a": 1,}
```
"""

    formatted, blocks_changed = format_markdown(markdown)

    assert blocks_changed == 0
    assert formatted == markdown


def test_format_markdown_skips_raw_blocks() -> None:
    markdown = """{% raw %}
```json
{"a":1}
```
{% endraw %}
"""

    formatted, blocks_changed = format_markdown(markdown)

    assert blocks_changed == 0
    assert formatted == markdown


def test_format_markdown_formats_compact_python_indent() -> None:
    markdown = """```python
model_configs = [
 dd.ModelConfig(
 provider="system/nvidia-build",
 )
]
```
"""

    formatted, blocks_changed = format_markdown(markdown)

    assert blocks_changed == 1
    assert (
        formatted
        == """```python
model_configs = [
    dd.ModelConfig(
        provider="system/nvidia-build",
    )
]
```
"""
    )


def test_format_markdown_formats_compact_python_indent_in_raw_block() -> None:
    markdown = """{% raw %}
```python
config_builder.add_column(
 dd.ExpressionColumnConfig(
 expr="{{ item.value }}",
 )
)
```
{% endraw %}
"""

    formatted, blocks_changed = format_markdown(markdown)

    assert blocks_changed == 1
    assert (
        formatted
        == """{% raw %}
```python
config_builder.add_column(
    dd.ExpressionColumnConfig(
        expr="{{ item.value }}",
    )
)
```
{% endraw %}
"""
    )


def test_format_markdown_preserves_markdown_indent_for_python() -> None:
    markdown = """=== "Python"

    ```python
    if enabled:
     print("enabled")
    ```
"""

    formatted, blocks_changed = format_markdown(markdown)

    assert blocks_changed == 1
    assert (
        formatted
        == """=== "Python"

    ```python
    if enabled:
        print("enabled")
    ```
"""
    )


def test_format_markdown_does_not_indent_python_blank_lines() -> None:
    markdown = (
        """!!! note

    ```python
    import os
"""
        "    \n"
        """    value=1
    ```
"""
    )

    formatted, blocks_changed = format_markdown(markdown)

    assert blocks_changed == 1
    assert (
        formatted
        == """!!! note

    ```python
    import os

    value = 1
    ```
"""
    )


def test_format_markdown_does_not_indent_json_blank_lines() -> None:
    markdown = (
        """!!! note

    ```json
    {
"""
        "    \n"
        """      "a": 1
    }
    ```
"""
    )

    formatted, blocks_changed = format_markdown(markdown)

    assert blocks_changed == 1
    assert (
        formatted
        == """!!! note

    ```json
    {
      "a": 1
    }
    ```
"""
    )


def test_format_markdown_skips_python_with_triple_quoted_strings() -> None:
    markdown = '''```python
prompt = """
 keep this leading space
"""
```
'''

    formatted, blocks_changed = format_markdown(markdown)

    assert blocks_changed == 0
    assert formatted == markdown


def test_display_path_handles_paths_outside_docs_dir() -> None:
    docs_dir = Path("/repo/docs")

    assert display_path(Path("/repo/docs/page.md"), docs_dir) == Path("page.md")
    assert display_path(Path("/tmp/page.md"), docs_dir) == Path("/tmp/page.md")
