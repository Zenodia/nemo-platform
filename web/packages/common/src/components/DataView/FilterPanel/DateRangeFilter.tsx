// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import type { DatetimeFilterValue } from '@nemo/common/src/components/DataView/dateTimeFilter';
import type { DataViewColumn } from '@nemo/common/src/components/DataView/FilterPanel/types';
import { parseUTCDateForPicker } from '@nemo/common/src/utils/formatDateRange';
import { DatePicker } from '@nvidia/foundations-react-core';

export function DateTimeFilterControl({ column }: { column: DataViewColumn }) {
  const value = column.getFilterValue() as DatetimeFilterValue | undefined;
  const fromDate = value?.$gte ? parseUTCDateForPicker(value.$gte) : undefined;
  const toDate = value?.$lte ? parseUTCDateForPicker(value.$lte) : undefined;

  const handleChange = (dateRange: { from?: Date; to?: Date } | undefined) => {
    if (!dateRange?.from && !dateRange?.to) {
      column.setFilterValue(undefined);
      return;
    }
    const $gte = dateRange?.from?.toISOString();
    const $lte = dateRange?.to
      ? new Date(new Date(dateRange.to).setUTCHours(23, 59, 59, 999)).toISOString()
      : undefined;
    column.setFilterValue({ $gte, $lte });
  };

  return (
    <DatePicker
      data-testid={`column-filter-${column.id}`}
      kind="range"
      placeholder="yyyy-mm-dd"
      format="yyyy-MM-dd"
      timeZone="utc"
      value={{ from: fromDate, to: toDate }}
      onValueChange={handleChange}
    />
  );
}
