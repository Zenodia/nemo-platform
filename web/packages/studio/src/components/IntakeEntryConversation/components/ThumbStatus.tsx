// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { ReviewerAnnotationEvent } from '@nemo/sdk/generated/platform/schema';
import { Block, Flex } from '@nvidia/foundations-react-core';
import { ThumbsDown, ThumbsUp } from 'lucide-react';
import { FC } from 'react';

interface ThumbStatusProps {
  /** The annotation containing thumb rating data */
  annotation: ReviewerAnnotationEvent;
}

/**
 * Displays thumb up/down indicators based on the annotation's rating.
 *
 * Shows two thumb icons side by side - the active one (up or down) is highlighted
 * with an accent color (green for up, red for down).
 *
 * @param props - Component props
 * @param props.annotation - The reviewer annotation containing the thumb rating
 * @returns A pill-shaped indicator with thumb up/down icons
 */
export const ThumbStatus: FC<ThumbStatusProps> = ({ annotation }) => {
  const { thumb } = annotation;

  // Generate accessible label based on current rating
  const getAriaLabel = () => {
    if (thumb === 'up') return 'Reviewer rating: thumbs up';
    if (thumb === 'down') return 'Reviewer rating: thumbs down';
    return 'Reviewer rating: no rating provided';
  };

  return (
    <Flex
      direction="row"
      gap="density-xs"
      paddingX="density-md"
      paddingY="density-xs"
      className="w-fit rounded-md border border-base"
      aria-label={getAriaLabel()}
      role="status"
    >
      <Block
        padding="density-xs"
        className={thumb === 'up' ? 'text-accent-green' : ''}
        data-testid="thumb-up-icon"
        aria-hidden={thumb !== 'up'}
      >
        <ThumbsUp width={16} height={16} />
      </Block>
      <Block
        padding="density-xs"
        className={thumb === 'down' ? 'text-accent-red' : ''}
        data-testid="thumb-down-icon"
        aria-hidden={thumb !== 'down'}
      >
        <ThumbsDown width={16} height={16} />
      </Block>
    </Flex>
  );
};
