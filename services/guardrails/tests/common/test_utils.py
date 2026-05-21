# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import pytest
from nmp.guardrails.app.common.utils import (
    _IMAGE_URL_HINT,
    MODEL_INITIALIZATION_ERROR_PREFIX,
    clean_llm_call_error,
    clean_model_initialization_error,
)


class TestCleanModelInitializationError:
    def test_standard_error_message_is_cleaned(self):
        """Test that the standard prefix format is properly removed."""
        error = "Failed to initialize model 'meta/llama-3.3-70b-instruct' with provider 'nimchat' in 'chat' mode: Invalid API key for model 'meta/llama-3.3-70b-instruct'"
        result = clean_model_initialization_error(error)
        assert result == "Invalid API key for model 'meta/llama-3.3-70b-instruct'"

    def test_error_with_multiple_colons_splits_on_first(self):
        """Test that only the first colon is used for splitting."""
        error = (
            "Failed to initialize model 'test' with provider 'nim' in 'chat' mode: Error: Connection refused: port 8080"
        )
        result = clean_model_initialization_error(error)
        assert result == "Error: Connection refused: port 8080"

    def test_error_without_prefix_returns_original(self):
        """Test that messages without the expected prefix are returned unchanged."""
        error = "Some other error message"
        result = clean_model_initialization_error(error)
        assert result == "Some other error message"

    def test_error_with_partial_prefix_returns_original(self):
        """Test that messages with partial prefix (no colon) return original."""
        error = "Failed to initialize model 'test' with provider 'nim' in 'chat' mode"
        result = clean_model_initialization_error(error)
        assert result == "Failed to initialize model 'test' with provider 'nim' in 'chat' mode"

    def test_error_with_prefix_but_empty_content_returns_original(self):
        """Test that messages with prefix but empty content after colon return original."""
        error = "Failed to initialize model 'test' with provider 'nim' in 'chat' mode:"
        result = clean_model_initialization_error(error)
        assert result == "Failed to initialize model 'test' with provider 'nim' in 'chat' mode:"

    def test_empty_string_returns_empty(self):
        """Test that empty string input returns empty string."""
        result = clean_model_initialization_error("")
        assert result == ""

    def test_error_with_colon_but_no_prefix_returns_original(self):
        """Test that messages with colon but without the specific prefix return original."""
        error = "Connection error: timeout after 30s"
        result = clean_model_initialization_error(error)
        assert result == "Connection error: timeout after 30s"


class TestCleanLLMCallError:
    def test_unknown_error_returned_unchanged(self):
        """Messages that match no transformer are returned as-is."""
        error = "Something went wrong internally"
        assert clean_llm_call_error(error) == error

    def test_has_image_urls_false_does_not_append_hint(self):
        """Hint is not appended when `has_image_urls` is False."""
        error = "Internal Server Error"
        result = clean_llm_call_error(error, has_image_urls=False)
        assert _IMAGE_URL_HINT not in result

    def test_has_image_urls_true_appends_hint(self):
        """Hint is appended when `has_image_urls` is True."""
        error = "Internal Server Error"
        result = clean_llm_call_error(error, has_image_urls=True)
        assert result == f"{error} {_IMAGE_URL_HINT}"


class TestModelInitializationErrorPrefix:
    """
    Tests to ensure our MODEL_INITIALIZATION_ERROR_PREFIX stays in sync
    with the nemo-guardrails library.

    If these tests fail, it means the nemo-guardrails library has changed
    the error message format in ModelInitializationError, and we need to update
    MODEL_INITIALIZATION_ERROR_PREFIX accordingly.
    """

    def test_llmrails_initialization_error_contains_expected_prefix(self):
        """
        Triggers a ModelInitializationError by instantiating LLMRails with an
        invalid model configuration, and verifies that the error message contains the expected prefix.
        """
        from nemoguardrails import LLMRails, RailsConfig
        from nemoguardrails.rails.llm.llmrails import ModelInitializationError

        # Create a config with an invalid/nonexistent LLM provider
        # This will cause LLMRails to fail during model initialization
        config = RailsConfig.from_content(
            yaml_content="""
            models:
              - type: main
                engine: nonexistent_provider
                model: fake-model
            """
        )

        with pytest.raises(ModelInitializationError) as exc_info:
            LLMRails(config=config)

        error_message = str(exc_info.value)

        # Verify the error message contains our expected prefix
        assert MODEL_INITIALIZATION_ERROR_PREFIX in error_message

        # Verify our cleaning function works on the real error
        cleaned = clean_model_initialization_error(error_message)

        # The cleaned message should not start with the prefix
        assert not cleaned.startswith(MODEL_INITIALIZATION_ERROR_PREFIX)
