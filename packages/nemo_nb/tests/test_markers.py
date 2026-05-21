# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Unit tests for marker-based command parsing."""

from nemo_nb.markers import CommandInterpreter, MarkerCommand, MarkerParser


class TestMarkerParser:
    """Test marker command parsing."""

    def test_parse_code_marker(self):
        """Test parsing code marker."""
        content = "# @nemo-nb: hide\nprint('hello')"
        parser = MarkerParser()

        cleaned, commands = parser.parse_cell(content, "code")

        assert cleaned == "print('hello')"
        assert len(commands) == 1
        assert commands[0].command == "hide"

    def test_parse_html_marker(self):
        """Test parsing HTML comment marker."""
        content = "<!-- @nemo-nb: hide -->\n# Title"
        parser = MarkerParser()

        cleaned, commands = parser.parse_cell(content, "markdown")

        assert cleaned == "# Title"
        assert len(commands) == 1
        assert commands[0].command == "hide"

    def test_parse_slash_marker(self):
        """Test parsing slash comment marker."""
        content = "// @nemo-nb: hide\nprint('hello')"
        parser = MarkerParser()

        cleaned, commands = parser.parse_cell(content, "code")

        assert cleaned == "print('hello')"
        assert len(commands) == 1
        assert commands[0].command == "hide"

    def test_marker_removed_from_output(self):
        """Test that marker lines are removed from output."""
        content = "# @nemo-nb: hide\nx = 1\ny = 2"
        parser = MarkerParser()

        cleaned, _ = parser.parse_cell(content, "code")

        assert "@nemo-nb" not in cleaned
        assert "x = 1" in cleaned
        assert "y = 2" in cleaned

    def test_parse_group_indent_space_start(self):
        """Test parsing multi-cell-indent-space-start command."""
        content = "# @nemo-nb: multi-cell-indent-space-start my-group 3\ncode"
        parser = MarkerParser()

        cleaned, commands = parser.parse_cell(content, "code")

        assert len(commands) == 1
        assert commands[0].command == "multi-cell-indent-space-start"
        assert commands[0].args == ["my-group", "3"]

    def test_parse_group_indent_space_end(self):
        """Test parsing multi-cell-indent-space-end command."""
        content = "# @nemo-nb: multi-cell-indent-space-end my-group\ncode"
        parser = MarkerParser()

        cleaned, commands = parser.parse_cell(content, "code")

        assert len(commands) == 1
        assert commands[0].command == "multi-cell-indent-space-end"
        assert commands[0].args == ["my-group"]

    def test_parse_group_indent_tab_start(self):
        """Test parsing multi-cell-indent-tab-start command."""
        content = "# @nemo-nb: multi-cell-indent-tab-start my-group 2\ncode"
        parser = MarkerParser()

        cleaned, commands = parser.parse_cell(content, "code")

        assert len(commands) == 1
        assert commands[0].command == "multi-cell-indent-tab-start"
        assert commands[0].args == ["my-group", "2"]

    def test_parse_group_indent_tab_end(self):
        """Test parsing multi-cell-indent-tab-end command."""
        content = "# @nemo-nb: multi-cell-indent-tab-end my-group\ncode"
        parser = MarkerParser()

        cleaned, commands = parser.parse_cell(content, "code")

        assert len(commands) == 1
        assert commands[0].command == "multi-cell-indent-tab-end"
        assert commands[0].args == ["my-group"]

    def test_parse_multiple_markers(self):
        """Test parsing multiple markers in same cell."""
        content = "# @nemo-nb: wrap-cell-start :::{dropdown} Example\n# @nemo-nb: hide\ncode"
        parser = MarkerParser()

        cleaned, commands = parser.parse_cell(content, "code")

        assert len(commands) == 2
        assert commands[0].command == "wrap-cell-start"
        assert commands[1].command == "hide"
        assert "@nemo-nb" not in cleaned

    def test_parse_mixed_marker_types(self):
        """Test parsing different marker types in same cell."""
        content = "# @nemo-nb: wrap-cell-start :::{dropdown} Example\n// @nemo-nb: hide\ncode"
        parser = MarkerParser()

        cleaned, commands = parser.parse_cell(content, "code")

        assert len(commands) == 2
        assert commands[0].command == "wrap-cell-start"
        assert commands[1].command == "hide"
        assert "@nemo-nb" not in cleaned

    def test_no_markers(self):
        """Test content without markers."""
        content = "# Regular comment\ncode here"
        parser = MarkerParser()

        cleaned, commands = parser.parse_cell(content, "code")

        assert len(commands) == 0
        assert cleaned == content


