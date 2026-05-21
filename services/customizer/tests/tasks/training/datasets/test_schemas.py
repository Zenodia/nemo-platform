# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""
Unit tests for dataset utilities.

These tests are CPU-safe and run in regular CI - no GPU dependencies.
"""

import pytest
from nmp.customizer.tasks.training.datasets.schemas import (
    BINARY_PREFERENCE_DATASET,
    HELPSTEER3_DATASET,
    PREFERENCE_DATASET,
    TULU3_PREFERENCE_DATASET,
    BinaryPreferenceDatasetItemSchema,
    ChatMessage,
    CompletionItem,
    DPOPreferenceDatasetSchemaType,
    FunctionCallDetails,
    FunctionDefinitionDetails,
    FunctionParameters,
    HelpSteer3DatasetItemSchema,
    PreferenceDatasetItemSchema,
    SFTChatMessage,
    ToolCall,
    ToolDefinition,
    Tulu3PreferenceDatasetItemSchema,
    get_preference_dataset_discriminator,
)
from pydantic import ValidationError

# =============================================================================
# Preference Dataset Schema Tests
# =============================================================================


class TestChatMessageSchema:
    """Tests for ChatMessage schema."""

    def test_valid_message(self):
        """Test valid message creation."""
        msg = ChatMessage(role="user", content="Hello")
        assert msg.role == "user"
        assert msg.content == "Hello"

    def test_assistant_message(self):
        """Test assistant role message."""
        msg = ChatMessage(role="assistant", content="Hi there!")
        assert msg.role == "assistant"

    def test_system_message(self):
        """Test system role message."""
        msg = ChatMessage(role="system", content="You are a helpful assistant.")
        assert msg.role == "system"


class TestCompletionItemSchema:
    """Tests for CompletionItem schema."""

    def test_valid_completion(self):
        """Test valid completion item."""
        completion = CompletionItem(
            rank=0,
            completion=[ChatMessage(role="assistant", content="Response")],
        )
        assert completion.rank == 0
        assert len(completion.completion) == 1
        assert completion.completion[0].content == "Response"

    def test_multi_message_completion(self):
        """Test completion with multiple messages."""
        completion = CompletionItem(
            rank=1,
            completion=[
                ChatMessage(role="assistant", content="Part 1"),
                ChatMessage(role="assistant", content="Part 2"),
            ],
        )
        assert len(completion.completion) == 2


class TestPreferenceDatasetItemSchema:
    """Tests for PreferenceDatasetItemSchema (native format)."""

    def test_valid_preference_data(self):
        """Test valid native preference format."""
        data = PreferenceDatasetItemSchema(
            context=[ChatMessage(role="user", content="What is 2+2?")],
            completions=[
                CompletionItem(
                    rank=0,
                    completion=[ChatMessage(role="assistant", content="4")],
                ),
                CompletionItem(
                    rank=1,
                    completion=[ChatMessage(role="assistant", content="5")],
                ),
            ],
        )
        assert len(data.context) == 1
        assert len(data.completions) == 2
        assert data.completions[0].rank == 0

    def test_multi_turn_context(self):
        """Test multi-turn conversation context."""
        data = PreferenceDatasetItemSchema(
            context=[
                ChatMessage(role="user", content="Hello"),
                ChatMessage(role="assistant", content="Hi!"),
                ChatMessage(role="user", content="How are you?"),
            ],
            completions=[
                CompletionItem(
                    rank=0,
                    completion=[ChatMessage(role="assistant", content="I'm doing great!")],
                ),
            ],
        )
        assert len(data.context) == 3

    def test_from_dict(self):
        """Test creation from dictionary (JSON parsing)."""
        data_dict = {
            "context": [{"role": "user", "content": "Test"}],
            "completions": [
                {"rank": 0, "completion": [{"role": "assistant", "content": "Good"}]},
                {"rank": 1, "completion": [{"role": "assistant", "content": "Bad"}]},
            ],
        }
        data = PreferenceDatasetItemSchema.model_validate(data_dict)
        assert data.context[0].content == "Test"
        assert data.completions[0].completion[0].content == "Good"


class TestBinaryPreferenceDatasetItemSchema:
    """Tests for BinaryPreferenceDatasetItemSchema."""

    def test_valid_binary_data_string_prompt(self):
        """Test valid binary format with string prompt."""
        data = BinaryPreferenceDatasetItemSchema(
            prompt="What is the capital of France?",
            chosen="The capital of France is Paris.",
            rejected="The capital of France is London.",
        )
        assert data.prompt == "What is the capital of France?"
        assert data.chosen == "The capital of France is Paris."
        assert data.rejected == "The capital of France is London."

    def test_valid_binary_data_message_prompt(self):
        """Test valid binary format with message list prompt."""
        data = BinaryPreferenceDatasetItemSchema(
            prompt=[ChatMessage(role="user", content="What is 2+2?")],
            chosen="4",
            rejected="5",
        )
        assert isinstance(data.prompt, list)
        assert data.prompt[0].content == "What is 2+2?"

    def test_from_dict(self):
        """Test creation from dictionary."""
        data_dict = {
            "prompt": "Question?",
            "chosen": "Good answer",
            "rejected": "Bad answer",
        }
        data = BinaryPreferenceDatasetItemSchema.model_validate(data_dict)
        assert data.prompt == "Question?"


class TestHelpSteer3DatasetItemSchema:
    """Tests for HelpSteer3DatasetItemSchema."""

    def test_valid_helpsteer3_string_context(self):
        """Test valid HelpSteer3 format with string context."""
        data = HelpSteer3DatasetItemSchema(
            context="Explain quantum computing",
            response1="Quantum computing uses qubits...",
            response2="Quantum computing is magic...",
            overall_preference=-2,
        )
        assert data.context == "Explain quantum computing"
        assert data.overall_preference == -2

    def test_valid_helpsteer3_message_context(self):
        """Test valid HelpSteer3 format with message list context."""
        data = HelpSteer3DatasetItemSchema(
            context=[ChatMessage(role="user", content="Explain AI")],
            response1="AI is artificial intelligence...",
            response2="AI is robots...",
            overall_preference=1,
        )
        assert isinstance(data.context, list)
        assert data.overall_preference == 1

    def test_zero_preference_tie(self):
        """Test zero preference indicating a tie."""
        data = HelpSteer3DatasetItemSchema(
            context="Test",
            response1="A",
            response2="B",
            overall_preference=0,
        )
        assert data.overall_preference == 0

    def test_from_dict(self):
        """Test creation from dictionary."""
        data_dict = {
            "context": "Question",
            "response1": "Answer 1",
            "response2": "Answer 2",
            "overall_preference": -1,
        }
        data = HelpSteer3DatasetItemSchema.model_validate(data_dict)
        assert data.overall_preference == -1


class TestTulu3PreferenceDatasetItemSchema:
    """Tests for Tulu3PreferenceDatasetItemSchema."""

    def test_valid_tulu3_data(self):
        """Test valid Tulu3 format."""
        data = Tulu3PreferenceDatasetItemSchema(
            chosen=[
                ChatMessage(role="user", content="Hello"),
                ChatMessage(role="assistant", content="Hi! How can I help?"),
            ],
            rejected=[
                ChatMessage(role="user", content="Hello"),
                ChatMessage(role="assistant", content="Go away."),
            ],
        )
        assert len(data.chosen) == 2
        assert len(data.rejected) == 2
        assert data.chosen[-1].role == "assistant"

    def test_multi_turn_tulu3(self):
        """Test multi-turn Tulu3 conversation."""
        data = Tulu3PreferenceDatasetItemSchema(
            chosen=[
                ChatMessage(role="user", content="Hi"),
                ChatMessage(role="assistant", content="Hello!"),
                ChatMessage(role="user", content="How are you?"),
                ChatMessage(role="assistant", content="I'm doing well, thanks!"),
            ],
            rejected=[
                ChatMessage(role="user", content="Hi"),
                ChatMessage(role="assistant", content="Hello!"),
                ChatMessage(role="user", content="How are you?"),
                ChatMessage(role="assistant", content="None of your business."),
            ],
        )
        assert len(data.chosen) == 4
        assert data.chosen[-1].content == "I'm doing well, thanks!"

    def test_from_dict(self):
        """Test creation from dictionary."""
        data_dict = {
            "chosen": [
                {"role": "user", "content": "Test"},
                {"role": "assistant", "content": "Good response"},
            ],
            "rejected": [
                {"role": "user", "content": "Test"},
                {"role": "assistant", "content": "Bad response"},
            ],
        }
        data = Tulu3PreferenceDatasetItemSchema.model_validate(data_dict)
        assert data.chosen[-1].content == "Good response"


class TestGetPreferenceDatasetDiscriminator:
    """Tests for the discriminator function."""

    def test_identifies_preference_format(self):
        """Test identification of native preference format."""
        data = {
            "context": [{"role": "user", "content": "Test"}],
            "completions": [{"rank": 0, "completion": [{"role": "assistant", "content": "A"}]}],
        }
        assert get_preference_dataset_discriminator(data) == "PreferenceDataset"

    def test_identifies_helpsteer3_format(self):
        """Test identification of HelpSteer3 format."""
        data = {
            "context": "Test",
            "response1": "A",
            "response2": "B",
            "overall_preference": -1,
        }
        assert get_preference_dataset_discriminator(data) == HELPSTEER3_DATASET

    def test_identifies_tulu3_format(self):
        """Test identification of Tulu3 format (list of messages)."""
        data = {
            "chosen": [{"role": "user", "content": "Hi"}, {"role": "assistant", "content": "Hello"}],
            "rejected": [{"role": "user", "content": "Hi"}, {"role": "assistant", "content": "Bye"}],
        }
        assert get_preference_dataset_discriminator(data) == TULU3_PREFERENCE_DATASET

    def test_identifies_binary_format(self):
        """Test identification of binary format (string responses)."""
        data = {
            "prompt": "Question",
            "chosen": "Good answer",
            "rejected": "Bad answer",
        }
        assert get_preference_dataset_discriminator(data) == BINARY_PREFERENCE_DATASET

    def test_binary_with_prompt_only(self):
        """Test binary format identification with prompt field."""
        data = {
            "prompt": "Test prompt",
            "chosen": "A",
            "rejected": "B",
        }
        assert get_preference_dataset_discriminator(data) == BINARY_PREFERENCE_DATASET

    def test_default_fallback(self):
        """Test default fallback for unrecognized format."""
        data = {"unknown_field": "value"}
        assert get_preference_dataset_discriminator(data) == PREFERENCE_DATASET


class TestDPOPreferenceDatasetSchemaTypeUnion:
    """Tests for the DPOPreferenceDatasetSchemaType union with discriminator."""

    def test_parses_preference_format(self):
        """Test parsing native preference format through union."""
        from pydantic import TypeAdapter

        adapter = TypeAdapter(DPOPreferenceDatasetSchemaType)
        data = {
            "context": [{"role": "user", "content": "Test"}],
            "completions": [
                {"rank": 0, "completion": [{"role": "assistant", "content": "Good"}]},
                {"rank": 1, "completion": [{"role": "assistant", "content": "Bad"}]},
            ],
        }
        result = adapter.validate_python(data)
        assert isinstance(result, PreferenceDatasetItemSchema)
        assert result.context[0].content == "Test"

    def test_parses_binary_format(self):
        """Test parsing binary preference format through union."""
        from pydantic import TypeAdapter

        adapter = TypeAdapter(DPOPreferenceDatasetSchemaType)
        data = {
            "prompt": "What is 2+2?",
            "chosen": "4",
            "rejected": "5",
        }
        result = adapter.validate_python(data)
        assert isinstance(result, BinaryPreferenceDatasetItemSchema)
        assert result.prompt == "What is 2+2?"

    def test_parses_helpsteer3_format(self):
        """Test parsing HelpSteer3 format through union."""
        from pydantic import TypeAdapter

        adapter = TypeAdapter(DPOPreferenceDatasetSchemaType)
        data = {
            "context": "Explain something",
            "response1": "Good explanation",
            "response2": "Bad explanation",
            "overall_preference": -1,
        }
        result = adapter.validate_python(data)
        assert isinstance(result, HelpSteer3DatasetItemSchema)
        assert result.overall_preference == -1

    def test_parses_tulu3_format(self):
        """Test parsing Tulu3 format through union."""
        from pydantic import TypeAdapter

        adapter = TypeAdapter(DPOPreferenceDatasetSchemaType)
        data = {
            "chosen": [
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi there!"},
            ],
            "rejected": [
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Whatever."},
            ],
        }
        result = adapter.validate_python(data)
        assert isinstance(result, Tulu3PreferenceDatasetItemSchema)
        assert result.chosen[-1].content == "Hi there!"


# =============================================================================
# SFT Chat Message Schema Tests
# =============================================================================


class TestSFTChatMessageSchema:
    """Tests for SFTChatMessage schema validation."""

    def test_valid_message_with_content_only(self):
        """Test valid message with only content field."""
        msg = SFTChatMessage(role="assistant", content="Hello, world!")
        assert msg.role == "assistant"
        assert msg.content == "Hello, world!"
        assert msg.thinking is None
        assert msg.tool_calls is None

    def test_valid_message_with_thinking_only(self):
        """Test valid message with only thinking field."""
        msg = SFTChatMessage(role="assistant", thinking="Let me think about this...")
        assert msg.role == "assistant"
        assert msg.thinking == "Let me think about this..."
        assert msg.content is None
        assert msg.tool_calls is None

    def test_valid_message_with_tool_calls_only(self):
        """Test valid message with only tool_calls field."""
        tool_calls = [
            ToolCall(
                type="function",
                function=FunctionCallDetails(
                    name="get_weather",
                    arguments={"location": "NYC"},
                ),
            )
        ]
        msg = SFTChatMessage(role="assistant", tool_calls=tool_calls)
        assert msg.role == "assistant"
        assert msg.tool_calls == tool_calls
        assert msg.content is None
        assert msg.thinking is None

    def test_valid_message_with_content_and_tool_calls(self):
        """Test valid message with both content and tool_calls."""
        tool_calls = [
            ToolCall(
                type="function",
                function=FunctionCallDetails(
                    name="search",
                    arguments={"query": "test"},
                ),
            )
        ]
        msg = SFTChatMessage(
            role="assistant",
            content="Let me search for that",
            tool_calls=tool_calls,
        )
        assert msg.content == "Let me search for that"
        assert msg.tool_calls == tool_calls
        assert msg.thinking is None

    def test_valid_message_with_thinking_and_tool_calls(self):
        """Test valid message with both thinking and tool_calls."""
        tool_calls = [
            ToolCall(
                type="function",
                function=FunctionCallDetails(
                    name="calculate",
                    arguments={"expression": "2+2"},
                ),
            )
        ]
        msg = SFTChatMessage(
            role="assistant",
            thinking="I should calculate this",
            tool_calls=tool_calls,
        )
        assert msg.thinking == "I should calculate this"
        assert msg.tool_calls == tool_calls
        assert msg.content is None

    def test_invalid_message_with_no_fields(self):
        """Test that message with no content, thinking, or tool_calls raises error."""
        with pytest.raises(ValidationError, match="Message must have at least one of"):
            SFTChatMessage(role="assistant")

    def test_invalid_message_with_both_content_and_thinking(self):
        """Test that message with both content and thinking raises error."""
        with pytest.raises(ValidationError, match="cannot have both content and thinking"):
            SFTChatMessage(
                role="assistant",
                content="Hello",
                thinking="Should I say hello?",
            )

    def test_invalid_message_with_all_three_fields(self):
        """Test that message with content, thinking, and tool_calls raises error."""
        tool_calls = [
            ToolCall(
                type="function",
                function=FunctionCallDetails(
                    name="test",
                    arguments={},
                ),
            )
        ]
        with pytest.raises(ValidationError, match="cannot have both content and thinking"):
            SFTChatMessage(
                role="assistant",
                content="Hello",
                thinking="Thinking...",
                tool_calls=tool_calls,
            )

    def test_message_from_dict_with_content(self):
        """Test creation from dictionary with content."""
        data = {"role": "user", "content": "What is 2+2?"}
        msg = SFTChatMessage.model_validate(data)
        assert msg.role == "user"
        assert msg.content == "What is 2+2?"

    def test_message_from_dict_with_thinking(self):
        """Test creation from dictionary with thinking."""
        data = {"role": "assistant", "thinking": "Let me calculate this"}
        msg = SFTChatMessage.model_validate(data)
        assert msg.role == "assistant"
        assert msg.thinking == "Let me calculate this"

    def test_message_from_dict_with_tool_calls(self):
        """Test creation from dictionary with tool_calls."""
        data = {
            "role": "assistant",
            "tool_calls": [
                {
                    "type": "function",
                    "function": {
                        "name": "get_weather",
                        "arguments": {"location": "SF"},
                    },
                }
            ],
        }
        msg = SFTChatMessage.model_validate(data)
        assert msg.role == "assistant"
        assert len(msg.tool_calls) == 1
        assert msg.tool_calls[0].function.name == "get_weather"

    def test_message_forbids_extra_fields(self):
        """Test that extra fields are forbidden."""
        with pytest.raises(ValidationError):
            SFTChatMessage.model_validate(
                {
                    "role": "assistant",
                    "content": "Hello",
                    "extra_field": "not allowed",
                }
            )


# =============================================================================
# Tool Call and Tool Definition Schema Tests
# =============================================================================


class TestFunctionCallDetailsSchema:
    """Tests for FunctionCallDetails schema."""

    def test_valid_function_call(self):
        """Test valid function call details creation."""
        call = FunctionCallDetails(
            name="get_weather",
            arguments={"location": "San Francisco"},
            content_type=None,
        )
        assert call.name == "get_weather"
        assert call.arguments == {"location": "San Francisco"}
        assert call.content_type is None

    def test_function_call_with_content_type(self):
        """Test function call with optional content_type."""
        call = FunctionCallDetails(
            name="get_weather",
            content_type="application/json",
            arguments={"location": "NYC"},
        )
        assert call.name == "get_weather"
        assert call.content_type == "application/json"
        assert call.arguments == {"location": "NYC"}

    def test_function_call_empty_arguments(self):
        """Test function call with empty arguments."""
        call = FunctionCallDetails(
            name="get_time",
            arguments={},
        )
        assert call.name == "get_time"
        assert call.arguments == {}

    def test_function_call_from_dict(self):
        """Test creation from dictionary."""
        data = {
            "name": "search",
            "arguments": {"query": "hello world"},
        }
        call = FunctionCallDetails.model_validate(data)
        assert call.name == "search"
        assert call.arguments["query"] == "hello world"

    def test_function_call_missing_name_raises(self):
        """Test that missing name raises validation error."""
        with pytest.raises(ValidationError):
            FunctionCallDetails.model_validate({"arguments": {}})

    def test_function_call_missing_arguments_raises(self):
        """Test that missing arguments raises validation error."""
        with pytest.raises(ValidationError):
            FunctionCallDetails.model_validate({"name": "test"})


class TestFunctionParametersSchema:
    """Tests for FunctionParameters schema."""

    def test_valid_function_parameters(self):
        """Test valid function parameters creation."""
        params = FunctionParameters(
            type="object",
            properties={
                "location": {"type": "string", "description": "The city name"},
                "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
            },
        )
        assert params.type == "object"
        assert "location" in params.properties
        assert "unit" in params.properties

    def test_function_parameters_empty_properties(self):
        """Test function parameters with empty properties."""
        params = FunctionParameters(
            type="object",
            properties={},
        )
        assert params.type == "object"
        assert params.properties == {}

    def test_function_parameters_from_dict(self):
        """Test creation from dictionary."""
        data = {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
            },
        }
        params = FunctionParameters.model_validate(data)
        assert params.type == "object"
        assert "query" in params.properties

    def test_function_parameters_invalid_type_raises(self):
        """Test that invalid type raises validation error."""
        with pytest.raises(ValidationError):
            FunctionParameters.model_validate({"type": "array", "properties": {}})

    def test_function_parameters_missing_type_raises(self):
        """Test that missing type raises validation error."""
        with pytest.raises(ValidationError):
            FunctionParameters.model_validate({"properties": {}})

    def test_function_parameters_missing_properties_raises(self):
        """Test that missing properties raises validation error."""
        with pytest.raises(ValidationError):
            FunctionParameters.model_validate({"type": "object"})


class TestFunctionDefinitionDetailsSchema:
    """Tests for FunctionDefinitionDetails schema."""

    def test_valid_function_definition(self):
        """Test valid function definition creation."""
        func_def = FunctionDefinitionDetails(
            name="get_weather",
            description="Get the current weather for a location",
            parameters=FunctionParameters(
                type="object",
                properties={"location": {"type": "string"}},
            ),
        )
        assert func_def.name == "get_weather"
        assert func_def.description == "Get the current weather for a location"
        assert func_def.parameters.type == "object"
        assert func_def.required is None

    def test_function_definition_with_required(self):
        """Test function definition with required parameters."""
        func_def = FunctionDefinitionDetails(
            name="search",
            description="Search for information",
            parameters=FunctionParameters(
                type="object",
                properties={
                    "query": {"type": "string"},
                    "limit": {"type": "integer"},
                },
            ),
            required=["query"],
        )
        assert func_def.required == ["query"]

    def test_function_definition_from_dict(self):
        """Test creation from dictionary."""
        data = {
            "name": "calculate",
            "description": "Perform a calculation",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {"type": "string"},
                },
            },
            "required": ["expression"],
        }
        func_def = FunctionDefinitionDetails.model_validate(data)
        assert func_def.name == "calculate"
        assert func_def.description == "Perform a calculation"
        assert func_def.parameters.type == "object"
        assert func_def.required == ["expression"]

    def test_function_definition_missing_name_raises(self):
        """Test that missing name raises validation error."""
        with pytest.raises(ValidationError):
            FunctionDefinitionDetails.model_validate(
                {
                    "description": "Test",
                    "parameters": {"type": "object", "properties": {}},
                }
            )

    def test_function_definition_missing_description_raises(self):
        """Test that missing description raises validation error."""
        with pytest.raises(ValidationError):
            FunctionDefinitionDetails.model_validate(
                {
                    "name": "test",
                    "parameters": {"type": "object", "properties": {}},
                }
            )

    def test_function_definition_missing_parameters_raises(self):
        """Test that missing parameters raises validation error."""
        with pytest.raises(ValidationError):
            FunctionDefinitionDetails.model_validate(
                {
                    "name": "test",
                    "description": "Test function",
                }
            )


class TestToolCallSchema:
    """Tests for ToolCall schema."""

    def test_valid_tool_call(self):
        """Test valid tool call creation."""
        tool_call = ToolCall(
            type="function",
            function=FunctionCallDetails(
                name="get_weather",
                arguments={"location": "NYC"},
            ),
        )
        assert tool_call.type == "function"
        assert tool_call.function.name == "get_weather"
        assert tool_call.function.arguments == {"location": "NYC"}

    def test_tool_call_from_dict(self):
        """Test creation from dictionary."""
        data = {
            "type": "function",
            "function": {
                "name": "search",
                "arguments": {"query": "test"},
            },
        }
        tool_call = ToolCall.model_validate(data)
        assert tool_call.type == "function"
        assert tool_call.function.name == "search"
        assert tool_call.function.arguments == {"query": "test"}

    def test_tool_call_with_content_type(self):
        """Test tool call with content_type in function."""
        data = {
            "type": "function",
            "function": {
                "name": "get_data",
                "content_type": "text/plain",
                "arguments": {},
            },
        }
        tool_call = ToolCall.model_validate(data)
        assert tool_call.function.content_type == "text/plain"

    def test_tool_call_invalid_type_raises(self):
        """Test that invalid type raises validation error."""
        with pytest.raises(ValidationError):
            ToolCall.model_validate(
                {
                    "type": "invalid",
                    "function": {"name": "test", "arguments": {}},
                }
            )

    def test_tool_call_missing_function_raises(self):
        """Test that missing function raises validation error."""
        with pytest.raises(ValidationError):
            ToolCall.model_validate({"type": "function"})


class TestToolDefinitionSchema:
    """Tests for ToolDefinition schema."""

    def test_valid_tool_definition(self):
        """Test valid tool definition creation."""
        tool_def = ToolDefinition(
            type="function",
            function=FunctionDefinitionDetails(
                name="get_weather",
                description="Get weather for a location",
                parameters=FunctionParameters(
                    type="object",
                    properties={"location": {"type": "string"}},
                ),
            ),
        )
        assert tool_def.type == "function"
        assert tool_def.function.name == "get_weather"
        assert tool_def.function.description == "Get weather for a location"

    def test_tool_definition_from_dict(self):
        """Test creation from dictionary."""
        data = {
            "type": "function",
            "function": {
                "name": "search",
                "description": "Search the web",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                    },
                },
                "required": ["query"],
            },
        }
        tool_def = ToolDefinition.model_validate(data)
        assert tool_def.type == "function"
        assert tool_def.function.name == "search"
        assert tool_def.function.description == "Search the web"
        assert tool_def.function.required == ["query"]

    def test_tool_definition_invalid_type_raises(self):
        """Test that invalid type raises validation error."""
        with pytest.raises(ValidationError):
            ToolDefinition.model_validate(
                {
                    "type": "invalid",
                    "function": {
                        "name": "test",
                        "description": "Test",
                        "parameters": {"type": "object", "properties": {}},
                    },
                }
            )

    def test_tool_definition_missing_function_raises(self):
        """Test that missing function raises validation error."""
        with pytest.raises(ValidationError):
            ToolDefinition.model_validate({"type": "function"})

    def test_tool_definition_nested_validation(self):
        """Test that nested validation catches errors in function definition."""
        with pytest.raises(ValidationError):
            ToolDefinition.model_validate(
                {
                    "type": "function",
                    "function": {
                        "name": "test",
                        # Missing description and parameters
                    },
                }
            )
