// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { MessageContent } from '@nemo/common/src/components/Chat/MessageContent';
import { FlexibleMessage } from '@nemo/sdk/generated/platform/schema';
import { Accordion, Flex } from '@nvidia/foundations-react-core';
import { getHumanReadableFileSize, getTextSizeInBytes } from '@studio/util/files';
import { MessageSquare } from 'lucide-react';
import { FC } from 'react';

interface SystemPromptProps {
  /** Array of system-role messages to display */
  systemMessages: FlexibleMessage[];
}

/**
 * Displays system prompt content in a collapsible accordion.
 *
 * Combines all system messages into a single block of content and renders it
 * within an expandable accordion. The accordion header shows:
 * - A chat message icon
 * - "System Prompt" label
 * - The combined content size (e.g., "225.89kB")
 *
 * Returns null if there's no meaningful content to display.
 *
 * @param props - Component props
 * @param props.systemMessages - Array of system-role messages to combine and display
 * @returns A collapsible accordion with system prompt content, or null if empty
 */
export const SystemPrompt: FC<SystemPromptProps> = ({ systemMessages }) => {
  const systemContent = systemMessages
    .map((m) => (typeof m.content === 'string' ? m.content : ''))
    .filter(Boolean)
    .join('\n\n');

  // Don't render if no meaningful content
  if (!systemContent || systemContent.trim() === '') {
    return null;
  }

  const systemPromptSize = getHumanReadableFileSize(getTextSizeInBytes(systemContent));

  return (
    <Accordion
      multiple
      items={[
        {
          value: 'system-prompt',
          attributes: {
            AccordionTrigger: { className: 'rounded-lg' },
            AccordionItem: { className: 'border-b-0 bg-surface-sunken rounded-lg' },
          },
          slotTrigger: (
            <Flex align="center" gap="density-xs" className="whitespace-nowrap">
              <MessageSquare />
              <span>System Prompt</span>
              <span className="text-content-secondary">({systemPromptSize})</span>
            </Flex>
          ),
          slotContent: <MessageContent content={systemContent} renderAsMarkdown />,
        },
      ]}
    />
  );
};
