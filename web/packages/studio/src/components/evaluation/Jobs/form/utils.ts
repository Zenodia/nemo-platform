// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import type { ChatCompletionMessageRowValues } from '@nemo/common/src/components/ChatCompletionInput';

export type LLMJudgePromptMessage = Pick<ChatCompletionMessageRowValues, 'role' | 'content'>;

export interface LLMJudgeChatPromptTemplate {
  [key: string]: unknown;
  messages: LLMJudgePromptMessage[];
}

export const buildLLMJudgeChatPromptTemplate = (
  messages: LLMJudgePromptMessage[]
): LLMJudgeChatPromptTemplate | null => {
  const normalizedMessages = messages
    .map(({ role, content }) => ({ role, content }))
    .filter((message) => message.content.trim().length > 0);

  return normalizedMessages.length > 0 ? { messages: normalizedMessages } : null;
};
