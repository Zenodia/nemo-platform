// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { FlexibleMessage } from '@nemo/sdk/generated/platform/schema';
import {
  ChatCompletion,
  ChatCompletionChunk,
  ChatCompletionMessageParam,
} from 'openai/resources/index.mjs';

import { ExcludedChatCompletionMessageParam } from '../types/chat';

/**
 * Given a message, return the content as a string. If the content is an array, join the array into a string.
 */
export const getContentFromMessage = (message?: ChatCompletionMessageParam): string => {
  if (!message?.content) {
    return '';
  } else if (Array.isArray(message.content)) {
    const content = message.content
      .map((c) => {
        if (c.type === 'text') {
          return c.text;
        } else if (c.type === 'image_url') {
          return c.image_url.url;
        } else if (c.type === 'refusal') {
          return c.refusal;
        }
        return '';
      })
      .join(' ');
    return content;
  }
  return message.content;
};

/**
 * Given a Chunk choice or Completion choice, return the delta or message. Useful for asserting the type of a response and indexing
 * keys relevant to the type.
 */
export const getDeltaOrMessage = (response: ChatCompletionChunk.Choice | ChatCompletion.Choice) => {
  if ('delta' in response) {
    return response.delta;
  }
  return response.message;
};

export const maybeInsertSystemMessage = (
  messages: ExcludedChatCompletionMessageParam[],
  systemPrompt?: string
): ExcludedChatCompletionMessageParam[] => {
  const parsedMessages = messages.map((message) => {
    if (message.role === 'assistant' && message.content === '' && message.tool_calls) {
      return {
        ...message,
        content: JSON.stringify(message.tool_calls),
      };
    }
    return message;
  });

  if (!systemPrompt) {
    return parsedMessages;
  }

  return [
    {
      role: 'system',
      content: systemPrompt,
    },
    ...parsedMessages,
  ];
};

/**
 * Safely extracts string content from a FlexibleMessage.
 * Returns empty string if content is undefined, null, or not a string.
 */
const getStringContent = (content: unknown): string => {
  if (typeof content === 'string') return content;
  if (content === null || content === undefined) return '';
  // Handle array content (OpenAI multi-part messages) by joining text parts
  if (Array.isArray(content)) {
    return content
      .filter(
        (part): part is { type: 'text'; text: string } =>
          typeof part === 'object' && part?.type === 'text' && typeof part?.text === 'string'
      )
      .map((part) => part.text)
      .join(' ');
  }
  return '';
};

/**
 * Converts a FlexibleMessage (intake API) to ChatCompletionMessageParam (OpenAI).
 * FlexibleMessage is provider-agnostic; this maps it to the OpenAI standard.
 */
export const toOpenAIMessage = (message: FlexibleMessage): ChatCompletionMessageParam => {
  const { role, content, name, tool_calls, tool_call_id } = message;
  const stringContent = getStringContent(content);

  switch (role) {
    case 'user':
      return {
        role: 'user',
        content: stringContent,
        ...(typeof name === 'string' && { name }),
      };
    case 'assistant':
      return {
        role: 'assistant',
        content: stringContent || null,
        ...(Array.isArray(tool_calls) && { tool_calls }),
      };
    case 'system':
      return {
        role: 'system',
        content: stringContent,
        ...(typeof name === 'string' && { name }),
      };
    case 'tool':
      return {
        role: 'tool',
        content: stringContent,
        tool_call_id: typeof tool_call_id === 'string' ? tool_call_id : '',
      };
    case 'function':
      // Map legacy 'function' role to 'tool' for OpenAI compatibility
      return {
        role: 'tool',
        content: stringContent,
        tool_call_id: typeof tool_call_id === 'string' ? tool_call_id : '',
      };
    case 'developer':
      return { role: 'developer', content: stringContent };
    default:
      return { role: 'user', content: stringContent };
  }
};
