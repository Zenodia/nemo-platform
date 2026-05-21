// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { MessageContent } from '@nemo/common/src/components/Chat/MessageContent';
import { getContentFromMessage } from '@nemo/common/src/utils/chat';
import { Block, Stack, Text } from '@nvidia/foundations-react-core';
import type { ChatCompletionUserMessageParam } from 'openai/resources/index.mjs';
import type { FC } from 'react';

interface UserMessageBubbleProps {
  message: ChatCompletionUserMessageParam;
}

export const UserMessageBubble: FC<UserMessageBubbleProps> = ({ message }) => {
  // message.content is properly typed as string | ContentPart[]
  const content = getContentFromMessage(message);

  return (
    <Stack gap="density-xl">
      <Text kind="body/regular/sm" className="text-end">
        User
      </Text>
      <Block
        data-testid="user-message-bubble"
        className="rounded-xl rounded-br-none bg-surface-sunken p-density-xl whitespace-pre-wrap w-auto self-end"
      >
        <MessageContent content={content} renderAsMarkdown />
      </Block>
    </Stack>
  );
};
