# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Responses API <-> OpenAI Chat Completions format conversion utilities.

This module provides pure functions for translating between the OpenAI
Responses API format and the OpenAI Chat Completions API format.

Canonical internal format: OpenAI Chat Completions (messages, tools, tool_choice).
Backend target: vLLM OpenAI-compatible endpoint.

Mapping summary (request):
- Responses ``input`` (string) -> single user message
- Responses ``input`` (array of items) -> messages list
- Responses ``instructions`` -> system message
- Responses ``max_output_tokens`` -> ``max_completion_tokens``
- Responses ``tools[i].{name, description, parameters}``
    -> ``tools[i].{type: "function", function: {name, description, parameters}}``
- Chat-compatible fields such as ``model``, ``temperature``, ``top_p``,
  ``stream``, ``parallel_tool_calls``, ``metadata`` -> passthrough

Mapping summary (response):
- ``choices[0].message.content`` -> output message with output_text
- ``choices[0].message.tool_calls`` -> output function_call items
- ``usage.prompt_tokens`` -> ``usage.input_tokens``
- ``usage.completion_tokens`` -> ``usage.output_tokens``
"""

import json
import time
import uuid
from collections.abc import AsyncGenerator, Mapping
from typing import Any

from openai.types.chat import ChatCompletionChunk

# -----------------------------------------------------------------------------
# Responses API -> Chat Completions (Request)
# -----------------------------------------------------------------------------

def convert_responses_request_to_chat_completions(body: dict[str, Any]) -> dict[str, Any]:
    """Convert a Responses API request body to Chat Completions format.

    Args:
        body: The raw Responses API request body.

    Returns:
        A dict suitable for ``proxy.acompletion(**result)``.
    """
    result: dict[str, Any] = {}

    # -- messages --
    messages: list[dict[str, Any]] = []

    # instructions -> system message
    instructions = body.get("instructions")
    if instructions:
        messages.append({
            "role": "system",
            "content": _convert_responses_message_content_to_chat(
                instructions,
                role="system",
            ),
        })

    # input -> user/assistant/tool messages
    input_data = body.get("input", "")
    if isinstance(input_data, str):
        messages.append({"role": "user", "content": input_data})
    elif isinstance(input_data, list):
        messages.extend(_convert_input_items_to_messages(input_data))

    result["messages"] = messages

    # -- model (passthrough) --
    if "model" in body:
        result["model"] = body["model"]

    # -- max_output_tokens -> max_completion_tokens --
    if "max_output_tokens" in body:
        result["max_completion_tokens"] = body["max_output_tokens"]

    # -- tools --
    tools = body.get("tools")
    if tools:
        chat_tools = _convert_responses_tools_to_chat(tools)
        if chat_tools:
            result["tools"] = chat_tools

    # -- tool_choice --
    if "tool_choice" in body:
        tool_choice = _convert_responses_tool_choice_to_chat(body["tool_choice"])
        if tool_choice is not None:
            result["tool_choice"] = tool_choice

    # -- Responses reasoning/text fields that have Chat equivalents --
    reasoning = body.get("reasoning")
    if isinstance(reasoning, dict) and reasoning.get("effort") is not None:
        result["reasoning_effort"] = reasoning["effort"]

    response_format = _convert_responses_text_to_chat_response_format(
        body.get("text"),
    )
    if response_format is not None:
        result["response_format"] = response_format

    # -- simple Chat-compatible passthrough params --
    # Responses state handles such as previous_response_id and conversation
    # have no Chat Completions equivalent, so they are intentionally omitted.
    for key in (
        "metadata",
        "parallel_tool_calls",
        "prompt_cache_key",
        "prompt_cache_retention",
        "safety_identifier",
        "service_tier",
        "store",
        "stream",
        "stream_options",
        "temperature",
        "top_logprobs",
        "top_p",
        "user",
    ):
        if key in body:
            result[key] = body[key]

    return result


def _convert_input_items_to_messages(
    items: list[Any],
) -> list[dict[str, Any]]:
    """Convert Responses API input items array to Chat Completions messages.

    Handles:
    - ``{type: "message", role: "user"|"system", content: ...}``
    - ``{type: "message", role: "assistant", content: ...}`` with possible
      tool calls embedded in content blocks
    - ``{type: "function_call", name, call_id, arguments}`` (assistant tool call)
    - ``{type: "function_call_output", call_id, output}`` (tool result)

    Consecutive ``function_call`` and ``function_call_output`` items are
    merged into a single assistant message with multiple ``tool_calls``
    followed by the corresponding tool result messages.  This encourages
    the model to generate parallel tool calls instead of one-per-turn.
    """
    messages: list[dict[str, Any]] = []
    # Buffers for a contiguous block of tool calls / outputs
    pending_tool_calls: list[dict[str, Any]] = []
    pending_tool_outputs: list[dict[str, Any]] = []
    deferred_messages: list[dict[str, Any]] = []

    def flush_tool_block() -> None:
        nonlocal pending_tool_calls, pending_tool_outputs, deferred_messages
        messages.extend(
            _flush_tool_block(pending_tool_calls, pending_tool_outputs)
        )
        pending_tool_calls = []
        pending_tool_outputs = []
        if deferred_messages:
            messages.extend(deferred_messages)
            deferred_messages = []

    for item in items:
        if not isinstance(item, dict):
            continue
        item_type = item.get("type")

        if item_type == "message":
            role = item.get("role", "user")
            content = _convert_responses_message_content_to_chat(
                item.get("content", ""),
                role=role,
            )
            message = {"role": role, "content": content}

            if pending_tool_calls and not pending_tool_outputs:
                deferred_messages.append(message)
                continue

            # Flush any pending tool block first
            if pending_tool_calls or pending_tool_outputs:
                flush_tool_block()

            messages.append(message)

        elif item_type == "function_call":
            # If we already have pending outputs, a new function_call means
            # we've crossed a turn boundary (the previous turn's outputs are
            # done and a new LLM response is starting).  Flush first.
            if pending_tool_outputs:
                flush_tool_block()

            # Buffer tool calls — they'll be merged into one assistant message
            pending_tool_calls.append({
                "id": item.get("call_id") or f"call_{uuid.uuid4().hex[:24]}",
                "type": "function",
                "function": {
                    "name": item.get("name", ""),
                    "arguments": _json_string(item.get("arguments", "{}")),
                },
            })

        elif item_type == "function_call_output":
            # Buffer tool outputs — they'll follow the merged assistant message
            pending_tool_outputs.append({
                "role": "tool",
                "tool_call_id": item.get("call_id") or "",
                "content": _tool_output_to_text(item.get("output", "")),
            })

    # Flush remaining tool block
    if pending_tool_calls or pending_tool_outputs:
        flush_tool_block()

    return messages


def _flush_tool_block(
    tool_calls: list[dict[str, Any]],
    tool_outputs: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Create an assistant message with all tool_calls followed by tool result messages.

    Merges all buffered ``function_call`` items into a single assistant
    message and appends all ``function_call_output`` items as tool messages.
    """
    result: list[dict[str, Any]] = []
    tool_call_ids = {
        tool_call.get("id")
        for tool_call in tool_calls
        if tool_call.get("id")
    }
    if tool_calls:
        result.append({
            "role": "assistant",
            "content": None,
            "tool_calls": list(tool_calls),
        })
    for output in tool_outputs:
        if output.get("tool_call_id") in tool_call_ids:
            result.append(output)
        else:
            result.append(_orphan_tool_output_to_user_message(output))
    return result


