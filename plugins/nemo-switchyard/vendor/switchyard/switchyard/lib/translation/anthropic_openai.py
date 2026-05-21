# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Anthropic ↔ OpenAI format conversion utilities.

This module provides pure functions for translating between Anthropic Messages API
and OpenAI Chat Completions API formats, including tool calls.

Canonical internal format: OpenAI Chat Completions (messages, tools, tool_choice).
Backend target: vLLM OpenAI-compatible endpoint.

Mapping summary:
- Anthropic `system` param → OpenAI system message
- Anthropic `text` block → OpenAI content string
- Anthropic `tool_use` block → OpenAI assistant message with `tool_calls`
- Anthropic `tool_result` block → OpenAI `tool` role message with `tool_call_id`
- Anthropic tool definitions → OpenAI `tools` with JSON schema
- Anthropic `stop_reason` ↔ OpenAI `finish_reason`
"""

import hashlib
import json
import logging
import re
import time
import uuid
from collections.abc import AsyncGenerator, Iterable, Mapping
from typing import Any
from urllib.parse import unquote

from anthropic._types import SequenceNotStr
from anthropic.types import (
    MessageParam,
    TextBlockParam,
    ToolChoiceParam,
    ToolUnionParam,
)
from openai.types.chat import (
    ChatCompletionChunk,
    ChatCompletionMessageParam,
    ChatCompletionToolChoiceOptionParam,
)
from openai.types.chat.chat_completion_tool_union_param import ChatCompletionToolUnionParam
from openai.types.chat.completion_create_params import CompletionCreateParamsBase

log = logging.getLogger(__name__)

# -----------------------------------------------------------------------------
# Anthropic → OpenAI (Request)
# -----------------------------------------------------------------------------

# Whitelist of top-level fields the OpenAI Chat Completions API accepts.
# Any ``extra_kwargs`` passed into ``convert_anthropic_request_to_openai``
# that isn't in this set gets dropped, because the OpenAI SDK raises
# ``TypeError: AsyncCompletions.create() got an unexpected keyword argument
# 'X'`` for unknown fields. Claude Code in particular sends Anthropic-only
# fields like ``thinking``, ``cache_control``, ``context_management``,
# ``container`` — including beta fields that aren't even in the Anthropic
# SDK's current ``MessageCreateParamsBase`` TypedDict — so a denylist is
# fragile. Using the OpenAI SDK's own TypedDict keeps this in sync
# automatically as OpenAI adds new top-level fields.
_OPENAI_CHAT_ALLOWED_TOP_LEVEL_FIELDS = frozenset(
    CompletionCreateParamsBase.__annotations__.keys(),
)

logger = logging.getLogger(__name__)

_ANTHROPIC_TOOL_USE_ID_RE = re.compile(r"^[a-zA-Z0-9_-]+$")
_ANTHROPIC_TOOL_USE_ID_INVALID_CHARS_RE = re.compile(r"[^a-zA-Z0-9_-]")


def sanitize_anthropic_tool_use_id(tool_use_id: object) -> str:
    """Return a non-empty Anthropic-compatible ``tool_use.id`` string."""
    raw = "" if tool_use_id is None else str(tool_use_id)
    if _ANTHROPIC_TOOL_USE_ID_RE.fullmatch(raw):
        return raw

    sanitized = _ANTHROPIC_TOOL_USE_ID_INVALID_CHARS_RE.sub("_", raw)
    if sanitized:
        return sanitized

    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]
    return f"toolu_{digest}"


def normalize_anthropic_tool_use_ids(messages: object) -> object:
    """Normalize ``tool_use.id`` / matching ``tool_result.tool_use_id`` values.

    Claude Code stores returned ``tool_use.id`` values in later request history.
    OpenAI-compatible backends can emit tool call IDs with characters Anthropic
    rejects, so normalize IDs before a native Anthropic request leaves
    Switchyard. Matching tool results are rewritten through the same map.
    """
    if not isinstance(messages, list):
        return messages

    id_map: dict[str, str] = {}
    used_ids: dict[str, str] = {}
    normalized_messages: list[object] = []
    changed = False

    for message in messages:
        if not isinstance(message, Mapping):
            normalized_messages.append(message)
            continue

        content = message.get("content")
        if not isinstance(content, list):
            normalized_messages.append(message)
            continue

        normalized_content: list[object] = []
        message_changed = False

        for block in content:
            if not isinstance(block, Mapping):
                normalized_content.append(block)
                continue

            block_type = block.get("type")
            normalized_block = block

            if block_type == "tool_use":
                raw_id = block.get("id")
                normalized_id = _mapped_anthropic_tool_use_id(
                    raw_id, id_map=id_map, used_ids=used_ids,
                )
                if normalized_id != raw_id:
                    normalized_block = dict(block)
                    normalized_block["id"] = normalized_id
                    message_changed = True

            elif block_type == "tool_result":
                raw_id = block.get("tool_use_id")
                raw_key = _tool_use_id_key(raw_id)
                mapped_id = id_map.get(raw_key)
                if mapped_id is None:
                    mapped_id = _mapped_anthropic_tool_use_id(
                        raw_id, id_map=id_map, used_ids=used_ids,
                    )
                if mapped_id != raw_id:
                    normalized_block = dict(block)
                    normalized_block["tool_use_id"] = mapped_id
                    message_changed = True

            normalized_content.append(normalized_block)

        if message_changed:
            normalized_message = dict(message)
            normalized_message["content"] = normalized_content
            normalized_messages.append(normalized_message)
            changed = True
        else:
            normalized_messages.append(message)

    return normalized_messages if changed else messages


def _tool_use_id_key(tool_use_id: object) -> str:
    return "" if tool_use_id is None else str(tool_use_id)


def _mapped_anthropic_tool_use_id(
    tool_use_id: object,
    *,
    id_map: dict[str, str],
    used_ids: dict[str, str],
) -> str:
    raw = _tool_use_id_key(tool_use_id)
    existing = id_map.get(raw)
    if existing is not None:
        return existing

    candidate = sanitize_anthropic_tool_use_id(raw)
    owner = used_ids.get(candidate)
    if owner is not None and owner != raw:
        digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:8]
        candidate = f"{candidate}_{digest}"

    id_map[raw] = candidate
    used_ids[candidate] = raw
    return candidate


def convert_anthropic_request_to_openai(
    messages: Iterable[MessageParam],
    system: str | Iterable[TextBlockParam] | None = None,
    tools: Iterable[ToolUnionParam] | None = None,
    tool_choice: ToolChoiceParam | str | None = None,
    model: str | None = None,
    max_tokens: int | None = None,
    temperature: float | None = None,
    top_p: float | None = None,
    top_k: int | None = None,
    stop_sequences: SequenceNotStr[str] | None = None,
    stream: bool | None = None,
    **extra_kwargs: object,
) -> dict[str, Any]:
    """
    Convert Anthropic Messages API request to OpenAI Chat Completions format.

    Args:
        messages: Anthropic messages list (with content blocks).
        system: Anthropic system prompt (string or list of blocks).
        tools: Anthropic tool definitions.
        tool_choice: Anthropic tool_choice.
        model: Model name.
        max_tokens: Max tokens.
        temperature: Temperature.
        top_p: Top-p sampling.
        top_k: Top-k sampling (not directly supported in OpenAI, passed as extra).
        stop_sequences: Anthropic stop sequences → OpenAI `stop`.
        stream: Whether to stream.
        **extra_kwargs: Additional kwargs to pass through.

    Returns:
        OpenAI-format request dict.
    """
    openai_messages: list[dict[str, Any]] = []

    # Convert system prompt
    if system:
        if isinstance(system, str):
            openai_messages.append({"role": "system", "content": system})
        else:
            # Handle structured system content blocks — any Iterable[TextBlockParam]
            # (list, tuple, generator, …) — not just list.
            system_text_parts = []
            for block in system:
                if isinstance(block, dict) and block.get("type") == "text":
                    system_text_parts.append(block.get("text", ""))
            if system_text_parts:
                openai_messages.append({"role": "system", "content": " ".join(system_text_parts)})

    # Convert messages
    for msg in messages:
        openai_msg = _convert_anthropic_message_to_openai(msg)
        if openai_msg:
            if isinstance(openai_msg, list):
                openai_messages.extend(openai_msg)
            else:
                openai_messages.append(openai_msg)

    # Build request dict
    request: dict[str, Any] = {
        "messages": openai_messages,
    }

    if model:
        request["model"] = model
    if max_tokens is not None:
        request["max_tokens"] = max_tokens
    if temperature is not None:
        request["temperature"] = temperature
    if top_p is not None:
        request["top_p"] = top_p
    if stop_sequences:
        request["stop"] = stop_sequences
    if stream is not None:
        request["stream"] = stream

    # Convert tools
    if tools:
        request["tools"] = _convert_anthropic_tools_to_openai(tools)

    # Convert tool_choice
    if tool_choice:
        request["tool_choice"] = _convert_anthropic_tool_choice_to_openai(tool_choice)

    # Pass through extra kwargs, but only those OpenAI Chat Completions
    # actually accepts — any Anthropic-only field (thinking, cache_control,
    # context_management, container, ...) would raise TypeError from the
    # OpenAI SDK otherwise.
    for key, value in extra_kwargs.items():
        if key not in _OPENAI_CHAT_ALLOWED_TOP_LEVEL_FIELDS:
            continue
        if key not in request and value is not None:
            request[key] = value

    return request


def _convert_anthropic_message_to_openai(
    msg: Mapping[str, Any],
) -> dict[str, Any] | list[dict[str, Any]] | None:
    """
    Convert a single Anthropic message to OpenAI format.

    Handles:
    - text blocks → content string
    - tool_use blocks → assistant message with tool_calls
    - tool_result blocks → tool role message
    """
    role = msg.get("role", "user")
    content = msg.get("content")

    if content is None:
        return {"role": role, "content": ""}

    # String content (simple case)
    if isinstance(content, str):
        return {"role": role, "content": content}

    # Content blocks (list)
    if isinstance(content, list):
        text_parts: list[str] = []
        tool_calls: list[dict[str, Any]] = []
        tool_results: list[dict[str, Any]] = []

        for block in content:
            if not isinstance(block, dict):
                continue

            block_type = block.get("type")

            if block_type == "text":
                text_parts.append(block.get("text", ""))

            elif block_type == "tool_use":
                # Anthropic tool_use → OpenAI tool_calls entry
                raw_input = block.get("input", {})
                # Avoid double-encoding: if input is already a JSON string,
                # use it directly; otherwise serialize the dict.
                arguments = (
                    raw_input if isinstance(raw_input, str)
                    else json.dumps(raw_input)
                )
                tool_call = {
                    "id": block.get("id", f"call_{uuid.uuid4().hex[:24]}"),
                    "type": "function",
                    "function": {
                        "name": block.get("name", ""),
                        "arguments": arguments,
                    },
                }
                tool_calls.append(tool_call)

            elif block_type == "tool_result":
                # Anthropic tool_result → OpenAI tool message
                tool_result_content = block.get("content", "")
                if isinstance(tool_result_content, list):
                    # Flatten content blocks to string.  Extract text
                    # blocks directly; serialize non-text blocks as JSON
                    # so their data is preserved rather than silently dropped.
                    parts: list[str] = []
                    for b in tool_result_content:
                        if not isinstance(b, dict):
                            continue
                        if b.get("type") == "text":
                            parts.append(b.get("text", ""))
                        else:
                            # Preserve non-text blocks (images, etc.) as
                            # JSON so downstream consumers can recover them.
                            parts.append(json.dumps(b))
                    tool_result_content = " ".join(parts)
                tool_results.append({
                    "role": "tool",
                    "tool_call_id": block.get("tool_use_id", ""),
                    "content": str(tool_result_content),
                })

        # Build output message(s)
        result_messages: list[dict[str, Any]] = []

        # If there are tool_results, they become separate tool messages
        if tool_results:
            result_messages.extend(tool_results)

        # If there are tool_calls (assistant requesting tools)
        if tool_calls:
            assistant_msg: dict[str, Any] = {
                "role": "assistant",
                "content": " ".join(text_parts) if text_parts else None,
                "tool_calls": tool_calls,
            }
            result_messages.insert(0, assistant_msg)
        elif text_parts:
            # Regular message with just text
            result_messages.append({
                "role": role,
                "content": " ".join(text_parts),
            })

        if len(result_messages) == 1:
            return result_messages[0]
        elif len(result_messages) > 1:
            return result_messages
        else:
            return {"role": role, "content": ""}

    return {"role": role, "content": str(content)}


def _convert_anthropic_tools_to_openai(
    tools: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    """Convert Anthropic tool definitions to OpenAI format."""
    openai_tools: list[dict[str, Any]] = []
    for tool in tools:
        openai_tool = {
            "type": "function",
            "function": {
                "name": tool.get("name", ""),
                "description": tool.get("description", ""),
                "parameters": tool.get("input_schema", {}),
            },
        }
        openai_tools.append(openai_tool)
    return openai_tools


def _convert_anthropic_tool_choice_to_openai(
    tool_choice: Mapping[str, Any] | str,
) -> str | dict[str, Any]:
    """Convert Anthropic tool_choice to OpenAI format."""
    if isinstance(tool_choice, str):
        # Anthropic: "auto", "any", "none" → OpenAI: "auto", "required", "none"
        mapping = {
            "auto": "auto",
            "any": "required",
            "none": "none",
        }
        return mapping.get(tool_choice, tool_choice)

    if isinstance(tool_choice, dict):
        choice_type = tool_choice.get("type")
        if choice_type == "tool":
            # Specific tool choice
            return {
                "type": "function",
                "function": {"name": tool_choice.get("name", "")},
            }
        elif choice_type == "auto":
            return "auto"
        elif choice_type == "any":
            return "required"
        elif choice_type == "none":
            return "none"

    return "auto"


# -----------------------------------------------------------------------------
# OpenAI → Anthropic (Response)
# -----------------------------------------------------------------------------

def convert_openai_response_to_anthropic(
    response: Any,
    model: str | None = None,
) -> dict[str, Any]:
    """
    Convert OpenAI Chat Completions response to Anthropic Messages format.

    Args:
        response: OpenAI response object (or dict).
        model: Model name override.

    Returns:
        Anthropic-format response dict.
    """
    # Extract from response object or dict
    if hasattr(response, "model_dump"):
        response_dict = response.model_dump()
    elif hasattr(response, "to_dict"):
        response_dict = response.to_dict()
    elif isinstance(response, dict):
        response_dict = response
    else:
        # Try to access attributes directly
        response_dict = {}
        for attr in ["id", "model", "choices", "usage"]:
            if hasattr(response, attr):
                response_dict[attr] = getattr(response, attr)

    # Extract model
    resp_model = model or response_dict.get("model", "unknown")

    # Extract first choice
    choices = response_dict.get("choices", [])
    if not choices:
        return _create_empty_anthropic_response(resp_model)

    choice = choices[0]

    # Handle dict or object choice
    if hasattr(choice, "message"):
        message = choice.message
        finish_reason = getattr(choice, "finish_reason", "end_turn")
    elif isinstance(choice, dict):
        message = choice.get("message", {})
        finish_reason = choice.get("finish_reason", "end_turn")
    else:
        return _create_empty_anthropic_response(resp_model)

    # Convert message to content blocks
    content_blocks = _convert_openai_message_to_anthropic_content(message)

    # Map finish_reason to stop_reason
    stop_reason = _map_openai_finish_reason_to_anthropic(finish_reason)

    # Extract usage
    usage = response_dict.get("usage", {})
    if hasattr(usage, "prompt_tokens"):
        input_tokens = usage.prompt_tokens
        output_tokens = getattr(usage, "completion_tokens", 0)
    elif isinstance(usage, dict):
        input_tokens = usage.get("prompt_tokens", 0)
        output_tokens = usage.get("completion_tokens", 0)
    else:
        input_tokens = 0
        output_tokens = 0

    return {
        "id": f"msg_{uuid.uuid4().hex[:24]}",
        "type": "message",
        "role": "assistant",
        "content": content_blocks,
        "model": resp_model,
        "stop_reason": stop_reason,
        "stop_sequence": None,
        "usage": {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
        },
    }


def _convert_openai_message_to_anthropic_content(
    message: Any,
) -> list[dict[str, Any]]:
    """Convert OpenAI assistant message to Anthropic content blocks."""
    content_blocks: list[dict[str, Any]] = []

    # Handle dict or object
    if hasattr(message, "content"):
        content = message.content
        tool_calls = getattr(message, "tool_calls", None)
    elif isinstance(message, dict):
        content = message.get("content")
        tool_calls = message.get("tool_calls")
    else:
        return [{"type": "text", "text": ""}]

    # Add text block if content exists
    if content:
        content_blocks.append({
            "type": "text",
            "text": str(content),
        })

    # Convert tool_calls to tool_use blocks
    if tool_calls:
        id_map: dict[str, str] = {}
        used_ids: dict[str, str] = {}
        for tc in tool_calls:
            if hasattr(tc, "id"):
                tc_id = tc.id or f"call_{uuid.uuid4().hex[:24]}"
                tc_function = tc.function
                tc_name = tc_function.name if hasattr(tc_function, "name") else ""
                tc_args = tc_function.arguments if hasattr(tc_function, "arguments") else "{}"
            elif isinstance(tc, dict):
                tc_id = tc.get("id") or f"call_{uuid.uuid4().hex[:24]}"
                tc_function = tc.get("function", {})
                tc_name = tc_function.get("name", "")
                tc_args = tc_function.get("arguments", "{}")
            else:
                continue

            # Parse arguments
            try:
                input_obj = json.loads(tc_args) if isinstance(tc_args, str) else tc_args
            except json.JSONDecodeError:
                input_obj = {"raw": tc_args}

            content_blocks.append({
                "type": "tool_use",
                "id": _mapped_anthropic_tool_use_id(
                    tc_id, id_map=id_map, used_ids=used_ids,
                ),
                "name": tc_name,
                "input": input_obj,
            })

    if not content_blocks:
        content_blocks.append({"type": "text", "text": ""})

    return content_blocks


def _map_openai_finish_reason_to_anthropic(finish_reason: str | None) -> str:
    """Map OpenAI finish_reason to Anthropic stop_reason."""
    mapping = {
        "stop": "end_turn",
        "length": "max_tokens",
        "tool_calls": "tool_use",
        "content_filter": "end_turn",
        "function_call": "tool_use",  # legacy
    }
    return mapping.get(finish_reason or "stop", "end_turn")


def _create_empty_anthropic_response(model: str) -> dict[str, Any]:
    """Create an empty Anthropic response."""
    return {
        "id": f"msg_{uuid.uuid4().hex[:24]}",
        "type": "message",
        "role": "assistant",
        "content": [{"type": "text", "text": ""}],
        "model": model,
        "stop_reason": "end_turn",
        "stop_sequence": None,
        "usage": {"input_tokens": 0, "output_tokens": 0},
    }


# -----------------------------------------------------------------------------
# OpenAI → Anthropic (Request) - for completeness / reverse proxy
# -----------------------------------------------------------------------------

def convert_openai_request_to_anthropic(
    messages: Iterable[ChatCompletionMessageParam],
    model: str | None = None,
    max_tokens: int | None = None,
    temperature: float | None = None,
    top_p: float | None = None,
    stop: str | Iterable[str] | None = None,
    stream: bool | None = None,
    tools: Iterable[ChatCompletionToolUnionParam] | None = None,
    tool_choice: ChatCompletionToolChoiceOptionParam | None = None,
    **extra_kwargs: object,
) -> dict[str, Any]:
    """
    Convert OpenAI Chat Completions request to Anthropic Messages format.

    Args:
        messages: OpenAI messages list.
        model: Model name.
        max_tokens: Max tokens (required for Anthropic).
        temperature: Temperature.
        top_p: Top-p sampling.
        stop: OpenAI stop sequences → Anthropic stop_sequences.
        stream: Whether to stream.
        tools: OpenAI tool definitions.
        tool_choice: OpenAI tool_choice.
        **extra_kwargs: Additional kwargs.

    Returns:
        Anthropic-format request dict.
    """
    anthropic_messages: list[dict[str, Any]] = []
    system_parts: list[str] = []
    pending_tool_results: list[dict[str, Any]] = []

    def flush_tool_results() -> None:
        nonlocal pending_tool_results
        if pending_tool_results:
            anthropic_messages.append({
                "role": "user",
                "content": pending_tool_results,
            })
            pending_tool_results = []

    for msg in messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        tool_calls = msg.get("tool_calls")
        tool_call_id = msg.get("tool_call_id")

        if role in {"system", "developer"}:
            # Extract system/developer prompts into Anthropic's top-level system.
            flush_tool_results()
            system_text = _openai_content_to_text(content)
            if system_text:
                system_parts.append(system_text)
            continue

        if role == "tool":
            # OpenAI tool message → Anthropic user message with tool_result block
            pending_tool_results.append({
                "type": "tool_result",
                "tool_use_id": tool_call_id or "",
                "content": _openai_content_to_text(content),
            })
            continue

        flush_tool_results()

        if role == "assistant" and isinstance(tool_calls, list):
            # Assistant with tool_calls → Anthropic assistant with tool_use blocks
            content_blocks: list[dict[str, Any]] = []
            text = _openai_content_to_text(content)
            if text:
                content_blocks.append({"type": "text", "text": text})
            for tc in tool_calls:
                if not isinstance(tc, dict):
                    logger.warning("Skipping non-dict tool call of type %s", type(tc).__name__)
                    continue
                tc_id = tc.get("id") or f"call_{uuid.uuid4().hex[:24]}"
                tc_function = tc.get("function", {})
                tc_name = tc_function.get("name", "")
                tc_args = tc_function.get("arguments", "{}")
                try:
                    input_obj = json.loads(tc_args) if isinstance(tc_args, str) else tc_args
                except json.JSONDecodeError:
                    input_obj = {"raw": tc_args}
                content_blocks.append({
                    "type": "tool_use",
                    "id": tc_id,
                    "name": tc_name,
                    "input": input_obj,
                })
            anthropic_messages.append({
                "role": "assistant",
                "content": content_blocks,
            })
            continue

        # Regular message
        if isinstance(content, str):
            anthropic_messages.append({
                "role": role,
                "content": content,
            })
        elif isinstance(content, list):
            # OpenAI multimodal content blocks → Anthropic blocks.
            # SDK content parts are TypedDicts (ChatCompletionContentPart*);
            # treat them as structural mappings for pass-through.
            anthropic_blocks = _convert_openai_content_parts_to_anthropic(content)
            anthropic_messages.append({
                "role": role,
                "content": anthropic_blocks if anthropic_blocks else "",
            })
        else:
            anthropic_messages.append({
                "role": role,
                "content": str(content) if content else "",
            })

    flush_tool_results()

    normalized_messages = normalize_anthropic_tool_use_ids(anthropic_messages)
    if isinstance(normalized_messages, list):
        anthropic_messages = normalized_messages

    # Build request
    request: dict[str, Any] = {
        "messages": anthropic_messages,
    }

    if model:
        request["model"] = model
    max_completion_tokens = extra_kwargs.get("max_completion_tokens")
    if max_tokens is not None:
        request["max_tokens"] = max_tokens
    elif isinstance(max_completion_tokens, int):
        request["max_tokens"] = max_completion_tokens
    else:
        # Anthropic requires ``max_tokens``.  Default generous for coding
        # workloads — long diffs, multi-file refactors, and whole-file
        # rewrites routinely blow past small caps.  Modern frontier coders
        # (Claude Opus/Sonnet 4.x, GPT-5.x) clamp this to their own output
        # ceiling server-side, so oversizing here is harmless.
        request["max_tokens"] = 128_000
    if temperature is not None:
        request["temperature"] = temperature
    if top_p is not None:
        request["top_p"] = top_p
    if stream is not None:
        request["stream"] = stream

    if stop:
        if isinstance(stop, str):
            request["stop_sequences"] = [stop]
        else:
            request["stop_sequences"] = stop

    if system_parts:
        request["system"] = "\n\n".join(system_parts)

    # Convert tools
    if tools:
        request["tools"] = _convert_openai_tools_to_anthropic(tools)

    # Convert tool_choice
    if tool_choice:
        request["tool_choice"] = _convert_openai_tool_choice_to_anthropic(tool_choice)

    reasoning_effort = extra_kwargs.get("reasoning_effort")
    if isinstance(reasoning_effort, str):
        if reasoning_effort in {"disabled", "none"}:
            request["thinking"] = {"type": "disabled"}
        else:
            request["thinking"] = {"type": "adaptive"}
            request["output_config"] = {"effort": reasoning_effort}

    return request


def _openai_content_to_text(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for block in content:
            if not isinstance(block, Mapping):
                continue
            block_type = block.get("type")
            if block_type == "text":
                text = block.get("text")
                if isinstance(text, str):
                    parts.append(text)
            elif block_type == "refusal":
                refusal = block.get("refusal")
                if isinstance(refusal, str):
                    parts.append(refusal)
        return "\n".join(parts)
    return str(content) if content else ""


def _convert_openai_content_parts_to_anthropic(
    content: Iterable[Any],
) -> list[Mapping[str, Any]]:
    anthropic_blocks: list[Mapping[str, Any]] = []
    for block in content:
        if not isinstance(block, Mapping):
            continue
        block_type = block.get("type")
        if block_type == "text":
            anthropic_blocks.append({"type": "text", "text": block.get("text", "")})
        elif block_type == "image_url":
            image_block = _convert_openai_image_part_to_anthropic(block)
            if image_block is not None:
                anthropic_blocks.append(image_block)
        else:
            # Preserve unsupported content as text rather than sending an
            # Anthropic-invalid block type.
            anthropic_blocks.append({"type": "text", "text": json.dumps(dict(block))})
    return anthropic_blocks


def _convert_openai_image_part_to_anthropic(
    block: Mapping[str, Any],
) -> dict[str, Any] | None:
    image_url = block.get("image_url")
    if isinstance(image_url, Mapping):
        url = image_url.get("url")
    else:
        url = image_url
    if not isinstance(url, str) or not url:
        return None
    data_url = _parse_data_url(url)
    if data_url is not None:
        media_type, data = data_url
        return {
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": media_type,
                "data": data,
            },
        }
    return {
        "type": "image",
        "source": {
            "type": "url",
            "url": url,
        },
    }


def _parse_data_url(url: str) -> tuple[str, str] | None:
    if not url.startswith("data:"):
        return None
    header, sep, data = url.partition(",")
    if not sep:
        return None
    media_type = header.removeprefix("data:").split(";", 1)[0]
    if not media_type:
        return None
    return media_type, unquote(data)


def _convert_openai_tools_to_anthropic(
    tools: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    """Convert OpenAI tool definitions to Anthropic format."""
    anthropic_tools: list[dict[str, Any]] = []
    for tool in tools:
        if tool.get("type") != "function":
            continue
        func = tool.get("function", {})
        anthropic_tools.append({
            "name": func.get("name", ""),
            "description": func.get("description", ""),
            "input_schema": func.get("parameters", {}),
        })
    return anthropic_tools


def _convert_openai_tool_choice_to_anthropic(
    tool_choice: str | Mapping[str, Any],
) -> dict[str, Any] | str:
    """Convert OpenAI tool_choice to Anthropic format."""
    if isinstance(tool_choice, str):
        mapping = {
            "auto": {"type": "auto"},
            "required": {"type": "any"},
            "none": {"type": "none"},
        }
        return mapping.get(tool_choice, {"type": "auto"})

    if isinstance(tool_choice, dict):
        if tool_choice.get("type") == "function":
            func = tool_choice.get("function", {})
            return {
                "type": "tool",
                "name": func.get("name", ""),
            }

    return {"type": "auto"}


# -----------------------------------------------------------------------------
# Anthropic → OpenAI (Response) - for completeness / reverse proxy
# -----------------------------------------------------------------------------

def convert_anthropic_response_to_openai(
    response: dict[str, Any],
    model: str | None = None,
) -> dict[str, Any]:
    """
    Convert Anthropic Messages response to OpenAI Chat Completions format.

    Args:
        response: Anthropic response dict.
        model: Model name override.

    Returns:
        OpenAI-format response dict.
    """
    import time

    resp_model = model or response.get("model", "unknown")
    content_blocks = response.get("content", [])
    stop_reason = response.get("stop_reason", "end_turn")
    usage = response.get("usage", {})

    # Convert content blocks to OpenAI message
    text_parts: list[str] = []
    tool_calls: list[dict[str, Any]] = []

    for block in content_blocks:
        if not isinstance(block, dict):
            continue
        block_type = block.get("type")
        if block_type == "text":
            text_parts.append(block.get("text", ""))
        elif block_type == "tool_use":
            tool_calls.append({
                "id": block.get("id", f"call_{uuid.uuid4().hex[:24]}"),
                "type": "function",
                "function": {
                    "name": block.get("name", ""),
                    "arguments": json.dumps(block.get("input", {})),
                },
            })

    # Build message
    message: dict[str, Any] = {
        "role": "assistant",
        "content": " ".join(text_parts) if text_parts else None,
    }
    if tool_calls:
        message["tool_calls"] = tool_calls

    # Map stop_reason to finish_reason
    finish_reason = _map_anthropic_stop_reason_to_openai(stop_reason)

    input_tokens = usage.get("input_tokens", 0) or 0
    cache_creation_tokens = usage.get("cache_creation_input_tokens", 0) or 0
    cache_read_tokens = usage.get("cache_read_input_tokens", 0) or 0
    output_tokens = usage.get("output_tokens", 0) or 0
    prompt_tokens = input_tokens + cache_creation_tokens + cache_read_tokens
    openai_shape_usage: dict[str, Any] = {
        "prompt_tokens": prompt_tokens,
        "completion_tokens": output_tokens,
        "total_tokens": prompt_tokens + output_tokens,
    }
    if cache_creation_tokens or cache_read_tokens:
        openai_shape_usage["prompt_tokens_details"] = {
            "cached_tokens": cache_read_tokens,
            "cache_creation_tokens": cache_creation_tokens,
        }

    return {
        "id": f"chatcmpl-{uuid.uuid4().hex[:24]}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": resp_model,
        "choices": [
            {
                "index": 0,
                "message": message,
                "finish_reason": finish_reason,
            }
        ],
        "usage": openai_shape_usage,
    }


def _map_anthropic_stop_reason_to_openai(stop_reason: str | None) -> str:
    """Map Anthropic stop_reason to OpenAI finish_reason."""
    mapping = {
        "end_turn": "stop",
        "max_tokens": "length",
        "tool_use": "tool_calls",
        "stop_sequence": "stop",
    }
    return mapping.get(stop_reason or "end_turn", "stop")


# -----------------------------------------------------------------------------
# Anthropic → OpenAI (Streaming Response)
# -----------------------------------------------------------------------------

async def stream_anthropic_to_openai(
    events: Any,
    *,
    model: str = "unknown",
) -> AsyncGenerator[ChatCompletionChunk, None]:
    """Convert Anthropic streaming events to OpenAI ChatCompletionChunk objects."""
    stream_id = f"chatcmpl_{uuid.uuid4().hex[:24]}"
    created = int(time.time())
    current_model = model
    started = False
    finished = False
    next_tool_index = 0
    tool_indexes: dict[int, int] = {}
    usage: dict[str, int] = {}

    async for event in events:
        event_dict = _anthropic_stream_event_dict(event)
        event_type = event_dict.get("type")

        if event_type == "message_start":
            message = event_dict.get("message")
            if isinstance(message, Mapping):
                msg_id = message.get("id")
                msg_model = message.get("model")
                if isinstance(msg_id, str) and msg_id:
                    stream_id = _chat_completion_stream_id(msg_id)
                if isinstance(msg_model, str) and msg_model:
                    current_model = msg_model
                _merge_anthropic_usage(usage, message.get("usage"))
            if not started:
                yield _openai_stream_chunk(
                    stream_id=stream_id,
                    created=created,
                    model=current_model,
                    delta={"role": "assistant"},
                )
                started = True
            continue

        if event_type == "content_block_start":
            if not started:
                yield _openai_stream_chunk(
                    stream_id=stream_id,
                    created=created,
                    model=current_model,
                    delta={"role": "assistant"},
                )
                started = True

            index = _int_value(event_dict.get("index"), 0)
            block = event_dict.get("content_block")
            if not isinstance(block, Mapping):
                continue
            block_type = block.get("type")
            if block_type == "text":
                text = block.get("text")
                if isinstance(text, str) and text:
                    yield _openai_stream_chunk(
                        stream_id=stream_id,
                        created=created,
                        model=current_model,
                        delta={"content": text},
                    )
                continue
            if block_type == "tool_use":
                tool_index = tool_indexes.setdefault(index, next_tool_index)
                if tool_index == next_tool_index:
                    next_tool_index += 1
                yield _openai_tool_call_chunk(
                    stream_id=stream_id,
                    created=created,
                    model=current_model,
                    index=tool_index,
                    tool_id=_str_value(block.get("id")),
                    name=_str_value(block.get("name")),
                    arguments=_json_arguments_delta(block.get("input")),
                )
            continue

        if event_type == "content_block_delta":
            if not started:
                yield _openai_stream_chunk(
                    stream_id=stream_id,
                    created=created,
                    model=current_model,
                    delta={"role": "assistant"},
                )
                started = True

            delta = event_dict.get("delta")
            if not isinstance(delta, Mapping):
                continue
            delta_type = delta.get("type")
            if delta_type == "text_delta":
                text = delta.get("text")
                if isinstance(text, str) and text:
                    yield _openai_stream_chunk(
                        stream_id=stream_id,
                        created=created,
                        model=current_model,
                        delta={"content": text},
                    )
                continue
            if delta_type == "thinking_delta":
                thinking = delta.get("thinking")
                if isinstance(thinking, str) and thinking:
                    yield _openai_stream_chunk(
                        stream_id=stream_id,
                        created=created,
                        model=current_model,
                        delta={"reasoning_content": thinking},
                    )
                continue
            if delta_type == "input_json_delta":
                block_index = _int_value(event_dict.get("index"), 0)
                tool_index = tool_indexes.setdefault(block_index, next_tool_index)
                if tool_index == next_tool_index:
                    next_tool_index += 1
                partial_json = delta.get("partial_json")
                if isinstance(partial_json, str) and partial_json:
                    yield _openai_tool_call_chunk(
                        stream_id=stream_id,
                        created=created,
                        model=current_model,
                        index=tool_index,
                        arguments=partial_json,
                    )
            continue

        if event_type == "message_delta":
            delta = event_dict.get("delta")
            stop_reason = None
            if isinstance(delta, Mapping):
                stop_reason = delta.get("stop_reason")
            _merge_anthropic_usage(usage, event_dict.get("usage"))
            if not started:
                yield _openai_stream_chunk(
                    stream_id=stream_id,
                    created=created,
                    model=current_model,
                    delta={"role": "assistant"},
                )
                started = True
            yield _openai_stream_chunk(
                stream_id=stream_id,
                created=created,
                model=current_model,
                delta={},
                finish_reason=_map_anthropic_stop_reason_to_openai(
                    stop_reason if isinstance(stop_reason, str) else None,
                ),
                usage=_openai_usage_from_anthropic(usage),
            )
            finished = True
            continue

        if event_type == "message_stop" and not finished:
            if not started:
                yield _openai_stream_chunk(
                    stream_id=stream_id,
                    created=created,
                    model=current_model,
                    delta={"role": "assistant"},
                )
            yield _openai_stream_chunk(
                stream_id=stream_id,
                created=created,
                model=current_model,
                delta={},
                finish_reason="stop",
                usage=_openai_usage_from_anthropic(usage),
            )
            finished = True


def _anthropic_stream_event_dict(event: object) -> Mapping[str, Any]:
    if isinstance(event, Mapping):
        return event
    if hasattr(event, "model_dump"):
        dumped = event.model_dump(exclude_none=True)
        return dumped if isinstance(dumped, Mapping) else {}
    return {}


def _openai_stream_chunk(
    *,
    stream_id: str,
    created: int,
    model: str,
    delta: Mapping[str, Any],
    finish_reason: str | None = None,
    usage: Mapping[str, Any] | None = None,
) -> ChatCompletionChunk:
    payload: dict[str, Any] = {
        "id": stream_id,
        "object": "chat.completion.chunk",
        "created": created,
        "model": model,
        "choices": [{
            "index": 0,
            "delta": dict(delta),
            "finish_reason": finish_reason,
        }],
    }
    if usage is not None:
        payload["usage"] = dict(usage)
    return ChatCompletionChunk.model_validate(payload)


def _openai_tool_call_chunk(
    *,
    stream_id: str,
    created: int,
    model: str,
    index: int,
    tool_id: str | None = None,
    name: str | None = None,
    arguments: str | None = None,
) -> ChatCompletionChunk:
    function: dict[str, str] = {}
    if name:
        function["name"] = name
    if arguments:
        function["arguments"] = arguments
    tool_call: dict[str, Any] = {
        "index": index,
        "type": "function",
        "function": function,
    }
    if tool_id:
        tool_call["id"] = tool_id
    return _openai_stream_chunk(
        stream_id=stream_id,
        created=created,
        model=model,
        delta={"tool_calls": [tool_call]},
    )


def _merge_anthropic_usage(target: dict[str, int], usage: object) -> None:
    if not isinstance(usage, Mapping):
        return
    for key in (
        "input_tokens",
        "output_tokens",
        "cache_creation_input_tokens",
        "cache_read_input_tokens",
    ):
        value = usage.get(key)
        if isinstance(value, int):
            target[key] = value


def _openai_usage_from_anthropic(usage: Mapping[str, int]) -> dict[str, Any] | None:
    if not usage:
        return None
    cache_creation_tokens = usage.get("cache_creation_input_tokens", 0)
    cache_read_tokens = usage.get("cache_read_input_tokens", 0)
    prompt_tokens = (
        usage.get("input_tokens", 0)
        + cache_creation_tokens
        + cache_read_tokens
    )
    completion_tokens = usage.get("output_tokens", 0)
    result: dict[str, Any] = {
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": prompt_tokens + completion_tokens,
    }
    if cache_creation_tokens or cache_read_tokens:
        result["prompt_tokens_details"] = {
            "cached_tokens": cache_read_tokens,
            "cache_creation_tokens": cache_creation_tokens,
        }
    return result


def _chat_completion_stream_id(message_id: str) -> str:
    if message_id.startswith("chatcmpl"):
        return message_id
    return f"chatcmpl_{message_id.removeprefix('msg_')}"


def _json_arguments_delta(value: object) -> str | None:
    if isinstance(value, str):
        return value if value else None
    if isinstance(value, Mapping) and value:
        return json.dumps(dict(value))
    return None


def _int_value(value: object, default: int) -> int:
    return value if isinstance(value, int) else default


def _str_value(value: object) -> str | None:
    return value if isinstance(value, str) and value else None


# -----------------------------------------------------------------------------
# OpenAI → Anthropic (Streaming Response)
# -----------------------------------------------------------------------------

async def stream_openai_to_anthropic(
    response: Any,
    model: str,
    msg_id: str | None = None,
) -> AsyncGenerator[dict[str, Any], None]:
    """Convert an OpenAI streaming response to Anthropic SSE event dicts.

    Yields plain dicts for each Anthropic SSE event (message_start,
    content_block_start, content_block_delta, content_block_stop,
    message_delta, message_stop). Does not wrap in ServerSentEvent;
    callers are responsible for that.

    Args:
        response: An async iterable of OpenAI streaming chunks.
        model: Model name to include in the message_start event.
        msg_id: Optional message ID; auto-generated if not provided.
    """
    if msg_id is None:
        msg_id = f"msg_{uuid.uuid4().hex[:24]}"

    yield {
        "type": "message_start",
        "message": {
            "id": msg_id,
            "type": "message",
            "role": "assistant",
            "content": [],
            "model": model,
            "stop_reason": None,
            "stop_sequence": None,
            "usage": {"input_tokens": 0, "output_tokens": 0},
        },
    }

    output_tokens = 0
    # Real usage from the backend (populated from the final stream chunk
    # when the upstream honours stream_options.include_usage=True).
    backend_usage: dict[str, Any] | None = None
    # Monotonically increasing index assigned to each content block in order.
    # Incremented when a block is *started*, so every block (text and tool_use)
    # gets a unique, gapless index regardless of how many tool calls there are.
    next_block_idx = 0
    text_block_idx = 0
    text_block_started = False
    emitted_content_block = False
    tool_calls: dict[int, dict[str, Any]] = {}
    stop_reason = "end_turn"

    async for chunk in response:
        # Capture usage from any chunk (typically the final one when
        # stream_options.include_usage is set).
        chunk_usage = getattr(chunk, "usage", None)
        if chunk_usage is not None:
            backend_usage = {
                "input_tokens": getattr(chunk_usage, "prompt_tokens", 0) or 0,
                "output_tokens": getattr(chunk_usage, "completion_tokens", 0) or 0,
            }
            details = getattr(chunk_usage, "prompt_tokens_details", None)
            if details is not None:
                backend_usage["cache_read_input_tokens"] = (
                    getattr(details, "cached_tokens", 0) or 0
                )

        if not (hasattr(chunk, "choices") and chunk.choices):
            continue

        choice = chunk.choices[0]
        delta = getattr(choice, "delta", None)
        finish_reason = getattr(choice, "finish_reason", None)

        if finish_reason is not None:
            stop_reason = _map_openai_finish_reason_to_anthropic(finish_reason)

        if not delta:
            continue

        # Handle text / reasoning content
        content = getattr(delta, "content", None) or ""
        if not content:
            content = getattr(delta, "reasoning", None) or ""
        if content:
            if not text_block_started:
                text_block_idx = next_block_idx
                next_block_idx += 1
                yield {
                    "type": "content_block_start",
                    "index": text_block_idx,
                    "content_block": {"type": "text", "text": ""},
                }
                text_block_started = True
                emitted_content_block = True

            output_tokens += 1
            yield {
                "type": "content_block_delta",
                "index": text_block_idx,
                "delta": {"type": "text_delta", "text": content},
            }

        # Handle tool calls
        tool_calls_delta = getattr(delta, "tool_calls", None)
        if not tool_calls_delta:
            continue

        for tc in tool_calls_delta:
            tc_index = getattr(tc, "index", 0)
            tc_id = getattr(tc, "id", None)
            tc_function = getattr(tc, "function", None)

            if tc_index not in tool_calls:
                tool_calls[tc_index] = {
                    "id": sanitize_anthropic_tool_use_id(
                        tc_id or f"toolu_{uuid.uuid4().hex[:24]}",
                    ),
                    "name": "",
                    "input_json": "",
                    "started": False,
                    "block_index": -1,
                }

            if tc_id and not tool_calls[tc_index]["id"]:
                tool_calls[tc_index]["id"] = sanitize_anthropic_tool_use_id(tc_id)

            if tc_function:
                fn_name = getattr(tc_function, "name", None)
                fn_args = getattr(tc_function, "arguments", None)
                if fn_name:
                    tool_calls[tc_index]["name"] = fn_name
                if fn_args:
                    tool_calls[tc_index]["input_json"] += fn_args

            if tool_calls[tc_index]["name"] and not tool_calls[tc_index]["started"]:
                # Close open text block before starting a tool_use block
                if text_block_started:
                    yield {"type": "content_block_stop", "index": text_block_idx}
                    text_block_started = False

                tool_block_idx = next_block_idx
                next_block_idx += 1
                tool_calls[tc_index]["block_index"] = tool_block_idx

                yield {
                    "type": "content_block_start",
                    "index": tool_block_idx,
                    "content_block": {
                        "type": "tool_use",
                        "id": tool_calls[tc_index]["id"],
                        "name": tool_calls[tc_index]["name"],
                        "input": {},
                    },
                }
                tool_calls[tc_index]["started"] = True
                emitted_content_block = True

                # Flush any buffered input_json
                if tool_calls[tc_index]["input_json"]:
                    yield {
                        "type": "content_block_delta",
                        "index": tool_block_idx,
                        "delta": {
                            "type": "input_json_delta",
                            "partial_json": tool_calls[tc_index]["input_json"],
                        },
                    }
                    tool_calls[tc_index]["input_json"] = ""

            elif tool_calls[tc_index]["started"] and tc_function:
                fn_args = getattr(tc_function, "arguments", None)
                if fn_args:
                    yield {
                        "type": "content_block_delta",
                        "index": tool_calls[tc_index]["block_index"],
                        "delta": {"type": "input_json_delta", "partial_json": fn_args},
                    }

    # Close any open text block
    if text_block_started:
        yield {"type": "content_block_stop", "index": text_block_idx}

    # Close tool call blocks (only those that were actually started)
    for tc_data in tool_calls.values():
        if tc_data["started"]:
            yield {"type": "content_block_stop", "index": tc_data["block_index"]}

    # Empty response: emit a minimal text block so the event stream is valid
    if not emitted_content_block:
        yield {
            "type": "content_block_start",
            "index": 0,
            "content_block": {"type": "text", "text": ""},
        }
        yield {"type": "content_block_stop", "index": 0}

    # Prefer real usage from the backend over the heuristic delta counter.
    final_usage: dict[str, Any] = {"output_tokens": output_tokens}
    if backend_usage is not None:
        final_usage.update(backend_usage)

    yield {
        "type": "message_delta",
        "delta": {"stop_reason": stop_reason, "stop_sequence": None},
        "usage": final_usage,
    }

    yield {"type": "message_stop"}
