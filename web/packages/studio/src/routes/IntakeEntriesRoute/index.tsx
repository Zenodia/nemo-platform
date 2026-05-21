// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { IntakeEntriesTable } from '@studio/components/IntakeEntriesTable';
import { FC } from 'react';

/**
 * Route component for the intake entries list.
 * Displays a table of individual completion entries.
 * Used as a child of IntakeLayout which provides the header and navigation.
 */
export const IntakeEntriesRoute: FC = () => {
  return (
    <IntakeEntriesTable
      enableSelection
      enableActions
      attributes={{
        Stack: {
          className: 'flex-1 min-h-0',
        },
      }}
    />
  );
};
