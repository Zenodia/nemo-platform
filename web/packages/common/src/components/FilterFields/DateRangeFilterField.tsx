/*
 * SPDX-FileCopyrightText: Copyright (c) 2022-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
 * SPDX-License-Identifier: Apache-2.0
 */

import { parseUTCDateForPicker } from '@nemo/common/src/utils/formatDateRange';
import { DatePicker } from '@nvidia/foundations-react-core';
import type { FC } from 'react';

/** Shape used by list APIs for date range (e.g. ModelEntitySearch created_at/updated_at). */
export interface DatetimeFilterValue {
  $gte?: string;
  $lte?: string;
}

export interface DateRangeFilterFieldProps {
  /** Current value (ISO date strings). */
  value?: DatetimeFilterValue;
  /** Called when the user changes the date range. */
  onValueChange: (value: DatetimeFilterValue | undefined) => void;
  /** Optional data-testid for the DatePicker. */
  dataTestId?: string;
}

export const DateRangeFilterField: FC<DateRangeFilterFieldProps> = ({
  value,
  onValueChange,
  dataTestId,
}) => {
  const fromDate = value?.$gte ? parseUTCDateForPicker(value.$gte) : undefined;
  const toDate = value?.$lte ? parseUTCDateForPicker(value.$lte) : undefined;

  const handleChange = (dateRange: { from?: Date; to?: Date } | undefined) => {
    if (!dateRange?.from && !dateRange?.to) {
      onValueChange(undefined);
      return;
    }
    const $gte = dateRange?.from?.toISOString();
    const $lte = dateRange?.to
      ? new Date(new Date(dateRange.to).setUTCHours(23, 59, 59, 999)).toISOString()
      : undefined;
    onValueChange({ $gte, $lte });
  };

  return (
    <DatePicker
      data-testid={dataTestId}
      kind="range"
      placeholder="yyyy-mm-dd"
      format="yyyy-MM-dd"
      timeZone="utc"
      value={{
        from: fromDate,
        to: toDate,
      }}
      onValueChange={handleChange}
    />
  );
};