class TestCommandInterpreter:
    """Test command interpretation."""

    def test_should_hide(self):
        """Test hide command detection."""
        cmd = MarkerCommand("hide", [], "")
        interpreter = CommandInterpreter()

        assert interpreter.should_hide([cmd]) is True
        assert interpreter.should_hide([]) is False

    def test_get_multi_cell_indent_space_start(self):
        """Test group indent space start extraction."""
        cmd = MarkerCommand("multi-cell-indent-space-start", ["my-group", "4"], "")
        interpreter = CommandInterpreter()

        info = interpreter.get_multi_cell_indent_space_start([cmd])

        assert info["id"] == "my-group"
        assert info["spaces"] == 4

    def test_get_multi_cell_indent_space_end(self):
        """Test group indent space end extraction."""
        cmd = MarkerCommand("multi-cell-indent-space-end", ["my-group"], "")
        interpreter = CommandInterpreter()

        group_id = interpreter.get_multi_cell_indent_space_end([cmd])

        assert group_id == "my-group"

    def test_get_multi_cell_indent_tab_start(self):
        """Test group indent tab start extraction."""
        cmd = MarkerCommand("multi-cell-indent-tab-start", ["my-group", "2"], "")
        interpreter = CommandInterpreter()

        info = interpreter.get_multi_cell_indent_tab_start([cmd])

        assert info["id"] == "my-group"
        assert info["tabs"] == 2

    def test_get_multi_cell_indent_tab_end(self):
        """Test group indent tab end extraction."""
        cmd = MarkerCommand("multi-cell-indent-tab-end", ["my-group"], "")
        interpreter = CommandInterpreter()

        group_id = interpreter.get_multi_cell_indent_tab_end([cmd])

        assert group_id == "my-group"

    def test_get_indent_spaces(self):
        """Test indent spaces extraction."""
        cmd = MarkerCommand("indent-space", ["4"], "")
        interpreter = CommandInterpreter()

        indent = interpreter.get_indent_spaces([cmd])

        assert indent == 4

    def test_get_indent_spaces_none(self):
        """Test indent spaces when no command exists."""
        interpreter = CommandInterpreter()

        indent = interpreter.get_indent_spaces([])

        assert indent is None

    def test_get_indent_spaces_invalid(self):
        """Test indent spaces with invalid number."""
        cmd = MarkerCommand("indent-space", ["abc"], "")
        interpreter = CommandInterpreter()

        indent = interpreter.get_indent_spaces([cmd])

        assert indent is None

    def test_get_indent_tabs(self):
        """Test indent tabs extraction."""
        cmd = MarkerCommand("indent-tab", ["2"], "")
        interpreter = CommandInterpreter()

        indent = interpreter.get_indent_tabs([cmd])

        assert indent == 2

    def test_get_indent_tabs_none(self):
        """Test indent tabs when no command exists."""
        interpreter = CommandInterpreter()

        indent = interpreter.get_indent_tabs([])

        assert indent is None

    def test_get_indent_tabs_invalid(self):
        """Test indent tabs with invalid number."""
        cmd = MarkerCommand("indent-tab", ["xyz"], "")
        interpreter = CommandInterpreter()

        indent = interpreter.get_indent_tabs([cmd])

        assert indent is None

    def test_has_download_split_true(self):
        """Test download split option detection."""
        cmd = MarkerCommand("download", ["split"], "")
        interpreter = CommandInterpreter()

        assert interpreter.has_download_split([cmd]) is True

    def test_has_download_split_false(self):
        """Test download split option not present."""
        cmd = MarkerCommand("download", [], "")
        interpreter = CommandInterpreter()

        assert interpreter.has_download_split([cmd]) is False

    def test_has_download_split_no_download_command(self):
        """Test download split when no download command exists."""
        cmd = MarkerCommand("hide", [], "")
        interpreter = CommandInterpreter()

        assert interpreter.has_download_split([cmd]) is False

    def test_has_download_split_multiple_download_commands(self):
        """Test download split with multiple download commands."""
        cmd1 = MarkerCommand("download", [], "")
        cmd2 = MarkerCommand("download", ["split"], "")
        interpreter = CommandInterpreter()

        # Should return True if any download command has split
        assert interpreter.has_download_split([cmd1, cmd2]) is True


