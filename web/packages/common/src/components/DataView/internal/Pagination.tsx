// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { useInnerDataViewContext } from '@nemo/common/src/components/DataView/internal/context';
import {
  Flex,
  PaginationArrowButton,
  PaginationControlsGroup,
  PaginationNavigationGroup,
  PaginationPageInput,
  PaginationPageList,
  PaginationPageSizeSelect,
  PaginationRoot,
  type PaginationRootProps,
  Text,
} from '@nvidia/foundations-react-core';
import classnames from 'classnames';
import { Fragment, type ComponentPropsWithoutRef, type JSX, type ReactNode } from 'react';

export interface DataViewPaginationProps extends Omit<PaginationRootProps, 'totalItems'> {
  /**
   * Treat `DataView.Pagination` as only a state provider and pass your own pagination
   * components as `children` for maximum control.
   */
  children?: ReactNode;
  /** Whether to show the first and last page buttons. @defaultValue true */
  showFirstAndLastButtons?: boolean;
  /** Whether to show the go to page input. @defaultValue true */
  showGoToPage?: boolean;
  /** Whether to show the items per page select. @defaultValue true */
  showItemsPerPage?: boolean;
  /** Whether to show pagination while in an empty state. @defaultValue false */
  showWhileEmpty?: boolean;
  /** Whether to show pagination while in an error state. @defaultValue false */
  showWhileError?: boolean;
  /** Whether to show pagination while in a loading state. @defaultValue false */
  showWhileLoading?: boolean;
  /** Whether to show pagination while items < page size. @defaultValue false */
  showWhileLessThanPageSize?: boolean;
}

/**
 * A pagination component for the DataView. Should be rendered below the table content.
 */
export function Pagination({
  className,
  children,
  showFirstAndLastButtons = true,
  showGoToPage = true,
  showItemsPerPage = true,
  showWhileError = false,
  showWhileEmpty = false,
  showWhileLoading = false,
  showWhileLessThanPageSize = false,
  ...props
}: DataViewPaginationProps): JSX.Element | null {
  const {
    state: { pagination },
    table,
    totalCount: controlledCount,
    isDataViewLoadingState,
    isDataViewEmptyState,
    isDataViewErrorState,
  } = useInnerDataViewContext();
  if (!showWhileLoading && isDataViewLoadingState) return null;
  if (!showWhileEmpty && isDataViewEmptyState) return null;
  if (!showWhileError && isDataViewErrorState) return null;
  const count = controlledCount ?? table.getRowCount();
  const currentPage = pagination.state.pageIndex + 1;
  const pageSize = pagination.state.pageSize;
  if (!showWhileLessThanPageSize && count < pageSize && !pagination.isPageSizeDirty) {
    return null;
  }
  return (
    <PaginationRoot
      className={classnames('data-view-pagination @container', className)}
      totalItems={count}
      page={currentPage}
      pageSize={pageSize}
      onPageSizeChange={(nextSize) => table.setPageSize(nextSize)}
      onPageChange={(page) => table.setPageIndex(page - 1)}
      {...props}
    >
      {children ?? (
        <Fragment>
          {showItemsPerPage && (
            <PaginationControlsGroup className="flex-1 @max-3xl:!hidden">
              <PaginationPageSizeSelect />
              <Text>Items</Text>
            </PaginationControlsGroup>
          )}
          <PaginationNavigationGroup className="flex-1 justify-center">
            {showFirstAndLastButtons && <PaginationArrowButton direction="first" />}
            <PaginationArrowButton direction="previous" />
            <PaginationPageList className="@max-md:!hidden" />
            <PaginationArrowButton direction="next" />
            {showFirstAndLastButtons && <PaginationArrowButton direction="last" />}
          </PaginationNavigationGroup>
          {showGoToPage && (
            <Flex className="flex-1 @max-3xl:!hidden" gap="density-md" align="center" justify="end">
              <Text>Go to</Text>
              <PaginationPageInput />
            </Flex>
          )}
        </Fragment>
      )}
    </PaginationRoot>
  );
}

/** Displays the total count of items in the DataView. */
export function PaginationStatus({
  className,
  text = { singular: 'Result', plural: 'Results' },
  ...props
}: {
  text?: { singular: string; plural: string };
} & ComponentPropsWithoutRef<'span'>): JSX.Element | null {
  const {
    table,
    totalCount: controlledCount,
    isDataViewErrorState,
    isDataViewLoadingState,
  } = useInnerDataViewContext();
  const count = controlledCount || table.getExpandedRowModel().flatRows.length;
  if (count === undefined || isDataViewLoadingState || isDataViewErrorState) {
    return null;
  }
  const suffix = count === 1 ? text.singular : text.plural;
  return (
    <Text
      className={classnames('hide-mobile text-secondary p-2 text-nowrap', className)}
      kind="body/regular/md"
      {...props}
    >
      {count ?? '-'} {suffix}
    </Text>
  );
}
