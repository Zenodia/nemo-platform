# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

from pathlib import Path

from docs._scripts.lint_notebooks import extract_python_blocks_with_line_numbers


def test_extract_python_blocks_skips_next_block_marked_for_type_check(tmp_path: Path) -> None:
    markdown = """<!-- @nemo-nb: process -->

<!-- @nemo-nb: skip-type-check -->
```python
from litellm import completion
completion(model="demo", messages=[])
```

```python
print("kept")
```
"""
    notebook = tmp_path / "notebook.md"
    notebook.write_text(markdown, encoding="utf-8")

    blocks = extract_python_blocks_with_line_numbers(notebook)

    assert blocks == [(10, 'print("kept")')]
