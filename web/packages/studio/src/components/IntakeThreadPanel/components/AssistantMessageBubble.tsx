// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { MessageContent } from '@nemo/common/src/components/Chat/MessageContent';
import { getContentFromMessage } from '@nemo/common/src/utils/chat';
import type { Entry } from '@nemo/sdk/generated/platform/schema';
import {
  StatusIndicator,
  Block,
  Button,
  Divider,
  Flex,
  Stack,
  Text,
} from '@nvidia/foundations-react-core';
import {
  getAnnotationFromEntry,
  getRewriteFromAnnotation,
  isEntryAnnotated,
} from '@studio/util/entries';
import { ThumbsDown, ThumbsUp } from 'lucide-react';
import type { ChatCompletionAssistantMessageParam } from 'openai/resources/index.mjs';
import { FC } from 'react';

interface AssistantMessageBubbleProps {
  message: ChatCompletionAssistantMessageParam;
  entry?: Entry;
  onViewEntry?: (entryId: string) => void;
}

export const AssistantMessageBubble: FC<AssistantMessageBubbleProps> = ({
  message,
  entry,
  onViewEntry,
}) => {
  // message.content and message.tool_calls are properly typed
  const content = getContentFromMessage(message);
  const toolCalls = message.tool_calls;

  // Entry-linked data (only if entry provided)
  const annotation = entry ? getAnnotationFromEntry(entry) : undefined;
  const annotated = entry ? isEntryAnnotated(entry) : false;
  const thumb = annotation?.thumb ?? entry?.user_rating?.thumb;
  const rewrite = getRewriteFromAnnotation(annotation);

  return (
    <Stack gap="density-md">
      <Text kind="body/regular/sm" className="text-start">
        Assistant
      </Text>
      <Block
        data-testid="assistant-message-bubble"
        className="rounded-xl rounded-bl-none bg-surface-overlay overflow-hidden whitespace-pre-wrap w-auto self-start"
      >
        <Block className={`p-density-xl ${annotation ? 'bg-interaction-disabled' : ''}`}>
          {toolCalls && !content ? (
            <ToolCallsDisplay toolCalls={toolCalls} />
          ) : (
            <MessageContent content={content} renderAsMarkdown />
          )}
        </Block>

        {/* Rewrite section (only if entry has annotation with rewrite) */}
        {rewrite && (
          <Stack>
            <Divider />
            <Stack gap="density-xs" className="p-density-xl">
              <Text kind="body/regular/sm" color="secondary">
                Rewrite
              </Text>
              <MessageContent content={rewrite} renderAsMarkdown />
            </Stack>
          </Stack>
        )}
      </Block>

      {/* Status row (only if linked to an entry) */}
      {entry && (
        <Flex
          align="center"
          padding="density-xs"
          className="w-fit rounded-md border border-base bg-surface-raised"
        >
          <Flex align="center" gap="density-lg" className="px-2">
            <AnnotationBadge annotated={annotated} />
            <span className={thumb === 'up' ? 'text-accent-green' : ''}>
              <ThumbsUp width={16} height={16} />
            </span>
            <span className={thumb === 'down' ? 'text-accent-red' : ''}>
              <ThumbsDown width={16} height={16} />
            </span>
          </Flex>

          {/* Vertical separator */}
          {onViewEntry && <div className="h-full w-px border-r border-base self-stretch" />}

          {/* View Entry button */}
          {onViewEntry && (
            <Button
              className="px-2"
              kind="tertiary"
              size="tiny"
              onClick={() => onViewEntry(entry.id!)}
            >
              View Entry
            </Button>
          )}
        </Flex>
      )}
    </Stack>
  );
};

// Sub-components (can be extracted if needed)
const AnnotationBadge: FC<{ annotated: boolean }> = ({ annotated }) => (
  <Flex align="center" gap="density-md">
    <StatusIndicator
      size="medium"
      color="green"
      className={annotated ? undefined : '!bg-accent-gray-subtle'}
    />
    <Text kind="body/regular/sm">{annotated ? 'Annotated' : 'Unannotated'}</Text>
  </Flex>
);

const ToolCallsDisplay: FC<{ toolCalls: unknown[] }> = ({ toolCalls }) => (
  <Text kind="body/regular/sm" color="secondary">
    Called {toolCalls.length} tool{toolCalls.length > 1 ? 's' : ''}
  </Text>
);
