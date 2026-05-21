// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { format as formatDate } from 'date-fns';

/**
 * Returns a function that formats a date string using the given date-fns format pattern.
 * @see https://date-fns.org/docs/format
 */
export function makeDateFormatter(format: string): (date: string) => string {
  return (date) => formatDate(new Date(date), format);
}

export const formatSimplifiedDateTime: (date: string) => string =
  makeDateFormatter('MM/dd/yyyy hh:mm a');

export function formatMultiCapitalize(str: string): string {
  return str
    .toLowerCase()
    .replace(/[-_]/g, ' ')
    .replace(/\b\w/g, (l) => l.toUpperCase());
}
