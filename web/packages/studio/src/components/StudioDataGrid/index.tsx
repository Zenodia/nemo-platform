// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { DataGrid, DataGridProps, GridRowClassNameParams } from '@mui/x-data-grid';
import { Pagination } from '@nvidia/foundations-react-core';
import { StudioDataGridPagination } from '@studio/components/StudioDataGrid/StudioDataGridPagination';
import { ComponentProps, FC } from 'react';

interface Props extends Omit<
  DataGridProps,
  'onPaginationModelChange' | 'pageSizeOptions' | 'pageSize'
> {
  disableClickStyles?: boolean;
  paginationProps?: ComponentProps<typeof Pagination>;
  alternateRowColor?: boolean;
}

/**
 * This component wraps MUI DataGrid and provides Studio specific implementation choices for a cohesive UX.
 * Notably, pagination has been offloaded to the KUI Pagination component. Therefore, related Datagrid pagination props are not supported.
 */
export const StudioDataGrid: FC<Props> = ({
  disableClickStyles,
  paginationProps,
  alternateRowColor,
  slots,
  slotProps,
  sx,
  getRowClassName: userGetRowClassName,
  ...dataGridProps
}) => {
  const cellPadding = `0 ${'var(--spacing-sm)'}`;
  const sxWithDefaults = {
    border: 'none',
    overflow: 'auto',
    '--DataGrid-containerBackground': 'var(--background-color-surface-base)',
    '.MuiDataGrid-cell, .MuiDataGrid-columnHeader': {
      backgroundColor: 'inherit',
      padding: cellPadding,
      fontSize: '0.875rem', // 14px base size
    },
    ...(alternateRowColor
      ? {
          '& .MuiDataGrid-row.odd': {
            backgroundColor: 'rgba(0, 0, 0, 0.04)',
            '&:hover': {
              backgroundColor: 'rgba(0, 0, 0, 0.08)',
            },
          },
        }
      : {}),
    ...(disableClickStyles
      ? {}
      : {
          // disable cell selection style
          '.MuiDataGrid-cell:focus': {
            outline: 'none',
          },
          // pointer cursor on ALL rows
          '& .MuiDataGrid-row:hover': {
            cursor: 'pointer',
          },
        }),
    ...sx,
  };

  const slotsWithDefaults = {
    footer: () => (paginationProps ? <StudioDataGridPagination {...paginationProps} /> : null),
    ...slots,
  };

  const slotPropsWithDefaults: ComponentProps<typeof DataGrid>['slotProps'] = {
    loadingOverlay: {
      variant: 'skeleton',
      noRowsVariant: 'skeleton',
    },
    ...slotProps,
  };

  const getRowClassName = (params: GridRowClassNameParams) => {
    const userClassName = userGetRowClassName?.(params) || '';
    const alternateClassName = alternateRowColor
      ? params.indexRelativeToCurrentPage % 2 === 0
        ? 'even'
        : 'odd'
      : '';

    return [userClassName, alternateClassName].filter(Boolean).join(' ');
  };

  return (
    <DataGrid
      slots={slotsWithDefaults}
      slotProps={slotPropsWithDefaults}
      sx={sxWithDefaults}
      getRowClassName={getRowClassName}
      {...dataGridProps}
      scrollbarSize={10}
      paginationMode={!dataGridProps.rowCount ? 'client' : dataGridProps.paginationMode} // Fixes error when rowCount is not provided for server pagination mode
    />
  );
};
