// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { Entry } from '@nemo/sdk/generated/platform/schema';
import { Flex, Panel, SegmentedControl, Stack, Text } from '@nvidia/foundations-react-core';
import { ChatView } from '@studio/components/IntakeEntryConversation/components/ChatView';
import { JSONView } from '@studio/components/IntakeEntryConversation/components/JSONView';
import { MessagesSquare } from 'lucide-react';
import { ComponentProps, FC, useState } from 'react';

/**
 * Available view modes for displaying intake entry data.
 * - `chat`: Renders the entry as an interactive chat conversation with styled bubbles
 * - `json`: Displays the raw entry data as formatted JSON in a code snippet
 */
type ViewMode = 'chat' | 'json';

/**
 * Props for the IntakeEntryConversation component.
 */
interface IntakeEntryConversationProps {
  /**
   * The intake entry containing conversation data to display.
   * Expected to contain messages with roles (system, user, assistant)
   * and optional reviewer annotations with ratings and rewrites.
   */
  entry: Entry;
  attributes?: {
    Panel?: ComponentProps<typeof Panel>;
  };
}

/**
 * Displays the conversation history from an intake entry with toggleable view modes.
 *
 * This component provides a panel interface for viewing intake entry data in two formats:
 *
 * **Chat View** ({@link ChatView}):
 * - System prompt in a collapsible accordion with size indicator
 * - User messages displayed as right-aligned bubbles
 * - Assistant responses as left-aligned bubbles with optional annotation overlays
 * - Thumb up/down rating indicators for reviewed responses
 *
 * **JSON View** ({@link JSONView}):
 * - Complete entry data as pretty-printed JSON
 * - Syntax highlighting and collapsible code snippet
 *
 * @example
 * ```tsx
 * import { IntakeEntryConversation } from '@studio/components/IntakeEntryConversation';
 *
 * <IntakeEntryConversation entry={selectedEntry} />
 * ```
 *
 * @param props - Component props
 * @param props.entry - The intake entry containing conversation messages and annotations
 * @returns A Panel with a segmented control to toggle between chat and JSON views
 *
 * @see {@link ChatView} for the chat bubble rendering implementation
 * @see {@link JSONView} for the JSON code snippet rendering
 */
export const IntakeEntryConversation: FC<IntakeEntryConversationProps> = ({
  entry,
  attributes,
}) => {
  const [viewMode, setViewMode] = useState<ViewMode>('chat');

  const handleViewModeChange = (value: string) => {
    // Type guard to ensure value is a valid ViewMode
    if (value === 'chat' || value === 'json') {
      setViewMode(value);
    }
  };

  return (
    <Panel
      elevation="high"
      slotIcon={<MessagesSquare />}
      slotHeading={
        <Flex align="center" justify="between" className="flex-1">
          <Text kind="label/bold/xl">Conversation</Text>
          <SegmentedControl
            size="tiny"
            value={viewMode}
            onValueChange={handleViewModeChange}
            items={[
              { value: 'chat', children: 'Chat' },
              { value: 'json', children: 'JSON' },
            ]}
          />
        </Flex>
      }
      {...attributes?.Panel}
    >
      <Stack gap="density-md" className="h-full">
        {viewMode === 'chat' ? <ChatView entry={entry} /> : <JSONView entry={entry} />}
      </Stack>
    </Panel>
  );
};
