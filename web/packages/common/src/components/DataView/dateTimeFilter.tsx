/*
 * SPDX-FileCopyrightText: Copyright (c) 2022-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
 * SPDX-License-Identifier: Apache-2.0
 */
import React from 'react';

export type { DatetimeFilterValue } from '@nemo/common/src/components/FilterFields/DateRangeFilterField';

interface DateTimeColumnFilter {
  label: string;
  type: 'custom';
  filterVariant: 'datetime';
  renderFilter: () => React.JSX.Element;
}

/** Creates a datetime range filter definition for use in column `meta.filter`. */
export function dateTimeFilter(label: string): DateTimeColumnFilter {
  return { label, type: 'custom', filterVariant: 'datetime', renderFilter: () => <></> };
}

/** Type guard: checks whether a filter def is a datetime range filter. */
export function isDateTimeFilter(
  filter: { type: string } | undefined | null
): filter is DateTimeColumnFilter {
  return (
    filter != null &&
    filter.type === 'custom' &&
    'filterVariant' in filter &&
    (filter as DateTimeColumnFilter).filterVariant === 'datetime'
  );
}
