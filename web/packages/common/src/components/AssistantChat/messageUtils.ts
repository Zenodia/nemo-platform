// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import type {
  AppendMessage,
  MessageStatus,
  TextMessagePart,
  ThreadMessageLike,
} from '@assistant-ui/react';
import type { ChatCompletionMessageParam } from 'openai/resources/index.mjs';

const createMessageId = (): string => {
  if (typeof crypto !== 'undefined' && crypto.randomUUID) {
    return crypto.randomUUID();
  }
  return `assistant-chat-${Date.now()}-${Math.random().toString(36).slice(2, 9)}`;
};

export const createTextMessage = (
  role: ThreadMessageLike['role'],
  text: string,
  status?: MessageStatus
): ThreadMessageLike => ({
  id: createMessageId(),
  role,
  content: [{ type: 'text', text }],
  status,
});

const isTextPart = (part: unknown): part is TextMessagePart => {
  if (typeof part !== 'object' || part === null) return false;
  return 'type' in part && part.type === 'text' && 'text' in part && typeof part.text === 'string';
};

export const getMessageText = (message: Pick<ThreadMessageLike, 'content'>): string => {
  if (typeof message.content === 'string') return message.content;
  return message.content
    .filter(isTextPart)
    .map((part) => part.text)
    .join('\n');
};

export const appendMessageToThreadMessage = (message: AppendMessage): ThreadMessageLike => ({
  id: createMessageId(),
  role: message.role,
  content: message.content,
});

const getOpenAIMessage = (message: ThreadMessageLike): ChatCompletionMessageParam | undefined => {
  if (!['assistant', 'system', 'user'].includes(message.role)) return undefined;

  const content = getMessageText(message);
  if (!content) return undefined;

  return {
    role: message.role,
    content,
  } as ChatCompletionMessageParam;
};

export const getOpenAIMessages = (
  messages: readonly ThreadMessageLike[],
  systemPrompt?: string
): ChatCompletionMessageParam[] => {
  const openAIMessages = messages
    .map(getOpenAIMessage)
    .filter((message): message is ChatCompletionMessageParam => message !== undefined);

  if (!systemPrompt) return openAIMessages;

  const withoutSystem = openAIMessages.filter((message) => message.role !== 'system');
  return [{ role: 'system', content: systemPrompt }, ...withoutSystem];
};

const getMessageIndex = (
  messages: readonly ThreadMessageLike[],
  messageId: string | null | undefined
): number => {
  if (!messageId) return -1;

  const explicitIndex = messages.findIndex((message) => message.id === messageId);
  if (explicitIndex !== -1) return explicitIndex;

  const fallbackIndex = Number(messageId);
  return Number.isInteger(fallbackIndex) &&
    fallbackIndex >= 0 &&
    fallbackIndex < messages.length &&
    String(fallbackIndex) === messageId
    ? fallbackIndex
    : -1;
};

export const getEditedMessageIndex = (
  messages: readonly ThreadMessageLike[],
  message: AppendMessage
): number => {
  const sourceIndex = getMessageIndex(messages, message.sourceId);
  if (sourceIndex !== -1) return sourceIndex;

  if (message.parentId === null) return 0;

  const parentIndex = getMessageIndex(messages, message.parentId);
  return parentIndex === -1 ? -1 : parentIndex + 1;
};
