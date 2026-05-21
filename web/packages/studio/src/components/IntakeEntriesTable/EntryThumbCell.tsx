// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import type { Entry } from '@nemo/sdk/generated/platform/schema';
import { Tag, Text } from '@nvidia/foundations-react-core';
import { getEventOrUserThumb } from '@studio/components/IntakeEntriesTable/utils';
import { ThumbsDown, ThumbsUp } from 'lucide-react';
import { FC } from 'react';

export interface EntryThumbCellProps {
  entry: Entry;
}

/**
 * Displays the thumb feedback for an entry.
 * - Up: Green thumbs up icon
 * - Down: Red thumbs down icon
 * - Not set: Em dash (—)
 */
export const EntryThumbCell: FC<EntryThumbCellProps> = ({ entry }) => {
  const thumb = getEventOrUserThumb(entry);

  if (!thumb) {
    return <Text>—</Text>;
  }

  if (thumb === 'up') {
    return (
      <Tag color="green">
        <ThumbsUp size="20" color="var(--text-color-feedback-success)" />
      </Tag>
    );
  }

  return (
    <Tag color="red">
      <ThumbsDown size="20" color="var(--text-color-feedback-danger)" />
    </Tag>
  );
};
