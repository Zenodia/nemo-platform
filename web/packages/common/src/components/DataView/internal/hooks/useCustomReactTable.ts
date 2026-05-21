// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { DefaultCell } from '@nemo/common/src/components/DataView/internal/cells/DefaultCell';
import type { DataMode, IntentionalAny } from '@nemo/common/src/components/DataView/internal/types';
import type { DataViewState } from '@nemo/common/src/components/DataView/internal/useDataViewState';
import { filterFunctions } from '@nemo/common/src/components/DataView/internal/utils/filterFunctions';
import {
  getCoreRowModel,
  getExpandedRowModel,
  getFacetedRowModel,
  getFacetedUniqueValues,
  getFilteredRowModel,
  getPaginationRowModel,
  getSortedRowModel,
  useReactTable,
  type ColumnDef,
  type Row,
  type Table,
  type TableOptions,
} from '@tanstack/react-table';
import { useCallback, type JSX } from 'react';

interface RowWithMaybeId {
  id?: string;
  uuid?: string;
  subRows?: unknown[];
}

const _getRowCanExpand = (row: Row<IntentionalAny>): boolean =>
  row.subRows ? row.subRows.length > 0 : false;
const _getRowCanExpandAlways = (): boolean => true;
const _getRowId = (data: RowWithMaybeId, index: number): string =>
  (data && (data.id ?? data.uuid)) ?? String(index);
const _getSubRows = (data: RowWithMaybeId | undefined): unknown[] | undefined => data?.subRows;

const defaultColumn: Partial<ColumnDef<IntentionalAny>> = {
  cell: DefaultCell,
  enableColumnFilter: false,
  enableSorting: false,
  enablePinning: true,
  minSize: 50,
  maxSize: 600,
};

export function useCustomReactTable<TData>({
  columns,
  data,
  dataMode,
  reactTableOptions,
  renderCustomRowExpansion,
  state,
  totalCount,
}: {
  columns: ColumnDef<TData, IntentionalAny>[];
  data: TData[];
  dataMode: DataMode;
  reactTableOptions?: Partial<TableOptions<TData>>;
  renderCustomRowExpansion?: (data: { row: Row<TData> }) => JSX.Element;
  state: DataViewState;
  totalCount: number | undefined;
}): Table<TData> {
  const onControlledColumnFiltersChange = useCallback(
    (updaterOrValue: Parameters<DataViewState['columnFiltering']['set']>[0]) => {
      state.pagination.goToFirstPage();
      state.columnFiltering.set(updaterOrValue);
    },
    [state.columnFiltering, state.pagination]
  );

  return useReactTable({
    columns,
    columnResizeMode: 'onChange',
    data,
    defaultColumn,
    getCoreRowModel: getCoreRowModel(),
    getExpandedRowModel: getExpandedRowModel(),
    getRowId: _getRowId as TableOptions<TData>['getRowId'],
    getSubRows: _getSubRows as TableOptions<TData>['getSubRows'],
    getRowCanExpand: renderCustomRowExpansion ? _getRowCanExpandAlways : _getRowCanExpand,
    filterFns: filterFunctions,
    getFilteredRowModel: getFilteredRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    getFacetedRowModel: getFacetedRowModel(),
    getFacetedUniqueValues: getFacetedUniqueValues(),
    globalFilterFn: filterFunctions.fuzzy,
    manualFiltering: dataMode === 'manual',
    manualSorting: dataMode === 'manual',
    manualPagination: dataMode === 'manual' || dataMode === 'sort-filter-only',
    onColumnFiltersChange:
      dataMode === 'manual' ? onControlledColumnFiltersChange : state.columnFiltering.set,
    onColumnPinningChange: state.columnPinning.set,
    onColumnOrderChange: state.columnOrder.set,
    onColumnVisibilityChange: state.columnVisibility.set,
    onGlobalFilterChange: state.searchBar.set,
    onExpandedChange: state.expansion.set,
    onRowSelectionChange: state.rowSelection.set,
    onSortingChange: state.sorting.set,
    onPaginationChange: state.pagination.set as TableOptions<TData>['onPaginationChange'],
    rowCount: totalCount,
    state: {
      columnFilters: state.columnFiltering.state,
      columnPinning: state.columnPinning.state,
      columnOrder: state.columnOrder.state,
      columnVisibility: state.columnVisibility.state,
      globalFilter: state.searchBar.state,
      expanded: state.expansion.state,
      rowSelection: state.rowSelection.state,
      sorting: state.sorting.state,
      pagination: state.pagination.state,
    },
    ...reactTableOptions,
  });
}
