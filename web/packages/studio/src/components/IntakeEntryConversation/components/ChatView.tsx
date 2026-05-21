// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import type { Entry } from '@nemo/sdk/generated/platform/schema';
import { Banner, Stack } from '@nvidia/foundations-react-core';
import { AssistantResponse } from '@studio/components/IntakeEntryConversation/components/AssistantResponse';
import { LastUserMessage } from '@studio/components/IntakeEntryConversation/components/LastUserMessage';
import { SystemPrompt } from '@studio/components/IntakeEntryConversation/components/SystemPrompt';
import {
  getAnnotationFromEntry,
  getLastInputOutputPair,
  getSystemContextFromEntry,
} from '@studio/util/entries';
import { FC } from 'react';

interface ChatViewProps {
  /** The intake entry to display as a conversation */
  entry: Entry;
}

/**
 * Renders an intake entry as a conversational chat interface.
 *
 * Parses the entry to extract and display:
 * - **System prompt**: Shown in a collapsible accordion via {@link SystemPrompt}
 * - **User message**: The last user input, right-aligned via {@link LastUserMessage}
 * - **Assistant response**: The last assistant output with annotations via {@link AssistantResponse}
 *
 * If no messages are found, displays a warning banner.
 *
 * @param props - Component props
 * @param props.entry - The intake entry containing conversation data
 * @returns A chat-style view of the conversation, or a warning if no messages exist
 */
export const ChatView: FC<ChatViewProps> = ({ entry }) => {
  const systemContext = getSystemContextFromEntry(entry);
  const lastInputOutput = getLastInputOutputPair(entry);
  const annotation = getAnnotationFromEntry(entry);

  const userMessage = lastInputOutput.find((m) => m.role === 'user');
  const assistantMessage = lastInputOutput.find((m) => m.role === 'assistant');

  if (!userMessage && !assistantMessage) {
    return (
      <Banner kind="header" slotSubheading="No messages found in this entry" status="warning">
        Chat History Unavailable
      </Banner>
    );
  }

  return (
    <Stack gap="density-xl">
      <SystemPrompt systemMessages={systemContext} />
      {userMessage && <LastUserMessage message={userMessage} />}
      {assistantMessage && <AssistantResponse message={assistantMessage} annotation={annotation} />}
    </Stack>
  );
};
