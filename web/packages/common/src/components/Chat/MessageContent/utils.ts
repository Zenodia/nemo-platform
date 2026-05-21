// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

export interface MessageSnippet {
  type: 'plaintext' | 'code';
  value: string;
}

/**
 * Splits a message into segments based on code blocks (denoted by triple backticks) and returns
 * an array of MessageSnippet objects.
 */
export const splitMessageWithLabels = (message?: string | null): Array<MessageSnippet> => {
  if (!message) return [];
  const segments: MessageSnippet[] = [];
  let currentSegment = '';
  let isInCodeBlock = false;

  for (let i = 0; i < message.length; i++) {
    if (message.slice(i, i + 3) === '```') {
      if (isInCodeBlock) {
        segments.push({ type: 'code', value: currentSegment.trim() });
        currentSegment = '';
        isInCodeBlock = false;
        i += 2;
      } else {
        if (currentSegment.trim()) {
          segments.push({ type: 'plaintext', value: currentSegment.trim() });
        }
        currentSegment = '';
        isInCodeBlock = true;
        i += 2;
      }
    } else {
      currentSegment += message[i];
    }
  }

  if (currentSegment.trim()) {
    segments.push({
      type: isInCodeBlock ? 'code' : 'plaintext',
      value: currentSegment.trim(),
    });
  }

  return segments;
};
