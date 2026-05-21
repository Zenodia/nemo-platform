// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import type {
  DataMode,
  IntentionalAny,
  QueryStatus,
} from '@nemo/common/src/components/DataView/internal/types';
import type { useDataViewState } from '@nemo/common/src/components/DataView/internal/useDataViewState';
import type { Row, Table } from '@tanstack/react-table';
import { createContext, useContext, type JSX } from 'react';

export interface DataViewContextStore {
  autoCellTooltips: boolean;
  data: unknown[];
  dataMode: DataMode;
  isDataViewEmptyState: boolean;
  isDataViewErrorState: boolean;
  isDataViewLoadingState: boolean;
  renderCustomRowExpansion: ((data: { row: Row<IntentionalAny> }) => JSX.Element) | undefined;
  requestStatus: QueryStatus | undefined;
  totalCount: number | undefined;
  state: ReturnType<typeof useDataViewState>;
  table: Table<IntentionalAny>;
}

const dataViewContext = createContext<DataViewContextStore>({} as DataViewContextStore);

export const DataViewContext = dataViewContext.Provider;

/**
 * A context to store data view state that is useful in data view sub-components.
 */
export function useInnerDataViewContext(): DataViewContextStore {
  const context = useContext(dataViewContext);
  if (!context) {
    throw new Error('useInnerDataViewContext must be used within a DataView component');
  }
  return context;
}