def _convert_responses_message_content_to_chat(
    content: Any,
    *,
    role: Any,
) -> str | list[dict[str, Any]]:
    """Convert Responses message content to a Chat message content value.

    Text-only content stays a string to preserve the long-standing
    Chat-Completions shape. User multimodal content becomes Chat content
    parts so images/files/audio survive the Responses -> Chat hop.
    """
    if isinstance(content, str):
        return content

    if not isinstance(content, list):
        return str(content) if content else ""

    text_parts: list[str] = []
    chat_parts: list[dict[str, Any]] = []
    has_non_text_part = False
    for block in content:
        if not isinstance(block, dict):
            continue
        block_type = block.get("type", "")
        if block_type in {"input_text", "output_text", "text"}:
            text = block.get("text", "")
            if isinstance(text, str):
                text_parts.append(text)
                chat_parts.append({"type": "text", "text": text})
        elif block_type == "refusal":
            refusal = block.get("refusal")
            if isinstance(refusal, str):
                text_parts.append(refusal)
                chat_parts.append({"type": "text", "text": refusal})
        elif block_type == "input_image":
            image_part = _convert_responses_image_to_chat(block)
            if image_part is not None:
                chat_parts.append(image_part)
                has_non_text_part = True
        elif block_type == "input_file":
            file_part = _convert_responses_file_to_chat(block)
            if file_part is not None:
                chat_parts.append(file_part)
                has_non_text_part = True

    if has_non_text_part and role == "user":
        return chat_parts
    return "\n".join(text_parts) if text_parts else ""


def _convert_responses_image_to_chat(block: dict[str, Any]) -> dict[str, Any] | None:
    image_url = block.get("image_url")
    if not image_url:
        return None
    if isinstance(image_url, dict):
        payload = dict(image_url)
    else:
        payload = {"url": str(image_url)}
    detail = block.get("detail")
    if detail in {"auto", "low", "high"}:
        payload["detail"] = detail
    return {"type": "image_url", "image_url": payload}


def _convert_responses_file_to_chat(block: dict[str, Any]) -> dict[str, Any] | None:
    file_payload: dict[str, Any] = {}
    for key in ("file_data", "file_id", "filename"):
        value = block.get(key)
        if value is not None:
            file_payload[key] = value
    if not file_payload:
        return None
    return {"type": "file", "file": file_payload}


