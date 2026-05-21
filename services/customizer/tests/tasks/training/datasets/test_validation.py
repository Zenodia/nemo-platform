# SPDX-FileCopyrightText: Copyright (c) 2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
# property and proprietary rights in and to this material, related
# documentation and any modifications thereto. Any use, reproduction,
# disclosure or distribution of this material and related documentation
# without an express license agreement from NVIDIA CORPORATION or
# its affiliates is strictly prohibited.

"""
Unit tests for dataset validation utilities.

These tests verify the detect_dpo_schema_name function correctly identifies
different DPO preference dataset formats from JSONL files.
"""

import json
from pathlib import Path

import pytest
from nmp.customizer.entities.values import TrainingType
from nmp.customizer.tasks.training.datasets.preparation import DatasetFormatError
from nmp.customizer.tasks.training.datasets.schemas import (
    BINARY_PREFERENCE_DATASET,
    HELPSTEER3_DATASET,
    TULU3_PREFERENCE_DATASET,
    get_preference_dataset_discriminator,
    get_sft_dataset_discriminator,
)
from nmp.customizer.tasks.training.datasets.validation import (
    DPO_SCHEMA,
    SFT_SCHEMA,
    DatasetValidator,
    detect_dpo_schema_name,
)

# Path to test data files
TESTDATA_DIR = Path(__file__).parent.parent.parent / "testdata"
DPO_TESTDATA_DIR = TESTDATA_DIR / "dpo"
SFT_TESTDATA_DIR = TESTDATA_DIR / "sft"


class TestDetectDpoSchemaName:
    """Tests for detect_dpo_schema_name function."""

    def test_detects_helpsteer3_schema(self):
        """Test detection of HelpSteer3 format from help_steer_small test data."""
        file_path = DPO_TESTDATA_DIR / "help_steer_small" / "validation.jsonl"
        assert file_path.exists(), f"Test data file not found: {file_path}"

        result = detect_dpo_schema_name(file_path)

        assert result == HELPSTEER3_DATASET

    def test_detects_tulu3_schema(self):
        """Test detection of Tulu3PreferenceDataset format from tulu3 test data."""
        file_path = DPO_TESTDATA_DIR / "tulu3" / "validation.jsonl"
        assert file_path.exists(), f"Test data file not found: {file_path}"

        result = detect_dpo_schema_name(file_path)

        assert result == TULU3_PREFERENCE_DATASET

    def test_detects_binary_schema(self, tmp_path: Path):
        """Test detection of BinaryPreferenceDataset format from fixture data."""
        # Create a test file with binary preference format
        binary_data = {
            "prompt": "What is the capital of France?",
            "chosen": "The capital of France is Paris.",
            "rejected": "The capital of France is London.",
        }
        test_file = tmp_path / "binary_validation.jsonl"
        test_file.write_text(json.dumps(binary_data) + "\n")

        result = detect_dpo_schema_name(test_file)

        assert result == "BinaryPreferenceDataset"

    def test_detects_preference_schema(self, tmp_path: Path):
        """Test detection of PreferenceDataset (native) format from fixture data."""
        # Create a test file with native preference format
        preference_data = {
            "context": [{"role": "user", "content": "What is 2+2?"}],
            "completions": [
                {"rank": 0, "completion": [{"role": "assistant", "content": "4"}]},
                {"rank": 1, "completion": [{"role": "assistant", "content": "5"}]},
            ],
        }
        test_file = tmp_path / "preference_validation.jsonl"
        test_file.write_text(json.dumps(preference_data) + "\n")

        result = detect_dpo_schema_name(test_file)

        assert result == "PreferenceDataset"

    def test_accepts_path_as_string(self, tmp_path: Path):
        """Test that function accepts file_path as string."""
        binary_data = {"prompt": "Q?", "chosen": "A", "rejected": "B"}
        test_file = tmp_path / "test.jsonl"
        test_file.write_text(json.dumps(binary_data) + "\n")

        result = detect_dpo_schema_name(str(test_file))

        assert result == "BinaryPreferenceDataset"

    def test_raises_error_for_missing_file(self):
        """Test that function raises error for missing file."""
        with pytest.raises(DatasetFormatError, match="not found"):
            detect_dpo_schema_name("/nonexistent/path/file.jsonl")

    def test_raises_error_for_empty_file(self, tmp_path: Path):
        """Test that function raises error for empty file."""
        test_file = tmp_path / "empty.jsonl"
        test_file.write_text("")

        with pytest.raises(DatasetFormatError, match="empty"):
            detect_dpo_schema_name(test_file)

    def test_raises_error_for_invalid_json(self, tmp_path: Path):
        """Test that function raises error for invalid JSON."""
        test_file = tmp_path / "invalid.jsonl"
        test_file.write_text("not valid json\n")

        with pytest.raises(DatasetFormatError, match="not valid JSON"):
            detect_dpo_schema_name(test_file)

    def test_binary_with_message_list_prompt(self, tmp_path: Path):
        """Test binary format detection with prompt as message list."""
        binary_data = {
            "prompt": [{"role": "user", "content": "What is 2+2?"}],
            "chosen": "4",
            "rejected": "5",
        }
        test_file = tmp_path / "binary_msg_prompt.jsonl"
        test_file.write_text(json.dumps(binary_data) + "\n")

        result = detect_dpo_schema_name(test_file)

        assert result == "BinaryPreferenceDataset"


