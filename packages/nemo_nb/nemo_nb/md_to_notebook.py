#!/usr/bin/env python3
# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Markdown to Jupyter Notebook converter with nemo-nb markers.

This module converts Markdown files to Jupyter notebooks by:
1. Detecting code blocks and converting them to code cells
2. Converting markdown text to markdown cells
3. Adding nemo-nb marker comments for advanced features like tab-sets and dropdowns
"""

import json
import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Tuple

from .structures import Cell

logger = logging.getLogger(__name__)

# --- Regex patterns for nemo-nb markers ---
# Document-wide marker to disable automatic fence-to-code-cell conversion
RE_DISABLE_FENCE = re.compile(r"<!--\s*@nemo-nb:\s*disable-fence-conversion\s*-->")
# Cell marker: <!-- @nemo-nb: cell <language> -->
RE_CELL_MARKER = re.compile(r"<!--\s*@nemo-nb:\s*cell\s+(\S+)\s*-->")
# Output marker: <!-- @nemo-nb: output [type] [name] -->
RE_OUTPUT_MARKER = re.compile(r"<!--\s*@nemo-nb:\s*output(?:\s+(\S+))?(?:\s+(\S+))?\s*-->")
# Stop markers for output collection
RE_STOP_MARKER = re.compile(r"<!--\s*@nemo-nb:\s*(cell|output)")

# {include} directive block: ```{include} path\n``` (both fences on their own lines)
RE_INCLUDE_DIRECTIVE = re.compile(r"^```\{include\}\s+(.+?)\s*\n```[ \t]*(?:\n|$)", re.MULTILINE)

# --- Regex patterns for MyST directive stripping ---
# Pattern to match MyST directive opening fences
# Matches: :::{directive}, :::{directive} Label, ::::{tab-set}, etc.
RE_ADMONITION_OPEN = re.compile(r"^:{3,}\{[^}]+\}.*$", re.MULTILINE)
# Pattern to match MyST directive closing fences: :::, ::::, etc.
RE_ADMONITION_CLOSE = re.compile(r"^:{3,}\s*$", re.MULTILINE)
# Pattern to match code directive fences: ```{literalinclude}, etc.
RE_CODE_DIRECTIVE_FENCE = re.compile(r"^```\{[^}]+\}.*$", re.MULTILINE)
# Pattern to match empty MyST cross-references: [](reference-name)
RE_EMPTY_XREF = re.compile(r"\[\]\([^)]+\)")
# Pattern to match MyST labels: (label-name)=
RE_LABEL = re.compile(r"^\([^)]+\)=\s*$", re.MULTILINE)

# Mapping from fence language to cell type override.
# Languages listed here are converted to the specified cell type instead of
# the default "code" cell type. For example, "text" and "yaml" fences contain
# non-executable content (ASCII diagrams, config examples) that should be
# displayed as-is rather than run as Python. Add new entries here to extend
# this behaviour to other non-executable fence languages.
FENCE_LANGUAGE_TO_CELL_TYPE: dict[str, str] = {
    "": "raw",
    "text": "raw",
    "yaml": "raw",
    "json": "raw",
    "output": "raw",
}

# --- Regex patterns for code fence detection ---
# Opening directive fence: ```{directive} with optional leading whitespace
RE_DIRECTIVE_FENCE_OPEN = re.compile(r"^(\s*)(`{3,})\{")
# Closing directive fence: ``` (3+ backticks) with optional whitespace
RE_DIRECTIVE_FENCE_CLOSE = re.compile(r"^\s*`{3,}\s*$")
# Code fence with language: ```lang with optional leading whitespace
RE_CODE_FENCE = re.compile(r"^(\s*)(`{3,})(\w*)\s*$")
# Plain code fence start (no language capture)
RE_CODE_FENCE_START = re.compile(r"^`{3,}")
# Leading whitespace capture
RE_LEADING_WHITESPACE = re.compile(r"^(\s*)")
# Markdown heading (h1-h6)
RE_HEADING = re.compile(r"^#{1,6}\s")
# Directive option (e.g., :sync: value)
RE_DIRECTIVE_OPTION = re.compile(r"^\s*:[a-zA-Z0-9_-]+:")


@dataclass
class ParseState:
    """Mutable state used while parsing markdown into notebook cells."""

    lines: List[str]
    index: int = 0
    current_cell_lines: List[str] = field(default_factory=list)
    current_cell_type: str = "markdown"
    current_language: str = "python"
    waiting_for_marker: bool = False
    explicit_markdown_cell: bool = False
    directive_fence_depth: int = 0
    directive_fence_lengths: List[int] = field(default_factory=list)  # Track fence lengths for proper nesting


def expand_includes(content: str, base_path: Path, max_depth: int = 10) -> str:
    """Expand MyST include directives in markdown content.

    This function recursively replaces ```{include} path``` directives
    with the content of the included files. This ensures that notebook
    conversions include all necessary setup code and context.

    Args:
        content: The markdown content to process
        base_path: Base directory for resolving relative include paths
        max_depth: Maximum recursion depth to prevent infinite loops

    Returns:
        Content with include directives expanded
    """
    if max_depth <= 0:
        return content

    def replace_include(match: re.Match) -> str:
        include_path_str = match.group(1).strip()
        resolved_path = (base_path / include_path_str).resolve()
        try:
            if not resolved_path.exists():
                logger.warning(f"Include file not found: {resolved_path}")
                return match.group(0)
            included_content = resolved_path.read_text(encoding="utf-8")
            # Recursively expand includes in the included file
            return expand_includes(included_content, resolved_path.parent, max_depth - 1)
        except Exception as e:
            logger.warning(f"Failed to read include file {resolved_path}: {e}")
            return match.group(0)

    return RE_INCLUDE_DIRECTIVE.sub(replace_include, content)


def expand_includes_in_text(content: str, md_path: Path) -> str:
    """Expand {include} directives in raw markdown text.

    Convenience wrapper around expand_includes() that takes a source file path
    instead of a base directory.  Runs before cell parsing so that code fences
    inside included files are properly converted to code cells rather than left
    as markdown text.

    Args:
        content: Raw markdown text
        md_path: Path to the source markdown file (used to resolve relative paths)

    Returns:
        Markdown text with {include} blocks replaced by file contents
    """
    return expand_includes(content, md_path.parent)


def strip_myst_directives(content: str) -> str:
    """Strip MyST-specific directives that don't work in Jupyter notebooks.

    Removes or converts MyST syntax to make notebooks more user-friendly:
    - Admonition directive fences (:::{tip}, :::{note}, etc.) - keeps content
    - Empty cross-references ([](ref)) - removes entirely
    - MyST labels ((label)=) - removes entirely
    - Code directive fences (```{directive}) - removes (content handled elsewhere)

    Args:
        content: Markdown content with potential MyST directives

    Returns:
        Content with MyST directives stripped
    """
    # Remove empty cross-references like [](reference-name)
    content = RE_EMPTY_XREF.sub("", content)

    # Remove MyST labels like (label-name)=
    content = RE_LABEL.sub("", content)

    # Remove admonition directive fences but keep the content
    # This handles :::{tip}, :::{note}, :::{warning}, etc.
    content = RE_ADMONITION_OPEN.sub("", content)
    content = RE_ADMONITION_CLOSE.sub("", content)

    # Remove code directive fences (but not regular code fences)
    # These are things like ```{literalinclude} that won't work in notebooks
    content = RE_CODE_DIRECTIVE_FENCE.sub("", content)

    return content


class MarkdownToNotebookConverter:
    """Convert Markdown files to Jupyter notebooks with nemo-nb markers."""

    def __init__(self):
        """Initialize the converter."""
        self.cells: List[Cell] = []
        self.indent_level = 0
        self.in_tab_set = False
        self.in_dropdown = False
        self.multi_cell_groups: List[Tuple[str, int]] = []  # (group_id, spaces)
        self.in_output_cell = False
        self.output_cell_type = "stream"
        self.output_cell_name = "stdout"
        self.fence_conversion_disabled = False  # Controls automatic fence-to-code-cell conversion

    def convert(self, md_path: Path, strip_myst: bool = False) -> Dict:
        """Convert a markdown file to a notebook dictionary.

        Args:
            md_path: Path to markdown file
            strip_myst: If True, strip MyST directives for standalone notebooks.
                       If False (default), keep directives for Sphinx processing.

        Returns:
            Notebook dictionary ready to be serialized to JSON
        """
        content = md_path.read_text(encoding="utf-8")
        self.cells = []
        self.fence_conversion_disabled = False

        # Expand {include} directives before parsing so that code fences inside
        # included snippets are processed as code cells, not markdown text.
        content = expand_includes(content, md_path.parent)

        # Strip MyST directives only for standalone notebooks (download)
        # Keep them for Sphinx processing (HTML docs need them)
        if strip_myst:
            content = strip_myst_directives(content)

        # Check if disable-fence-conversion marker is present anywhere in the document
        self._check_disable_fence_conversion(content)

        self._parse_markdown_with_context(content)

        # Ensure the process marker is present in the first cell
        self._ensure_process_marker()

        return self._create_notebook_dict()

    def _ensure_process_marker(self) -> None:
        """Ensure the @nemo-nb: process marker is present in the first cell."""
        if not self.cells:
            # If no cells, add a markdown cell with the marker
            self.cells.append(Cell(cell_type="markdown", source=["<!-- @nemo-nb: process -->"]))
            return

        first_cell = self.cells[0]
        marker_present = False

        # Check if marker is already in the first cell
        for line in first_cell.source:
            if "@nemo-nb: process" in line:
                marker_present = True
                break

        if not marker_present:
            # Add marker to the beginning of the first cell
            if first_cell.cell_type == "markdown":
                first_cell.source.insert(0, "<!-- @nemo-nb: process -->\n")
            else:
                comment_char = first_cell.get_comment_char()
                first_cell.source.insert(0, f"{comment_char} @nemo-nb: process\n")

    def _check_disable_fence_conversion(self, content: str) -> None:
        """Check if disable-fence-conversion marker is present in the document.

        This is a document-wide setting that disables automatic conversion
        of triple-backtick fenced code blocks to code cells.

        Args:
            content: Markdown content as string
        """
        if RE_DISABLE_FENCE.search(content):
            self.fence_conversion_disabled = True

    def _parse_markdown_with_context(self, content: str) -> None:
        """Parse markdown content using cell markers and fenced code blocks."""
        state = ParseState(lines=content.split("\n"))

        while state.index < len(state.lines):
            line = state.lines[state.index]

            if self._handle_directive_fence_line(line, state):
                continue
            if self._handle_cell_marker_line(line, state):
                continue
            if self._handle_code_fence_line(line, state):
                continue
            if self._handle_output_marker_line(line, state):
                continue

            self._append_regular_line(line, state)
            state.index += 1

        self._save_current_cell(
            state.current_cell_lines,
            state.current_cell_type,
            state.current_language,
            state.waiting_for_marker,
        )

    def _handle_directive_fence_line(self, line: str, state: ParseState) -> bool:
        """Handle ```{directive} fences so we don't treat them as code cells.

        Properly handles nested fences by tracking the fence delimiter length.
        Only closes a directive fence when we see a fence with matching or greater length.
        """
        directive_open = RE_DIRECTIVE_FENCE_OPEN.match(line)
        if directive_open:
            # Track the fence length (number of backticks) for proper nesting
            fence_delimiter = directive_open.group(2)
            fence_length = len(fence_delimiter)
            state.directive_fence_lengths.append(fence_length)
            state.directive_fence_depth += 1
            state.current_cell_lines.append(line)
            state.index += 1
            return True

        # Check if this could be a closing fence for a directive
        if state.directive_fence_depth > 0:
            close_match = RE_DIRECTIVE_FENCE_CLOSE.match(line)
            if close_match:
                # Count the backticks in this closing fence
                fence_length = len(line.strip())
                # Get the expected fence length for the current directive level
                expected_length = state.directive_fence_lengths[-1] if state.directive_fence_lengths else 3

                # Only close if fence length matches or exceeds the opening fence
                if fence_length >= expected_length:
                    state.directive_fence_depth = max(state.directive_fence_depth - 1, 0)
                    if state.directive_fence_lengths:
                        state.directive_fence_lengths.pop()
                    state.current_cell_lines.append(line)
                    state.index += 1
                    return True

        return False

    def _handle_cell_marker_line(self, line: str, state: ParseState) -> bool:
        """Handle <!-- @nemo-nb: cell ... --> markers."""
        cell_match = RE_CELL_MARKER.search(line)
        if not cell_match:
            return False

        self._save_current_cell(
            state.current_cell_lines,
            state.current_cell_type,
            state.current_language,
            state.waiting_for_marker,
        )

        language = cell_match.group(1)
        state.current_cell_lines = []
        state.waiting_for_marker = False

        if language == "markdown":
            state.current_cell_type = "markdown"
            state.explicit_markdown_cell = True
        else:
            state.current_cell_type = "code"
            state.current_language = language
            state.explicit_markdown_cell = False

        state.index += 1
        return True

    def _handle_code_fence_line(self, line: str, state: ParseState) -> bool:
        """Handle fenced code blocks (```lang)."""
        fence_match = RE_CODE_FENCE.match(line)
        if not fence_match:
            return False

        if (
            state.directive_fence_depth > 0
            or state.explicit_markdown_cell
            or state.waiting_for_marker
            or self.fence_conversion_disabled
        ):
            return False

        indentation = fence_match.group(1)
        fence_delimiter = fence_match.group(2)
        language = fence_match.group(3)  # empty string when no language is specified

        if "\t" in indentation:
            raise ValueError("Code block start fence contains tabs, which is not allowed.")

        self._save_current_cell(state.current_cell_lines, state.current_cell_type, state.current_language, False)
        code_lines, next_index = self._extract_fenced_code_block(state.lines, state.index, fence_delimiter)
        code_lines = self._remove_code_block_indentation(code_lines, indentation)

        if code_lines:
            leading_whitespace_match = RE_LEADING_WHITESPACE.match(code_lines[0])
            if leading_whitespace_match and "\t" in leading_whitespace_match.group(1):
                raise ValueError("First line of code block contains tabs, which is not allowed.")

        cell_type_override = FENCE_LANGUAGE_TO_CELL_TYPE.get(language)
        if cell_type_override == "raw":
            self._add_raw_cell(code_lines, language, indentation)
        else:
            self._add_code_cell(code_lines, language or "python", indentation)

        state.current_cell_lines = []
        state.current_cell_type = "markdown"
        state.current_language = "python"
        state.explicit_markdown_cell = False
        state.waiting_for_marker = False
        state.index = next_index
        return True

    def _handle_output_marker_line(self, line: str, state: ParseState) -> bool:
        """Handle <!-- @nemo-nb: output --> markers."""
        output_match = RE_OUTPUT_MARKER.search(line)
        if not output_match:
            return False

        state.index = self._handle_output_marker(
            output_match,
            state.lines,
            state.index,
            state.current_cell_lines,
            state.current_cell_type,
            state.current_language,
            state.waiting_for_marker,
        )

        state.current_cell_lines = []
        state.current_cell_type = "markdown"
        state.waiting_for_marker = False
        state.explicit_markdown_cell = False
        return True

    def _append_regular_line(self, line: str, state: ParseState) -> None:
        """Append a normal markdown line to the current cell buffer."""
        if not state.waiting_for_marker:
            state.current_cell_lines.append(line)
            return

        if line.strip():
            state.current_cell_type = "markdown"
            state.waiting_for_marker = False
            state.current_cell_lines.append(line)

    def _save_current_cell(self, cell_lines: List[str], cell_type: str, language: str, skip: bool) -> None:
        """Save the current accumulated cell if it has content.

        Args:
            cell_lines: Accumulated lines for the cell
            cell_type: Type of cell ('code' or 'markdown')
            language: Programming language for code cells
            skip: If True, don't save the cell
        """
        if not cell_lines or skip:
            return

        # Check if we should preserve a trailing blank line
        # (e.g., if the last line is a directive option like :sync:)
        should_preserve_blank = False
        if cell_type == "markdown" and cell_lines:
            # Find last non-empty line
            last_content_idx = -1
            for i in range(len(cell_lines) - 1, -1, -1):
                if cell_lines[i].strip():
                    last_content_idx = i
                    break

            if last_content_idx >= 0:
                # Check for directive option pattern (e.g., :sync: val)
                if RE_DIRECTIVE_OPTION.match(cell_lines[last_content_idx]):
                    # Only preserve if there WAS a blank line to begin with
                    if len(cell_lines) > last_content_idx + 1:
                        should_preserve_blank = True

        # Remove trailing newline before marker
        cell_lines = self._strip_trailing_empty_lines(cell_lines)

        if should_preserve_blank:
            cell_lines.append("")
        # Assertion: after stripping, if original had content, we should have valid list
        assert isinstance(cell_lines, list), "cell_lines must be a list"

        if not cell_lines:
            return

        # Validate cell_type to prevent silent failures
        if cell_type not in ("markdown", "code"):
            raise ValueError(f"Invalid cell_type: {cell_type!r}. Expected 'markdown' or 'code'.")

        if cell_type == "markdown":
            self._add_markdown_cell(cell_lines)
        elif cell_type == "code":
            self._add_code_cell(cell_lines, language)

    def _handle_output_marker(
        self,
        output_match,
        lines: List[str],
        current_index: int,
        current_cell_lines: List[str],
        current_cell_type: str,
        current_language: str,
        waiting_for_marker: bool,
    ) -> int:
        """Handle output marker and extract output content.

        Args:
            output_match: Regex match object for output marker
            lines: All lines in the document
            current_index: Current line index
            current_cell_lines: Accumulated lines for current cell
            current_cell_type: Type of current cell
            current_language: Current code cell language
            waiting_for_marker: Whether we're waiting for a marker

        Returns:
            New line index after processing output
        """
        # Save accumulated code cell content
        if current_cell_lines and not waiting_for_marker:
            # Strip trailing empty line if present
            current_cell_lines = self._strip_trailing_empty_lines(current_cell_lines)

            if current_cell_type == "code":
                self._add_code_cell(current_cell_lines, current_language)
            elif current_cell_type == "markdown":
                self._add_markdown_cell(current_cell_lines)

        # Parse output type and name
        output_type = output_match.group(1) if output_match.group(1) else "stream"
        output_name = output_match.group(2) if output_match.group(2) else "stdout"

        # Collect output content
        i = current_index + 1
        output_lines = self._collect_output_lines(lines, i, output_type)

        # Update index
        i += len(output_lines)

        # Remove leading and trailing empty lines
        output_lines = self._strip_empty_lines(output_lines)

        # Attach output to previous code cell
        if output_lines:
            self._add_output_to_previous_cell(output_lines, output_type, output_name)

        return i

    def _collect_output_lines(self, lines: List[str], start_index: int, output_type: str) -> List[str]:
        """Collect output lines until next marker, fence, or appropriate stopping point.

        Args:
            lines: All lines in the document
            start_index: Starting line index
            output_type: Type of output (affects stopping conditions)

        Returns:
            List of output lines
        """
        output_lines = []
        found_content = False

        for line in lines[start_index:]:
            # Check stopping conditions
            if self._should_stop_collecting_output(line, output_lines, output_type, found_content):
                break

            # Track if we've seen non-empty content
            if line.strip():
                found_content = True
            output_lines.append(line)

        return output_lines

    def _should_stop_collecting_output(
        self, line: str, output_lines: List[str], output_type: str, found_content: bool
    ) -> bool:
        """Determine if we should stop collecting output lines.

        Args:
            line: Current line to check
            output_lines: Lines collected so far
            output_type: Type of output
            found_content: Whether we've seen non-empty content

        Returns:
            True if we should stop collecting
        """
        # Check if we hit another marker
        if RE_STOP_MARKER.search(line):
            return True

        # Check if we hit a code fence
        if RE_CODE_FENCE_START.match(line):
            return True

        # Check if we hit a markdown heading after blank line
        if found_content and output_lines and not output_lines[-1].strip():
            if RE_HEADING.match(line):
                return True

        # For error outputs, don't stop at blank lines (tracebacks can have them)
        # For other outputs, stop at blank line after content
        if output_type != "error" and found_content and not line.strip():
            return True

        return False

    def _strip_leading_empty_lines(self, lines: List[str]) -> List[str]:
        """Remove leading empty lines using functional approach.

        Args:
            lines: Lines to strip

        Returns:
            New list with leading empty lines removed
        """
        start_idx = 0
        while start_idx < len(lines) and not lines[start_idx].strip():
            start_idx += 1
        result = lines[start_idx:]
        # Assertion: if we had lines to begin with and found content, result should not be empty
        assert not lines or len(result) >= 0, "Strip leading should never produce negative length"
        return result

    def _strip_trailing_empty_lines(self, lines: List[str]) -> List[str]:
        """Remove trailing empty lines using functional approach.

        Args:
            lines: Lines to strip

        Returns:
            New list with trailing empty lines removed
        """
        end_idx = len(lines)
        while end_idx > 0 and not lines[end_idx - 1].strip():
            end_idx -= 1
        result = lines[:end_idx]
        # Assertion: result length should never exceed original
        assert len(result) <= len(lines), "Strip trailing should never increase length"
        return result

    def _strip_empty_lines(self, lines: List[str]) -> List[str]:
        """Remove leading and trailing empty lines using functional approach.

        Args:
            lines: Lines to strip

        Returns:
            New list with empty lines removed from start and end
        """
        # Use functional approach: find start and end indices
        start_idx = 0
        while start_idx < len(lines) and not lines[start_idx].strip():
            start_idx += 1

        end_idx = len(lines)
        while end_idx > start_idx and not lines[end_idx - 1].strip():
            end_idx -= 1

        result = lines[start_idx:end_idx]
        # Assertion: result should never be longer than input
        assert len(result) <= len(lines), "Stripped list should not be longer than original"
        return result

    def _extract_fenced_code_block(
        self, lines: List[str], start: int, fence_delimiter: str = "```"
    ) -> Tuple[List[str], int]:
        """Extract code block content from fenced block.

        Args:
            lines: All lines in the document
            start: Starting index (line with opening fence)
            fence_delimiter: The fence delimiter to look for (e.g., "```" or "````")

        Returns:
            Tuple of (code_lines, next_index_after_closing_fence)
        """
        code_lines = []

        # Dynamic pattern: must match the exact fence delimiter (e.g., ``` or ````)
        fence_pattern = re.compile(rf"^{re.escape(fence_delimiter)}\s*$")

        # Collect lines until closing fence (skip opening fence at start)
        for i, current_line in enumerate(lines[start + 1 :], start=start + 1):
            if fence_pattern.match(current_line.lstrip()):
                # Found closing fence with same delimiter
                return code_lines, i + 1
            code_lines.append(current_line)

        # No closing fence found - treat rest as code
        return code_lines, len(lines)

    def _remove_code_block_indentation(self, lines: List[str], indentation: str) -> List[str]:
        """Remove shared indentation introduced by list nesting from code lines."""
        if not indentation:
            return lines

        indent_len = len(indentation)
        if indent_len == 0:
            return lines

        dedented_lines = []
        for line in lines:
            if line.startswith(indentation):
                dedented_lines.append(line[indent_len:])
            else:
                # Remove up to indent_len leading spaces if present
                strip_count = 0
                while strip_count < indent_len and strip_count < len(line) and line[strip_count] == " ":
                    strip_count += 1
                dedented_lines.append(line[strip_count:])
        return dedented_lines

    def _add_markdown_cell(self, lines: List[str]) -> None:
        """Add a markdown cell from accumulated lines.

        Args:
            lines: Lines of markdown content
        """
        if not lines:
            return

        # Strip leading blank lines
        lines = self._strip_leading_empty_lines(lines)
        # Assertion: stripped lines should still be a list
        assert isinstance(lines, list), "lines must be a list after stripping"

        if not lines:
            return

        # Add newline to each line for notebook format
        source = [line + "\n" for line in lines]
        # Last line shouldn't have newline
        if source:
            source[-1] = source[-1].rstrip("\n")

        cell = Cell(cell_type="markdown", source=source)
        self.cells.append(cell)

    def _add_code_cell(self, lines: List[str], language: str, indentation: str = "") -> None:
        """Add a code cell from code block.

        Args:
            lines: Lines of code
            language: Programming language
            indentation: Original indentation of the code block fence
        """
        if not lines:
            return

        # Add indentation marker if present
        if indentation:
            spaces = len(indentation)
            # Use # for python and shell comments
            # Note: For languages that don't support # comments, this might be visible
            # but nemo-nb is primarily for Python-based docs.
            # The converter will strip this line.
            marker = f"# @nemo-nb: indent-space {spaces}"
            lines.insert(0, marker)

        # Add newline to each line for notebook format
        source = [line + "\n" for line in lines]
        # Last line shouldn't have newline
        if source:
            source[-1] = source[-1].rstrip("\n")

        # Determine the language metadata
        metadata = {}
        if language and language != "python":
            metadata["language"] = language

        # Handle special languages that need vscode languageId
        if language in ["bash", "sh", "shell"]:
            metadata["vscode"] = {"languageId": "shellscript"}
            metadata["language"] = language
        elif language == "jsonc":
            metadata["vscode"] = {"languageId": "jsonc"}

        cell = Cell(cell_type="code", source=source, metadata=metadata)
        self.cells.append(cell)

    def _add_raw_cell(self, lines: List[str], language: str, indentation: str = "") -> None:
        """Add a raw cell from a code block.

        Raw cells are not executed and not rendered as markdown; Jupyter
        displays their content as-is.  Used for non-runnable fence languages
        such as ``text`` (ASCII diagrams) and ``yaml`` (config snippets).

        The original fence language is stored in cell metadata so the
        notebook→markdown converter can reconstruct the correct code fence
        for HTML rendering.  The original list-nesting indentation is stored
        under the ``indent-space`` metadata key so the converter can restore
        the fence to its original indented position on round-trip.

        Args:
            lines: Lines of content
            language: Original fence language identifier (e.g. "text", "yaml")
            indentation: Leading whitespace of the opening code fence (for list nesting)
        """
        if not lines:
            return

        source = [line + "\n" for line in lines]
        if source:
            source[-1] = source[-1].rstrip("\n")

        metadata: dict = {"language": language}
        if indentation:
            metadata["indent-space"] = len(indentation)

        cell = Cell(cell_type="raw", source=source, metadata=metadata)
        self.cells.append(cell)

    def _add_output_to_previous_cell(self, lines: List[str], output_type: str, output_name: str) -> None:
        """Add output to the previous code cell.

        Args:
            lines: Output content lines
            output_type: Type of output (stream, execute_result, display_data, error)
            output_name: Name of output stream (stdout, stderr)
        """
        if not self.cells or self.cells[-1].cell_type != "code":
            # No previous code cell to attach output to, skip
            return

        # Format output based on type
        if output_type == "stream":
            output = {"output_type": "stream", "name": output_name, "text": [line + "\n" for line in lines]}
        elif output_type == "execute_result":
            output = {
                "output_type": "execute_result",
                "data": {"text/plain": [line + "\n" for line in lines]},
                "execution_count": None,
                "metadata": {},
            }
        elif output_type == "display_data":
            output = {
                "output_type": "display_data",
                "data": {"text/plain": [line + "\n" for line in lines]},
                "metadata": {},
            }
        elif output_type == "error":
            # Group traceback lines into 4 items to match Jupyter's structure:
            # - Item 0: Separator line
            # - Item 1: Error type and "Traceback" header
            # - Item 2: Code context (may span multiple lines with embedded newlines)
            # - Item 3: Final error message
            traceback_items = []
            if len(lines) >= 1:
                # Item 0: First line (separator)
                traceback_items.append(lines[0])
            if len(lines) >= 2:
                # Item 1: Second line (error header)
                traceback_items.append(lines[1])
            if len(lines) >= 4:
                # Item 2: Middle lines (code context) - join all but first 2 and last
                middle_lines = lines[2:-1]
                # Remove trailing empty lines from middle section
                middle_lines = self._strip_trailing_empty_lines(middle_lines)
                # Assertion: middle_lines should be a list
                assert isinstance(middle_lines, list), "middle_lines must be a list"
                # Join with newline and add trailing newline
                traceback_items.append("\n".join(middle_lines) + "\n")
            if len(lines) >= 3:
                # Item 3: Last line (final error message)
                traceback_items.append(lines[-1])

            output = {
                "output_type": "error",
                "ename": "Error",
                "evalue": "",
                "traceback": traceback_items,
            }
        else:
            # Default to stream
            output = {"output_type": "stream", "name": "stdout", "text": [line + "\n" for line in lines]}

        # Add output to the previous code cell
        self.cells[-1].outputs.append(output)

    def _create_notebook_dict(self) -> Dict:
        """Create a notebook dictionary from cells.

        Returns:
            Notebook dictionary ready for JSON serialization
        """
        nb_cells = []

        for cell in self.cells:
            nb_cell = {
                "cell_type": cell.cell_type,
                "metadata": cell.metadata,
                "source": cell.source,
            }

            if cell.cell_type == "code":
                nb_cell["outputs"] = cell.outputs
                nb_cell["execution_count"] = cell.execution_count

            nb_cells.append(nb_cell)

        notebook = {
            "cells": nb_cells,
            "metadata": {
                "kernelspec": {
                    "display_name": "Python 3",
                    "language": "python",
                    "name": "python3",
                },
                "language_info": {
                    "codemirror_mode": {"name": "ipython", "version": 3},
                    "file_extension": ".py",
                    "mimetype": "text/x-python",
                    "name": "python",
                    "nbconvert_exporter": "python",
                    "pygments_lexer": "ipython3",
                    "version": "3.8.0",
                },
            },
            "nbformat": 4,
            "nbformat_minor": 4,
        }

        return notebook

    def write_notebook(self, notebook: Dict, output_path: Path) -> None:
        """Write notebook dictionary to a file.

        Args:
            notebook: Notebook dictionary
            output_path: Output file path
        """
        output_path.write_text(json.dumps(notebook, indent=1), encoding="utf-8")
