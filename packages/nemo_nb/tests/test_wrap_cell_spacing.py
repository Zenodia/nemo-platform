# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Test wrap-cell marker spacing.

Issue: Blank line appears after :sync: sdk insert, not before.
"""

from nemo_nb.converter import NotebookConverter


def test_wrap_cell_with_insert_spacing():
    """Test that blank line appears AFTER wrap-cell markers, not inside them."""
    notebook = {
        "cells": [
            {
                "cell_type": "code",
                "metadata": {},
                "execution_count": None,
                "outputs": [],
                "source": [
                    "# @nemo-nb: wrap-cell-start :::{tab-item} Python SDK\n",
                    "# @nemo-nb: insert :sync: sdk\n",
                    "# @nemo-nb: wrap-cell-end :::\n",
                    "\n",
                    "print('hello')",
                ],
            },
        ],
        "metadata": {},
        "nbformat": 4,
        "nbformat_minor": 4,
    }

    converter = NotebookConverter()
    result = converter.convert_notebook_dict(notebook)

    # Expected: blank line AFTER `:sync: sdk`, not before
    expected_lines = [
        ":::{tab-item} Python SDK",
        ":sync: sdk",
        "",  # Blank line HERE (from the blank line before print in source)
        "```python",
        "print('hello')",
        "```",
        ":::",
    ]

    result_lines = [line.rstrip() for line in result.splitlines()]

    print("\n=== EXPECTED ===")
    for i, line in enumerate(expected_lines, 1):
        print(f"{i:3}: {repr(line)}")

    print("\n=== ACTUAL ===")
    for i, line in enumerate(result_lines, 1):
        print(f"{i:3}: {repr(line)}")

    assert result_lines == expected_lines, f"Wrap-cell spacing issue\\nExpected: {expected_lines}\\nGot: {result_lines}"
