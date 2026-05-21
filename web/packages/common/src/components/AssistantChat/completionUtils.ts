// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import type { ChatCompletion, ChatCompletionChunk } from 'openai/resources/index.mjs';
import type { Stream } from 'openai/streaming.mjs';

export const isChatCompletionStream = (
  value: ChatCompletion | Stream<ChatCompletionChunk> | null | undefined
): value is Stream<ChatCompletionChunk> =>
  value != null && typeof value === 'object' && Symbol.asyncIterator in value;

export const isAbortError = (error: unknown): boolean => {
  if (!(error instanceof Error)) return false;
  return error.name === 'AbortError' || error.name === 'APIUserAbortError';
};

export const getCompletionText = (completion: ChatCompletion): string => {
  const content = completion.choices[0]?.message.content;
  return typeof content === 'string' ? content : '';
};