def _orphan_tool_output_to_user_message(output: dict[str, Any]) -> dict[str, str]:
    call_id = output.get("tool_call_id")
    content = _tool_output_to_text(output.get("content", ""))
    if call_id:
        return {"role": "user", "content": f"Tool result {call_id}: {content}"}
    return {"role": "user", "content": f"Tool result: {content}"}


def _tool_output_to_text(output: Any) -> str:
    if isinstance(output, str):
        return output
    return _json_string(output)


def _json_string(value: Any) -> str:
    if isinstance(value, str):
        return value
    try:
        return json.dumps(value, default=str)
    except (TypeError, ValueError):
        return str(value)


def _convert_responses_tools_to_chat(
    tools: list[Any],
) -> list[dict[str, Any]]:
    """Convert Responses API tool definitions to Chat Completions format.

    Handles two tool definition formats:
    - Standard Responses API: ``{type: "function", name: "...", parameters: {...}}``
    - Codex CLI format: ``{id: "...", inputSchema: {jsonSchema: {...}}}``
    """
    chat_tools: list[dict[str, Any]] = []
    for tool in tools:
        if not isinstance(tool, dict):
            continue
        tool_type = tool.get("type")
        is_codex_tool = "id" in tool and "inputSchema" in tool
        if tool_type not in (None, "function") and not is_codex_tool:
            continue

        nested_function = tool.get("function")
        if isinstance(nested_function, dict):
            name = nested_function.get("name", "")
            description = nested_function.get("description", "")
            parameters = nested_function.get("parameters", {})
            strict = nested_function.get("strict")
        else:
            # Tool name: prefer "name", fall back to "id" (Codex format)
            name = tool.get("name") or tool.get("id", "")
            description = tool.get("description", "")
            parameters = tool.get("parameters")
            strict = tool.get("strict")

        # Skip tools with empty names (e.g. ghost entries from Codex)
        if not name:
            continue

        # Parameters: prefer "parameters", fall back to
        # "inputSchema.jsonSchema" (Codex format)
        if parameters is None:
            input_schema = tool.get("inputSchema")
            if isinstance(input_schema, dict):
                parameters = input_schema.get("jsonSchema", {})
            else:
                parameters = {}

        function: dict[str, Any] = {
            "name": name,
            "description": description,
            "parameters": parameters,
        }
        if strict is not None:
            function["strict"] = strict
        chat_tools.append({"type": "function", "function": function})
    return chat_tools


def _convert_responses_tool_choice_to_chat(choice: Any) -> str | dict[str, Any] | None:
    if isinstance(choice, str):
        if choice in {"auto", "none", "required"}:
            return choice
        return None
    if not isinstance(choice, dict):
        return None
    choice_type = choice.get("type")
    if choice_type == "function":
        name = choice.get("name")
        if isinstance(name, str) and name:
            return {"type": "function", "function": {"name": name}}
    if choice_type == "tool":
        name = choice.get("name")
        if isinstance(name, str) and name:
            return {"type": "function", "function": {"name": name}}
    return None


def _convert_responses_text_to_chat_response_format(
    text: Any,
) -> dict[str, Any] | None:
    if not isinstance(text, dict):
        return None
    fmt = text.get("format")
    if not isinstance(fmt, dict):
        return None
    fmt_type = fmt.get("type")
    if fmt_type == "json_schema":
        if isinstance(fmt.get("json_schema"), dict):
            return {"type": "json_schema", "json_schema": fmt["json_schema"]}
        json_schema: dict[str, Any] = {}
        for key in ("name", "description", "schema", "strict"):
            if key in fmt:
                json_schema[key] = fmt[key]
        if json_schema:
            return {"type": "json_schema", "json_schema": json_schema}
    if fmt_type in {"json_object", "text"}:
        return {"type": fmt_type}
    return None


# -----------------------------------------------------------------------------
# Chat Completions -> Responses API (Response, non-streaming)
# -----------------------------------------------------------------------------

