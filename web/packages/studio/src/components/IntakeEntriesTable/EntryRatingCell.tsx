// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { Entry } from '@nemo/sdk/generated/platform/schema';
import { Text } from '@nvidia/foundations-react-core';
import { getEventOrUserRating } from '@studio/components/IntakeEntriesTable/utils';
import { FC } from 'react';

export interface EntryRatingCellProps {
  entry: Entry;
}

/**
 * Displays the numeric rating for an entry.
 * Shows the rating value if present, otherwise shows em dash (—).
 */
export const EntryRatingCell: FC<EntryRatingCellProps> = ({ entry }) => {
  const rating = getEventOrUserRating(entry);

  if (rating === undefined || rating === null) {
    return <Text>—</Text>;
  }

  return <Text>{rating}</Text>;
};
