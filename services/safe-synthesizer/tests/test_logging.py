# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Unit tests for the JSONFormatter logging class."""

import json
import logging
import sys
from datetime import datetime
from io import StringIO

import pytest
from nmp.safe_synthesizer.tasks.safe_synthesizer.logging_setup import JSONFormatter, configure_logging


class TestJSONFormatter:
    """Test suite for JSONFormatter class."""

    @pytest.fixture
    def formatter(self):
        """Create a JSONFormatter instance for testing."""
        return JSONFormatter(datefmt="%Y-%m-%dT%H:%M:%S")

    @pytest.fixture
    def logger_with_formatter(self, formatter):
        """Create a logger configured with JSONFormatter."""
        logger = logging.getLogger("test_logger")
        logger.setLevel(logging.DEBUG)
        logger.handlers.clear()

        stream = StringIO()
        handler = logging.StreamHandler(stream)
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        return logger, stream

    def test_formatter_creates_valid_json(self, logger_with_formatter):
        """Test that the formatter outputs valid JSON."""
        logger, stream = logger_with_formatter

        logger.info("Test message")
        output = stream.getvalue().strip()

        # Should be valid JSON
        log_entry = json.loads(output)
        assert isinstance(log_entry, dict)

    def test_formatter_includes_all_fields(self, logger_with_formatter):
        """Test that the formatter includes all required fields."""
        logger, stream = logger_with_formatter

        logger.info("Test message")
        output = stream.getvalue().strip()
        log_entry = json.loads(output)

        # Check all required fields are present
        assert "timestamp" in log_entry
        assert "level" in log_entry
        assert "logger" in log_entry
        assert "message" in log_entry

    def test_formatter_preserves_simple_message(self, logger_with_formatter):
        """Test that simple messages are preserved correctly."""
        logger, stream = logger_with_formatter

        test_message = "Simple log message"
        logger.info(test_message)
        output = stream.getvalue().strip()
        log_entry = json.loads(output)

        assert log_entry["message"] == test_message

    def test_formatter_escapes_quotes(self, logger_with_formatter):
        """Test that quotes in messages are properly escaped."""
        logger, stream = logger_with_formatter

        test_message = "Message with \"double quotes\" and 'single quotes'"
        logger.error(test_message)
        output = stream.getvalue().strip()

        # Should be valid JSON
        log_entry = json.loads(output)
        assert log_entry["message"] == test_message

    def test_formatter_escapes_backslashes(self, logger_with_formatter):
        """Test that backslashes are properly escaped."""
        logger, stream = logger_with_formatter

        test_message = "Path: C:\\Users\\Documents\\file.txt"
        logger.info(test_message)
        output = stream.getvalue().strip()

        log_entry = json.loads(output)
        assert log_entry["message"] == test_message

    def test_formatter_handles_newlines_and_tabs(self, logger_with_formatter):
        """Test that newlines and tabs are properly escaped."""
        logger, stream = logger_with_formatter

        test_message = "Line 1\nLine 2\tTabbed"
        logger.warning(test_message)
        output = stream.getvalue().strip()

        log_entry = json.loads(output)
        assert log_entry["message"] == test_message

    def test_formatter_handles_angle_brackets(self, logger_with_formatter):
        """Test that angle brackets are properly handled."""
        logger, stream = logger_with_formatter

        test_message = "Error: <class 'ValueError'> occurred"
        logger.error(test_message)
        output = stream.getvalue().strip()

        log_entry = json.loads(output)
        assert log_entry["message"] == test_message

    def test_formatter_handles_problematic_error_message(self, logger_with_formatter):
        """Test the exact problematic message from the user's issue."""
        logger, stream = logger_with_formatter

        # The exact message that was causing issues
        test_message = (
            "Failed to load JSON from file '/tmp/tmp7n1d5g05/databricks-dolly-15k.jsonl' "
            "with error <class 'pyarrow.lib.ArrowInvalid'>: JSON parse error: "
            "Missing a comma or '}' after an object member. in row 4"
        )

        logger.error(test_message)
        output = stream.getvalue().strip()

        # Should produce valid JSON
        log_entry = json.loads(output)
        assert log_entry["message"] == test_message
        assert log_entry["level"] == "ERROR"

    def test_formatter_handles_json_like_content(self, logger_with_formatter):
        """Test that messages containing JSON-like content are handled correctly."""
        logger, stream = logger_with_formatter

        # Message that looks like malformed JSON
        test_message = '{"key": value without quotes, "error": <class>}'
        logger.info(test_message)
        output = stream.getvalue().strip()

        log_entry = json.loads(output)
        assert log_entry["message"] == test_message

    def test_formatter_handles_unicode(self, logger_with_formatter):
        """Test that unicode characters are preserved."""
        logger, stream = logger_with_formatter

        test_message = "Unicode: émojis 🎉 中文 עברית"
        logger.info(test_message)
        output = stream.getvalue().strip()

        log_entry = json.loads(output)
        assert log_entry["message"] == test_message

    def test_formatter_handles_empty_message(self, logger_with_formatter):
        """Test that empty messages are handled correctly."""
        logger, stream = logger_with_formatter

        logger.info("")
        output = stream.getvalue().strip()

        log_entry = json.loads(output)
        assert log_entry["message"] == ""

    def test_formatter_preserves_log_level(self, logger_with_formatter):
        """Test that log levels are correctly recorded."""
        logger, stream = logger_with_formatter

        levels = [
            (logging.DEBUG, "DEBUG"),
            (logging.INFO, "INFO"),
            (logging.WARNING, "WARNING"),
            (logging.ERROR, "ERROR"),
            (logging.CRITICAL, "CRITICAL"),
        ]

        for level_num, level_name in levels:
            stream.truncate(0)
            stream.seek(0)

            logger.log(level_num, "Test")
            output = stream.getvalue().strip()
            log_entry = json.loads(output)

            assert log_entry["level"] == level_name

    def test_formatter_preserves_logger_name(self, formatter):
        """Test that logger names are correctly recorded."""
        logger = logging.getLogger("datasets.packaged_modules.json.json")
        logger.handlers.clear()

        stream = StringIO()
        handler = logging.StreamHandler(stream)
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        logger.error("Test")
        output = stream.getvalue().strip()
        log_entry = json.loads(output)

        assert log_entry["logger"] == "datasets.packaged_modules.json.json"

    def test_formatter_output_can_be_reserialized(self, logger_with_formatter):
        """Test that formatter output can be re-serialized without errors."""
        logger, stream = logger_with_formatter

        test_message = 'Complex: "quotes", newlines\n, and <special> chars!'
        logger.info(test_message)
        output = stream.getvalue().strip()

        # Parse once
        log_entry = json.loads(output)

        # Re-serialize
        reserialized = json.dumps(log_entry)

        # Parse again
        reparsed = json.loads(reserialized)

        assert reparsed["message"] == test_message

    def test_formatter_timestamp_format(self, logger_with_formatter):
        """Test that timestamps are formatted correctly."""
        logger, stream = logger_with_formatter

        logger.info("Test")
        output = stream.getvalue().strip()
        log_entry = json.loads(output)

        # Should match the format: %Y-%m-%dT%H:%M:%S
        timestamp = log_entry["timestamp"]
        assert "T" in timestamp
        assert len(timestamp) == 19  # YYYY-MM-DDTHH:MM:SS

        # Should be parseable as a datetime
        datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S")

    def test_formatter_with_percentage_signs(self, logger_with_formatter):
        """Test that percentage signs are handled correctly."""
        logger, stream = logger_with_formatter

        test_message = "Progress: 100% complete, disk at 95%"
        logger.info(test_message)
        output = stream.getvalue().strip()

        log_entry = json.loads(output)
        assert log_entry["message"] == test_message

    def test_formatter_with_curly_braces(self, logger_with_formatter):
        """Test that curly braces are handled correctly."""
        logger, stream = logger_with_formatter

        test_message = "Dict: {key: value}, Set: {1, 2, 3}"
        logger.info(test_message)
        output = stream.getvalue().strip()

        log_entry = json.loads(output)
        assert log_entry["message"] == test_message


