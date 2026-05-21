// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { useInnerDataViewContext } from '@nemo/common/src/components/DataView/internal/context';
import type { IntentionalAny } from '@nemo/common/src/components/DataView/internal/types';
import { getHeaderId } from '@nemo/common/src/components/DataView/internal/utils/header-utils';
import type { Column, ColumnSizingState, Header } from '@tanstack/react-table';
import type { CSSProperties, MouseEvent, TouchEvent } from 'react';

export function getColumnWidth(id: string): string {
  const variable = `--col-${id}-size`;
  return `calc(var(${variable}) * 1px)`;
}

export function isColumnAutoSized(
  column: Column<IntentionalAny>,
  columnSizing: ColumnSizingState
): boolean {
  return !columnSizing[column.id] && !column.columnDef.meta?._isSizeInitialized;
}

export function getCellStyle({
  column,
  disableAutoSizing,
}: {
  column: Column<IntentionalAny>;
  disableAutoSizing: boolean;
}): CSSProperties {
  const width = disableAutoSizing ? column.getSize() : getColumnWidth(column.id);
  const cellStyle: CSSProperties = {
    minWidth: width,
    width,
    maxWidth: width,
  };
  if (column.getIsPinned() === 'left') {
    cellStyle.left = column.getStart('left');
  } else if (column.getIsPinned() === 'right') {
    cellStyle.right = column.getAfter('right');
  }
  return cellStyle;
}

export function getColumnWidths({
  columnSizing,
  columns,
  disableAutoSizing,
}: {
  columnSizing: ColumnSizingState;
  columns: Column<IntentionalAny>[];
  disableAutoSizing: boolean;
}): Record<string, string | number> {
  const colSizes: Record<string, string | number> = {};
  columns.forEach((column) => {
    const shouldUseTableSize = disableAutoSizing || !isColumnAutoSized(column, columnSizing);
    colSizes[`--col-${column.id}-size`] = shouldUseTableSize ? column.getSize() : 'auto';
  });
  return colSizes;
}

export function useHandleResize(header: Header<IntentionalAny, unknown>) {
  const { table } = useInnerDataViewContext();
  return {
    handleResize: (event: MouseEvent | TouchEvent) => {
      const isAutoSizedColumn = isColumnAutoSized(header.column, table.getState().columnSizing);
      if (isAutoSizedColumn) {
        const element = document.getElementById(getHeaderId(header.id));
        const elementWidth = element?.getBoundingClientRect().width;
        if (elementWidth) {
          table.setColumnSizing((columnSizingInfo) => {
            columnSizingInfo[header.id] = elementWidth;
            return columnSizingInfo;
          });
        }
      }
      const handler = header.getResizeHandler();
      handler(event);
    },
    handleDoubleClick: () => {
      header.column.resetSize();
    },
  };
}
