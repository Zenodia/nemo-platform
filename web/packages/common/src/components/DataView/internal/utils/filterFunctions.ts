// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import type { MultiState } from '@nemo/common/src/components/DataView/internal/types';
import { rankItem } from '@tanstack/match-sorter-utils';
import type { FilterMeta, Row } from '@tanstack/react-table';

/**
 * Supplemental filter functions for the DataView component. These are custom filter functions
 * that can be used in the `filterFn` or `globalFilterFn` props.
 */
export const filterFunctions = {
  /**
   * Fuzzy filter — approximately matches the text entered to the data in the column.
   * @see https://tanstack.com/table/latest/docs/guide/fuzzy-filtering#defining-a-custom-fuzzy-filter-function
   */
  // eslint-disable-next-line @typescript-eslint/no-explicit-any -- generic across data types
  fuzzy: (row: Row<any>, columnId: string, value: any, addMeta: (meta: FilterMeta) => void) => {
    const itemRank = rankItem(row.getValue(columnId), value);
    addMeta({ itemRank });
    return itemRank.passed;
  },
  /** @deprecated Use `includesString` instead. */
  // eslint-disable-next-line @typescript-eslint/no-explicit-any -- generic across data types
  singleSelect: (row: Row<any>, columnId: string, value: string | undefined) => {
    const rowValue = `${row.getValue(columnId)}`.toLowerCase();
    return rowValue === value?.toLowerCase();
  },
  /** Case insensitive multi-select filter. */
  // eslint-disable-next-line @typescript-eslint/no-explicit-any -- generic across data types
  multiSelect: (row: Row<any>, columnId: string, value: MultiState | undefined) => {
    const rowValue = `${row.getValue(columnId)}`;
    return Object.keys(value ?? {}).some((v) => v.toLowerCase() === rowValue.toLowerCase());
  },
  /** Case sensitive multi-select filter. */
  // eslint-disable-next-line @typescript-eslint/no-explicit-any -- generic across data types
  multiSelectSensitive: (row: Row<any>, columnId: string, value: MultiState | undefined) => {
    const rowValue = `${row.getValue(columnId)}`;
    return Object.keys(value ?? {}).some((v) => v === rowValue);
  },
};