class TestMarkerIntegration:
    """Integration tests for marker parsing."""

    def test_realistic_code_cell(self):
        """Test realistic code cell with marker."""
        content = """# @nemo-nb: hide
from nemo import Client
client = Client()
print(client)"""

        parser = MarkerParser()
        interpreter = CommandInterpreter()

        cleaned, commands = parser.parse_cell(content, "code")

        assert "@nemo-nb" not in cleaned
        assert "from nemo import Client" in cleaned
        assert interpreter.should_hide(commands) is True

    def test_realistic_markdown_cell(self):
        """Test realistic markdown cell with HTML comment markers."""
        content = """<!-- @nemo-nb: wrap-cell-start :::{note} Important -->
<!-- @nemo-nb: wrap-cell-end ::: -->
This is an important note about the API."""

        parser = MarkerParser()
        interpreter = CommandInterpreter()

        cleaned, commands = parser.parse_cell(content, "markdown")

        assert "@nemo-nb" not in cleaned
        assert "This is an important note" in cleaned

        wrap_start = interpreter.get_wrap_cell_start(commands)
        wrap_end = interpreter.get_wrap_cell_end(commands)
        assert wrap_start == ":::{note} Important"
        assert wrap_end == ":::"

    def test_marker_at_end_of_cell(self):
        """Test marker at the end of a cell."""
        content = """code here
# @nemo-nb: hide"""

        parser = MarkerParser()
        cleaned, commands = parser.parse_cell(content, "code")

        assert "@nemo-nb" not in cleaned
        assert "code here" in cleaned
        assert len(commands) == 1

    def test_indent_marker(self):
        """Test indent-space marker parsing."""
        content = """# @nemo-nb: indent-space 4
print('hello')"""

        parser = MarkerParser()
        interpreter = CommandInterpreter()

        cleaned, commands = parser.parse_cell(content, "code")

        assert "@nemo-nb" not in cleaned
        assert "print('hello')" in cleaned
        assert interpreter.get_indent_spaces(commands) == 4

    def test_indent_tab_marker(self):
        """Test indent-tab marker parsing."""
        content = """# @nemo-nb: indent-tab 2
print('hello')"""

        parser = MarkerParser()
        interpreter = CommandInterpreter()

        cleaned, commands = parser.parse_cell(content, "code")

        assert "@nemo-nb" not in cleaned
        assert "print('hello')" in cleaned
        assert interpreter.get_indent_tabs(commands) == 2

    def test_indent_with_wrap(self):
        """Test indent marker combined with wrap."""
        content = """# @nemo-nb: wrap-cell-start :::{dropdown} Example
# @nemo-nb: wrap-cell-end :::
# @nemo-nb: indent-space 3
print('indented dropdown')"""

        parser = MarkerParser()
        interpreter = CommandInterpreter()

        cleaned, commands = parser.parse_cell(content, "code")

        assert len(commands) == 3
        assert interpreter.get_wrap_cell_start(commands) == ":::{dropdown} Example"
        assert interpreter.get_wrap_cell_end(commands) == ":::"
        assert interpreter.get_indent_spaces(commands) == 3

    def test_parse_wrap_cell_start_command(self):
        """Test parsing wrap-cell-start command with full directive syntax."""
        content = "# @nemo-nb: wrap-cell-start :::{dropdown} Click to expand\ncode here"
        parser = MarkerParser()

        cleaned, commands = parser.parse_cell(content, "code")

        assert len(commands) == 1
        assert commands[0].command == "wrap-cell-start"
        assert " ".join(commands[0].args) == ":::{dropdown} Click to expand"
        assert "code here" in cleaned

    def test_parse_wrap_cell_end_command(self):
        """Test parsing wrap-cell-end command."""
        content = "code here\n# @nemo-nb: wrap-cell-end :::"
        parser = MarkerParser()

        cleaned, commands = parser.parse_cell(content, "code")

        assert len(commands) == 1
        assert commands[0].command == "wrap-cell-end"
        assert commands[0].args == [":::"]
        assert "code here" in cleaned

    def test_parse_insert_command(self):
        """Test parsing insert command."""
        content = "# @nemo-nb: insert :sync: sdk\ncode here"
        parser = MarkerParser()

        cleaned, commands = parser.parse_cell(content, "code")

        assert len(commands) == 1
        assert commands[0].command == "insert"
        assert " ".join(commands[0].args) == ":sync: sdk"
        assert commands[0].position == 0  # Insert at beginning
        assert "code here" in cleaned
        assert ":sync:" not in cleaned

    def test_insert_command_preserves_position(self):
        """Test that insert commands track their relative position."""
        content = """line1
# @nemo-nb: insert :option: value
line2
# @nemo-nb: insert :another: option
line3"""
        parser = MarkerParser()

        cleaned, commands = parser.parse_cell(content, "code")

        inserts = [cmd for cmd in commands if cmd.command == "insert"]
        assert len(inserts) == 2
        assert inserts[0].position == 1  # After line1
        assert inserts[1].position == 2  # After line2
        assert "line1\nline2\nline3" == cleaned

    def test_get_wrap_cell_start(self):
        """Test wrap-cell-start extraction."""
        cmd = MarkerCommand("wrap-cell-start", ["::::{tab-set}"], "")
        interpreter = CommandInterpreter()

        wrap_start = interpreter.get_wrap_cell_start([cmd])

        assert wrap_start == "::::{tab-set}"

    def test_get_wrap_cell_end(self):
        """Test wrap-cell-end extraction."""
        cmd = MarkerCommand("wrap-cell-end", ["::::"], "")
        interpreter = CommandInterpreter()

        wrap_end = interpreter.get_wrap_cell_end([cmd])

        assert wrap_end == "::::"

    def test_get_insert_lines(self):
        """Test insert lines extraction."""
        cmd1 = MarkerCommand("insert", [":sync:", "sdk"], "")
        cmd2 = MarkerCommand("insert", [":emphasize-lines:", "18-21"], "")
        interpreter = CommandInterpreter()

        insert_lines = interpreter.get_insert_lines([cmd1, cmd2])

        assert len(insert_lines) == 2
        assert insert_lines[0] == ":sync: sdk"
        assert insert_lines[1] == ":emphasize-lines: 18-21"

    def test_parse_language_command(self):
        """Test parsing language command."""
        content = "# @nemo-nb: language {code-block}\ncode here"
        parser = MarkerParser()

        cleaned, commands = parser.parse_cell(content, "code")

        assert len(commands) == 1
        assert commands[0].command == "language"
        assert commands[0].args == ["{code-block}"]
        assert "code here" in cleaned

    def test_get_language_override(self):
        """Test language override extraction."""
        cmd = MarkerCommand("language", ["{code-block}"], "")
        interpreter = CommandInterpreter()

        lang = interpreter.get_language_override([cmd])

        assert lang == "{code-block}"

    def test_get_language_override_none(self):
        """Test language override when no command exists."""
        interpreter = CommandInterpreter()

        lang = interpreter.get_language_override([])

        assert lang is None

    def test_slash_marker_all_commands(self):
        """Test slash marker with various commands."""
        test_cases = [
            ("// @nemo-nb: hide\ncode", "hide", []),
            ("// @nemo-nb: wrap-cell-start :::{note}\ncode", "wrap-cell-start", [":::{note}"]),
            ("// @nemo-nb: insert :sync: sdk\ncode", "insert", [":sync: sdk"]),
            ("// @nemo-nb: indent-space 4\ncode", "indent-space", ["4"]),
            ("// @nemo-nb: language python\ncode", "language", ["python"]),
        ]

        parser = MarkerParser()

        for content, expected_cmd, expected_args in test_cases:
            cleaned, commands = parser.parse_cell(content, "code")
            assert len(commands) == 1
            assert commands[0].command == expected_cmd
            assert commands[0].args == expected_args
            assert "@nemo-nb" not in cleaned

    def test_notebook_convert_4_space_to_tab_marker(self):
        """Test notebook-convert-4-space-to-tab marker parsing."""
        content = "# @nemo-nb: notebook-convert-4-space-to-tab\nprint('hello')"
        parser = MarkerParser()
        interpreter = CommandInterpreter()

        cleaned, commands = parser.parse_cell(content, "code")

        assert len(commands) == 1
        assert commands[0].command == "notebook-convert-4-space-to-tab"
        assert interpreter.has_notebook_convert_4_space_to_tab(commands) is True
        assert "@nemo-nb" not in cleaned

    def test_notebook_convert_4_space_to_tab_not_present(self):
        """Test when notebook-convert-4-space-to-tab is not present."""
        content = "print('hello')"
        parser = MarkerParser()
        interpreter = CommandInterpreter()

        cleaned, commands = parser.parse_cell(content, "code")

        assert interpreter.has_notebook_convert_4_space_to_tab(commands) is False

    def test_parse_insert_code_block_start(self):
        """Test parsing insert-code-block-start command."""
        content = "# @nemo-nb: insert-code-block-start :emphasize-lines: 18-21\ncode here"
        parser = MarkerParser()

        cleaned, commands = parser.parse_cell(content, "code")

        assert len(commands) == 1
        assert commands[0].command == "insert-code-block-start"
        assert " ".join(commands[0].args) == ":emphasize-lines: 18-21"
        assert "code here" in cleaned
        assert "@nemo-nb" not in cleaned

    def test_get_insert_code_block_start(self):
        """Test insert-code-block-start extraction."""
        cmd = MarkerCommand("insert-code-block-start", [":emphasize-lines:", "18-21"], "")
        interpreter = CommandInterpreter()

        options = interpreter.get_insert_code_block_start([cmd])

        assert options == ":emphasize-lines: 18-21"

    def test_get_insert_code_block_start_multiple_options(self):
        """Test insert-code-block-start with multiple options."""
        content = "# @nemo-nb: insert-code-block-start :linenos:\ncode"
        parser = MarkerParser()
        interpreter = CommandInterpreter()

        cleaned, commands = parser.parse_cell(content, "code")

        options = interpreter.get_insert_code_block_start(commands)
        assert options == ":linenos:"

    def test_get_insert_code_block_start_none(self):
        """Test insert-code-block-start when no command exists."""
        interpreter = CommandInterpreter()

        options = interpreter.get_insert_code_block_start([])

        assert options is None

    def test_parse_download_split_marker(self):
        """Test parsing download split marker."""
        content = "<!-- @nemo-nb: download split -->\n# Tutorial"
        parser = MarkerParser()
        interpreter = CommandInterpreter()

        cleaned, commands = parser.parse_cell(content, "markdown")

        assert "@nemo-nb" not in cleaned
        assert "# Tutorial" in cleaned
        assert len(commands) == 1
        assert commands[0].command == "download"
        assert commands[0].args == ["split"]
        assert interpreter.has_download_split(commands) is True
