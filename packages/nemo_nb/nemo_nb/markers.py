# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Marker-based command parsing for cell content.

Replaces metadata-based features with inline markers:
- # @nemo-nb: COMMAND (code cells)
- // @nemo-nb: COMMAND (code cells, alternative)
- <!-- @nemo-nb: COMMAND --> (markdown cells)

Supported commands:
- hide: Hide the cell from output
- wrap-cell-start <directive>: Start wrapping content with exact directive syntax
- wrap-cell-end <closing>: End wrapping content with exact closing syntax
- insert <text>: Insert literal line at current position
- download: Insert a download link to the notebook at current position
- download split: Generate separate notebook downloads for Python and CLI code
- insert-code-block-start <options>: Convert code cell to {code-block} directive with options
- multi-cell-indent-space-start <id> <number>: Start a multi-cell block with space indentation
- multi-cell-indent-space-end <id>: End a multi-cell block with space indentation
- multi-cell-indent-tab-start <id> <number>: Start a multi-cell block with tab indentation
- multi-cell-indent-tab-end <id>: End a multi-cell block with tab indentation
- indent-space <number>: Indent cell content and directives by X spaces
- indent-tab <number>: Indent cell content and directives by X tabs
- language <lang>: Override the language in the code fence
- notebook-convert-4-space-to-tab: Notebook-wide setting to convert 4 spaces to tabs in final output
- disable-fence-conversion: Disable automatic triple-backtick to code cell conversion (markdown format only)
- output-cell-start [type] [name]: Mark the beginning of output cell content with optional type and name
  (defaults: type=stream, name=stdout)