class TestConfigureLogging:
    """Test suite for configure_logging function."""

    def test_configure_logging_sets_up_handlers(self):
        """Test that configure_logging sets up logging handlers."""
        # Clear existing handlers
        root_logger = logging.getLogger()
        root_logger.handlers.clear()

        configure_logging("INFO")

        # Should have at least one handler (stderr)
        assert len(root_logger.handlers) >= 1

        # Check that the formatter is JSONFormatter
        handler = root_logger.handlers[0]
        assert isinstance(handler.formatter, JSONFormatter)

    def test_configure_logging_respects_log_level(self):
        """Test that configure_logging respects the log level parameter."""
        root_logger = logging.getLogger()

        configure_logging("DEBUG")
        assert root_logger.level == logging.DEBUG

        configure_logging("WARNING")
        assert root_logger.level == logging.WARNING

        configure_logging("ERROR")
        assert root_logger.level == logging.ERROR

    def test_configure_logging_clears_existing_handlers(self):
        """Test that configure_logging clears existing handlers."""
        root_logger = logging.getLogger()

        # Add a dummy handler
        dummy_handler = logging.StreamHandler()
        root_logger.addHandler(dummy_handler)

        configure_logging("INFO")

        # Should have cleared and recreated handlers
        assert dummy_handler not in root_logger.handlers

    def test_configure_logging_stderr_handler_works(self):
        """Test that the stderr handler actually logs output."""
        # Capture stderr
        old_stderr = sys.stderr
        sys.stderr = StringIO()

        try:
            configure_logging("INFO")
            logger = logging.getLogger("test")
            logger.info("Test message")

            output = sys.stderr.getvalue()
            assert "Test message" in output

            # Should be valid JSON
            log_entry = json.loads(output.strip())
            assert log_entry["message"] == "Test message"

        finally:
            sys.stderr = old_stderr

    def test_configure_logging_creates_file_handler_when_env_var_set(self, tmp_path):
        """Test that a file handler is created when NEMO_JOB_LOG_PATH is set."""
        import os

        # Set the environment variable to a temporary directory
        log_dir = tmp_path / "logs"
        old_env = os.environ.get("NEMO_JOB_LOG_PATH")

        try:
            os.environ["NEMO_JOB_LOG_PATH"] = str(log_dir)

            # Configure logging
            configure_logging("INFO")

            # Should have created the log directory
            assert log_dir.exists()

            # Should have created the log file
            log_file = log_dir / "application.log"

            # Log a message
            logger = logging.getLogger("test_file")
            logger.info("Test file logging")

            # File should exist and contain the message
            assert log_file.exists()
            content = log_file.read_text()
            assert "Test file logging" in content

            # Content should be valid JSON
            log_entry = json.loads(content.strip())
            assert log_entry["message"] == "Test file logging"

        finally:
            # Restore environment
            if old_env is not None:
                os.environ["NEMO_JOB_LOG_PATH"] = old_env
            elif "NEMO_JOB_LOG_PATH" in os.environ:
                del os.environ["NEMO_JOB_LOG_PATH"]

            # Clear handlers
            logging.getLogger().handlers.clear()


