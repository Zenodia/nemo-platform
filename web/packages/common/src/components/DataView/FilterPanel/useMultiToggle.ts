// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import type {
  DataViewColumn,
  MultiState,
} from '@nemo/common/src/components/DataView/FilterPanel/types';
import { useCallback } from 'react';

export function useMultiToggle(column: DataViewColumn) {
  const currentValue = column.getFilterValue() as MultiState | undefined;

  return useCallback(
    (key: string) => {
      const prev = (currentValue ?? {}) as MultiState;
      if (prev[key]) {
        const rest = { ...prev };
        delete rest[key];
        column.setFilterValue(Object.keys(rest).length > 0 ? rest : undefined);
      } else {
        column.setFilterValue({ ...prev, [key]: true });
      }
    },
    [column, currentValue]
  );
}
