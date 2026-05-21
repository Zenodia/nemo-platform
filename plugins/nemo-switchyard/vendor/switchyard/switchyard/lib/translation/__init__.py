# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Translation utilities for format conversion between LLM API protocols.

Pure functions live in ``anthropic_openai`` and ``responses_openai``.
The ``ChatRequestTranslationEngine`` and ``ChatResponseTranslationEngine``
wrap those functions for typed, on-demand conversion between
``ChatRequest`` / ``ChatResponse`` subclasses.
"""

from switchyard.lib.translation.anthropic_openai import (
    convert_anthropic_request_to_openai,
    convert_anthropic_response_to_openai,
    convert_openai_request_to_anthropic,
    convert_openai_response_to_anthropic,
    stream_openai_to_anthropic,
)
from switchyard.lib.translation.request_engine import ChatRequestTranslationEngine
from switchyard.lib.translation.response_engine import ChatResponseTranslationEngine
from switchyard.lib.translation.responses_openai import (
    convert_chat_response_to_responses,
    convert_responses_request_to_chat_completions,
    convert_responses_response_to_chat_completions,
    stream_chat_to_responses_sse,
    synthesize_responses_sse,
)

__all__ = [
    # Engines
    "ChatRequestTranslationEngine",
    "ChatResponseTranslationEngine",
    # Anthropic ↔ OpenAI pure functions
    "convert_anthropic_request_to_openai",
    "convert_anthropic_response_to_openai",
    "convert_openai_request_to_anthropic",
    "convert_openai_response_to_anthropic",
    "stream_openai_to_anthropic",
    # Responses API ↔ Chat Completions pure functions
    "convert_chat_response_to_responses",
    "convert_responses_request_to_chat_completions",
    "convert_responses_response_to_chat_completions",
    "stream_chat_to_responses_sse",
    "synthesize_responses_sse",
]
