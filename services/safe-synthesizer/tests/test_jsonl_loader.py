# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Tests for JSONL file loading with unicode and escaping support."""

from dataclasses import dataclass

import pytest
from nmp.safe_synthesizer.tasks.safe_synthesizer.jsonl_loader import (
    load_jsonl_file,
    try_repair_json_line,
)


@dataclass
class RepairTestCase:
    """Test case for JSON line repair."""

    line: str
    expected: str


class TestTryRepairJsonLine:
    """Tests for the JSON line repair function."""

    @pytest.mark.parametrize(
        "line",
        [
            '{"key": "value", "num": 123}',
            '{"content": "what\\u2019s the name"}',
            '{"content": "He said \\"hello\\" to her"}',
        ],
    )
    def test_unchanged_lines(self, line):
        """Valid JSON and legitimate escapes should pass through unchanged."""
        assert try_repair_json_line(line) == line

    @pytest.mark.parametrize(
        "case",
        [
            RepairTestCase(
                '{"content": "The Lumi\\u00e8res\\"}',
                '{"content": "The Lumi\\u00e8res"}',
            ),
            RepairTestCase(
                '{"items": ["item1\\", "item2\\"]}',
                '{"items": ["item1", "item2"]}',
            ),
            RepairTestCase(
                '{"a": "val1\\", "b": "val2"}',
                '{"a": "val1", "b": "val2"}',
            ),
            RepairTestCase(
                '{"a": "x\\", "b": "y\\", "c": "z\\"}',
                '{"a": "x", "b": "y", "c": "z"}',
            ),
        ],
    )
    def test_repairs_escaped_quotes(self, case):
        """Escaped quotes before }, ], or , should be repaired."""
        assert try_repair_json_line(case.line) == case.expected


@dataclass
class ErrorHandlingTestCase:
    """Test case for error handling scenarios."""

    content: str
    strict_mode: bool
    should_raise: bool
    expected_count: int | None = None
    error_contains: list[str] | None = None


class TestLoadJsonlFile:
    """Tests for the JSONL file loader."""

    def test_loads_valid_jsonl(self, tmp_path):
        """Should load a valid JSONL file."""
        filepath = tmp_path / "test.jsonl"
        filepath.write_text(
            '{"a": 1, "b": "hello"}\n{"a": 2, "b": "world"}\n',
            encoding="utf-8",
        )

        df = load_jsonl_file(str(filepath))

        assert len(df) == 2
        assert list(df.columns) == ["a", "b"]
        assert df.iloc[0]["a"] == 1
        assert df.iloc[1]["b"] == "world"

    def test_skips_empty_lines(self, tmp_path):
        """Should skip empty lines in JSONL file."""
        filepath = tmp_path / "test.jsonl"
        filepath.write_text(
            '{"a": 1}\n\n{"a": 2}\n   \n{"a": 3}\n',
            encoding="utf-8",
        )

        df = load_jsonl_file(str(filepath))

        assert len(df) == 3

    def test_handles_nested_structures(self, tmp_path):
        """Should properly handle nested JSON structures."""
        filepath = tmp_path / "test.jsonl"
        filepath.write_text(
            '{"messages": [{"role": "user", "content": "hello"}, {"role": "system", "content": "hi"}]}\n',
            encoding="utf-8",
        )

        df = load_jsonl_file(str(filepath))

        assert len(df) == 1
        messages = df.iloc[0]["messages"]
        assert len(messages) == 2
        assert messages[0]["role"] == "user"

    def test_loads_unicode_escape_sequences(self, tmp_path):
        """Should properly handle unicode escape sequences like \\u2019."""
        filepath = tmp_path / "test.jsonl"
        filepath.write_text(
            '{"content": "what\\u2019s the name"}\n',
            encoding="utf-8",
        )

        df = load_jsonl_file(str(filepath))

        assert len(df) == 1
        # \u2019 is the right single quotation mark (')
        assert df.iloc[0]["content"] == "what\u2019s the name"

    def test_repairs_common_escaping_issues(self, tmp_path):
        """Should repair common JSON escaping issues."""
        filepath = tmp_path / "test.jsonl"
        # Simulates the problematic pattern from databricks-dolly-15k
        content = (
            '{"messages": [{"role": "user", "content": "The Lumi\\u00e8res\\"}, '
            '{"role": "system", "content": "response"}]}\n'
        )
        filepath.write_text(content, encoding="utf-8")

        df = load_jsonl_file(str(filepath))

        assert len(df) == 1
        assert df.iloc[0]["messages"][0]["content"] == "The Lumières"

    def test_handles_special_characters(self, tmp_path):
        """Should handle various special characters in content."""
        filepath = tmp_path / "test.jsonl"
        filepath.write_text(
            '{"content": "Line1\\nLine2\\tTabbed"}\n'
            '{"content": "Quote: \\"hello\\""}\n'
            '{"content": "Emoji: \\ud83d\\ude00"}\n',
            encoding="utf-8",
        )

        df = load_jsonl_file(str(filepath))

        assert len(df) == 3
        assert df.iloc[0]["content"] == "Line1\nLine2\tTabbed"
        assert df.iloc[1]["content"] == 'Quote: "hello"'
        # Emoji is a smiling face
        assert df.iloc[2]["content"] == "Emoji: 😀"

    @pytest.mark.parametrize(
        "case",
        [
            ErrorHandlingTestCase(
                content='{"valid": "json"}\nthis is not json at all\n',
                strict_mode=False,
                should_raise=False,
                expected_count=1,
            ),
            ErrorHandlingTestCase(
                content='{"valid": "json"}\nthis is not json at all\n',
                strict_mode=True,
                should_raise=True,
                error_contains=["malformed JSON lines", "line 2"],
            ),
            ErrorHandlingTestCase(
                content="",
                strict_mode=False,
                should_raise=True,
                error_contains=["no valid records"],
            ),
            ErrorHandlingTestCase(
                content='{"valid": 1}\nbad line 1\n{"valid": 2}\nbad line 2\nbad line 3\n',
                strict_mode=True,
                should_raise=True,
                error_contains=["3 malformed JSON lines"],
            ),
            ErrorHandlingTestCase(
                content='{"valid": 1}\nbad line 1\n{"valid": 2}\nbad line 2\nbad line 3\n',
                strict_mode=False,
                should_raise=False,
                expected_count=2,
            ),
            ErrorHandlingTestCase(
                content='{"valid": 1}\nbad1\nbad2\nbad3\nbad4\nbad5\nbad6\nbad7\n',
                strict_mode=True,
                should_raise=True,
                error_contains=["7 malformed JSON lines", "... and 2 more errors"],
            ),
        ],
    )
    def test_error_handling(self, tmp_path, case):
        """Should handle errors appropriately based on strict mode."""
        filepath = tmp_path / "test.jsonl"
        filepath.write_text(case.content, encoding="utf-8")

        if case.should_raise:
            with pytest.raises(ValueError) as exc_info:
                load_jsonl_file(str(filepath), strict=case.strict_mode)
            if case.error_contains:
                error_msg = str(exc_info.value)
                for expected_text in case.error_contains:
                    assert expected_text in error_msg
        else:
            df = load_jsonl_file(str(filepath), strict=case.strict_mode)
            assert len(df) == case.expected_count