class TestValidateDPOPreferenceDatasetSchema:
    """Tests for DPO_SCHEMA and DPOPreferenceDatasetSchemaType validation."""

    def test_dpo_schema_structure(self):
        """Test that DPO schema has correct structure with all preference formats."""
        schema = DPO_SCHEMA(None)

        assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
        # Schema should have oneOf for discriminated union
        assert "oneOf" in schema
        # Schema should have $defs with the sub-schemas
        assert "$defs" in schema
        assert "PreferenceDatasetItemSchema" in schema["$defs"]
        assert "BinaryPreferenceDatasetItemSchema" in schema["$defs"]
        assert "HelpSteer3DatasetItemSchema" in schema["$defs"]
        assert "Tulu3PreferenceDatasetItemSchema" in schema["$defs"]

    def test_validates_real_helpsteer3_data(self, tmp_path: Path):
        """Test validation of real HelpSteer3 data from help_steer_small dataset."""
        file_path = DPO_TESTDATA_DIR / "help_steer_small" / "validation.jsonl"
        assert file_path.exists(), f"Test data file not found: {file_path}"

        # Read only the first line from the source file
        with open(file_path) as f:
            first_line = f.readline()

        # Write the single line to a temp file
        test_file = tmp_path / "helpsteer3_single.jsonl"
        test_file.write_text(first_line)

        validator = DatasetValidator(training_type=TrainingType.DPO)

        # Should not raise - validates a single record
        validator.validate_dataset(str(test_file))

    def test_validates_real_tulu3_data(self, tmp_path: Path):
        """Test validation of real Tulu3 data from tulu3 dataset."""
        file_path = DPO_TESTDATA_DIR / "tulu3" / "validation.jsonl"
        assert file_path.exists(), f"Test data file not found: {file_path}"

        # Read only the first line from the source file
        with open(file_path) as f:
            first_line = f.readline()

        # Write the single line to a temp file
        test_file = tmp_path / "tulu3_single.jsonl"
        test_file.write_text(first_line)

        validator = DatasetValidator(training_type=TrainingType.DPO)

        # Should not raise - validates a single record
        validator.validate_dataset(str(test_file))

    def test_validates_binary_preference_format(self, tmp_path: Path):
        """Test validation of BinaryPreferenceDataset format."""
        validator = DatasetValidator(training_type=TrainingType.DPO)

        binary_data = {
            "prompt": "What is the capital of France?",
            "chosen": "The capital of France is Paris.",
            "rejected": "The capital of France is London.",
        }
        test_file = tmp_path / "binary_preference.jsonl"
        test_file.write_text(json.dumps(binary_data) + "\n")

        # Should not raise
        validator.validate_dataset(str(test_file))

    def test_validates_binary_preference_with_message_list_prompt(self, tmp_path: Path):
        """Test validation of BinaryPreferenceDataset with prompt as message list."""
        validator = DatasetValidator(training_type=TrainingType.DPO)

        binary_data = {
            "prompt": [{"role": "user", "content": "What is 2+2?"}],
            "chosen": "4",
            "rejected": "5",
        }
        test_file = tmp_path / "binary_msg_prompt.jsonl"
        test_file.write_text(json.dumps(binary_data) + "\n")

        # Should not raise
        validator.validate_dataset(str(test_file))

    def test_validates_native_preference_format(self, tmp_path: Path):
        """Test validation of native PreferenceDataset format."""
        validator = DatasetValidator(training_type=TrainingType.DPO)

        preference_data = {
            "context": [{"role": "user", "content": "What is 2+2?"}],
            "completions": [
                {"rank": 0, "completion": [{"role": "assistant", "content": "4"}]},
                {"rank": 1, "completion": [{"role": "assistant", "content": "5"}]},
            ],
        }
        test_file = tmp_path / "native_preference.jsonl"
        test_file.write_text(json.dumps(preference_data) + "\n")

        # Should not raise
        validator.validate_dataset(str(test_file))

    def test_validates_helpsteer3_format(self, tmp_path: Path):
        """Test validation of HelpSteer3Dataset format."""
        validator = DatasetValidator(training_type=TrainingType.DPO)

        helpsteer_data = {
            "context": "Explain quantum computing",
            "response1": "Quantum computing uses qubits...",
            "response2": "Quantum computing is magic...",
            "overall_preference": -2,
        }
        test_file = tmp_path / "helpsteer3.jsonl"
        test_file.write_text(json.dumps(helpsteer_data) + "\n")

        # Should not raise
        validator.validate_dataset(str(test_file))

    def test_validates_helpsteer3_with_message_context(self, tmp_path: Path):
        """Test validation of HelpSteer3Dataset with context as message list."""
        validator = DatasetValidator(training_type=TrainingType.DPO)

        helpsteer_data = {
            "context": [{"role": "user", "content": "Explain quantum computing"}],
            "response1": "Quantum computing uses qubits...",
            "response2": "Quantum computing is magic...",
            "overall_preference": 1,
        }
        test_file = tmp_path / "helpsteer3_msg.jsonl"
        test_file.write_text(json.dumps(helpsteer_data) + "\n")

        # Should not raise
        validator.validate_dataset(str(test_file))

    def test_validates_tulu3_format(self, tmp_path: Path):
        """Test validation of Tulu3PreferenceDataset format."""
        validator = DatasetValidator(training_type=TrainingType.DPO)

        tulu3_data = {
            "chosen": [
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi! How can I help?"},
            ],
            "rejected": [
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Go away."},
            ],
        }
        test_file = tmp_path / "tulu3.jsonl"
        test_file.write_text(json.dumps(tulu3_data) + "\n")

        # Should not raise
        validator.validate_dataset(str(test_file))

    def test_rejects_binary_missing_chosen(self, tmp_path: Path):
        """Test that validation fails for binary format missing chosen field."""
        validator = DatasetValidator(training_type=TrainingType.DPO)

        invalid_data = {
            "prompt": "What is AI?",
            "rejected": "AI is magic.",
        }
        test_file = tmp_path / "invalid_binary.jsonl"
        test_file.write_text(json.dumps(invalid_data) + "\n")

        with pytest.raises(DatasetFormatError):
            validator.validate_dataset(str(test_file))

    def test_rejects_binary_missing_rejected(self, tmp_path: Path):
        """Test that validation fails for binary format missing rejected field."""
        validator = DatasetValidator(training_type=TrainingType.DPO)

        invalid_data = {
            "prompt": "What is AI?",
            "chosen": "AI stands for Artificial Intelligence.",
        }
        test_file = tmp_path / "invalid_binary_no_rejected.jsonl"
        test_file.write_text(json.dumps(invalid_data) + "\n")

        with pytest.raises(DatasetFormatError):
            validator.validate_dataset(str(test_file))

    def test_rejects_tulu3_with_wrong_type(self, tmp_path: Path):
        """Test that validation fails when tulu3 chosen/rejected are strings instead of lists."""
        validator = DatasetValidator(training_type=TrainingType.DPO)

        invalid_data = {
            "chosen": "This should be a list of messages",
            "rejected": "This too should be a list",
        }
        test_file = tmp_path / "invalid_tulu3.jsonl"
        test_file.write_text(json.dumps(invalid_data) + "\n")

        # This will be detected as BinaryPreferenceDataset format (prompt/chosen/rejected)
        # but will fail because prompt is missing
        with pytest.raises(DatasetFormatError):
            validator.validate_dataset(str(test_file))

    def test_rejects_helpsteer3_missing_overall_preference(self, tmp_path: Path):
        """Test that validation fails for HelpSteer3 missing overall_preference."""
        validator = DatasetValidator(training_type=TrainingType.DPO)

        invalid_data = {
            "context": "Explain something",
            "response1": "Response one",
            "response2": "Response two",
            # missing overall_preference
        }
        test_file = tmp_path / "invalid_helpsteer3.jsonl"
        test_file.write_text(json.dumps(invalid_data) + "\n")

        with pytest.raises(DatasetFormatError):
            validator.validate_dataset(str(test_file))

    def test_rejects_native_format_missing_completions(self, tmp_path: Path):
        """Test that validation fails for native format missing completions."""
        validator = DatasetValidator(training_type=TrainingType.DPO)

        invalid_data = {
            "context": [{"role": "user", "content": "What is 2+2?"}],
            # missing completions
        }
        test_file = tmp_path / "invalid_native.jsonl"
        test_file.write_text(json.dumps(invalid_data) + "\n")

        with pytest.raises(DatasetFormatError):
            validator.validate_dataset(str(test_file))

    def test_validates_complete_jsonl_file(self, tmp_path: Path):
        """Test validation of a complete JSONL file with multiple entries."""
        validator = DatasetValidator(training_type=TrainingType.DPO)

        test_data = [
            {"prompt": "Q1", "chosen": "A1 good", "rejected": "A1 bad"},
            {"prompt": "Q2", "chosen": "A2 good", "rejected": "A2 bad"},
            {"prompt": "Q3", "chosen": "A3 good", "rejected": "A3 bad"},
        ]

        test_file = tmp_path / "test_dpo.jsonl"
        test_file.write_text("\n".join(json.dumps(item) for item in test_data))

        # Should validate all lines successfully
        validator.validate_dataset(str(test_file))

    def test_rejects_jsonl_with_invalid_line(self, tmp_path: Path):
        """Test that validation properly detects invalid lines in JSONL file."""
        validator = DatasetValidator(training_type=TrainingType.DPO)

        test_data = [
            {"prompt": "Q1", "chosen": "A1 good", "rejected": "A1 bad"},
            {"prompt": "Q2", "chosen": "A2 good"},  # Missing rejected
            {"prompt": "Q3", "chosen": "A3 good", "rejected": "A3 bad"},
        ]

        test_file = tmp_path / "test_invalid_dpo.jsonl"
        test_file.write_text("\n".join(json.dumps(item) for item in test_data))

        # Should fail on the second line
        with pytest.raises(DatasetFormatError):
            validator.validate_dataset(str(test_file))

    def test_discriminator_detects_preference_formats(self):
        """Test discriminator correctly identifies different preference formats."""
        # Native PreferenceDataset format
        native_data = {
            "context": [{"role": "user", "content": "Hello"}],
            "completions": [{"rank": 0, "completion": [{"role": "assistant", "content": "Hi"}]}],
        }
        assert get_preference_dataset_discriminator(native_data) == "PreferenceDataset"

        # BinaryPreferenceDataset format
        binary_data = {"prompt": "Q?", "chosen": "A", "rejected": "B"}
        assert get_preference_dataset_discriminator(binary_data) == BINARY_PREFERENCE_DATASET

        # HelpSteer3Dataset format
        helpsteer_data = {
            "context": "Question",
            "response1": "R1",
            "response2": "R2",
            "overall_preference": 1,
        }
        assert get_preference_dataset_discriminator(helpsteer_data) == HELPSTEER3_DATASET

        # Tulu3PreferenceDataset format
        tulu3_data = {
            "chosen": [{"role": "user", "content": "Hi"}, {"role": "assistant", "content": "Hello"}],
            "rejected": [{"role": "user", "content": "Hi"}, {"role": "assistant", "content": "Bye"}],
        }
        assert get_preference_dataset_discriminator(tulu3_data) == TULU3_PREFERENCE_DATASET

    def test_dpo_all_formats_in_same_validator(self):
        """Test validator handles all DPO formats with same instance."""
        validator = DatasetValidator(TrainingType.DPO)
        schema = DPO_SCHEMA()

        # Validate binary format
        binary_data = {"prompt": "Q", "chosen": "A", "rejected": "B"}
        validator._validate_json_object(binary_data, schema)

        # Validate tulu3 format
        tulu3_data = {
            "chosen": [{"role": "user", "content": "Q"}, {"role": "assistant", "content": "A"}],
            "rejected": [{"role": "user", "content": "Q"}, {"role": "assistant", "content": "B"}],
        }
        validator._validate_json_object(tulu3_data, schema)

        # Validate helpsteer3 format
        helpsteer_data = {"context": "Q", "response1": "R1", "response2": "R2", "overall_preference": 0}
        validator._validate_json_object(helpsteer_data, schema)