class TestIntegration:
    """Integration tests for the complete logging flow."""

    def test_end_to_end_logging_flow(self):
        """Test the complete flow from log to JSON output."""
        old_stderr = sys.stderr
        sys.stderr = StringIO()

        try:
            # Configure logging
            configure_logging("ERROR")

            # Get a logger
            logger = logging.getLogger("datasets.packaged_modules.json.json")

            # Log the problematic message
            problematic_message = (
                "Failed to load JSON from file '/tmp/tmp7n1d5g05/databricks-dolly-15k.jsonl' "
                "with error <class 'pyarrow.lib.ArrowInvalid'>: JSON parse error: "
                "Missing a comma or '}' after an object member. in row 4"
            )
            logger.error(problematic_message)

            # Get output
            output = sys.stderr.getvalue().strip()

            # Verify it's valid JSON
            log_entry = json.loads(output)

            # Verify all fields
            assert log_entry["level"] == "ERROR"
            assert log_entry["logger"] == "datasets.packaged_modules.json.json"
            assert log_entry["message"] == problematic_message
            assert "timestamp" in log_entry

            # Verify it can be re-serialized
            reserialized = json.dumps(log_entry)
            reparsed = json.loads(reserialized)
            assert reparsed["message"] == problematic_message

        finally:
            sys.stderr = old_stderr
