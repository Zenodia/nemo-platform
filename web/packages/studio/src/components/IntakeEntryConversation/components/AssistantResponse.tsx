// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { MessageContent } from '@nemo/common/src/components/Chat/MessageContent';
import { getContentFromMessage, toOpenAIMessage } from '@nemo/common/src/utils/chat';
import { FlexibleMessage, ReviewerAnnotationEvent } from '@nemo/sdk/generated/platform/schema';
import { Block, Stack, Text } from '@nvidia/foundations-react-core';
import { Annotation } from '@studio/components/IntakeEntryConversation/components/Annotation';
import { ThumbStatus } from '@studio/components/IntakeEntryConversation/components/ThumbStatus';
import { FC } from 'react';

interface AssistantResponseProps {
  /** The assistant's response message */
  message: FlexibleMessage;
  /** Optional reviewer annotation with feedback and potential rewrite */
  annotation?: ReviewerAnnotationEvent;
}

/**
 * Displays an assistant response message in a chat bubble format.
 *
 * Renders the assistant's message with an "Assistant" label and styled chat bubble.
 * When an annotation is present:
 * - The message bubble has a disabled background to indicate it was reviewed
 * - An {@link Annotation} is shown with any rewrite content
 * - A {@link ThumbStatus} indicator appears below showing the rating
 *
 * @param props - Component props
 * @param props.message - The assistant's response message to display
 * @param props.annotation - Optional reviewer annotation with feedback data
 * @returns A styled assistant message with optional annotation feedback
 */
export const AssistantResponse: FC<AssistantResponseProps> = ({ message, annotation }) => {
  const content = getContentFromMessage(toOpenAIMessage(message));
  return (
    <Stack gap="density-xl">
      <Text kind="body/regular/sm" className="text-start">
        Assistant
      </Text>
      <Block
        data-testid="chat-message"
        data-testspeaker="assistant"
        className="rounded-xl rounded-bl-none bg-surface-overlay overflow-hidden whitespace-pre-wrap w-auto self-start"
      >
        <Block
          data-testid="message-content-block"
          className={`p-density-xl ${annotation ? 'bg-interaction-disabled' : ''}`}
        >
          <MessageContent content={content} renderAsMarkdown />
        </Block>

        {annotation && <Annotation annotation={annotation} />}
      </Block>
      {annotation && <ThumbStatus annotation={annotation} />}
    </Stack>
  );
};
