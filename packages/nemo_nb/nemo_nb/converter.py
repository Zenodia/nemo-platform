# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Notebook to Markdown converter with marker-based commands.

Conversion rules:
1. Markdown cells → passthrough (preserves directives)
2. Code cells → ```{language}\n{code}\n```
3. Outputs → stripped (removed before processing)
4. Marker commands → processed and removed from output

Marker syntax:
- # @nemo-nb: COMMAND (code cells)
- // @nemo-nb: COMMAND (code cells, alternative)
- <!-- @nemo-nb: COMMAND --> (markdown cells)

Supported commands:
- hide: Hide the cell
- wrap-cell-start <directive>: Start wrapping with exact directive syntax
- wrap-cell-end <closing>: End wrapping with exact closing syntax
- insert <text>: Insert literal line at position
- download: Insert a download link to the notebook at position
- insert-code-block-start <options>: Convert code cell to {code-block} directive with options
- multi-cell-indent-space-start <id> <number>: Start multi-cell block with space indentation
- multi-cell-indent-space-end <id>: End multi-cell block with space indentation
- multi-cell-indent-tab-start <id> <number>: Start multi-cell block with tab indentation
- multi-cell-indent-tab-end <id>: End multi-cell block with tab indentation
- indent-space <number>: Indent content by X spaces
- indent-tab <number>: Indent content by X tabs
- language <lang>: Override the language in the code fence
- notebook-convert-4-space-to-tab: Notebook-wide setting to convert 4 spaces to tabs in final output
"""

import json
import re
from dataclasses import replace
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from .markers import CommandInterpreter, MarkerParser
from .structures import CellInput, CellMetadata, GroupMarkers, ProcessingResult, ProcessingState

# --- Regex patterns for MyST directive detection ---
# MyST directives use 3-5 colons (e.g., :::{note}, ::::{tab-set}, :::::{dropdown})
RE_DIRECTIVE_OPEN = re.compile(r":::+\{([^}]+)\}")  # Matches :::{directive} and captures name
RE_DIRECTIVE_CLOSE = re.compile(r"^:::+$")  # Matches standalone ::: closing markers
RE_CODE_FENCE = re.compile(r"^(\s*)```")  # Matches code fence with optional leading whitespace

# Patterns for detecting directive markers at content boundaries (for smart spacing)
RE_DIRECTIVE_END = re.compile(r":::+\{[^}]+\}$|```\{[^}]+\}$")  # Directive at end of content
RE_DIRECTIVE_START = re.compile(r"^:::+\{[^}]+\}|^```\{[^}]+\}")

# Notebook variant suffixes for split download links
NOTEBOOK_SUFFIX_PYTHON = "-python"
NOTEBOOK_SUFFIX_CLI = "-cli"


class NotebookConverter:
    """Convert Jupyter notebooks to Markdown."""

    def __init__(self, config: Optional[Dict] = None):
        """Initialize converter with configuration.

        Args:
            config: Optional configuration dict from Sphinx conf.py
        """
        self.config = config or {}
        self.parser = MarkerParser()
        self.interpreter = CommandInterpreter()
        self.current_notebook_path: Optional[Path] = None

    def convert(self, notebook_path: Path) -> str:
        """Convert notebook file to markdown string.

        Args:
            notebook_path: Path to .ipynb file

        Returns:
            Markdown string with converted content
        """
        self.current_notebook_path = notebook_path
        nb = json.loads(notebook_path.read_text())
        nb = self._strip_outputs(nb)
        return self.convert_notebook_dict(nb)

    def convert_from_dict(self, notebook_dict: Dict, notebook_path: Path) -> str:
        """Convert a pre-processed notebook dict to markdown string.

        Like convert(), but accepts a pre-processed notebook dict instead of
        loading from disk. Use this when you need to transform the notebook
        before conversion (e.g. expanding include directives).

        Args:
            notebook_dict: Notebook dictionary (will have outputs stripped)
            notebook_path: Path to the source notebook file (used to set
                current_notebook_path for any path-relative operations)

        Returns:
            Markdown string with converted content
        """
        self.current_notebook_path = notebook_path
        nb = self._strip_outputs(notebook_dict)
        return self.convert_notebook_dict(nb)

    def convert_notebook_dict(self, notebook: Dict) -> str:
        """Convert notebook dictionary to markdown string.

        Args:
            notebook: Parsed notebook JSON as dict

        Returns:
            Markdown string with converted content
        """
        cells = notebook.get("cells", [])

        # Check if notebook-convert-4-space-to-tab is enabled in any cell
        use_tab_indent = self._check_notebook_convert_4_space_to_tab(cells)

        # Process cells with context-aware indentation and marker commands
        processed_cells = self._process_cells_with_context(cells)

        # Join cells with smart spacing (avoid extra blank lines at directive boundaries)
        result = self._join_cells_with_smart_spacing(processed_cells)

        # Apply notebook-wide postprocessing if enabled
        if use_tab_indent:
            result = self._postprocess_spaces_to_tabs(result)

        return result

    def _process_cells_with_context(self, cells: List[Dict]) -> List[str]:
        """Process cells with context-aware indentation and marker commands.

        Handles:
        - Marker command parsing and processing
        - Multi-cell grouping (including tab-sets)
        - Directive context tracking for indentation

        Args:
            cells: List of cell dictionaries

        Returns:
            List of markdown strings with proper indentation
        """
        result = []
        state = ProcessingState()

        for cell in cells:
            meta = CellMetadata(cell)

            # Get raw cell content
            cell_content = "".join(cell.get("source", []))
            cell_type = cell.get("cell_type", "")

            # Parse markers from cell content
            cleaned_content, commands = self.parser.parse_cell(cell_content, cell_type)

            # Check if cell should be hidden (metadata or marker)
            if meta.should_hide() or self.interpreter.should_hide(commands):
                continue

            # Create cell input
            cell_input = CellInput(
                content=cleaned_content,
                commands=commands,
                cell_type=cell_type,
                meta=meta if cell_type in ("code", "raw") else None,
            )

            # Detect group markers
            markers = GroupMarkers(
                end_info=self._detect_group_end_info(commands, state.active_group),
                end_at_start=self._is_group_end_at_start(commands),
                start_info=self._detect_group_start_info(commands),
                start_at_start=self._is_group_start_at_start(commands),
            )

            # Process cell based on type
            if cell_type == "markdown":
                processing_result = self._process_markdown_cell(cell_input, markers, state)
            elif cell_type == "code":
                processing_result = self._process_code_cell(cell_input, markers, state)
            elif cell_type == "raw":
                processing_result = self._process_raw_cell(cell_input, state)
            else:
                continue

            # Update state and result
            state = processing_result.state
            result.extend(processing_result.output)

        # Handle unclosed group (shouldn't happen, but be safe)
        if state.active_group and state.group_cells:
            group_md = self._close_active_group(state.group_cells, state.active_group)
            result.append(group_md)

        return result

    def _process_markdown_cell(
        self, cell: CellInput, markers: GroupMarkers, state: ProcessingState
    ) -> ProcessingResult:
        """Process a markdown cell with group markers.

        Args:
            cell: Cell input data
            markers: Detected group markers
            state: Current processing state

        Returns:
            ProcessingResult with updated state and output
        """
        # Strip blank lines if no insert or download commands
        content = cell.content
        has_inserts = any(cmd.command == "insert" for cmd in cell.commands)
        has_downloads = any(cmd.command == "download" for cmd in cell.commands)
        if not has_inserts and not has_downloads:
            content = self._strip_blank_lines(content)

        # Handle group end marker
        if markers.end_info:
            return self._handle_markdown_group_end(replace(cell, content=content), markers, state)

        # Handle group start in middle of cell
        if markers.start_info and not markers.start_at_start:
            return self._handle_markdown_group_start_middle(replace(cell, content=content), markers, state)

        # Normal processing - marker at start or no marker
        new_state = state.copy()
        output = []

        if markers.start_info and markers.start_at_start:
            new_state.active_group = markers.start_info
            new_state.group_cells = []

        new_state.directive_stack = self._update_directive_stack(content, new_state.directive_stack)
        cell_md = self._apply_cell_transformations(content, cell.commands)

        if new_state.active_group and markers.start_at_start:
            if cell_md:
                new_state.group_cells.append(cell_md)
        elif not new_state.active_group:
            if cell_md:
                output.append(cell_md)

        return ProcessingResult(state=new_state, output=output)

    def _handle_markdown_group_end(
        self, cell: CellInput, markers: GroupMarkers, state: ProcessingState
    ) -> ProcessingResult:
        """Handle group end marker in markdown cell.

        Args:
            cell: Cell input data
            markers: Detected group markers
            state: Current processing state

        Returns:
            ProcessingResult with updated state and output
        """
        new_state = state.copy()
        output = []

        if markers.end_at_start:
            # Check for insert commands that appear before the end marker in the commands list
            # These should be processed as part of the group before closing it
            insert_commands_before_end = []
            end_marker_index = len(cell.commands)
            for i, cmd in enumerate(cell.commands):
                if cmd.command in ["multi-cell-indent-space-end", "multi-cell-indent-tab-end"]:
                    end_marker_index = i
                    break
            for i, cmd in enumerate(cell.commands):
                if cmd.command == "insert" and i < end_marker_index:
                    insert_commands_before_end.append(cmd)

            # If there are inserts before the end marker, process them as part of the group
            if insert_commands_before_end:
                # Build content from insert commands
                insert_content_lines = []
                for cmd in insert_commands_before_end:
                    insert_text = " ".join(cmd.args)
                    insert_content_lines.append(insert_text)
                insert_content = "\n".join(insert_content_lines)
                if insert_content.strip():
                    new_state.group_cells.append(insert_content)

            # Close the active group
            group_md = self._close_active_group(new_state.group_cells, new_state.active_group)
            output.append(group_md)
            new_state.active_group = None
            new_state.group_cells = []

            # Check if there's a group start marker after the end
            if markers.start_info:
                return self._handle_end_then_start_markers(cell, markers, new_state, output)
            else:
                # No group start, process the rest normally
                # Filter out insert commands that were already processed
                remaining_commands = [
                    cmd for i, cmd in enumerate(cell.commands) if cmd.command != "insert" or i >= end_marker_index
                ]
                if cell.content.strip():
                    content_to_process = cell.content
                    has_remaining_inserts = any(cmd.command == "insert" for cmd in remaining_commands)
                    if not has_remaining_inserts:
                        content_to_process = self._strip_blank_lines(content_to_process)

                    new_state.directive_stack = self._update_directive_stack(
                        content_to_process, new_state.directive_stack
                    )
                    cell_md = self._apply_cell_transformations(content_to_process, remaining_commands)
                    if cell_md:
                        output.append(cell_md)
        else:
            # End marker in middle: split content
            marker_position, pre_marker_lines, post_marker_lines = self._split_content_at_marker(
                cell.content, cell.commands, ["multi-cell-indent-space-end", "multi-cell-indent-tab-end"]
            )

            # Process pre-marker content
            pre_marker_md = self._process_pre_marker_content(pre_marker_lines, cell.commands, marker_position)
            if pre_marker_md and pre_marker_md.strip():
                new_state.directive_stack = self._update_directive_stack(pre_marker_md, new_state.directive_stack)
                new_state.group_cells.append(pre_marker_md)

            # Close the group
            group_md = self._close_active_group(new_state.group_cells, new_state.active_group)
            output.append(group_md)
            new_state.active_group = None
            new_state.group_cells = []

            # Process post-marker content
            post_marker_md = self._process_post_marker_content(post_marker_lines, cell.commands, marker_position)
            if post_marker_md.strip():
                new_state.directive_stack = self._update_directive_stack(post_marker_md, new_state.directive_stack)
                post_marker_md = self._apply_cell_transformations(post_marker_md, cell.commands)
                if post_marker_md:
                    output.append(post_marker_md)

        return ProcessingResult(state=new_state, output=output)

    def _handle_end_then_start_markers(
        self, cell: CellInput, markers: GroupMarkers, state: ProcessingState, existing_output: List[str]
    ) -> ProcessingResult:
        """Handle case where group end and start markers are in same cell.

        Args:
            cell: Cell input data
            markers: Detected group markers
            state: Current processing state (after group end)
            existing_output: Output accumulated so far

        Returns:
            ProcessingResult with updated state and output
        """
        new_state = state.copy()
        output = existing_output.copy()

        if not markers.start_at_start:
            # Group start is in the middle - split content
            marker_position, pre_marker_lines, post_marker_lines = self._split_content_at_marker(
                cell.content, cell.commands, ["multi-cell-indent-space-start", "multi-cell-indent-tab-start"]
            )

            # Process pre-marker content
            pre_marker_md = self._process_pre_marker_content(pre_marker_lines, cell.commands, marker_position)
            if pre_marker_md:
                new_state.directive_stack = self._update_directive_stack(pre_marker_md, new_state.directive_stack)
                output.append(pre_marker_md)

            # Process post-marker content (will be in new group)
            post_marker_md = self._process_post_marker_content(post_marker_lines, cell.commands, marker_position)
            new_state.directive_stack = self._update_directive_stack(post_marker_md, new_state.directive_stack)

            # Initialize new group
            new_state.active_group = markers.start_info
            new_state.group_cells = [post_marker_md] if post_marker_md.strip() else []
        else:
            # Group start is at the beginning (right after end marker)
            new_state.active_group = markers.start_info
            new_state.group_cells = []

            # Process content normally and add to new group
            if cell.content.strip():
                new_state.directive_stack = self._update_directive_stack(cell.content, new_state.directive_stack)
                cell_md = self._apply_cell_transformations(cell.content, cell.commands)
                if cell_md:
                    new_state.group_cells.append(cell_md)

        return ProcessingResult(state=new_state, output=output)

    def _handle_markdown_group_start_middle(
        self, cell: CellInput, markers: GroupMarkers, state: ProcessingState
    ) -> ProcessingResult:
        """Handle case where group start marker is in middle of cell.

        Args:
            cell: Cell input data
            markers: Detected group markers
            state: Current processing state

        Returns:
            ProcessingResult with updated state and output
        """
        new_state = state.copy()
        output = []

        marker_position, pre_marker_lines, post_marker_lines = self._split_content_at_marker(
            cell.content, cell.commands, ["multi-cell-indent-space-start", "multi-cell-indent-tab-start"]
        )

        # Process pre-marker content (not in group)
        pre_marker_md = self._process_pre_marker_content(pre_marker_lines, cell.commands, marker_position)
        if pre_marker_md:
            new_state.directive_stack = self._update_directive_stack(pre_marker_md, new_state.directive_stack)
            output.append(pre_marker_md)

        # Process post-marker content (will be in group)
        post_marker_md = self._process_post_marker_content(post_marker_lines, cell.commands, marker_position)
        new_state.directive_stack = self._update_directive_stack(post_marker_md, new_state.directive_stack)

        # Initialize group
        new_state.active_group = markers.start_info
        new_state.group_cells = [post_marker_md] if post_marker_md.strip() else []

        return ProcessingResult(state=new_state, output=output)

    def _process_code_cell(self, cell: CellInput, markers: GroupMarkers, state: ProcessingState) -> ProcessingResult:
        """Process a code cell with group markers.

        Args:
            cell: Cell input data
            markers: Detected group markers
            state: Current processing state

        Returns:
            ProcessingResult with updated state and output
        """
        new_state = state.copy()
        output = []

        # Handle group end marker if present and at start of cell
        if markers.end_info and markers.end_at_start:
            group_md = self._close_active_group(new_state.group_cells, new_state.active_group)
            output.append(group_md)
            new_state.active_group = None
            new_state.group_cells = []

        # Code cells with group markers are always treated as "marker at start"
        if markers.start_info:
            new_state.active_group = markers.start_info
            new_state.group_cells = []

        # Convert code cell to fence
        code_md, leading_blanks = self._convert_code_cell(cell.content, cell.meta, cell.commands)

        if code_md:
            # Check if explicit indentation is defined
            has_explicit_indent = any(cmd.command in ["indent-space", "indent-tab"] for cmd in cell.commands)

            # Apply indentation based on directive stack if not in group AND no explicit indent
            if new_state.directive_stack and not new_state.active_group and not has_explicit_indent:
                base_indent = new_state.directive_stack[-1][1]
                indented_code = self._indent_code_fence_markers(code_md, base_indent)
                code_md = indented_code.rstrip()

            # Apply transformations
            cell_md = self._apply_code_cell_transformations(code_md, cell.content, cell.commands, leading_blanks)

            if new_state.active_group:
                new_state.group_cells.append(cell_md)
            else:
                output.append(cell_md)

        return ProcessingResult(state=new_state, output=output)

    def _process_raw_cell(self, cell: CellInput, state: ProcessingState) -> ProcessingResult:
        """Convert a raw cell back to a markdown code fence for HTML rendering.

        Raw cells hold non-executable content (ASCII diagrams, YAML snippets, etc.)
        that was tagged with a non-runnable fence language in the source markdown.
        The original language is stored in cell metadata and used to reconstruct the
        code fence so Sphinx renders the block correctly in the HTML docs.

        Args:
            cell: Cell input data (meta carries the stored fence language)
            state: Current processing state

        Returns:
            ProcessingResult with the fenced code string appended to output
        """
        new_state = state.copy()
        output: List[str] = []

        if not cell.content.strip():
            return ProcessingResult(state=new_state, output=output)

        language = cell.meta.get_language() if cell.meta else "text"
        fenced = f"```{language}\n{cell.content}\n```"

        if new_state.active_group:
            new_state.group_cells.append(fenced)
        else:
            output.append(fenced)

        return ProcessingResult(state=new_state, output=output)

    def _detect_group_end_info(self, commands: List, active_group: Optional[Dict]) -> Optional[Dict]:
        """Detect if a group end marker is present and matches the active group.

        Args:
            commands: List of marker commands
            active_group: Current active group info or None

        Returns:
            Group end info dict or None
        """
        group_space_end_id = self.interpreter.get_multi_cell_indent_space_end(commands)
        group_tab_end_id = self.interpreter.get_multi_cell_indent_tab_end(commands)

        if (
            group_space_end_id
            and active_group
            and active_group.get("type") == "space"
            and group_space_end_id == active_group["id"]
        ):
            return {"type": "space", "id": group_space_end_id}
        elif (
            group_tab_end_id
            and active_group
            and active_group.get("type") == "tab"
            and group_tab_end_id == active_group["id"]
        ):
            return {"type": "tab", "id": group_tab_end_id}

        return None

    def _is_group_end_at_start(self, commands: List) -> bool:
        """Check if group end marker appears at cell start.

        Args:
            commands: List of marker commands

        Returns:
            True if end marker is at start of cell
        """
        for cmd in commands:
            if cmd.command in ["multi-cell-indent-space-end", "multi-cell-indent-tab-end"]:
                return cmd.is_at_cell_start
        return False

    def _detect_group_start_info(self, commands: List) -> Optional[Dict]:
        """Detect if a group start marker is present.

        Args:
            commands: List of marker commands

        Returns:
            Group start info dict or None
        """
        group_space_start = self.interpreter.get_multi_cell_indent_space_start(commands)
        group_tab_start = self.interpreter.get_multi_cell_indent_tab_start(commands)

        if group_space_start:
            return {"type": "space", **group_space_start}
        elif group_tab_start:
            return {"type": "tab", **group_tab_start}

        return None

    def _is_group_start_at_start(self, commands: List) -> bool:
        """Check if group start marker appears at cell start.

        Args:
            commands: List of marker commands

        Returns:
            True if start marker is at start of cell
        """
        for cmd in commands:
            if cmd.command in ["multi-cell-indent-space-start", "multi-cell-indent-tab-start"]:
                return cmd.is_at_cell_start
        return True  # Default to True if no marker found

    def _split_content_at_marker(
        self, cleaned_content: str, commands: List, marker_commands: List[str]
    ) -> Tuple[int, List[str], List[str]]:
        """Split content at a marker position and return pre/post marker lines.

        Args:
            cleaned_content: Cleaned cell content
            commands: List of all commands
            marker_commands: List of command names to look for (e.g., ['multi-cell-indent-space-start'])

        Returns:
            Tuple of (marker_position, pre_marker_lines, post_marker_lines)
        """
        marker_position = 0
        for cmd in commands:
            if cmd.command in marker_commands:
                marker_position = cmd.position
                break

        lines = cleaned_content.split("\n")
        pre_marker_lines = lines[:marker_position]
        post_marker_lines = lines[marker_position:]

        return marker_position, pre_marker_lines, post_marker_lines

    def _process_pre_marker_content(
        self, pre_marker_lines: List[str], commands: List, marker_position: int
    ) -> Optional[str]:
        """Process content before a marker position.

        Args:
            pre_marker_lines: Lines before the marker
            commands: List of all commands
            marker_position: Position of the marker

        Returns:
            Processed markdown string or None if no content
        """
        has_pre_marker_content = pre_marker_lines and any(line.strip() for line in pre_marker_lines)
        pre_marker_inserts = [cmd for cmd in commands if cmd.command == "insert" and cmd.position < marker_position]

        if not has_pre_marker_content and not pre_marker_inserts:
            return None

        pre_marker_content = "\n".join(pre_marker_lines) if pre_marker_lines else ""
        pre_marker_commands = [cmd for cmd in commands if cmd.command != "insert" or cmd.position < marker_position]
        pre_marker_md = self._apply_insert_commands(pre_marker_content, pre_marker_commands)
        pre_marker_md = self._strip_blank_lines(pre_marker_md)

        return pre_marker_md if pre_marker_md else None

    def _process_post_marker_content(self, post_marker_lines: List[str], commands: List, marker_position: int) -> str:
        """Process content after a marker position.

        Args:
            post_marker_lines: Lines after the marker
            commands: List of all commands
            marker_position: Position of the marker

        Returns:
            Processed markdown string
        """
        post_marker_content = "\n".join(post_marker_lines)
        post_marker_commands = [cmd for cmd in commands if cmd.command != "insert" or cmd.position >= marker_position]
        # Adjust insert positions relative to post-marker content
        adjusted_commands = []
        for cmd in post_marker_commands:
            if cmd.command == "insert":
                adjusted_commands.append(replace(cmd, position=cmd.position - marker_position))
            else:
                adjusted_commands.append(cmd)

        post_marker_md = self._apply_insert_commands(post_marker_content, adjusted_commands)
        post_marker_md = self._strip_blank_lines(post_marker_md)

        return post_marker_md

    def _close_active_group(self, group_cells: List[str], active_group: Dict) -> str:
        """Close an active multi-cell group by joining cells and applying indentation.

        Args:
            group_cells: List of cell markdown strings in the group
            active_group: Active group info dict with 'type', 'spaces' or 'tabs'

        Returns:
            Joined and indented group markdown
        """
        # Use smart join for group cells (same logic as top-level cells)
        group_md = self._join_cells_with_smart_spacing(group_cells)

        if active_group.get("type") == "space":
            spaces = active_group.get("spaces", 0)
            if spaces:
                group_md = self._indent_content_smart(group_md, spaces)
        elif active_group.get("type") == "tab":
            tabs = active_group.get("tabs", 0)
            if tabs:
                group_md = self._indent_by_tabs(group_md, tabs)

        return group_md

    def _generate_download_link(self, suffix: str = "") -> str:
        """Generate download link for the current notebook.

        Args:
            suffix: Optional suffix for the filename (e.g., "-python" or "-cli")

        Returns:
            HTML link string for downloading the notebook
        """
        if not self.current_notebook_path:
            return ""

        # Get the base filename (without .ipynb extension)
        notebook_name = self.current_notebook_path.stem

        # Handle index.md special case: use parent directory name
        if notebook_name == "index":
            parent_name = self.current_notebook_path.parent.name
            if parent_name:
                notebook_name = parent_name

        # Generate the download link as raw HTML with explicit download attribute
        # We can't use {download} role because the files are generated and in _generated/
        # which is excluded. Instead, we copy the files to the output in the build-finished hook.
        # Using raw HTML ensures the browser treats it as a download, not navigation.
        ipynb_filename = f"{notebook_name}{suffix}.ipynb"

        # Customize link text based on suffix
        if suffix == NOTEBOOK_SUFFIX_PYTHON:
            download_text = "Download Python notebook"
        elif suffix == NOTEBOOK_SUFFIX_CLI:
            download_text = "Download CLI notebook"
        else:
            download_text = "Download this tutorial as a Jupyter notebook"

        return f'<a href="{ipynb_filename}" download="{ipynb_filename}">{download_text}</a>'

    def _apply_download_commands(self, content: str, commands: List) -> str:
        """Apply download commands by inserting download link at marker position.

        Download markers are replaced with a generated download link to the notebook.
        If the download command has the 'split' option, generates separate links for
        Python and CLI notebooks.

        Args:
            content: Cleaned cell content (markers already removed)
            commands: List of marker commands with position tracking

        Returns:
            Content with download links inserted at marker positions
        """
        # Get download commands sorted by position
        download_commands = [cmd for cmd in commands if cmd.command == "download"]
        if not download_commands:
            return content

        # Check if split option is present
        has_split = self.interpreter.has_download_split(commands)

        # Generate the download link(s)
        if has_split:
            # Generate separate links for Python and CLI notebooks
            python_link = self._generate_download_link(NOTEBOOK_SUFFIX_PYTHON)
            cli_link = self._generate_download_link(NOTEBOOK_SUFFIX_CLI)
            download_link = f"{python_link} | {cli_link}"
        else:
            # Generate single link (backward compatible)
            download_link = self._generate_download_link()

        if not download_link:
            return content

        # Sort by position (should already be in order, but ensure it)
        download_commands.sort(key=lambda x: x.position)

        # Split content into lines
        lines = content.split("\n") if content else []

        # Insert download links at their positions (in reverse to maintain indices)
        for cmd in reversed(download_commands):
            position = cmd.position

            # Insert at the tracked position
            if position < 0:
                position = 0
            if position > len(lines):
                position = len(lines)

            lines.insert(position, download_link)

        return "\n".join(lines)

    def _apply_cell_transformations(self, content: str, commands: List) -> str:
        """Apply marker-based transformations to cell content.

        Args:
            content: Cell content (already cleaned of marker lines)
            commands: List of marker commands

        Returns:
            Transformed content with inserts, wrapping, and indentation applied
        """
        # Step 0: Apply download command by inserting download link
        content = self._apply_download_commands(content, commands)

        # Step 1: Apply insert commands at their relative positions
        # Note: This must happen BEFORE wrapping, as inserts should be inside wrapped content
        # Important: Process inserts even if content is empty (insert-only cells)
        content = self._apply_insert_commands(content, commands)

        # If still empty after inserts/downloads and no other transformations, return empty
        # Note: download commands should have already added content in Step 0
        if not content and not self.interpreter.get_all_wrap_cell_pairs(commands):
            return ""

        # Step 2: Apply wrap-cell-start and wrap-cell-end directives
        # Multiple wrap pairs work like defer/stack (LIFO) - apply in reverse order
        # so the first wrap in source becomes the outermost wrapper
        wrap_pairs = self.interpreter.get_all_wrap_cell_pairs(commands)
        if wrap_pairs:
            # Apply wraps in REVERSE order to create proper nesting (defer pattern)
            # First wrap in source -> outermost, last wrap in source -> innermost
            for wrap_start, wrap_end in reversed(wrap_pairs):
                content = f"{wrap_start}\n{content}\n{wrap_end}"

        # Step 3: Apply indentation (last, so it indents everything including directives)
        indent_spaces = self.interpreter.get_indent_spaces(commands)
        if indent_spaces:
            content = self._indent_by_spaces(content, indent_spaces)

        indent_tabs = self.interpreter.get_indent_tabs(commands)
        if indent_tabs:
            content = self._indent_by_tabs(content, indent_tabs)

        return content

    def _apply_code_cell_transformations(
        self, fenced_content: str, cleaned_content: str, commands: List, leading_blanks: int = 0
    ) -> str:
        """Apply transformations to fenced code cell content.

        For code cells with wrap-cell markers, inserts should appear at the wrap-cell level
        (inside the wrap-cell but outside the code fence). This means we need to:
        1. Apply wrap-cell first (which wraps the fenced code)
        2. Then apply inserts at the wrap-cell content level
        3. Re-insert leading blank lines that were extracted from the code

        Args:
            fenced_content: Code cell content already wrapped in fences (```language...```)
            cleaned_content: Original cleaned content (before fencing) for position mapping
            commands: List of marker commands
            leading_blanks: Number of leading blank lines that were extracted from code

        Returns:
            Transformed content with wrapping, inserts, and indentation applied
        """
        # Step 1: Apply wrap-cell-start and wrap-cell-end directives first
        # This wraps the fenced code block
        wrap_pairs = self.interpreter.get_all_wrap_cell_pairs(commands)
        if wrap_pairs:
            # Apply wraps in REVERSE order to create proper nesting (defer pattern)
            for wrap_start, wrap_end in reversed(wrap_pairs):
                fenced_content = f"{wrap_start}\n{fenced_content}\n{wrap_end}"

        # Step 2: Apply insert commands at the wrap-cell content level
        # For code cells, inserts go OUTSIDE the fence (inside wrap-cell if present)
        # Insert at position 0 means after the wrap-cell-start, before the fence
        insert_commands = [cmd for cmd in commands if cmd.command == "insert"]
        if insert_commands or leading_blanks > 0:
            lines = fenced_content.split("\n")

            # Group inserts by position, maintaining original order within each group
            # Then process positions in descending order so insertions don't affect indices
            from collections import defaultdict

            inserts_by_position: dict = defaultdict(list)
            for cmd in insert_commands:
                inserts_by_position[cmd.position].append(cmd)

            # Process positions in descending order
            for position in sorted(inserts_by_position.keys(), reverse=True):
                cmds_at_position = inserts_by_position[position]
                # For wrapped code cells, position 0 means after the wrap-cell-start (line 0)
                # So we insert at position 1 (after the wrap-cell-start, before fence)
                if wrap_pairs:
                    insert_pos = position + 1  # +1 to skip wrap-cell-start line
                else:
                    insert_pos = position  # No wrap, insert at the beginning

                # Clamp position to valid range
                if insert_pos < 0:
                    insert_pos = 0
                if insert_pos > len(lines):
                    insert_pos = len(lines)

                # Insert all commands at this position in REVERSE order
                # so that the first command ends up at the top
                for cmd in reversed(cmds_at_position):
                    insert_text = " ".join(cmd.args)
                    lines.insert(insert_pos, insert_text)

            # Re-insert leading blank lines that were extracted from code
            # They should appear after inserts, before the fence
            if leading_blanks > 0:
                # Find the position of the fence (after wrap-cell-start and inserts)
                fence_position = 1 if wrap_pairs else 0
                # Add the number of inserts that were added
                fence_position += len(insert_commands)

                # Insert blank lines before the fence
                for _ in range(leading_blanks):
                    lines.insert(fence_position, "")

            fenced_content = "\n".join(lines)

        # Step 3: Apply indentation (last, so it indents everything including directives)
        indent_spaces = self.interpreter.get_indent_spaces(commands)
        if indent_spaces:
            fenced_content = self._indent_by_spaces(fenced_content, indent_spaces)

        indent_tabs = self.interpreter.get_indent_tabs(commands)
        if indent_tabs:
            fenced_content = self._indent_by_tabs(fenced_content, indent_tabs)

        return fenced_content

    def _apply_insert_commands(self, content: str, commands: List) -> str:
        """Apply insert commands by placing literal lines at their relative positions.

        Insert markers track their position relative to the cleaned content.
        We reconstruct the content with inserts at their original line positions.

        Args:
            content: Cleaned cell content (markers already removed)
            commands: List of marker commands with position tracking

        Returns:
            Content with insert lines added at their original positions
        """
        # Get insert commands sorted by position
        insert_commands = [cmd for cmd in commands if cmd.command == "insert"]
        if not insert_commands:
            return content

        # Sort by position (should already be in order, but ensure it)
        insert_commands.sort(key=lambda x: x.position)

        # Split content into lines
        lines = content.split("\n") if content else []

        # Insert lines at their positions (in reverse to maintain indices)
        for cmd in reversed(insert_commands):
            insert_text = " ".join(cmd.args)
            position = cmd.position

            # Insert at the tracked position
            if position < 0:
                position = 0
            if position > len(lines):
                position = len(lines)

            lines.insert(position, insert_text)

        return "\n".join(lines)

    def _strip_type_checker_comments(self, content: str) -> str:
        """Strip type checker comments from code content.

        Removes comments like:
        - # ty: ignore[...]
        - # ty: ...
        - # type: ignore[...]  (also strip standard type ignore comments)

        These are development artifacts that shouldn't appear in user-facing documentation.

        Args:
            content: Code content

        Returns:
            Content with type checker comments removed
        """
        lines = content.split("\n")
        cleaned_lines = []

        for line in lines:
            # Check if line ends with a type checker comment
            # Match patterns: # ty: ..., # type: ignore..., etc.
            # Use a simple regex to find and remove these trailing comments
            # Pattern matches:
            # - Any amount of code before the comment
            # - Optional whitespace before the comment
            # - # ty: or # type: ignore
            # - Any text after that until end of line
            # The pattern preserves everything before the comment
            cleaned_line = re.sub(r"\s*#\s*ty:\s*\S+.*$", "", line)
            cleaned_line = re.sub(r"\s*#\s*type:\s*ignore\[.*?\].*$", "", cleaned_line)

            # Also handle plain # type: ignore without brackets
            cleaned_line = re.sub(r"\s*#\s*type:\s*ignore\s*$", "", cleaned_line)

            cleaned_lines.append(cleaned_line)

        return "\n".join(cleaned_lines)

    def _convert_code_cell(self, content: str, meta: CellMetadata, commands: List) -> tuple[str, int]:
        """Convert code cell content to markdown code fence.

        Args:
            content: Code cell content (already cleaned of markers)
            meta: Cell metadata
            commands: Marker commands

        Returns:
            Tuple of (fenced code string, number of leading blank lines extracted)
        """
        # Check for language override from marker, otherwise use metadata
        language_override = self.interpreter.get_language_override(commands)
        language = language_override if language_override else meta.get_language()

        # Strip type checker comments before processing
        # These are development artifacts that shouldn't appear in user-facing documentation
        content = self._strip_type_checker_comments(content)

        # Extract leading blank lines to preserve them as markdown spacing
        # (they should appear outside the fence, not inside)
        lines = content.split("\n") if content else []
        leading_blanks = 0
        for line in lines:
            if not line.strip():
                leading_blanks += 1
            else:
                break

        # Remove leading blank lines from code content
        if leading_blanks > 0:
            content = "\n".join(lines[leading_blanks:])

        # Check for insert-code-block-start marker
        code_block_options = self.interpreter.get_insert_code_block_start(commands)

        if code_block_options:
            # Insert options after the opening fence
            return f"```{language}\n{code_block_options}\n\n{content}\n```", leading_blanks

        # Jupyter/MyST format: code fences have a blank line after opening
        # This is the standard format for Jupyter notebooks converted to MyST,
        # BUT it causes whitespace issues in rendered HTML (extra leading newline).
        # We should be more conservative and only add it if it was there in the input
        # or if it's strictly required. Standard markdown fences don't require it.
        # If we remove it, we match standard markdown behavior better.
        return f"```{language}\n{content}\n```", leading_blanks

    def _update_directive_stack(self, markdown_content: str, current_stack: List[Tuple]) -> List[Tuple]:
        """Update directive stack based on markdown content.

        Args:
            markdown_content: Markdown text to analyze
            current_stack: Current directive stack [(type, indent), ...]

        Returns:
            Updated directive stack
        """
        stack = current_stack.copy()
        lines = markdown_content.split("\n")

        for line in lines:
            stripped = line.strip()

            # Check for directive opens
            if stripped.startswith(":::") and "{" in stripped:
                match = RE_DIRECTIVE_OPEN.search(stripped)
                if match:
                    directive_type = match.group(1)
                    indent = len(line) - len(line.lstrip())
                    stack.append((directive_type, indent))

            # Check for directive closes
            elif RE_DIRECTIVE_CLOSE.match(stripped):
                if stack:
                    stack.pop()

        return stack

    def _strip_blank_lines(self, content: str) -> str:
        """Strip leading and trailing blank lines.

        Args:
            content: Content to strip

        Returns:
            Content with leading/trailing blank lines removed
        """
        lines = content.split("\n")

        while lines and not lines[0].strip():
            lines.pop(0)

        while lines and not lines[-1].strip():
            lines.pop()

        return "\n".join(lines)

    def _indent_content(self, content: str, indent_str: str) -> str:
        """Indent content with the given indentation string.

        Args:
            content: Content to indent
            indent_str: Indentation string (e.g., '    ' or '\t')

        Returns:
            Indented content
        """
        lines = content.split("\n")
        indented_lines = []

        for line in lines:
            if line.strip():
                indented_lines.append(indent_str + line)
            else:
                indented_lines.append("")

        return "\n".join(indented_lines)

    def _indent_by_spaces(self, content: str, spaces: int) -> str:
        """Indent content by a specific number of spaces.

        Args:
            content: Content to indent
            spaces: Number of spaces to indent

        Returns:
            Indented content
        """
        return self._indent_content(content, " " * spaces)

    def _indent_by_tabs(self, content: str, tabs: int) -> str:
        """Indent content by a specific number of tabs.

        Args:
            content: Content to indent
            tabs: Number of tabs to indent

        Returns:
            Indented content
        """
        return self._indent_content(content, "\t" * tabs)

    def _indent_code_fence_markers(self, fence_content: str, spaces: int) -> str:
        """Indent only the code fence markers, not the content inside.

        Args:
            fence_content: Code fence content (```language\\n...\\n```)
            spaces: Number of spaces to indent

        Returns:
            Content with only fence markers indented
        """
        lines = fence_content.split("\n")
        if len(lines) < 2:
            return fence_content

        indent_str = " " * spaces
        indented_lines = []

        for i, line in enumerate(lines):
            # Indent only the first line (```language) and last line (```)
            if i == 0 or i == len(lines) - 1:
                if line.strip():
                    indented_lines.append(indent_str + line)
                else:
                    indented_lines.append(line)
            else:
                # Keep content lines at their original indentation
                indented_lines.append(line)

        return "\n".join(indented_lines)

    def _indent_content_smart(self, content: str, spaces: int) -> str:
        """Intelligently indent content - code fence markers only for fences, everything else normally.

        Args:
            content: Content to indent (may contain code fences)
            spaces: Number of spaces to indent

        Returns:
            Indented content with code fences handled specially
        """
        lines = content.split("\n")
        if not lines:
            return content

        indent_str = " " * spaces
        indented_lines = []
        in_code_fence = False

        for line in lines:
            # Check if this line is a code fence marker
            fence_match = RE_CODE_FENCE.match(line)

            if fence_match:
                # This is a fence marker - indent it
                if line.strip():
                    indented_lines.append(indent_str + line)
                else:
                    indented_lines.append(line)
                # Toggle fence state
                in_code_fence = not in_code_fence
            elif in_code_fence:
                # Inside code fence - indent by the specified amount (add to existing indentation)
                # Empty lines stay empty
                if line.strip():
                    indented_lines.append(indent_str + line)
                else:
                    indented_lines.append(line)
            else:
                # Outside code fence - indent normally
                if line.strip():
                    indented_lines.append(indent_str + line)
                else:
                    indented_lines.append(line)

        return "\n".join(indented_lines)

    def _check_notebook_convert_4_space_to_tab(self, cells: List[Dict]) -> bool:
        """Check if notebook-convert-4-space-to-tab marker is present in any cell.

        This is a notebook-wide setting, so we check all cells.

        Args:
            cells: List of cell dictionaries

        Returns:
            True if notebook-convert-4-space-to-tab is enabled
        """
        for cell in cells:
            cell_content = "".join(cell.get("source", []))
            cell_type = cell.get("cell_type", "")
            _, commands = self.parser.parse_cell(cell_content, cell_type)
            if self.interpreter.has_notebook_convert_4_space_to_tab(commands):
                return True
        return False

    def _postprocess_spaces_to_tabs(self, content: str) -> str:
        """Convert 4 consecutive spaces to tabs in the content.

        This is applied as a final postprocessing step when notebook-convert-4-space-to-tab
        is enabled. It converts leading spaces (indentation) from 4 spaces to 1 tab.

        Args:
            content: Markdown content to process

        Returns:
            Content with 4 spaces converted to tabs
        """
        lines = content.split("\n")
        processed_lines = []

        for line in lines:
            # Process leading spaces only (indentation)
            if line and line[0] == " ":
                # Count leading spaces
                leading_spaces = len(line) - len(line.lstrip(" "))
                # Convert groups of 4 spaces to tabs
                tabs = leading_spaces // 4
                remaining_spaces = leading_spaces % 4
                rest_of_line = line.lstrip(" ")
                new_line = ("\t" * tabs) + (" " * remaining_spaces) + rest_of_line
                processed_lines.append(new_line)
            else:
                processed_lines.append(line)

        return "\n".join(processed_lines)

    def _join_cells_with_smart_spacing(self, processed_cells: List[str]) -> str:
        """Join cells with smart spacing.

        Rules:
        - Normal case: join with "\\n\\n" (double newline)
        - Special case: if previous cell ends with directive marker (like ::::{tab-set})
          and next cell starts with directive marker (like :::{tab-item}),
          join with "\\n" (single newline)

        Args:
            processed_cells: List of processed cell content strings

        Returns:
            Joined content with appropriate spacing
        """
        if not processed_cells:
            return ""

        result_parts = [processed_cells[0]]

        for i in range(1, len(processed_cells)):
            prev_cell = processed_cells[i - 1]
            curr_cell = processed_cells[i]

            # Check if we should use single newline
            prev_ends_with_directive = self._ends_with_directive_marker(prev_cell)
            curr_starts_with_directive = self._starts_with_directive_marker(curr_cell)

            if prev_ends_with_directive and curr_starts_with_directive:
                separator = "\n"  # Single newline
            else:
                # Standard markdown: ensure there's exactly one blank line between blocks.
                # Since cells might have been stripped or modified, we usually want \n\n.
                # However, sometimes we might want tighter spacing if it's not a block level split.
                # But cells are usually block level units.

                # Check for special case: closing directive (:::) followed by next directive or content
                # We often want consistent spacing there.

                separator = "\n\n"  # Double newline (normal)

            # Ensure previous cell doesn't have trailing newlines that would compound with separator
            if result_parts:
                result_parts[-1] = result_parts[-1].rstrip("\n")

            result_parts.append(separator)
            result_parts.append(curr_cell)

        return "".join(result_parts)

    def _ends_with_directive_marker(self, content: str) -> bool:
        """Check if content ends with a MyST directive marker.

        Args:
            content: Content to check

        Returns:
            True if content ends with a directive marker
        """
        return bool(RE_DIRECTIVE_END.search(content.rstrip()))

    def _starts_with_directive_marker(self, content: str) -> bool:
        """Check if content starts with a MyST directive marker.

        Args:
            content: Content to check

        Returns:
            True if content starts with a directive marker
        """
        return bool(RE_DIRECTIVE_START.match(content.lstrip()))

    def _strip_outputs(self, notebook: Dict) -> Dict:
        """Remove all output data from notebook cells.

        Args:
            notebook: Parsed notebook JSON

        Returns:
            Notebook dict with outputs cleared
        """
        cleaned = notebook.copy()
        cleaned["cells"] = []

        for cell in notebook.get("cells", []):
            cell_copy = cell.copy()
            if cell_copy.get("cell_type") == "code":
                cell_copy["outputs"] = []
                cell_copy["execution_count"] = None
                # Clear execution metadata
                if "metadata" in cell_copy:
                    metadata_copy = cell_copy["metadata"].copy()
                    metadata_copy.pop("execution", None)
                    cell_copy["metadata"] = metadata_copy
            cleaned["cells"].append(cell_copy)

        return cleaned


class NotebookToMarkdownConverter:
    """Convert Jupyter notebooks to Markdown source format (with fences).

    This converter is for notebook → markdown source format (for authoring),
    NOT for Sphinx documentation format. Code cells are converted to
    triple backtick fenced code blocks (```python), making the output
    more readable and standard markdown-compatible.
    """

    def __init__(self, config: Optional[Dict] = None):
        """Initialize converter with configuration.

        Args:
            config: Optional configuration dict
        """
        self.config = config or {}

    def convert(self, notebook_path: Path) -> str:
        """Convert notebook file to markdown string.

        Args:
            notebook_path: Path to .ipynb file

        Returns:
            Markdown string with converted content
        """
        nb = json.loads(notebook_path.read_text())
        return self.convert_notebook_dict(nb)

    def convert_notebook_dict(self, notebook: Dict) -> str:
        """Convert notebook dictionary to markdown source format.

        Args:
            notebook: Parsed notebook JSON as dict

        Returns:
            Markdown string with fence-based code cells
        """
        cells = notebook.get("cells", [])
        parts = []

        # Check if any cell contains triple backticks - if so, need disable-fence-conversion
        needs_disable_fence = self._check_needs_disable_fence_conversion(cells)

        for cell in cells:
            cell_type = cell.get("cell_type", "")
            content = "".join(cell.get("source", []))

            if cell_type == "markdown":
                # Passthrough markdown cells, but add explicit marker if disable-fence is needed
                if content.strip():
                    if needs_disable_fence:
                        # Add explicit markdown cell marker for clarity
                        parts.append(("markdown", f"<!-- @nemo-nb: cell markdown -->\n{content.rstrip()}"))
                    else:
                        parts.append(("markdown", content.rstrip()))

            elif cell_type == "code":
                # Convert to code cell
                meta = CellMetadata(cell)
                language = meta.get_language()

                if needs_disable_fence:
                    # Use explicit cell marker instead of fences when disable-fence is needed
                    code_content = f"<!-- @nemo-nb: cell {language} -->\n{content.rstrip()}"
                    parts.append(("code", code_content))
                else:
                    # Use fences normally
                    fence_content = f"```{language}\n{content.rstrip()}\n```"
                    parts.append(("code", fence_content))

                # Add outputs if present
                outputs = cell.get("outputs", [])
                if outputs:
                    output_md = self._format_outputs(outputs)
                    if output_md:
                        parts.append(("output", output_md))

            elif cell_type == "raw":
                # Raw cells hold non-executable content (ASCII diagrams, YAML, etc.).
                # Reconstruct the original code fence using the stored language and indentation.
                if content.strip():
                    meta = CellMetadata(cell)
                    language = meta.get_language()
                    indent_spaces = cell.get("metadata", {}).get("indent-space", 0)
                    indent = " " * indent_spaces
                    inner = content.rstrip().replace("\n", f"\n{indent}")
                    fence_content = f"{indent}```{language}\n{indent}{inner}\n{indent}```"
                    parts.append(("raw", fence_content))

        # Join parts with appropriate spacing
        result = []

        # Add disable-fence-conversion marker at the start if needed
        if needs_disable_fence:
            result.append("<!-- @nemo-nb: disable-fence-conversion -->")
            result.append("\n\n")

        for i, (part_type, part_content) in enumerate(parts):
            if i == 0:
                result.append(part_content)
            else:
                prev_type, _ = parts[i - 1]
                # Code followed by output: one blank line
                # Output followed by markdown: one blank line
                # Everything else: two blank lines
                if (prev_type == "code" and part_type == "output") or (
                    prev_type == "output" and part_type == "markdown"
                ):
                    result.append("\n\n" + part_content)
                elif prev_type == "output" or part_type == "output":
                    result.append("\n" + part_content)
                else:
                    result.append("\n\n" + part_content)

        final_result = "".join(result)
        # Ensure final newline
        if final_result and not final_result.endswith("\n"):
            final_result += "\n"
        return final_result

    def _check_needs_disable_fence_conversion(self, cells: List[Dict]) -> bool:
        """Check if any cell contains triple backticks that would conflict with fence format.

        When converting from notebook to markdown, if any cell contains triple backticks (```),
        we need to use the disable-fence-conversion marker. Otherwise, when converting back
        from markdown to notebook, those triple backticks would be misinterpreted as cell
        boundaries.

        Args:
            cells: List of cell dictionaries from notebook

        Returns:
            True if disable-fence-conversion marker should be added
        """
        for cell in cells:
            content = "".join(cell.get("source", []))
            # Check if content contains 3 or more consecutive backticks
            if "```" in content:
                return True
        return False

    def _format_outputs(self, outputs: List[Dict]) -> str:
        """Format notebook outputs as markdown with output markers.

        Args:
            outputs: List of output dictionaries from notebook

        Returns:
            Formatted output markdown with markers
        """
        output_parts = []

        for output in outputs:
            output_type = output.get("output_type", "")

            if output_type == "stream":
                name = output.get("name", "stdout")
                text = "".join(output.get("text", []))
                if text.strip():
                    if name == "stdout":
                        output_parts.append("<!-- @nemo-nb: output -->")
                    else:
                        output_parts.append(f"<!-- @nemo-nb: output stream {name} -->")
                    output_parts.append(text.rstrip())

            elif output_type == "execute_result":
                data = output.get("data", {})
                text = "".join(data.get("text/plain", []))
                if text.strip():
                    output_parts.append("<!-- @nemo-nb: output execute_result -->")
                    output_parts.append(text.rstrip())

            elif output_type == "display_data":
                data = output.get("data", {})
                text = "".join(data.get("text/plain", []))
                if text.strip():
                    output_parts.append("<!-- @nemo-nb: output display_data -->")
                    output_parts.append(text.rstrip())

            elif output_type == "error":
                # Format error output with traceback
                traceback = output.get("traceback", [])
                if traceback:
                    output_parts.append("<!-- @nemo-nb: output error -->")
                    # Join traceback lines
                    output_parts.append("\n".join(traceback).rstrip())

        return "\n".join(output_parts) if output_parts else ""
