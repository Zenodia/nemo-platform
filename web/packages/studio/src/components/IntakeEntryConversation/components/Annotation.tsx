// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { MessageContent } from '@nemo/common/src/components/Chat/MessageContent';
import { ReviewerAnnotationEvent } from '@nemo/sdk/generated/platform/schema';
import { Block, Divider, Stack, Text } from '@nvidia/foundations-react-core';
import { getRewriteFromAnnotation } from '@studio/util/entries';
import { FC } from 'react';

interface AnnotationProps {
  /** The annotation containing potential rewrite content */
  annotation: ReviewerAnnotationEvent;
}

/**
 * Displays annotation feedback as a footer section below an assistant message.
 *
 * When a reviewer provides a rewrite for the assistant's response, this component
 * renders it with a "Rewrite" label and markdown formatting. The footer is
 * separated from the original message by a divider.
 *
 * @param props - Component props
 * @param props.annotation - The reviewer annotation containing potential rewrite content
 * @returns A footer section with rewrite content, or null if no rewrite exists
 */
export const Annotation: FC<AnnotationProps> = ({ annotation }) => {
  const rewriteContent = getRewriteFromAnnotation(annotation);

  if (!rewriteContent) {
    return null;
  }

  return (
    <Stack>
      <Divider />
      <Stack gap="density-xs" className="p-density-xl">
        <Text kind="body/regular/sm" color="secondary">
          Rewrite
        </Text>
        <Block className="self-start" data-testid="rewrite-content">
          <MessageContent content={rewriteContent} renderAsMarkdown />
        </Block>
      </Stack>
    </Stack>
  );
};
