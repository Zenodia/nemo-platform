// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import type { CellContext, NoInfer } from '@tanstack/react-table';

/**
 * The default cell rendered for columns. Renders the value or a dash if the value is undefined.
 */
export function DefaultCell<TData, TValue>(
  cellContext: CellContext<TData, TValue>
): (NoInfer<TValue> & {}) | '-' {
  const value = cellContext.getValue();
  if (value === null || value === undefined || (value as unknown) === '') {
    return '-';
  }
  return value as NoInfer<TValue> & {};
}
