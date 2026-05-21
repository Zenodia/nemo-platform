// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import type { IntentionalAny } from '@nemo/common/src/components/DataView/internal/types';
import { childrenToText } from '@nvidia/foundations-react-core/lib';
import { flexRender, type Cell, type CellContext, type Row } from '@tanstack/react-table';
import type { ReactNode } from 'react';

/**
 * Renders the cell for the given row & columnId. Useful when reusing cell rendering logic
 * manually — for example, when rendering a cell in a Card format instead of a table.
 */
export function renderCell(row: Row<IntentionalAny>, columnId: string): ReactNode {
  const columns = row._getAllCellsByColumnId();
  const cell = columns[columnId];
  if (!cell) {
    console.error(
      `DataView - no cell with columnId ${columnId} can be found, available cells:`,
      columns
    );
    return null;
  }
  return flexRender(cell.column.columnDef.cell, cell.getContext());
}

/**
 * Convenience function to create a cell renderer function for use in the `cell` prop of a
 * column definition. Handles typing of the cell context.
 */
export function makeCell(
  cellRenderFunction: <TData, TValue>(cellContext: CellContext<TData, TValue>) => ReactNode
): <TData, TValue>(cellContext: CellContext<TData, TValue>) => ReactNode {
  return cellRenderFunction;
}

/** Resolves whether the given input is a CellContext. */
export function isCellContext<TData, TValue, TOther>(
  cellOrContext: TOther | CellContext<TData, TValue>
): cellOrContext is CellContext<TData, TValue> {
  return (cellOrContext as CellContext<TData, TValue>).getValue !== undefined;
}

/** Returns the title to be used for a cell. */
export function getCellTitle(cell: Cell<unknown, unknown>): string | undefined {
  const columnMeta = cell.column.columnDef.meta;
  const columnTooltip = columnMeta?.title ?? columnMeta?.tooltip;
  if (columnTooltip === false) return undefined;
  if (columnTooltip) return columnTooltip(cell);
  const value = cell.getValue();
  if (
    value === null ||
    value === undefined ||
    (typeof value === 'string' && value.trim() === '') ||
    (typeof value === 'number' && isNaN(value)) ||
    (typeof value === 'object' && Object.keys(value).length === 0)
  ) {
    return undefined;
  }
  return childrenToText(value as ReactNode);
}
