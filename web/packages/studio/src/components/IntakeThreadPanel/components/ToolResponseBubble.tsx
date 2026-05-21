// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { getContentFromMessage } from '@nemo/common/src/utils/chat';
import { Block, Flex, Stack, Text } from '@nvidia/foundations-react-core';
import { Wrench } from 'lucide-react';
import type { ChatCompletionToolMessageParam } from 'openai/resources/index.mjs';
import { FC } from 'react';

interface ToolResponseBubbleProps {
  message: ChatCompletionToolMessageParam;
}

export const ToolResponseBubble: FC<ToolResponseBubbleProps> = ({ message }) => {
  // Use getContentFromMessage to handle string | ContentPart[] types
  const content = getContentFromMessage(message);
  const toolCallId = message.tool_call_id;

  const label = toolCallId || 'Tool Response';

  return (
    <Stack gap="density-xs" className="ml-density-xl">
      <Flex align="center" gap="density-xs">
        <Wrench width={14} height={14} className="text-secondary" />
        <Text kind="label/regular/xs" color="secondary">
          {label}
        </Text>
      </Flex>
      <Block
        data-testid="tool-response-bubble"
        className="rounded-lg bg-surface-sunken p-density-md font-mono text-sm overflow-x-auto"
      >
        <pre className="whitespace-pre-wrap">{content}</pre>
      </Block>
    </Stack>
  );
};
