#!/usr/bin/env python3
# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Lint notebook documentation files for syntax errors.

This script validates markdown notebooks without executing them, making it
suitable for CI/CD pipelines and pre-commit hooks.

Usage:
    uv run python docs/_scripts/lint_notebooks.py <path> [<path> ...]
    uv run python docs/_scripts/lint_notebooks.py docs/run-inference/
    uv run python docs/_scripts/lint_notebooks.py docs/run-inference/ docs/safe-synthesizer/
    uv run python docs/_scripts/lint_notebooks.py docs/run-inference/ --type-check
    uv run python docs/_scripts/lint_notebooks.py docs/run-inference/ --markers-only  # Only files with marker
"""

import argparse
import ast
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import List, Tuple

from nemo_nb import (
    MarkdownToNotebookConverter,
    expand_includes,
    find_processable_notebooks,
    is_excluded_file,
    is_in_excluded_dir,
    print_conflicts_error,
)

# Pattern to detect Python code blocks in markdown
RE_PYTHON_CODE_BLOCK = re.compile(r"^```python\s*$", re.MULTILINE)
SKIP_TYPE_CHECK_MARKER = "<!-- @nemo-nb: skip-type-check -->"

# Pattern to match code fence opening (```python) with optional leading whitespace
RE_CODE_FENCE_OPEN = re.compile(r"^(\s*)(`{3,})python\s*$")
# Pattern to match code fence closing
RE_CODE_FENCE_CLOSE = re.compile(r"^(\s*)`{3,}\s*$")


def has_python_code_blocks(md_path: Path) -> bool:
    """Check if a markdown file has Python code blocks.

    Args:
        md_path: Path to the markdown file

    Returns:
        True if the file contains at least one ```python code block
    """
    try:
        content = md_path.read_text(encoding="utf-8")
        return bool(RE_PYTHON_CODE_BLOCK.search(content))
    except Exception:
        return False


def extract_python_blocks_with_line_numbers(md_path: Path) -> List[Tuple[int, str]]:
    """Extract Python code blocks from markdown with their starting line numbers.

    Args:
        md_path: Path to the markdown file

    Returns:
        List of (start_line_in_markdown, code_content) tuples.
        start_line_in_markdown is 1-indexed and points to the first line of code
        (the line after the opening ```python fence).
    """
    try:
        content = md_path.read_text(encoding="utf-8")
        # Expand include directives before extracting code blocks
        content = expand_includes(content, md_path.parent)
    except Exception:
        return []

    lines = content.split("\n")
    blocks: List[Tuple[int, str]] = []
    skip_next_python_block = False

    i = 0
    while i < len(lines):
        line = lines[i]
        if line.strip() == SKIP_TYPE_CHECK_MARKER:
            skip_next_python_block = True
            i += 1
            continue

        fence_match = RE_CODE_FENCE_OPEN.match(line)

        if fence_match:
            fence_delimiter = fence_match.group(2)
            fence_len = len(fence_delimiter)
            indentation = fence_match.group(1)
            indent_len = len(indentation)

            # Code starts on the next line (1-indexed for display)
            code_start_line = i + 2  # +1 for 0-indexed to 1-indexed, +1 to skip fence line

            # Find closing fence
            code_lines = []
            j = i + 1
            while j < len(lines):
                close_match = RE_CODE_FENCE_CLOSE.match(lines[j])
                if close_match:
                    # Check if this fence closes our block (same or more backticks)
                    close_fence = lines[j].lstrip()
                    if len(close_fence.rstrip()) >= fence_len:
                        break
                # Remove indentation from code line if present
                code_line = lines[j]
                if indent_len > 0 and code_line.startswith(indentation):
                    code_line = code_line[indent_len:]
                code_lines.append(code_line)
                j += 1

            if code_lines and not skip_next_python_block:
                blocks.append((code_start_line, "\n".join(code_lines)))

            skip_next_python_block = False

            i = j + 1
        else:
            i += 1

    return blocks


def prepare_notebook_for_type_check(notebook_path: Path) -> Tuple[str, List[int]]:
    """
    Extract and combine Python code blocks from a markdown file for type checking.

    Args:
        notebook_path: Path to the markdown file

    Returns:
        Tuple of (combined_source, line_mapping) where line_mapping maps
        1-indexed line numbers in the combined source to 1-indexed line numbers
        in the original markdown file. Returns ("", []) if extraction fails.
    """
    blocks = extract_python_blocks_with_line_numbers(notebook_path)

    if not blocks:
        return "", []

    combined_lines: List[str] = []
    # line_mapping[i] = markdown line number for combined source line i+1 (1-indexed)
    line_mapping: List[int] = []

    for md_start_line, source in blocks:
        source_lines = source.splitlines()
        for offset, line in enumerate(source_lines):
            combined_lines.append(line)
            line_mapping.append(md_start_line + offset)
        # Add blank line between blocks (maps to last line of previous block)
        combined_lines.append("")
        if source_lines:
            line_mapping.append(md_start_line + len(source_lines) - 1)
        else:
            line_mapping.append(md_start_line)

    return "\n".join(combined_lines), line_mapping


def translate_line_number(line_in_combined: int, line_mapping: List[int]) -> int:
    """Translate a line number from combined source to original markdown.

    Args:
        line_in_combined: 1-indexed line number in the combined Python source
        line_mapping: Mapping from combined line numbers to markdown line numbers

    Returns:
        1-indexed line number in the original markdown file
    """
    if not line_mapping:
        return line_in_combined

    # line_mapping is 0-indexed (line_mapping[0] = markdown line for combined line 1)
    idx = line_in_combined - 1
    if 0 <= idx < len(line_mapping):
        return line_mapping[idx]

    # Fallback: return original line number if out of range
    return line_in_combined


def batch_type_check(notebook_paths: List[Path]) -> dict[Path, Tuple[int, str]]:
    """
    Run ty type checker on multiple notebooks in a single batch.

    This is much faster than running ty separately for each notebook,
    as it eliminates the repeated uv startup overhead.

    Args:
        notebook_paths: List of notebook paths to type check

    Returns:
        Dictionary mapping notebook path to (exit_code, output) tuple
    """
    if not notebook_paths:
        return {}

    # Prepare all notebooks and create temp files
    temp_files: dict[Path, str] = {}  # notebook_path -> temp_file_path
    temp_to_notebook: dict[str, Path] = {}  # temp_file_path -> notebook_path
    line_mappings: dict[Path, List[int]] = {}  # notebook_path -> line mapping

    try:
        for nb_path in notebook_paths:
            combined_source, line_mapping = prepare_notebook_for_type_check(nb_path)
            if not combined_source:
                continue

            f = tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False)
            f.write(combined_source)
            f.close()

            temp_files[nb_path] = f.name
            temp_to_notebook[f.name] = nb_path
            line_mappings[nb_path] = line_mapping

        if not temp_files:
            return {nb: (0, "") for nb in notebook_paths}

        # Run ty check once on all files
        temp_paths = list(temp_files.values())
        result = subprocess.run(
            ["uv", "run", "ty", "check", "--output-format", "concise"] + temp_paths,
            capture_output=True,
            text=True,
            timeout=120,
        )

        # Parse output to map errors back to notebooks
        output_by_notebook: dict[Path, List[str]] = {nb: [] for nb in notebook_paths}

        # Warnings to filter out (common SDK false positives)
        ignored_warnings = ["possibly-unbound-attribute"]

        # Pattern to parse ty output: "path:line:col: message"
        ty_output_pattern = re.compile(r"^(.+?):(\d+):(\d+): (.+)$")

        for line in result.stdout.splitlines():
            # Skip ignored warning types
            if any(f"[{warning}]" in line for warning in ignored_warnings):
                continue

            # ty output format: "path/to/file.py:line:col: error message"
            for temp_path, nb_path in temp_to_notebook.items():
                if line.startswith(temp_path):
                    # Parse and translate line number
                    match = ty_output_pattern.match(line)
                    if match:
                        combined_line = int(match.group(2))
                        col = match.group(3)
                        message = match.group(4)
                        md_line = translate_line_number(combined_line, line_mappings.get(nb_path, []))
                        cleaned_line = f"{nb_path.name}:{md_line}:{col}: {message}"
                    else:
                        # Fallback: just replace path
                        cleaned_line = line.replace(temp_path, str(nb_path.name))
                    output_by_notebook[nb_path].append(cleaned_line)
                    break

        # Build result dictionary
        results: dict[Path, Tuple[int, str]] = {}

        # Check if ty produced any per-file output at all
        has_any_output = any(output_by_notebook[nb] for nb in notebook_paths if nb in output_by_notebook)

        for nb_path in notebook_paths:
            if nb_path in temp_files:
                # Had Python code and was checked
                nb_output = "\n".join(output_by_notebook[nb_path])
                # If this notebook had errors, return non-zero exit code
                if output_by_notebook[nb_path]:
                    exit_code = 1
                elif result.returncode != 0 and not has_any_output:
                    # ty failed but produced no per-file output - ty itself failed
                    exit_code = 1
                    nb_output = "Type checking failed: ty exited with non-zero status but produced no output"
                else:
                    exit_code = 0
                results[nb_path] = (exit_code, nb_output)
            else:
                # No Python code or conversion failed
                results[nb_path] = (0, "")

        return results

    except subprocess.TimeoutExpired:
        return {nb: (1, "Type checking timed out") for nb in notebook_paths}
    except FileNotFoundError:
        return {nb: (0, "") for nb in notebook_paths}
    except Exception as e:
        return {nb: (1, f"Type checking failed: {e}") for nb in notebook_paths}
    finally:
        # Clean up temp files
        for temp_path in temp_files.values():
            Path(temp_path).unlink(missing_ok=True)


def lint_notebook_syntax_only(notebook_path: Path) -> List[Tuple[str, str]]:
    """
    Lint a notebook file for syntax errors only (fast).

    Args:
        notebook_path: Path to the notebook file

    Returns:
        List of (error_type, message) tuples
    """
    errors = []

    try:
        # Read and expand includes before conversion
        content = notebook_path.read_text(encoding="utf-8")
        expanded_content = expand_includes(content, notebook_path.parent)

        # Write expanded content to temporary file for conversion
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False, encoding="utf-8") as temp_file:
            temp_file.write(expanded_content)
            temp_path = Path(temp_file.name)

        try:
            converter = MarkdownToNotebookConverter()
            notebook = converter.convert(temp_path)
        finally:
            temp_path.unlink(missing_ok=True)
    except Exception as e:
        return [("conversion", f"Failed to convert notebook: {e}")]

    # Check Python cells for syntax errors
    python_cells = [
        (i, c)
        for i, c in enumerate(notebook["cells"])
        if c.get("cell_type") == "code" and c.get("metadata", {}).get("language", "python") == "python"
    ]

    for cell_idx, cell in python_cells:
        source = cell.get("source", [])
        if isinstance(source, list):
            source = "".join(source)

        if not source.strip():
            continue

        # Syntax check (fast, always enabled)
        try:
            ast.parse(source)
        except SyntaxError as e:
            errors.append(("syntax", f"Cell {cell_idx + 1}: {e.msg} at line {e.lineno}"))

    return errors


def lint_notebooks(
    notebooks_dir: str,
    enable_type_check: bool = False,
    markers_only: bool = False,
) -> int:
    """
    Lint all notebooks in a directory.

    Args:
        notebooks_dir: Directory to search for notebooks
        enable_type_check: Enable ty type checking
        markers_only: If True, only lint files with @nemo-nb: process marker.
                      If False (default), lint any markdown file with Python code blocks.

    Returns:
        Exit code: 0 if all valid, 1 if errors found
    """
    path_obj = Path(notebooks_dir)

    # Handle single file case
    if path_obj.is_file() and path_obj.suffix == ".md":
        if is_excluded_file(path_obj):
            print(f"Skipping {path_obj}: excluded filename")
            return 0

        content = path_obj.read_text(encoding="utf-8")
        has_marker = "@nemo-nb: process" in content
        has_python = has_python_code_blocks(path_obj)

        if markers_only and not has_marker:
            print(f"Skipping {path_obj}: no @nemo-nb: process marker (use without --markers-only to lint anyway)")
            return 0

        if not has_marker and not has_python:
            print(f"Skipping {path_obj}: no @nemo-nb: process marker and no Python code blocks")
            return 0

        return _lint_single_file(path_obj, enable_type_check)

    # Directory case
    if markers_only:
        # Only use marked files
        result = find_processable_notebooks(notebooks_dir)

        if result.conflicts:
            print_conflicts_error(result.conflicts)
            return 1

        md_files = list(result.md_files)
        ipynb_files = list(result.ipynb_files)
    else:
        # Find all markdown files with Python code blocks
        ipynb_files: List[Path] = []
        md_files: List[Path] = []

        if path_obj.is_dir():
            all_md = list(path_obj.rglob("*.md"))
            # Filter out excluded directories (_generated, _build), excluded filenames, and check for Python code
            md_files = [
                md
                for md in all_md
                if not is_in_excluded_dir(md) and not is_excluded_file(md) and has_python_code_blocks(md)
            ]

            # Also include .ipynb files with marker (for completeness)
            result = find_processable_notebooks(notebooks_dir)
            if result.conflicts:
                print_conflicts_error(result.conflicts)
                return 1
            ipynb_files = list(result.ipynb_files)

    total_count = len(ipynb_files) + len(md_files)

    if total_count == 0:
        print(f"No markdown files with Python code blocks found in {notebooks_dir}")
        if path_obj.is_dir():
            all_md = list(path_obj.rglob("*.md"))
            if all_md:
                print(f"(Found {len(all_md)} .md files total, but none had Python code blocks)")
        return 0

    print(f"Linting {total_count} file(s) with Python code...\n")

    failed = []

    # Lint .ipynb files
    for nb in ipynb_files:
        # For .ipynb, we need to check if it's already a valid notebook
        # This is a placeholder - you might want to add actual ipynb linting
        print(f"ℹ {nb} (skipping .ipynb linting for now)")

    # Step 1: Syntax check all files (fast, always enabled)
    print("Running syntax checks...")
    syntax_results: dict[Path, List[Tuple[str, str]]] = {}
    for md in md_files:
        syntax_results[md] = lint_notebook_syntax_only(md)

    # Step 2: Batch type check all files (if enabled)
    type_results: dict[Path, Tuple[int, str]] = {}
    if enable_type_check:
        print("Running batch type checking...")
        type_results = batch_type_check(md_files)
    else:
        type_results = {md: (0, "") for md in md_files}

    # Step 3: Print results
    print("\nResults:\n")
    for md in md_files:
        syntax_errors = syntax_results[md]
        ty_exit_code, ty_output = type_results.get(md, (0, ""))

        has_errors = bool(syntax_errors) or ty_exit_code != 0

        if not has_errors:
            print(f"✓ {md}")
            continue

        print(f"✗ {md}")

        for error_type, message in syntax_errors:
            print(f"  SYNTAX ERROR: {message}")

        if ty_exit_code != 0 and ty_output:
            print(f"  TYPE CHECK FAILED (exit code {ty_exit_code}):")
            for line in ty_output.strip().splitlines():
                print(f"    {line}")

        failed.append(md)

    print("\n" + "=" * 60)
    if failed:
        print(f"✗ FAILED: {len(failed)} page(s) have errors")
        for nb in failed:
            print(f"  - {nb}")
        return 1
    else:
        print("✓ All pages passed")
        return 0


def _lint_single_file(md_path: Path, enable_type_check: bool) -> int:
    """Lint a single markdown file.

    Args:
        md_path: Path to the markdown file
        enable_type_check: Enable ty type checking

    Returns:
        Exit code: 0 if valid, 1 if errors found
    """
    print(f"Linting {md_path}...\n")

    # Syntax check
    syntax_errors = lint_notebook_syntax_only(md_path)

    # Type check
    ty_exit_code, ty_output = 0, ""
    if enable_type_check:
        type_results = batch_type_check([md_path])
        ty_exit_code, ty_output = type_results.get(md_path, (0, ""))

    has_errors = bool(syntax_errors) or ty_exit_code != 0

    if not has_errors:
        print(f"✓ {md_path}")
        print("\n" + "=" * 60)
        print("✓ All notebooks passed")
        return 0

    print(f"✗ {md_path}")

    for error_type, message in syntax_errors:
        print(f"  SYNTAX ERROR: {message}")

    if ty_exit_code != 0 and ty_output:
        print(f"  TYPE CHECK FAILED (exit code {ty_exit_code}):")
        for line in ty_output.strip().splitlines():
            print(f"    {line}")

    print("\n" + "=" * 60)
    print("✗ FAILED: 1 page has errors")
    print(f"  - {md_path}")
    return 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Lint notebook files for syntax and type errors without executing them"
    )
    parser.add_argument("paths", nargs="+", help="Directories or files to lint")
    parser.add_argument(
        "--type-check",
        action="store_true",
        help="Enable ty type checking (slower but catches parameter errors, type mismatches, etc.)",
    )
    parser.add_argument(
        "--markers-only",
        action="store_true",
        help="Only lint files with @nemo-nb: process marker. "
        "By default, any markdown file with Python code blocks is linted.",
    )
    args = parser.parse_args()

    overall_exit = 0
    for path in args.paths:
        result = lint_notebooks(path, args.type_check, args.markers_only)
        if result != 0:
            overall_exit = result
    sys.exit(overall_exit)
