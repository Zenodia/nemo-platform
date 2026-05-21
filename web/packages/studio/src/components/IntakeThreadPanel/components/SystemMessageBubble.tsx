// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { MessageContent } from '@nemo/common/src/components/Chat/MessageContent';
import { getContentFromMessage } from '@nemo/common/src/utils/chat';
import { Accordion, Block, Text } from '@nvidia/foundations-react-core';
import type { ChatCompletionSystemMessageParam } from 'openai/resources/index.mjs';
import type { FC } from 'react';

interface SystemMessageBubbleProps {
  message: ChatCompletionSystemMessageParam;
  label?: string;
  defaultExpanded?: boolean;
}

export const SystemMessageBubble: FC<SystemMessageBubbleProps> = ({
  message,
  label = 'System Prompt',
  defaultExpanded = false,
}) => {
  // message.content is properly typed as string
  const content = getContentFromMessage(message);
  const charCount = content.length;

  return (
    <Accordion
      defaultValue={defaultExpanded ? 'system' : undefined}
      items={[
        {
          value: 'system',
          slotTrigger: (
            <Text kind="body/regular/sm" color="secondary">
              {label} ({charCount.toLocaleString()} chars)
            </Text>
          ),
          slotContent: (
            <Block className="p-density-md bg-surface-sunken rounded-md">
              <MessageContent content={content} renderAsMarkdown />
            </Block>
          ),
        },
      ]}
    />
  );
};
