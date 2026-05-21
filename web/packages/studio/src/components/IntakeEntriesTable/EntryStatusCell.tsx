// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { Entry } from '@nemo/sdk/generated/platform/schema';
import { Flex, StatusIndicator, Text } from '@nvidia/foundations-react-core';
import { isEntryAnnotated } from '@studio/components/IntakeEntriesTable/utils';
import { FC } from 'react';

export interface EntryStatusCellProps {
  entry: Entry;
}

/**
 * Displays the annotation status of an entry with a colored indicator dot.
 * - Annotated: Green StatusIndicator
 * - Unannotated: Gray StatusIndicator (via className override)
 */
export const EntryStatusCell: FC<EntryStatusCellProps> = ({ entry }) => {
  const isAnnotated = isEntryAnnotated(entry);

  return (
    <Flex gap="density-sm" align="center">
      <StatusIndicator
        color="green"
        size="small"
        className={isAnnotated ? undefined : '!bg-accent-gray-subtle'}
      />
      <Text>{isAnnotated ? 'Annotated' : 'Unannotated'}</Text>
    </Flex>
  );
};
