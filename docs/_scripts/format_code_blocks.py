#!/usr/bin/env python3
# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Format fenced code blocks in Markdown documentation."""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from functools import cache
from pathlib import Path
from typing import Iterable

FENCE_RE = re.compile(r"^([ \t]*)(`{3,}|~{3,})(.*)$")
JSON_LANGUAGES = {"json", "output"}
PYTHON_LANGUAGES = {"python", "py"}
RAW_START = "{% raw %}"
RAW_END = "{% endraw %}"
RUFF_FORMAT_TIMEOUT_SECONDS = 30
SKIP_DIRS = {
    ".git",
    ".venv-docs",
    ".venv-mkdocs",
    "_build",
    "_test_serve",
    "site",
}


@dataclass
class FileResult:
    path: Path
    changed: bool
    blocks_changed: int


def find_markdown_files(paths: Iterable[Path], docs_dir: Path) -> list[Path]:
    markdown_files: list[Path] = []
    for path in paths:
        if not path.exists():
            raise FileNotFoundError(f"{path} does not exist")
        if path.is_file():
            if path.suffix == ".md":
                markdown_files.append(path)
            continue
        for root, dirs, files in os.walk(path):
            dirs[:] = [directory for directory in dirs if directory not in SKIP_DIRS]
            for filename in files:
                file_path = Path(root) / filename
                if file_path.suffix == ".md" and file_path.is_relative_to(docs_dir):
                    markdown_files.append(file_path)
    return sorted(set(markdown_files))


def fence_closes(line: str, fence_marker: str) -> bool:
    stripped = line.lstrip(" \t")
    marker_char = fence_marker[0]
    marker_len = len(fence_marker)
    if not stripped.startswith(marker_char * marker_len):
        return False
    return stripped.strip(marker_char).strip() == ""


def get_language(info_string: str) -> str:
    stripped = info_string.strip()
    if not stripped:
        return ""
    return stripped.split(maxsplit=1)[0].lower()


def remove_markdown_indent(lines: list[str], indent: str) -> str:
    if not indent:
        return "\n".join(lines)
    return "\n".join(line[len(indent) :] if line.startswith(indent) else line for line in lines)


def format_json_lines(content_lines: list[str], indent: str, language: str) -> tuple[list[str], bool]:
    if language not in JSON_LANGUAGES:
        return content_lines, False
    if any("{% raw %}" in line or "{% endraw %}" in line for line in content_lines):
        return content_lines, False

    raw_content = remove_markdown_indent(content_lines, indent)
    candidate = raw_content.strip()
    if not candidate or candidate[0] not in "[{":
        return content_lines, False

    try:
        parsed = json.loads(candidate)
    except json.JSONDecodeError:
        return content_lines, False

    if not isinstance(parsed, (dict, list)):
        return content_lines, False

    formatted = json.dumps(parsed, ensure_ascii=False, indent=2)
    formatted_lines = [add_markdown_indent(line, indent) for line in formatted.splitlines()]
    return formatted_lines, formatted_lines != content_lines


def format_python_lines(content_lines: list[str], indent: str, language: str) -> tuple[list[str], bool]:
    if language not in PYTHON_LANGUAGES:
        return content_lines, False
    if not ruff_available():
        raise RuntimeError("Ruff is required to format Python code blocks. Run `make -C docs mkdocs-env` first.")

    raw_lines = [line[len(indent) :] if indent and line.startswith(indent) else line for line in content_lines]
    raw_content = "\n".join(raw_lines).rstrip("\n")
    if not raw_content.strip():
        return content_lines, False

    try:
        result = subprocess.run(
            [sys.executable, "-m", "ruff", "format", "--stdin-filename", "docs-code-block.py", "-"],
            input=f"{raw_content}\n",
            text=True,
            capture_output=True,
            check=False,
            timeout=RUFF_FORMAT_TIMEOUT_SECONDS,
        )
    except (OSError, subprocess.TimeoutExpired):
        return content_lines, False

    if result.returncode != 0:
        return content_lines, False

    formatted_lines = [add_markdown_indent(line, indent) for line in result.stdout.rstrip("\n").splitlines()]
    return formatted_lines, formatted_lines != content_lines