- output-cell-end: Mark the end of output cell content
- skip-test: Exclude notebook from automated e2e test runs (still processed for docs builds)
"""

import re
from dataclasses import dataclass, replace
from typing import Dict, List, Optional, Tuple

# Commands that need position tracking for insertion/indentation
POSITION_TRACKED_COMMANDS = [
    "insert",
    "download",
    "multi-cell-indent-space-start",
    "multi-cell-indent-tab-start",
    "multi-cell-indent-space-end",
    "multi-cell-indent-tab-end",
    "output-cell-start",
    "output-cell-end",
]


@dataclass(frozen=True)
class MarkerCommand:
    """Represents a parsed marker command extracted from cell content.

    Marker commands are inline annotations in notebook cells that control
    how cells are transformed during conversion to Markdown. They are
    removed from the output but their effects are applied.

    Attributes:
        command: Command name identifying the action to perform.
                 Examples: 'hide', 'wrap-cell-start', 'insert', 'indent-space'

        args: List of command arguments.
              For 'insert': ['Text to insert']
              For 'indent-space': ['4']
              For 'wrap-cell-start': [':::{note} Title']
              Empty list for commands without arguments like 'hide'.

        line: Original line containing the marker in the cell.
              Used for debugging and error reporting.
              Example: '# @nemo-nb: hide'

        position: Line position in the cleaned content (after marker removal).
                  Defaults to -1 for non-position-tracked commands.
                  For position-tracked commands (insert, multi-cell markers),
                  this indicates where in the cleaned content the command
                  should take effect.

        is_at_cell_start: Whether this marker appears before any non-empty content.
                          True: Marker is at the very start of the cell
                          False: Marker appears after some content
                          Used to determine if multi-cell group markers split
                          the cell or apply to the entire cell.

    Example - From notebook cell to MarkerCommand:
        Notebook cell content:
        ```
        # @nemo-nb: hide
        # @nemo-nb: wrap-cell-start :::{note} Important
        print('hello')
        # @nemo-nb: insert Additional text
        # @nemo-nb: wrap-cell-end :::
        ```

        After parsing, produces these MarkerCommands:
        >>> cmd1 = MarkerCommand(
        ...     command='hide',
        ...     args=[],
        ...     line='# @nemo-nb: hide',
        ...     position=-1,
        ...     is_at_cell_start=True
        ... )
        >>> cmd2 = MarkerCommand(
        ...     command='wrap-cell-start',
        ...     args=[':::{note} Important'],
        ...     line='# @nemo-nb: wrap-cell-start :::{note} Important',
        ...     position=-1,
        ...     is_at_cell_start=True
        ... )
        >>> cmd3 = MarkerCommand(
        ...     command='insert',
        ...     args=['Additional text'],
        ...     line='# @nemo-nb: insert Additional text',
        ...     position=1,
        ...     is_at_cell_start=False
        ... )

        Cleaned content (markers removed):
        ```
        print('hello')
        ```
    """

    command: str
    args: List[str]
    line: str
    position: int = -1
    is_at_cell_start: bool = False


class MarkerParser:
    """Parse and process marker commands in cell content."""

    # Patterns for detecting markers
    CODE_MARKER = re.compile(r"^#\s*@nemo-nb:\s*(.+)$", re.MULTILINE)
    SLASH_MARKER = re.compile(r"^//\s*@nemo-nb:\s*(.+)$", re.MULTILINE)
    HTML_MARKER = re.compile(r"^<!--\s*@nemo-nb:\s*(.+?)\s*-->$", re.MULTILINE)

    def __init__(self):
        """Initialize parser."""
        pass

    def parse_cell(self, cell_content: str, cell_type: str = "code") -> Tuple[str, List["MarkerCommand"]]:
        """Parse cell content for markers and extract commands.

        Args:
            cell_content: Raw cell content
            cell_type: Type of cell ('code' or 'markdown')

        Returns:
            Tuple of (cleaned_content, list of commands)
        """
        commands = []
        cleaned_lines = []
        has_non_empty_content = False

        lines = cell_content.split("\n")

        for line_num, line in enumerate(lines):
            # Check for code marker (# @nemo-nb: ...)
            code_match = self.CODE_MARKER.match(line)
            if code_match:
                command_str = code_match.group(1).strip()
                cmd = self._parse_command(command_str, line, line_num)
                if cmd:
                    # Track position relative to cleaned content for relevant commands
                    position = len(cleaned_lines) if cmd.command in POSITION_TRACKED_COMMANDS else cmd.position
                    # Track if this marker is at the start of the cell
                    is_at_start = not has_non_empty_content
                    # Create new command with updated fields
                    cmd = replace(cmd, position=position, is_at_cell_start=is_at_start)
                    commands.append(cmd)
                continue  # Skip this line (remove marker from output)

            # Check for slash marker (// @nemo-nb: ...)
            slash_match = self.SLASH_MARKER.match(line)
            if slash_match:
                command_str = slash_match.group(1).strip()
                cmd = self._parse_command(command_str, line, line_num)
                if cmd:
                    # Track position relative to cleaned content for relevant commands
                    position = len(cleaned_lines) if cmd.command in POSITION_TRACKED_COMMANDS else cmd.position
                    # Track if this marker is at the start of the cell
                    is_at_start = not has_non_empty_content
                    # Create new command with updated fields
                    cmd = replace(cmd, position=position, is_at_cell_start=is_at_start)
                    commands.append(cmd)
                continue  # Skip this line (remove marker from output)

            # Check for HTML comment marker (<!-- @nemo-nb: ... -->)
            html_match = self.HTML_MARKER.match(line)
            if html_match:
                command_str = html_match.group(1).strip()
                cmd = self._parse_command(command_str, line, line_num)
                if cmd:
                    # Track position relative to cleaned content for relevant commands
                    position = len(cleaned_lines) if cmd.command in POSITION_TRACKED_COMMANDS else cmd.position
                    # Track if this marker is at the start of the cell
                    is_at_start = not has_non_empty_content
                    # Create new command with updated fields
                    cmd = replace(cmd, position=position, is_at_cell_start=is_at_start)
                    commands.append(cmd)
                continue  # Skip this line (remove marker from output)

            # Keep all other lines
            cleaned_lines.append(line)
            # Track if we've seen non-empty content
            if line.strip():
                has_non_empty_content = True

        cleaned_content = "\n".join(cleaned_lines)
        return cleaned_content, commands

    def _parse_command(self, command_str: str, line: str, line_num: int = -1) -> Optional[MarkerCommand]:
        """Parse a command string into a MarkerCommand.

        Args:
            command_str: Command string (e.g., "hide", "wrap-start :::{dropdown} Title")
            line: Original line for reference
            line_num: Line number in original content

        Returns:
            MarkerCommand or None if parsing fails
        """
        parts = command_str.split(None, 1)  # Split on first whitespace only
        if not parts:
            return None

        command = parts[0].lower()

        # For insert, insert-code-block-start, wrap-cell-start, and wrap-cell-end, preserve everything after command as-is
        if command in ["insert", "insert-code-block-start", "wrap-cell-start", "wrap-cell-end"]:
            args = [parts[1]] if len(parts) > 1 else []
        else:
            # For other commands, split args normally
            args = parts[1].split() if len(parts) > 1 else []

        return MarkerCommand(command, args, line, line_num)

    def extract_commands_by_type(self, commands: List["MarkerCommand"], command_type: str) -> List["MarkerCommand"]:
        """Extract all commands of a specific type.

        Args:
            commands: List of all commands
            command_type: Command type to filter for

        Returns:
            List of matching commands
        """
        return [cmd for cmd in commands if cmd.command == command_type]

    def has_command(self, commands: List["MarkerCommand"], command_type: str) -> bool:
        """Check if a specific command type exists.

        Args:
            commands: List of commands
            command_type: Command type to check for

        Returns:
            True if command exists
        """
        return any(cmd.command == command_type for cmd in commands)

    def get_command_args(self, commands: List["MarkerCommand"], command_type: str) -> Optional[List[str]]:
        """Get arguments for the first matching command.

        Args:
            commands: List of commands
            command_type: Command type to get args for

        Returns:
            List of arguments or None if command not found
        """
        for cmd in commands:
            if cmd.command == command_type:
                return cmd.args
        return None


class CommandInterpreter:
    """Interpret marker commands and apply transformations."""

    def __init__(self):
        """Initialize interpreter."""
        self.parser = MarkerParser()

    def should_hide(self, commands: List["MarkerCommand"]) -> bool:
        """Check if cell should be hidden.

        Args:
            commands: List of marker commands

        Returns:
            True if cell should be hidden
        """
        return self.parser.has_command(commands, "hide")

    def get_wrap_cell_start(self, commands: List["MarkerCommand"]) -> Optional[str]:
        """Get wrap-cell-start directive syntax from commands.

        Args:
            commands: List of marker commands

        Returns:
            Complete directive opening (e.g., ":::{dropdown} Title") or None
        """
        args = self.parser.get_command_args(commands, "wrap-cell-start")
        if args:
            return " ".join(args)  # Return the entire directive as-is
        return None

    def get_wrap_cell_end(self, commands: List["MarkerCommand"]) -> Optional[str]:
        """Get wrap-cell-end closing syntax from commands.

        Args:
            commands: List of marker commands

        Returns:
            Complete directive closing (e.g., ":::") or None
        """
        args = self.parser.get_command_args(commands, "wrap-cell-end")
        if args:
            return " ".join(args)  # Return the entire closing as-is
        return None

    def get_insert_lines(self, commands: List["MarkerCommand"]) -> List[str]:
        """Get all insert command lines from commands.

        Args:
            commands: List of marker commands

        Returns:
            List of lines to insert (preserves order)
        """
        insert_commands = self.parser.extract_commands_by_type(commands, "insert")
        return [" ".join(cmd.args) for cmd in insert_commands]

    def get_all_wrap_cell_pairs(self, commands: List["MarkerCommand"]) -> List[tuple]:
        """Get all wrap-cell-start/wrap-cell-end pairs from commands in order.

        Wrap directives work like a defer/stack pattern. Multiple pairs
        are applied in order, creating nested structures.

        Args:
            commands: List of marker commands

        Returns:
            List of (wrap_cell_start, wrap_cell_end) tuples in the order they appear
        """
        wrap_starts = self.parser.extract_commands_by_type(commands, "wrap-cell-start")
        wrap_ends = self.parser.extract_commands_by_type(commands, "wrap-cell-end")

        # Pair them up in order
        pairs = []
        min_len = min(len(wrap_starts), len(wrap_ends))

        for i in range(min_len):
            start_text = " ".join(wrap_starts[i].args)
            end_text = " ".join(wrap_ends[i].args)
            pairs.append((start_text, end_text))

        return pairs

    def get_multi_cell_indent_space_start(self, commands: List["MarkerCommand"]) -> Optional[Dict]:
        """Get multi-cell indent space start information.

        Args:
            commands: List of marker commands

        Returns:
            Dict with id and spaces or None
        """
        args = self.parser.get_command_args(commands, "multi-cell-indent-space-start")
        if not args or len(args) < 2:
            return None

        group_id = args[0]
        try:
            spaces = int(args[1])
        except (ValueError, IndexError):
            return None

        return {"id": group_id, "spaces": spaces}

    def get_multi_cell_indent_space_end(self, commands: List["MarkerCommand"]) -> Optional[str]:
        """Get multi-cell indent space end ID.

        Args:
            commands: List of marker commands

        Returns:
            Multi-cell block ID or None
        """
        args = self.parser.get_command_args(commands, "multi-cell-indent-space-end")
        if args:
            return args[0]
        return None

    def get_multi_cell_indent_tab_start(self, commands: List["MarkerCommand"]) -> Optional[Dict]:
        """Get multi-cell indent tab start information.

        Args:
            commands: List of marker commands

        Returns:
            Dict with id and tabs or None
        """
        args = self.parser.get_command_args(commands, "multi-cell-indent-tab-start")
        if not args or len(args) < 2:
            return None

        group_id = args[0]
        try:
            tabs = int(args[1])
        except (ValueError, IndexError):
            return None

        return {"id": group_id, "tabs": tabs}

    def get_multi_cell_indent_tab_end(self, commands: List["MarkerCommand"]) -> Optional[str]:
        """Get multi-cell indent tab end ID.

        Args:
            commands: List of marker commands

        Returns:
            Multi-cell block ID or None
        """
        args = self.parser.get_command_args(commands, "multi-cell-indent-tab-end")
        if args:
            return args[0]
        return None

    def get_indent_spaces(self, commands: List["MarkerCommand"]) -> Optional[int]:
        """Get number of spaces to indent cell content.

        Args:
            commands: List of marker commands

        Returns:
            Number of spaces or None
        """
        args = self.parser.get_command_args(commands, "indent-space")
        if args:
            try:
                return int(args[0])
            except (ValueError, IndexError):
                return None
        return None

    def get_indent_tabs(self, commands: List["MarkerCommand"]) -> Optional[int]:
        """Get number of tabs to indent cell content.

        Args:
            commands: List of marker commands

        Returns:
            Number of tabs or None
        """
        args = self.parser.get_command_args(commands, "indent-tab")
        if args:
            try:
                return int(args[0])
            except (ValueError, IndexError):
                return None
        return None

    def get_language_override(self, commands: List["MarkerCommand"]) -> Optional[str]:
        """Get language override for code fence.

        Args:
            commands: List of marker commands

        Returns:
            Language string or None
        """
        args = self.parser.get_command_args(commands, "language")
        if args:
            return args[0]
        return None

    def has_notebook_convert_4_space_to_tab(self, commands: List["MarkerCommand"]) -> bool:
        """Check if notebook-convert-4-space-to-tab is enabled.

        This is a notebook-wide setting that converts 4 spaces to tabs
        in the final output after all other processing.

        Args:
            commands: List of marker commands

        Returns:
            True if notebook-convert-4-space-to-tab is enabled
        """
        return self.parser.has_command(commands, "notebook-convert-4-space-to-tab")

    def get_insert_code_block_start(self, commands: List["MarkerCommand"]) -> Optional[str]:
        """Get insert-code-block-start options from commands.

        This marker converts the code cell to use {code-block} directive
        with the specified options inserted after the opening fence.

        Args:
            commands: List of marker commands

        Returns:
            Options string (e.g., ":emphasize-lines: 18-21") or None
        """
        args = self.parser.get_command_args(commands, "insert-code-block-start")
        if args:
            return " ".join(args)  # Return the entire options string as-is
        return None

    def get_output_cell_start(self, commands: List["MarkerCommand"]) -> bool:
        """Check if output-cell-start marker is present.

        Args:
            commands: List of marker commands

        Returns:
            True if output-cell-start marker is present
        """
        return self.parser.has_command(commands, "output-cell-start")

    def get_output_cell_end(self, commands: List["MarkerCommand"]) -> bool:
        """Check if output-cell-end marker is present.

        Args:
            commands: List of marker commands

        Returns:
            True if output-cell-end marker is present
        """
        return self.parser.has_command(commands, "output-cell-end")

    def get_output_type(self, commands: List["MarkerCommand"]) -> str:
        """Get output type from commands.

        Args:
            commands: List of marker commands

        Returns:
            Output type (stream, execute_result, display_data, error)
            Defaults to 'stream' if not specified
        """
        args = self.parser.get_command_args(commands, "output-type")
        return args[0] if args else "stream"

    def get_output_name(self, commands: List["MarkerCommand"]) -> str:
        """Get output name from commands.

        Args:
            commands: List of marker commands

        Returns:
            Output name (e.g., stdout, stderr)
            Defaults to 'stdout' if not specified
        """
        args = self.parser.get_command_args(commands, "output-name")
        return args[0] if args else "stdout"

    def has_disable_fence_conversion(self, commands: List["MarkerCommand"]) -> bool:
        """Check if disable-fence-conversion is enabled.

        This is a document-wide setting that disables automatic conversion
        of triple-backtick fenced code blocks to code cells in markdown format.
        When enabled, only explicit <!-- @nemo-nb: cell <language> --> markers
        create code cells.

        Args:
            commands: List of marker commands

        Returns:
            True if disable-fence-conversion is enabled
        """
        return self.parser.has_command(commands, "disable-fence-conversion")

    def has_download_split(self, commands: List["MarkerCommand"]) -> bool:
        """Check if download split option is enabled.

        When enabled, separate notebook variants are generated for Python and CLI code.
        Instead of a single download link, generates two links: one for Python notebook
        and one for CLI notebook. All markdown cells are included in both variants.

        Args:
            commands: List of marker commands

        Returns:
            True if download command has 'split' argument
        """
        download_commands = self.parser.extract_commands_by_type(commands, "download")
        for cmd in download_commands:
            if "split" in cmd.args:
                return True
        return False
