// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import type { DataViewColumn } from '@nemo/common/src/components/DataView/FilterPanel/types';
import type { FilterValue } from '@nemo/common/src/components/DataView/internal';
import { useCallback } from 'react';

export function CustomFilterControl({ column }: { column: DataViewColumn }) {
  const filter = column.columnDef.meta?.filter;
  const value = column.getFilterValue() as FilterValue;
  const setValue = useCallback((v: FilterValue) => column.setFilterValue(v), [column]);

  if (filter?.type !== 'custom') return null;

  return <>{filter.renderFilter({ column, setValue, value })}</>;
}
