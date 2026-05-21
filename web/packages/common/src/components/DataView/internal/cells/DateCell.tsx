// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import type { TSFixMe } from '@nemo/common/src/components/DataView/internal/types';
import { isCellContext } from '@nemo/common/src/components/DataView/internal/utils/cell-utils';
import {
  formatSimplifiedDateTime,
  makeDateFormatter,
} from '@nemo/common/src/components/DataView/internal/utils/formatters';
import type { CellContext } from '@tanstack/react-table';

interface DateCellProps {
  format?: string;
}

/**
 * Plugin cell that renders a date. Can pass a format to customize the date format.
 *
 * @example
 * ```tsx
 * columnHelper.accessor('lastModified', { cell: DateCell, header: 'Last Modified' });
 * columnHelper.accessor('created', { cell: DateCell({ format: 'yyyy-MM-dd' }), header: 'Created' });
 * ```
 */
export function DateCell<TData, TValue>(
  cellOrContext: DateCellProps | CellContext<TData, TValue>
): TSFixMe {
  if (isCellContext<TData, TValue, DateCellProps>(cellOrContext)) {
    const value = cellOrContext.getValue() as string | undefined;
    return value && formatSimplifiedDateTime(value);
  }
  const format = cellOrContext.format;
  const formatter = format ? makeDateFormatter(format) : formatSimplifiedDateTime;
  return (context: CellContext<TData, TValue>) => {
    const value = context.getValue() as string | undefined;
    return value && formatter(value);
  };
}
