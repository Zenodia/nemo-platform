// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { DataViewContext } from '@nemo/common/src/components/DataView/internal/context';
import { useCustomReactTable } from '@nemo/common/src/components/DataView/internal/hooks/useCustomReactTable';
import {
  type MakeColumns,
  useMakeColumns,
} from '@nemo/common/src/components/DataView/internal/hooks/useMakeColumns';
import type {
  IntentionalAny,
  QueryStatus,
  WithDataViewDataMode,
} from '@nemo/common/src/components/DataView/internal/types';
import type { DataViewState } from '@nemo/common/src/components/DataView/internal/useDataViewState';
import { Flex, type FlexProps } from '@nvidia/foundations-react-core';
import type { Row, TableOptions } from '@tanstack/react-table';
import classnames from 'classnames';
import { useMemo, type JSX } from 'react';

export type DataViewCommonProps<TData> = {
  /**
   * If true, tooltips via the "title" attribute will be automatically added to cells. This will
   * help when cells are truncated.
   * @defaultValue true
   */
  autoCellTooltips?: boolean;
  /** The data to display in the table. */
  data: TData[] | undefined;
  /** Builds the column definitions. */
  makeColumns: MakeColumns<TData>;
  /** Pass options to the underlying tanstack/react-table hook. */
  reactTableOptions?: Partial<TableOptions<TData>>;
  /**
   * Custom row expansion component, as an alternative to subRows. If both are provided, both
   * will be rendered.
   */
  renderCustomRowExpansion?: (data: { row: Row<TData> }) => JSX.Element;
  /** If provided, the table will display a loading or error state. */
  requestStatus?: QueryStatus;
  /** The returned object from `useDataViewState`. Manages the state of the DataView. */
  state: DataViewState;
  /** Number of rows to display while loading. */
  loadingRows?: number;
};

export type DataViewProps<TData> = DataViewCommonProps<TData> & WithDataViewDataMode;

/**
 * The root component for the DataView. All DataView components should be rendered within this
 * component, which provides the context.
 */
export function Root<TData>({
  autoCellTooltips = true,
  className,
  children,
  data: _data,
  dataMode = 'auto',
  makeColumns,
  reactTableOptions,
  renderCustomRowExpansion,
  requestStatus,
  state,
  totalCount,
  loadingRows = 3,
  ...props
}: DataViewProps<TData> & FlexProps): JSX.Element {
  const isLoading = requestStatus === 'loading';
  const data = useMemo(
    () =>
      isLoading
        ? (Array.from({ length: loadingRows }, () => ({}) as TData) as TData[])
        : (_data ?? []),
    [_data, isLoading, loadingRows]
  );
  const columns = useMakeColumns({ makeColumns, overrideToLoadingCells: isLoading });
  const table = useCustomReactTable({
    columns,
    data,
    dataMode,
    reactTableOptions,
    renderCustomRowExpansion,
    state,
    totalCount: dataMode !== 'auto' ? totalCount : undefined,
  });
  return (
    <DataViewContext
      value={{
        autoCellTooltips,
        data,
        dataMode,
        isDataViewEmptyState:
          requestStatus !== 'loading' &&
          requestStatus !== 'error' &&
          ((dataMode !== 'auto' ? totalCount : undefined) === 0 ||
            table.getRowModel().rows.length === 0),
        isDataViewErrorState: requestStatus === 'error',
        isDataViewLoadingState: requestStatus === 'loading',
        renderCustomRowExpansion:
          renderCustomRowExpansion as DataViewContextValueRenderCustomRowExpansion,
        requestStatus,
        state,
        table: table as unknown as DataViewContextTable,
        totalCount: dataMode !== 'auto' ? totalCount : undefined,
      }}
    >
      <Flex
        className={classnames('data-view-content text-primary w-full font-sans', className)}
        direction="col"
        data-testid="data-view-content"
        gap="density-sm"
        {...props}
      >
        {children}
      </Flex>
    </DataViewContext>
  );
}

type DataViewContextValueRenderCustomRowExpansion =
  | ((data: { row: Row<IntentionalAny> }) => JSX.Element)
  | undefined;

type DataViewContextTable = ReturnType<typeof useCustomReactTable<IntentionalAny>>;