def convert_chat_response_to_responses(
    response: Any,
    original_body: dict[str, Any],
) -> dict[str, Any]:
    """Convert a Chat Completions response to Responses API format.

    Args:
        response: The Chat Completions response (object or dict).
        original_body: The original Responses API request body (for model name).

    Returns:
        Responses API response dict.
    """
    # Normalise to dict
    if hasattr(response, "model_dump"):
        resp = response.model_dump()
    elif hasattr(response, "to_dict"):
        resp = response.to_dict()
    elif isinstance(response, dict):
        resp = response
    else:
        resp = {}

    resp_id = resp.get("id", f"resp_{uuid.uuid4().hex[:24]}")
    model = resp.get("model") or original_body.get("model", "unknown")

    # Extract choice
    choices = resp.get("choices", [])
    output: list[dict[str, Any]] = []
    status = "completed"

    if choices:
        choice = choices[0]
        message = choice.get("message", {})
        # Text content
        text = _chat_message_content_to_text(message.get("content"))
        if text:
            output.append({
                "type": "message",
                "id": f"msg_{uuid.uuid4().hex[:24]}",
                "role": "assistant",
                "status": "completed",
                "content": [{"type": "output_text", "text": text}],
            })

        # Tool calls
        tool_calls = message.get("tool_calls")
        if tool_calls:
            for tc in tool_calls:
                func = tc.get("function", {})
                output.append({
                    "type": "function_call",
                    "id": f"fc_{uuid.uuid4().hex[:24]}",
                    "call_id": tc.get("id", f"call_{uuid.uuid4().hex[:24]}"),
                    "name": func.get("name", ""),
                    "arguments": func.get("arguments", "{}"),
                    "status": "completed",
                })

    # Usage
    usage_data = _dump_response_mapping(resp.get("usage"))
    usage = {
        "input_tokens": usage_data.get("prompt_tokens", 0),
        "output_tokens": usage_data.get("completion_tokens", 0),
        "total_tokens": usage_data.get("total_tokens", 0),
    }

    return {
        "id": resp_id,
        "object": "response",
        "status": status,
        "model": model,
        "output": output,
        "usage": usage,
    }


def _chat_message_content_to_text(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for part in content:
            if not isinstance(part, dict):
                continue
            if part.get("type") == "text":
                text = part.get("text")
                if isinstance(text, str):
                    parts.append(text)
            elif part.get("type") == "refusal":
                refusal = part.get("refusal")
                if isinstance(refusal, str):
                    parts.append(refusal)
        return "\n".join(parts)
    return str(content) if content else ""


def convert_responses_response_to_chat_completions(
    response: Any,
    *,
    fallback_model: str = "unknown",
) -> dict[str, Any]:
    """Convert an OpenAI Responses API response to Chat Completions format."""
    resp = _dump_response_mapping(response)
    model = resp.get("model") or fallback_model
    created = resp.get("created") or resp.get("created_at")

    content = ""
    tool_calls: list[dict[str, Any]] = []
    output = resp.get("output")
    if isinstance(output, list):
        for item in output:
            if not isinstance(item, dict):
                continue
            if item.get("type") == "message":
                content += _extract_responses_output_text(item)
            elif item.get("type") == "function_call":
                tool_calls.append({
                    "id": item.get("call_id") or item.get("id"),
                    "type": "function",
                    "function": {
                        "name": item.get("name") or "",
                        "arguments": item.get("arguments") or "",
                    },
                })

    message: dict[str, Any] = {
        "role": "assistant",
        "content": content or None,
    }
    if tool_calls:
        message["tool_calls"] = tool_calls

    result: dict[str, Any] = {
        "id": f"chatcmpl-{uuid.uuid4().hex[:24]}",
        "object": "chat.completion",
        "created": created if isinstance(created, int) else 0,
        "model": str(model),
        "choices": [{
            "index": 0,
            "message": message,
            "finish_reason": "tool_calls" if tool_calls else "stop",
        }],
    }
    usage = _responses_usage_to_chat_completion(resp.get("usage"))
    if usage is not None:
        result["usage"] = usage
    return result


def _dump_response_mapping(response: Any) -> dict[str, Any]:
    if isinstance(response, dict):
        return dict(response)
    if hasattr(response, "model_dump"):
        dumped = response.model_dump(mode="json", exclude_none=True)
        return dict(dumped) if isinstance(dumped, dict) else {}
    if hasattr(response, "to_dict"):
        dumped = response.to_dict()
        return dict(dumped) if isinstance(dumped, dict) else {}
    return {}


def _extract_responses_output_text(item: dict[str, Any]) -> str:
    content = item.get("content")
    if not isinstance(content, list):
        return ""
    parts: list[str] = []
    for part in content:
        if not isinstance(part, dict):
            continue
        if part.get("type") not in {"output_text", "text"}:
            continue
        text = part.get("text")
        if isinstance(text, str):
            parts.append(text)
    return "".join(parts)


def _responses_usage_to_chat_completion(usage: Any) -> dict[str, Any] | None:
    usage_dict = _dump_response_mapping(usage)
    if not usage_dict:
        return None
    prompt_tokens = usage_dict.get("input_tokens", 0) or 0
    completion_tokens = usage_dict.get("output_tokens", 0) or 0
    result: dict[str, Any] = {
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": usage_dict.get(
            "total_tokens",
            prompt_tokens + completion_tokens,
        ) or 0,
    }
    input_details = usage_dict.get("input_tokens_details")
    if isinstance(input_details, dict):
        cached_tokens = input_details.get("cached_tokens")
        if isinstance(cached_tokens, int):
            result["prompt_tokens_details"] = {"cached_tokens": cached_tokens}
    output_details = usage_dict.get("output_tokens_details")
    if isinstance(output_details, dict):
        reasoning_tokens = output_details.get("reasoning_tokens")
        if isinstance(reasoning_tokens, int):
            result["completion_tokens_details"] = {
                "reasoning_tokens": reasoning_tokens,
            }
    return result