def add_markdown_indent(line: str, indent: str) -> str:
    if not line:
        return line
    return f"{indent}{line}"


@cache
def ruff_available() -> bool:
    return importlib.util.find_spec("ruff") is not None


def format_code_lines(
    content_lines: list[str],
    indent: str,
    language: str,
    inside_raw_block: bool,
) -> tuple[list[str], bool]:
    python_lines, python_changed = format_python_lines(content_lines, indent, language)
    if python_changed:
        return python_lines, True
    if inside_raw_block:
        return content_lines, False
    return format_json_lines(content_lines, indent, language)


def format_markdown(text: str) -> tuple[str, int]:
    trailing_newline = text.endswith("\n")
    lines = text.splitlines()
    formatted_lines: list[str] = []
    blocks_changed = 0
    index = 0
    inside_raw_block = False

    while index < len(lines):
        line = lines[index]
        fence_match = FENCE_RE.match(line)
        if not fence_match:
            formatted_lines.append(line)
            inside_raw_block = update_raw_block_state(line, inside_raw_block)
            index += 1
            continue

        indent, fence_marker, info_string = fence_match.groups()
        language = get_language(info_string)
        formatted_lines.append(line)
        index += 1

        content_lines: list[str] = []
        while index < len(lines) and not fence_closes(lines[index], fence_marker):
            content_lines.append(lines[index])
            index += 1

        new_content_lines, changed = format_code_lines(content_lines, indent, language, inside_raw_block)
        if changed:
            blocks_changed += 1
        formatted_lines.extend(new_content_lines)

        if index < len(lines):
            formatted_lines.append(lines[index])
            index += 1

    formatted = "\n".join(formatted_lines)
    if trailing_newline:
        formatted += "\n"
    return formatted, blocks_changed


def update_raw_block_state(line: str, inside_raw_block: bool) -> bool:
    raw_start = RAW_START in line
    raw_end = RAW_END in line
    if raw_start and not raw_end:
        return True
    if raw_end and not raw_start:
        return False
    return inside_raw_block


def process_file(path: Path, check: bool) -> FileResult:
    original = path.read_text(encoding="utf-8")
    formatted, blocks_changed = format_markdown(original)
    changed = formatted != original
    if changed and not check:
        path.write_text(formatted, encoding="utf-8")
    return FileResult(path=path, changed=changed, blocks_changed=blocks_changed)


def display_path(path: Path, docs_dir: Path) -> Path:
    if path.is_relative_to(docs_dir):
        return path.relative_to(docs_dir)
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description="Format fenced code blocks in Markdown docs.")
    parser.add_argument("paths", nargs="*", type=Path, help="Markdown files or directories to process.")
    parser.add_argument(
        "--docs-dir", type=Path, default=Path("."), help="Docs directory. Defaults to current directory."
    )
    parser.add_argument("--check", action="store_true", help="Exit non-zero if any files would be changed.")
    args = parser.parse_args()

    docs_dir = args.docs_dir.resolve()
    paths = [path.resolve() for path in args.paths] if args.paths else [docs_dir]

    try:
        markdown_files = find_markdown_files(paths, docs_dir)
    except FileNotFoundError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    changed_results: list[FileResult] = []
    total_blocks = 0
    try:
        for path in markdown_files:
            result = process_file(path, args.check)
            if result.changed:
                changed_results.append(result)
                total_blocks += result.blocks_changed
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    if changed_results:
        action = "Would format" if args.check else "Formatted"
        for result in changed_results:
            print(f"{action} {display_path(result.path, docs_dir)} ({result.blocks_changed} code block(s))")
        print(f"{action} {len(changed_results)} file(s), {total_blocks} code block(s)")
        return 1 if args.check else 0

    print("All supported code blocks are already formatted.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
