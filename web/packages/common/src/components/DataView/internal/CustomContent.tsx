// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { useInnerDataViewContext } from '@nemo/common/src/components/DataView/internal/context';
import {
  StatusResult,
  type StatusResultProps,
} from '@nemo/common/src/components/DataView/internal/StatusResult';
import { Flex, Spinner } from '@nvidia/foundations-react-core';
import type { Row, Table } from '@tanstack/react-table';
import type { JSX } from 'react';

export interface CustomContentProps<TData> extends Pick<
  StatusResultProps,
  'renderErrorState' | 'renderEmptyState'
> {
  children: (args: { rows: Row<TData>[] }) => JSX.Element;
  /** Custom loading state. By default a spinner is rendered. */
  renderLoadingState?: () => JSX.Element;
  /** Associated displayMode value. If provided, only render when the displayMode matches. */
  value?: string;
}

const defaultRenderLoadingState = () => (
  <Flex justify="center" align="center" className="p-density-md">
    <Spinner aria-label="Loading contents" />
  </Flex>
);

/**
 * Manages loading, empty, and error states and provides rows for rendering custom content
 * such as cards.
 */
export function CustomContent<TData>({
  children,
  renderEmptyState,
  renderErrorState,
  renderLoadingState = defaultRenderLoadingState,
  value,
}: CustomContentProps<TData>): JSX.Element | null {
  const {
    state: { displayMode },
    isDataViewErrorState,
    isDataViewEmptyState,
    isDataViewLoadingState,
    table,
  } = useInnerDataViewContext();
  if (value && value !== displayMode.state) {
    return null;
  }
  if (isDataViewErrorState || isDataViewEmptyState) {
    return <StatusResult renderErrorState={renderErrorState} renderEmptyState={renderEmptyState} />;
  }
  if (isDataViewLoadingState && renderLoadingState) {
    return renderLoadingState();
  }
  return children({ rows: (table as unknown as Table<TData>).getRowModel().rows });
}