# -----------------------------------------------------------------------------
# Responses API -> Chat Completions (Streaming)
# -----------------------------------------------------------------------------

async def stream_responses_to_chat_completion_chunks(
    responses_stream: Any,
    *,
    model: str = "unknown",
) -> AsyncGenerator[ChatCompletionChunk, None]:
    """Convert Responses API streaming events to ChatCompletionChunk objects."""
    stream_id = f"chatcmpl_{uuid.uuid4().hex[:24]}"
    created = int(time.time())
    current_model = model
    started = False
    finished = False
    saw_tool_call = False
    tool_indexes: dict[int, int] = {}
    next_tool_index = 0
    tool_arguments: dict[int, str] = {}

    async for event in responses_stream:
        event_dict = _dump_response_mapping(event)
        event_type = event_dict.get("type")
        response = event_dict.get("response")
        if isinstance(response, dict):
            stream_id = _chat_completion_stream_id(str(response.get("id") or stream_id))
            current_model = str(response.get("model") or current_model)
            created_at = response.get("created_at")
            if isinstance(created_at, (int, float)):
                created = int(created_at)

        if event_type == "response.created":
            if not started:
                yield _chat_stream_chunk(
                    stream_id=stream_id,
                    created=created,
                    model=current_model,
                    delta={"role": "assistant"},
                )
                started = True
            continue

        if event_type == "response.output_text.delta":
            if not started:
                yield _chat_stream_chunk(
                    stream_id=stream_id,
                    created=created,
                    model=current_model,
                    delta={"role": "assistant"},
                )
                started = True
            delta = event_dict.get("delta")
            if isinstance(delta, str) and delta:
                yield _chat_stream_chunk(
                    stream_id=stream_id,
                    created=created,
                    model=current_model,
                    delta={"content": delta},
                )
            continue

        if event_type == "response.output_item.added":
            item = event_dict.get("item")
            if not isinstance(item, dict) or item.get("type") != "function_call":
                continue
            output_index = _int_value(event_dict.get("output_index"), 0)
            tool_index = tool_indexes.setdefault(output_index, next_tool_index)
            if tool_index == next_tool_index:
                next_tool_index += 1
            saw_tool_call = True
            arguments = _str_value(item.get("arguments"))
            if arguments:
                tool_arguments[output_index] = arguments
            yield _chat_tool_call_chunk(
                stream_id=stream_id,
                created=created,
                model=current_model,
                index=tool_index,
                tool_id=_str_value(item.get("call_id") or item.get("id")),
                name=_str_value(item.get("name")),
                arguments=arguments,
            )
            continue

        if event_type == "response.function_call_arguments.delta":
            output_index = _int_value(event_dict.get("output_index"), 0)
            tool_index = tool_indexes.setdefault(output_index, next_tool_index)
            if tool_index == next_tool_index:
                next_tool_index += 1
            delta = event_dict.get("delta")
            if isinstance(delta, str) and delta:
                saw_tool_call = True
                tool_arguments[output_index] = tool_arguments.get(output_index, "") + delta
                yield _chat_tool_call_chunk(
                    stream_id=stream_id,
                    created=created,
                    model=current_model,
                    index=tool_index,
                    arguments=delta,
                )
            continue

        if event_type == "response.output_item.done":
            item = event_dict.get("item")
            if not isinstance(item, dict) or item.get("type") != "function_call":
                continue
            output_index = _int_value(event_dict.get("output_index"), 0)
            arguments = _str_value(item.get("arguments"))
            if arguments and arguments != tool_arguments.get(output_index):
                tool_index = tool_indexes.setdefault(output_index, next_tool_index)
                if tool_index == next_tool_index:
                    next_tool_index += 1
                saw_tool_call = True
                yield _chat_tool_call_chunk(
                    stream_id=stream_id,
                    created=created,
                    model=current_model,
                    index=tool_index,
                    arguments=arguments,
                )
            continue

        if event_type == "response.completed":
            if not started:
                yield _chat_stream_chunk(
                    stream_id=stream_id,
                    created=created,
                    model=current_model,
                    delta={"role": "assistant"},
                )
                started = True
            yield _chat_stream_chunk(
                stream_id=stream_id,
                created=created,
                model=current_model,
                delta={},
                finish_reason="tool_calls" if saw_tool_call else "stop",
                usage=(
                    _responses_usage_to_chat_completion(response.get("usage"))
                    if isinstance(response, dict)
                    else None
                ),
            )
            finished = True

    if not finished:
        if not started:
            yield _chat_stream_chunk(
                stream_id=stream_id,
                created=created,
                model=current_model,
                delta={"role": "assistant"},
            )
        yield _chat_stream_chunk(
            stream_id=stream_id,
            created=created,
            model=current_model,
            delta={},
            finish_reason="tool_calls" if saw_tool_call else "stop",
        )