class TestValidateSFTPromptTemplateSchema:
    """Tests for SFT_SCHEMA function."""

    def test_default_schema_structure(self):
        """Test that default schema has correct structure with prompt and completion."""
        schema = SFT_SCHEMA(None)

        assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
        assert schema["title"] == "SFT Schema"
        # Schema should have oneOf for discriminated union
        assert "oneOf" in schema
        # Schema should have $defs with the sub-schemas
        assert "$defs" in schema
        assert "SFTPromptTemplateDatasetItemSchema" in schema["$defs"]
        assert "SFTPChatDatasetItemSchema" in schema["$defs"]
        # Prompt template schema should have required prompt and completion fields
        template_schema = schema["$defs"]["SFTPromptTemplateDatasetItemSchema"]
        assert template_schema["additionalProperties"] is True
        assert "prompt" in template_schema["properties"]
        assert "completion" in template_schema["properties"]
        assert template_schema["properties"]["prompt"]["type"] == "string"
        assert template_schema["properties"]["completion"]["type"] == "string"
        assert set(template_schema["required"]) == {"prompt", "completion"}

    def test_validates_real_sft_data_default_schema(self):
        """Test validation of real SFT data from email-composition-small dataset with default schema."""
        file_path = SFT_TESTDATA_DIR / "email-composition-small" / "training.jsonl"
        assert file_path.exists(), f"Test data file not found: {file_path}"

        # Use DatasetValidator with default schema (no prompt_template)
        validator = DatasetValidator(training_type=TrainingType.SFT, prompt_template=None)

        # Should not raise - validates the entire file
        validator.validate_dataset(str(file_path))

    def test_validates_real_sft_data_custom_template(self):
        """Test validation of real SFT data with custom template matching the data."""
        file_path = SFT_TESTDATA_DIR / "email-composition-small" / "training.jsonl"
        assert file_path.exists(), f"Test data file not found: {file_path}"

        # Template that matches the actual data structure
        template = "{taskname} {prompt} {completion}"
        validator = DatasetValidator(training_type=TrainingType.SFT, prompt_template=template)

        # Should not raise - validates the entire file
        validator.validate_dataset(str(file_path))

    def test_rejects_data_missing_required_field(self, tmp_path: Path):
        """Test that validation fails when data is missing a required field."""
        validator = DatasetValidator(training_type=TrainingType.SFT, prompt_template=None)

        # Create JSONL file with missing completion field
        invalid_data = {"prompt": "What is the capital of France?"}
        test_file = tmp_path / "invalid_missing_field.jsonl"
        test_file.write_text(json.dumps(invalid_data) + "\n")

        with pytest.raises(DatasetFormatError, match="completion"):
            validator.validate_dataset(str(test_file))

    def test_rejects_data_with_wrong_type(self, tmp_path: Path):
        """Test that validation fails when field has wrong type."""
        validator = DatasetValidator(training_type=TrainingType.SFT, prompt_template=None)

        # Create JSONL file with completion as integer instead of string
        invalid_data = {"prompt": "What is 2+2?", "completion": 4}
        test_file = tmp_path / "invalid_wrong_type.jsonl"
        test_file.write_text(json.dumps(invalid_data) + "\n")

        with pytest.raises(DatasetFormatError):
            validator.validate_dataset(str(test_file))

    def test_accepts_data_with_extra_fields(self, tmp_path: Path):
        """Test that schema allows additional properties beyond required fields."""
        validator = DatasetValidator(training_type=TrainingType.SFT, prompt_template=None)

        # Has required fields plus extra fields
        valid_data = {
            "prompt": "What is AI?",
            "completion": "AI stands for Artificial Intelligence.",
            "taskname": "qa",
            "metadata": {"source": "wikipedia"},
        }
        test_file = tmp_path / "valid_extra_fields.jsonl"
        test_file.write_text(json.dumps(valid_data) + "\n")

        # Should not raise
        validator.validate_dataset(str(test_file))

    def test_empty_template_string(self):
        """Test schema generation with empty template string."""
        schema = SFT_SCHEMA("")

        # Empty template should default to standard prompt/completion format (same as None)
        # Required fields are in the prompt template sub-schema in $defs
        template_schema = schema["$defs"]["SFTPromptTemplateDatasetItemSchema"]
        assert template_schema["required"] == ["prompt", "completion"]

    def test_template_with_repeated_placeholders(self):
        """Test that duplicate placeholders raise an error."""
        template = "{input} and {input} again"

        # Should raise ValueError for duplicate placeholders
        with pytest.raises(ValueError, match="duplicate placeholders"):
            SFT_SCHEMA(template)

    def test_validates_complete_jsonl_file(self, tmp_path: Path):
        """Test validation of a complete JSONL file with multiple entries."""
        validator = DatasetValidator(training_type=TrainingType.SFT, prompt_template=None)

        test_data = [
            {"prompt": "Question 1", "completion": "Answer 1"},
            {"prompt": "Question 2", "completion": "Answer 2", "extra": "field"},
            {"prompt": "Question 3", "completion": "Answer 3"},
        ]

        test_file = tmp_path / "test_sft.jsonl"
        test_file.write_text("\n".join(json.dumps(item) for item in test_data))

        # Should validate all lines successfully
        validator.validate_dataset(str(test_file))

    def test_rejects_jsonl_with_invalid_line(self, tmp_path: Path):
        """Test that validation properly detects invalid lines in JSONL file."""
        validator = DatasetValidator(training_type=TrainingType.SFT, prompt_template=None)

        test_data = [
            {"prompt": "Question 1", "completion": "Answer 1"},
            {"prompt": "Question 2"},  # Missing completion
            {"prompt": "Question 3", "completion": "Answer 3"},
        ]

        test_file = tmp_path / "test_invalid_sft.jsonl"
        test_file.write_text("\n".join(json.dumps(item) for item in test_data))

        # Should fail on the second line (missing completion)
        with pytest.raises(DatasetFormatError):
            validator.validate_dataset(str(test_file))


