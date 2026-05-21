// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import type { DataViewColumn } from '@nemo/common/src/components/DataView/FilterPanel/types';
import type { FilterItem } from '@nemo/common/src/components/DataView/internal';
import { Select } from '@nvidia/foundations-react-core';

interface SingleSelectFilterControlProps {
  column: DataViewColumn;
}

export function SingleSelectFilterControl({ column }: SingleSelectFilterControlProps) {
  const filter = column.columnDef.meta?.filter;
  if (filter?.type !== 'single-select') return null;

  const options: FilterItem[] | undefined = filter.options ?? filter.optionsBuilder?.(column);
  if (!options) return null;

  const value = column.getFilterValue() as string | undefined;

  return (
    <Select
      data-testid={`column-filter-${column.id}`}
      placeholder="Select..."
      value={value ?? ''}
      dismissible
      onValueChange={(v) => column.setFilterValue((typeof v === 'string' && v) || undefined)}
      items={options.map((opt) => ({
        value: opt.value,
        children: opt.label ?? opt.value,
        disabled: opt.disabled,
      }))}
    />
  );
}