def _chat_stream_chunk(
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


def _chat_tool_call_chunk(
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
    return _chat_stream_chunk(
        stream_id=stream_id,
        created=created,
        model=model,
        delta={"tool_calls": [tool_call]},
    )


def _chat_completion_stream_id(response_id: str) -> str:
    if response_id.startswith("chatcmpl"):
        return response_id
    return f"chatcmpl_{response_id.removeprefix('resp_')}"


def _int_value(value: object, default: int) -> int:
    return value if isinstance(value, int) else default


def _str_value(value: object) -> str | None:
    return value if isinstance(value, str) and value else None


# -----------------------------------------------------------------------------
# Chat Completions -> Responses API (Streaming)
# -----------------------------------------------------------------------------

async def stream_chat_to_responses_sse(
    chat_stream: Any,
    original_body: dict[str, Any],
) -> AsyncGenerator[str, None]:
    """Convert Chat Completions streaming chunks to Responses API SSE events.

    Pure async generator — no server/FastAPI dependencies.

    Emits the full Responses API SSE lifecycle:
    1. ``response.created``
    2. For text: ``response.output_item.added`` (message),
       ``response.content_part.added``, ``response.output_text.delta`` per chunk,
       ``response.content_part.done``, ``response.output_item.done``
    3. For each tool call: ``response.output_item.added`` (function_call),
       ``response.function_call_arguments.delta`` per chunk,
       ``response.output_item.done``
    4. ``response.completed``
    """
    resp_id = f"resp_{uuid.uuid4().hex[:24]}"
    model = original_body.get("model", "unknown")

    # Tracking state
    text_started = False
    text_content = ""
    tool_calls: dict[int, dict[str, Any]] = {}
    usage = {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0}
    next_output_index = 0
    text_output_index: int | None = None

    # 1. response.created
    created_event = {
        "type": "response.created",
        "response": {
            "id": resp_id,
            "object": "response",
            "status": "in_progress",
            "model": model,
            "output": [],
            "usage": usage,
        },
    }
    yield f"event: response.created\ndata: {json.dumps(created_event)}\n\n"

    async for chunk in chat_stream:
        if not hasattr(chunk, "choices") or not chunk.choices:
            # Capture usage from final chunk
            chunk_usage = getattr(chunk, "usage", None)
            if chunk_usage:
                usage["input_tokens"] = (
                    getattr(chunk_usage, "prompt_tokens", 0) or 0
                )
                usage["output_tokens"] = (
                    getattr(chunk_usage, "completion_tokens", 0) or 0
                )
                usage["total_tokens"] = (
                    getattr(chunk_usage, "total_tokens", 0) or 0
                )
            continue

        choice = chunk.choices[0]
        delta = getattr(choice, "delta", None)

        # Capture usage from chunk if present
        chunk_usage = getattr(chunk, "usage", None)
        if chunk_usage:
            usage["input_tokens"] = (
                getattr(chunk_usage, "prompt_tokens", 0) or 0
            )
            usage["output_tokens"] = (
                getattr(chunk_usage, "completion_tokens", 0) or 0
            )
            usage["total_tokens"] = (
                getattr(chunk_usage, "total_tokens", 0) or 0
            )

        if delta:
            # --- Text content ---
            content = getattr(delta, "content", None)
            if content:
                if not text_started:
                    text_started = True
                    text_output_index = next_output_index
                    next_output_index += 1

                    msg_id = f"msg_{uuid.uuid4().hex[:24]}"
                    item_added = {
                        "type": "response.output_item.added",
                        "output_index": text_output_index,
                        "item": {
                            "type": "message",
                            "id": msg_id,
                            "role": "assistant",
                            "status": "in_progress",
                            "content": [],
                        },
                    }
                    yield (
                        f"event: response.output_item.added\n"
                        f"data: {json.dumps(item_added)}\n\n"
                    )

                    part_added = {
                        "type": "response.content_part.added",
                        "output_index": text_output_index,
                        "content_index": 0,
                        "part": {"type": "output_text", "text": ""},
                    }
                    yield (
                        f"event: response.content_part.added\n"
                        f"data: {json.dumps(part_added)}\n\n"
                    )

                assert text_output_index is not None
                text_content += content
                text_delta = {
                    "type": "response.output_text.delta",
                    "output_index": text_output_index,
                    "content_index": 0,
                    "delta": content,
                }
                yield (
                    f"event: response.output_text.delta\n"
                    f"data: {json.dumps(text_delta)}\n\n"
                )

            # --- Tool calls ---
            tool_calls_delta = getattr(delta, "tool_calls", None)
            if tool_calls_delta:
                for tc in tool_calls_delta:
                    tc_index = getattr(tc, "index", 0)
                    tc_id = getattr(tc, "id", None)
                    tc_function = getattr(tc, "function", None)

                    if tc_index not in tool_calls:
                        tool_calls[tc_index] = {
                            "name": "",
                            "call_id": tc_id or f"call_{uuid.uuid4().hex[:24]}",
                            "arguments": "",
                            "started": False,
                            "output_index": None,
                        }

                    if tc_id and tc_id != tool_calls[tc_index]["call_id"]:
                        tool_calls[tc_index]["call_id"] = tc_id

                    if tc_function:
                        fn_name = getattr(tc_function, "name", None)
                        fn_args = getattr(tc_function, "arguments", None)

                        if fn_name:
                            tool_calls[tc_index]["name"] = fn_name
                        if fn_args:
                            tool_calls[tc_index]["arguments"] += fn_args

                    # Emit output_item.added once we have the name
                    if (
                        tool_calls[tc_index]["name"]
                        and not tool_calls[tc_index]["started"]
                    ):
                        tool_calls[tc_index]["started"] = True
                        output_idx = next_output_index
                        next_output_index += 1
                        tool_calls[tc_index]["output_index"] = output_idx

                        fc_id = f"fc_{uuid.uuid4().hex[:24]}"
                        tool_calls[tc_index]["fc_id"] = fc_id
                        item_added = {
                            "type": "response.output_item.added",
                            "output_index": output_idx,
                            "item": {
                                "type": "function_call",
                                "id": fc_id,
                                "call_id": tool_calls[tc_index]["call_id"],
                                "name": tool_calls[tc_index]["name"],
                                "arguments": "",
                                "status": "in_progress",
                            },
                        }
                        yield (
                            f"event: response.output_item.added\n"
                            f"data: {json.dumps(item_added)}\n\n"
                        )

                        # Emit any buffered arguments
                        if tool_calls[tc_index]["arguments"]:
                            args_delta = {
                                "type": "response.function_call_arguments.delta",
                                "output_index": output_idx,
                                "delta": tool_calls[tc_index]["arguments"],
                            }
                            yield (
                                f"event: response.function_call_arguments.delta\n"
                                f"data: {json.dumps(args_delta)}\n\n"
                            )

                    elif tool_calls[tc_index]["started"] and tc_function:
                        fn_args = getattr(tc_function, "arguments", None)
                        if fn_args:
                            output_idx_value = tool_calls[tc_index].get("output_index")
                            if not isinstance(output_idx_value, int):
                                continue
                            args_delta = {
                                "type": "response.function_call_arguments.delta",
                                "output_index": output_idx_value,
                                "delta": fn_args,
                            }
                            yield (
                                f"event: response.function_call_arguments.delta\n"
                                f"data: {json.dumps(args_delta)}\n\n"
                            )

    # --- Close lifecycle events ---

    if text_started and text_output_index is not None:
        part_done = {
            "type": "response.content_part.done",
            "output_index": text_output_index,
            "content_index": 0,
            "part": {"type": "output_text", "text": text_content},
        }
        yield (
            f"event: response.content_part.done\n"
            f"data: {json.dumps(part_done)}\n\n"
        )

        item_done = {
            "type": "response.output_item.done",
            "output_index": text_output_index,
            "item": {
                "type": "message",
                "role": "assistant",
                "status": "completed",
                "content": [{"type": "output_text", "text": text_content}],
            },
        }
        yield (
            f"event: response.output_item.done\n"
            f"data: {json.dumps(item_done)}\n\n"
        )

    for tc_index in sorted(tool_calls.keys()):
        tc_info = tool_calls[tc_index]
        if not tc_info.get("started"):
            continue
        output_idx_value = tc_info.get("output_index")
        if not isinstance(output_idx_value, int):
            continue

        args_done = {
            "type": "response.function_call_arguments.done",
            "output_index": output_idx_value,
            "arguments": tc_info["arguments"],
        }
        yield (
            f"event: response.function_call_arguments.done\n"
            f"data: {json.dumps(args_done)}\n\n"
        )

        item_done = {
            "type": "response.output_item.done",
            "output_index": output_idx_value,
            "item": {
                "type": "function_call",
                "id": tc_info.get("fc_id", f"fc_{uuid.uuid4().hex[:24]}"),
                "call_id": tc_info["call_id"],
                "name": tc_info["name"],
                "arguments": tc_info["arguments"],
                "status": "completed",
            },
        }
        yield (
            f"event: response.output_item.done\n"
            f"data: {json.dumps(item_done)}\n\n"
        )

    # Build final output array
    final_items: list[tuple[int, dict[str, Any]]] = []
    if text_started and text_output_index is not None:
        final_items.append(
            (
                text_output_index,
                {
                    "type": "message",
                    "role": "assistant",
                    "status": "completed",
                    "content": [{"type": "output_text", "text": text_content}],
                },
            ),
        )
    for tc_index in sorted(tool_calls.keys()):
        tc_info = tool_calls[tc_index]
        if tc_info.get("started"):
            output_idx_value = tc_info.get("output_index")
            if not isinstance(output_idx_value, int):
                continue
            final_items.append(
                (
                    output_idx_value,
                    {
                        "type": "function_call",
                        "id": tc_info.get("fc_id", f"fc_{uuid.uuid4().hex[:24]}"),
                        "call_id": tc_info["call_id"],
                        "name": tc_info["name"],
                        "arguments": tc_info["arguments"],
                        "status": "completed",
                    },
                ),
            )
    final_output = [item for _, item in sorted(final_items, key=lambda pair: pair[0])]

    completed_event = {
        "type": "response.completed",
        "response": {
            "id": resp_id,
            "object": "response",
            "status": "completed",
            "model": model,
            "output": final_output,
            "usage": usage,
        },
    }
    yield (
        f"event: response.completed\n"
        f"data: {json.dumps(completed_event)}\n\n"
    )


async def synthesize_responses_sse(
    response: Any,
    original_body: dict[str, Any],
) -> AsyncGenerator[str, None]:
    """Synthesize Responses API SSE events from a non-streaming response.

    Used when the backend doesn't support streaming tool call parsing
    (e.g. vLLM with ``llama_nemotron_json`` parser).  The proxy makes a
    non-streaming request, then synthesizes the full SSE lifecycle so the
    client sees a normal streaming response.
    """
    resp_id = f"resp_{uuid.uuid4().hex[:24]}"
    model = original_body.get("model", "unknown")

    responses_result = convert_chat_response_to_responses(response, original_body)
    output = responses_result.get("output", [])
    usage = responses_result.get(
        "usage", {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0},
    )

    # 1. response.created
    created_event = {
        "type": "response.created",
        "response": {
            "id": resp_id,
            "object": "response",
            "status": "in_progress",
            "model": model,
            "output": [],
            "usage": usage,
        },
    }
    yield f"event: response.created\ndata: {json.dumps(created_event)}\n\n"

    # 2. Emit lifecycle events for each output item
    for idx, item in enumerate(output):
        if item.get("type") == "message":
            item_added = {
                "type": "response.output_item.added",
                "output_index": idx,
                "item": {
                    "type": "message",
                    "id": item.get("id", f"msg_{uuid.uuid4().hex[:24]}"),
                    "role": "assistant",
                    "status": "in_progress",
                    "content": [],
                },
            }
            yield (
                f"event: response.output_item.added\n"
                f"data: {json.dumps(item_added)}\n\n"
            )

            for ci, part in enumerate(item.get("content", [])):
                text = part.get("text", "")

                part_added = {
                    "type": "response.content_part.added",
                    "output_index": idx,
                    "content_index": ci,
                    "part": {"type": "output_text", "text": ""},
                }
                yield (
                    f"event: response.content_part.added\n"
                    f"data: {json.dumps(part_added)}\n\n"
                )

                if text:
                    text_delta = {
                        "type": "response.output_text.delta",
                        "output_index": idx,
                        "content_index": ci,
                        "delta": text,
                    }
                    yield (
                        f"event: response.output_text.delta\n"
                        f"data: {json.dumps(text_delta)}\n\n"
                    )

                part_done = {
                    "type": "response.content_part.done",
                    "output_index": idx,
                    "content_index": ci,
                    "part": {"type": "output_text", "text": text},
                }
                yield (
                    f"event: response.content_part.done\n"
                    f"data: {json.dumps(part_done)}\n\n"
                )

            item_done = {
                "type": "response.output_item.done",
                "output_index": idx,
                "item": {**item, "status": "completed"},
            }
            yield (
                f"event: response.output_item.done\n"
                f"data: {json.dumps(item_done)}\n\n"
            )

        elif item.get("type") == "function_call":
            item_added = {
                "type": "response.output_item.added",
                "output_index": idx,
                "item": {**item, "arguments": "", "status": "in_progress"},
            }
            yield (
                f"event: response.output_item.added\n"
                f"data: {json.dumps(item_added)}\n\n"
            )

            args = item.get("arguments", "")
            if args:
                args_delta = {
                    "type": "response.function_call_arguments.delta",
                    "output_index": idx,
                    "delta": args,
                }
                yield (
                    f"event: response.function_call_arguments.delta\n"
                    f"data: {json.dumps(args_delta)}\n\n"
                )

            args_done = {
                "type": "response.function_call_arguments.done",
                "output_index": idx,
                "arguments": args,
            }
            yield (
                f"event: response.function_call_arguments.done\n"
                f"data: {json.dumps(args_done)}\n\n"
            )

            item_done = {
                "type": "response.output_item.done",
                "output_index": idx,
                "item": {**item, "status": "completed"},
            }
            yield (
                f"event: response.output_item.done\n"
                f"data: {json.dumps(item_done)}\n\n"
            )

    # 3. response.completed
    completed_event = {
        "type": "response.completed",
        "response": {
            "id": resp_id,
            "object": "response",
            "status": "completed",
            "model": model,
            "output": output,
            "usage": usage,
        },
    }
    yield f"event: response.completed\ndata: {json.dumps(completed_event)}\n\n"
