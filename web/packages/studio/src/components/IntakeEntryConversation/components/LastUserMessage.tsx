// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { MessageContent } from '@nemo/common/src/components/Chat/MessageContent';
import { getContentFromMessage, toOpenAIMessage } from '@nemo/common/src/utils/chat';
import { FlexibleMessage } from '@nemo/sdk/generated/platform/schema';
import { Block, Stack, Text } from '@nvidia/foundations-react-core';
import { FC } from 'react';

interface LastUserMessageProps {
  /** The user's message to display */
  message: FlexibleMessage;
}

/**
 * Displays the user's message in a chat bubble format.
 *
 * Renders the message with a "User" label aligned to the right and a styled
 * chat bubble with rounded corners (except bottom-right). The bubble is
 * positioned on the right side to distinguish it from assistant messages.
 *
 * @param props - Component props
 * @param props.message - The user's message to display
 * @returns A right-aligned styled user message bubble
 */
export const LastUserMessage: FC<LastUserMessageProps> = ({ message }) => {
  const content = getContentFromMessage(toOpenAIMessage(message));
  return (
    <Stack gap="density-xl">
      <Text kind="body/regular/sm" className="text-end">
        User
      </Text>
      <Block
        data-testid="chat-message"
        data-testspeaker="user"
        className="rounded-xl rounded-br-none bg-surface-sunken p-density-xl whitespace-pre-wrap w-auto self-end"
      >
        <MessageContent content={content} renderAsMarkdown />
      </Block>
    </Stack>
  );
};
