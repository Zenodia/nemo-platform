# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Core library — typed chat request/response hierarchy, translation, routing, and recipes.

This subpackage holds the protocol-agnostic building blocks used across the rest
of the library:

- ``chat_request`` — typed request hierarchy (OpenAI, Responses, Anthropic)
- ``chat_response`` — typed response hierarchy (streaming and non-streaming)
- ``translation`` — pure format-conversion functions and typed translation engines
- ``processors`` — request/response middleware chain (routing, stats, intake, translation)
- ``backends`` — LLM backend implementations (OpenAI, Anthropic, multi-tier routing)
- ``roles`` — protocol definitions (RequestProcessor, LLMBackend, ResponseProcessor, ResponseTranslator)
"""
