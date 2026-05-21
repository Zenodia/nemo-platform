// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { IntakeThreadsTable } from '@studio/components/IntakeThreadsTable';
import { FC } from 'react';

/**
 * Route component for the intake threads list.
 * Displays a table of conversation threads (grouped by thread_id).
 * Used as a child of IntakeLayout which provides the header and navigation.
 */
export const IntakeThreadsRoute: FC = () => {
  return (
    <IntakeThreadsTable
      enableSelection
      attributes={{
        Stack: {
          className: 'flex-1 min-h-0',
        },
      }}
    />
  );
};