class TestValidateSFTChatSchema:
    """Tests for SFT chat format validation."""

    def test_sft_chat_schema_structure(self):
        """Test basic SFT chat schema structure."""
        schema = SFT_SCHEMA(None)
        assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
        assert schema["title"] == "SFT Schema"

    def test_sft_chat_format_valid(self):
        """Test validation accepts valid chat format."""
        validator = DatasetValidator(TrainingType.SFT)
        data = {"messages": [{"role": "user", "content": "Hello"}, {"role": "assistant", "content": "Hi there!"}]}
        schema = SFT_SCHEMA(None)
        validator._validate_json_object(data, schema)  # Should not raise

    def test_sft_chat_format_with_tools(self):
        """Test validation accepts chat format with tools."""
        validator = DatasetValidator(TrainingType.SFT)
        data = {
            "messages": [
                {"role": "user", "content": "Get weather"},
                {
                    "role": "assistant",
                    "tool_calls": [{"type": "function", "function": {"name": "get_weather", "arguments": {}}}],
                },
            ],
            "tools": [
                {
                    "type": "function",
                    "function": {
                        "name": "get_weather",
                        "description": "Get weather",
                        "parameters": {"type": "object", "properties": {}},
                    },
                }
            ],
        }
        schema = SFT_SCHEMA(None)
        validator._validate_json_object(data, schema)  # Should not raise

    def test_sft_discriminator_detects_chat(self):
        """Test discriminator correctly identifies chat format."""

        chat_data = {"messages": [{"role": "user", "content": "Hello"}]}
        assert get_sft_dataset_discriminator(chat_data) == "SFTChatDatasetItemSchema"

        template_data = {"prompt": "Hello", "completion": "Hi"}
        assert get_sft_dataset_discriminator(template_data) == "SFTPromptTemplateDatasetItemSchema"

    def test_sft_both_formats_in_same_validator(self):
        """Test validator handles both formats with same instance."""
        validator = DatasetValidator(TrainingType.SFT)

        # Validate template format
        template_data = {"prompt": "Test", "completion": "Response"}
        schema = SFT_SCHEMA(None)
        validator._validate_json_object(template_data, schema)

        # Validate chat format
        chat_data = {"messages": [{"role": "user", "content": "Test"}]}
        validator._validate_json_object(chat_data, schema)

    def test_validates_chat_format_file(self, tmp_path: Path):
        """Test validation of a complete JSONL file with chat format."""
        validator = DatasetValidator(training_type=TrainingType.SFT, prompt_template=None)

        test_data = [
            {
                "messages": [
                    {"role": "user", "content": "What is Python?"},
                    {"role": "assistant", "content": "Python is a programming language."},
                ]
            },
            {
                "messages": [
                    {"role": "user", "content": "Explain AI"},
                    {"role": "assistant", "content": "AI stands for Artificial Intelligence."},
                ]
            },
        ]

        test_file = tmp_path / "test_sft_chat.jsonl"
        test_file.write_text("\n".join(json.dumps(item) for item in test_data))

        # Should validate all lines successfully
        validator.validate_dataset(str(test_file))

    def test_rejects_chat_format_with_missing_role(self, tmp_path: Path):
        """Test that validation fails for chat format missing required role field."""
        validator = DatasetValidator(TrainingType.SFT)

        # Missing role field in message
        invalid_data = {"messages": [{"content": "Hello"}]}
        test_file = tmp_path / "invalid_chat.jsonl"
        test_file.write_text(json.dumps(invalid_data) + "\n")

        with pytest.raises(DatasetFormatError):
            validator.validate_dataset(str(test_file))

    def test_rejects_chat_format_with_no_content_or_tool_calls(self, tmp_path: Path):
        """Test that validation fails when message has neither content nor tool_calls."""
        validator = DatasetValidator(TrainingType.SFT)

        # Message with role but no content or tool_calls
        invalid_data = {"messages": [{"role": "user"}]}
        test_file = tmp_path / "invalid_no_content.jsonl"
        test_file.write_text(json.dumps(invalid_data) + "\n")

        with pytest.raises(DatasetFormatError):
            validator.validate_dataset(str(test_file))
