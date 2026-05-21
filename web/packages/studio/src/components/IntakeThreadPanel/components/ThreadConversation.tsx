// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { toOpenAIMessage } from '@nemo/common/src/utils/chat';
import { Entry, FlexibleMessage } from '@nemo/sdk/generated/platform/schema';
import { Stack } from '@nvidia/foundations-react-core';
import { AssistantMessageBubble } from '@studio/components/IntakeThreadPanel/components/AssistantMessageBubble';
import { SystemMessageBubble } from '@studio/components/IntakeThreadPanel/components/SystemMessageBubble';
import { ToolResponseBubble } from '@studio/components/IntakeThreadPanel/components/ToolResponseBubble';
import { UserMessageBubble } from '@studio/components/IntakeThreadPanel/components/UserMessageBubble';
import type { ChatCompletionSystemMessageParam } from 'openai/resources/index.mjs';
import { FC, useMemo } from 'react';

interface ThreadConversationProps {
  entries: Entry[];
  onViewEntry: (entryId: string) => void;
}

export const ThreadConversation: FC<ThreadConversationProps> = ({ entries, onViewEntry }) => {
  // Build content → Entry map for assistant message matching
  const responseContentToEntry = useMemo(() => {
    const map = new Map<string, Entry>();
    for (const entry of entries) {
      // Cast choices to access message.content (SDK types are loosely defined)
      const choices = entry.data?.response?.choices as
        | Array<{ message?: { content?: string } }>
        | undefined;
      const content = choices?.[0]?.message?.content;
      if (typeof content === 'string' && content.trim()) {
        map.set(content.trim(), entry);
      }
    }
    return map;
  }, [entries]);

  // Get the full conversation from the last entry
  const lastEntry = entries.at(-1);
  if (!lastEntry) return null;

  const allMessages: FlexibleMessage[] = [...(lastEntry.data?.request?.messages ?? [])];

  // Add the final response from the last entry
  const finalResponse = lastEntry.data?.response?.choices?.[0]?.message as
    | FlexibleMessage
    | undefined;
  if (finalResponse) {
    allMessages.push(finalResponse);
  }

  return (
    <Stack gap="density-lg">
      {allMessages.map((flexibleMessage, index) => {
        // Convert to OpenAI format - this enables type narrowing in the switch
        const message = toOpenAIMessage(flexibleMessage);
        const key = `${message.role}-${index}`;

        switch (message.role) {
          case 'user':
            // TypeScript knows: ChatCompletionUserMessageParam
            return <UserMessageBubble key={key} message={message} />;

          case 'assistant': {
            // TypeScript knows: ChatCompletionAssistantMessageParam
            const content = typeof message.content === 'string' ? message.content.trim() : '';
            const matchingEntry =
              responseContentToEntry.get(content) ??
              (flexibleMessage === finalResponse ? lastEntry : undefined);

            return (
              <AssistantMessageBubble
                key={key}
                message={message}
                entry={matchingEntry}
                onViewEntry={onViewEntry}
              />
            );
          }

          case 'system':
            // TypeScript knows: ChatCompletionSystemMessageParam
            return <SystemMessageBubble key={key} message={message} />;

          case 'developer':
            // developer role maps to system-like display
            // Cast needed since OpenAI types don't include 'developer' in discriminant
            return (
              <SystemMessageBubble
                key={key}
                message={message as unknown as ChatCompletionSystemMessageParam}
                label="Developer Instructions"
              />
            );

          case 'tool':
            // TypeScript knows: ChatCompletionToolMessageParam
            return <ToolResponseBubble key={key} message={message} />;

          default:
            return null;
        }
      })}
    </Stack>
  );
};
