// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import * as DataView from '@nemo/common/src/components/DataView/internal';
import {
  ROW_SELECTION_COLUMN_SIZE,
  StudioDataView,
} from '@nemo/common/src/components/DataView/StudioDataView';
import { ErrorMessage } from '@nemo/common/src/components/ErrorMessage';
import { RelativeTime } from '@nemo/common/src/components/RelativeTime';
import { TableEmptyState } from '@nemo/common/src/components/TableEmptyState';
import { useStudioDataViewState } from '@nemo/common/src/hooks/useStudioDataViewState';
import { getSortParamWithWhitelist } from '@nemo/common/src/utils/query';
import { useListEntries } from '@nemo/sdk/generated/platform/api';
import { Entry, EntrySortField } from '@nemo/sdk/generated/platform/schema';
import { Anchor, Button, Stack, Text } from '@nvidia/foundations-react-core';
import { useWorkspaceFromPathIfExists } from '@studio/hooks/useWorkspaceFromPath';
import {
  getLastAssistantMessage,
  getLastUserMessageContent,
  getTurnCount,
} from '@studio/util/entries';
import { keepPreviousData } from '@tanstack/react-query';
import { ComponentProps, FC, useEffect, useMemo, useRef } from 'react';
import { Link } from 'react-router-dom';

type ThreadEntry = Entry & { id: string };

/** Intake list entries API only supports sorting by created_at / updated_at. */
const LIST_ENTRIES_SORT_FIELDS = ['created_at', 'updated_at'] as const;
const THREADS_ENTRY_SCAN_PAGE_SIZE = 1000;

export interface IntakeThreadsTableProps {
  /** Optional workspace override. Falls back to reading workspace from the URL path. */
  workspace?: string;
  /** Callback when threads are selected */
  onThreadsSelected?: (entries: Entry[]) => void;
  /** Callback when a row is clicked */
  onRowClick?: (entry: Entry) => void;
  /** Enable checkbox selection (default: false) */
  enableSelection?: boolean;
  /** Type of selection (default: 'multiple') */
  selectionType?: 'multiple' | 'single';
  /** Render thread ID as link - provide a function that returns the route */
  getThreadRoute?: (entry: Entry) => string;
  attributes?: {
    Stack?: ComponentProps<typeof Stack>;
  };
}

/**
 * A table that displays a list of intake threads (grouped by thread_id).
 */
export const IntakeThreadsTable: FC<IntakeThreadsTableProps> = ({
  workspace: workspaceProp,
  onThreadsSelected,
  onRowClick,
  enableSelection,
  selectionType = 'multiple',
  getThreadRoute,
  attributes,
}) => {
  const workspaceFromPath = useWorkspaceFromPathIfExists();
  const workspace = workspaceProp ?? workspaceFromPath;
  const workspaceKey = workspace ?? '';

  const dataViewState = useStudioDataViewState({
    defaultSort: { id: 'created_at', desc: true },
  });
  const pageIndex = dataViewState.pagination.state.pageIndex;
  const pageSize = dataViewState.pagination.state.pageSize;

  // Clear selections when page changes
  const prevPageIndexRef = useRef(pageIndex);
  useEffect(() => {
    if (prevPageIndexRef.current !== pageIndex) {
      prevPageIndexRef.current = pageIndex;
      dataViewState.rowSelection.set({});
    }
  }, [pageIndex, dataViewState.rowSelection]);

  const {
    data: entriesResponse,
    refetch,
    isFetching,
    error,
  } = useListEntries(
    workspaceKey,
    {
      filter: {
        context: dataViewState.debouncedSearchBar
          ? { thread_id: dataViewState.debouncedSearchBar }
          : undefined,
      },
      page: 1,
      page_size: THREADS_ENTRY_SCAN_PAGE_SIZE,
      sort: getSortParamWithWhitelist(
        dataViewState.sorting.state,
        LIST_ENTRIES_SORT_FIELDS,
        '-created_at'
      ) as EntrySortField,
    },
    {
      query: {
        placeholderData: keepPreviousData,
        enabled: Boolean(workspace),
      },
    }
  );

  // Group the scanned entries locally because some deployed backends reject filter[longest_per_thread].
  const threads = useMemo<ThreadEntry[]>(() => {
    const entriesByThread = new Map<string, Entry>();

    for (const entry of entriesResponse?.data || []) {
      const threadId = entry.context?.thread_id;
      if (!threadId) continue;

      const currentEntry = entriesByThread.get(threadId);
      if (!currentEntry || getTurnCount(entry) > getTurnCount(currentEntry)) {
        entriesByThread.set(threadId, entry);
      }
    }

    return Array.from(entriesByThread.entries()).map(([threadId, entry]) => ({
      ...entry,
      id: threadId,
    }));
  }, [entriesResponse?.data]);

  const paginatedThreads = useMemo(
    () => threads.slice(pageIndex * pageSize, pageIndex * pageSize + pageSize),
    [pageIndex, pageSize, threads]
  );

  // Derive selected threads from DataView's row selection state
  const selectedThreads = useMemo<ThreadEntry[]>(() => {
    const selectedIds = Object.keys(dataViewState.rowSelection.state);
    if (selectedIds.length === 0) return [];

    const selected = selectedIds
      .map((id) => threads.find((thread) => thread.id === id))
      .filter((thread): thread is ThreadEntry => thread !== undefined);

    // For single selection mode, return only the last selected item
    if (selectionType === 'single' && selected.length > 1) {
      return [selected[selected.length - 1]];
    }

    return selected;
  }, [dataViewState.rowSelection.state, threads, selectionType]);

  // Notify parent when selection changes
  const prevSelectedRef = useRef<ThreadEntry[]>([]);
  useEffect(() => {
    // Only notify if selection actually changed (by reference or length)
    if (
      prevSelectedRef.current.length !== selectedThreads.length ||
      !selectedThreads.every((t, i) => t.id === prevSelectedRef.current[i]?.id)
    ) {
      prevSelectedRef.current = selectedThreads;
      onThreadsSelected?.(selectedThreads);
    }
  }, [selectedThreads, onThreadsSelected]);

  // Column definitions
  const makeColumns: ComponentProps<typeof StudioDataView<ThreadEntry>>['makeColumns'] = (
    { accessor },
    { rowSelectionColumn }
  ) =>
    (
      [
        enableSelection && rowSelectionColumn({ size: ROW_SELECTION_COLUMN_SIZE }),
        {
          id: 'thread_id',
          header: 'Thread ID',
          enableSorting: false,
          size: 180,
          cell: ({ row }: { row: DataView.TanstackTable.Row<ThreadEntry> }) => {
            const threadId = row.original.context?.thread_id || '—';
            if (getThreadRoute) {
              return (
                <Anchor asChild>
                  <Link to={getThreadRoute(row.original)} className="truncate" title={threadId}>
                    {threadId}
                  </Link>
                </Anchor>
              );
            }
            return (
              <Text className="truncate" title={threadId}>
                {threadId}
              </Text>
            );
          },
        },
        {
          id: 'entries_count',
          header: 'Turns',
          enableSorting: false,
          size: 80,
          cell: ({ row }: { row: DataView.TanstackTable.Row<ThreadEntry> }) => {
            const count = getTurnCount(row.original);
            return <Text>{count}</Text>;
          },
        },
        {
          id: 'model_name',
          header: 'Model Name',
          enableSorting: false,
          size: 150,
          cell: ({ row }: { row: DataView.TanstackTable.Row<ThreadEntry> }) => {
            const modelName = row.original.data?.request?.model || '—';
            return (
              <Text className="truncate" title={modelName}>
                {modelName}
              </Text>
            );
          },
        },
        {
          id: 'input',
          header: 'Input',
          enableSorting: false,
          cell: ({ row }: { row: DataView.TanstackTable.Row<ThreadEntry> }) => {
            const content = getLastUserMessageContent(row.original);
            return (
              <Text className="truncate" title={content}>
                {content || '—'}
              </Text>
            );
          },
        },
        {
          id: 'output',
          header: 'Output',
          enableSorting: false,
          cell: ({ row }: { row: DataView.TanstackTable.Row<ThreadEntry> }) => {
            const content = getLastAssistantMessage(row.original);
            return (
              <Text className="truncate" title={content}>
                {content || '—'}
              </Text>
            );
          },
        },
        accessor('created_at', {
          id: 'created_at',
          header: 'Created',
          enableSorting: true,
          size: 150,
          maxSize: 150,
          minSize: 150,
          cell({ row }) {
            return row.original?.created_at ? (
              <RelativeTime datetime={row.original.created_at} />
            ) : null;
          },
        }),
        // TODO: Add row actions dropdown menu with thread operations
        // rowActionsColumn will be added in a future diff
      ] as (DataView.TanstackTable.ColumnDef<ThreadEntry> | false | undefined)[]
    ).filter((col): col is DataView.TanstackTable.ColumnDef<ThreadEntry> => Boolean(col));

  // Check if we have an active search (for empty state messaging)
  const hasActiveSearch = !!dataViewState.debouncedSearchBar;

  return (
    <Stack gap="density-2xl" {...attributes?.Stack}>
      <StudioDataView<ThreadEntry>
        dataViewState={dataViewState}
        searchField="thread_id"
        makeColumns={makeColumns}
        onRowClick={onRowClick ? (row) => onRowClick(row) : undefined}
        attributes={{
          DataViewSearchBar: {
            placeholder: 'Search by thread ID',
          },
          DataViewRoot: {
            data: paginatedThreads,
            totalCount: threads.length,
            requestStatus: error ? 'error' : isFetching ? 'loading' : undefined,
          },
          DataViewTableContent: {
            renderErrorState: () => (
              <ErrorMessage
                message="Failed to fetch threads"
                slotFooter={
                  <Button type="button" kind="tertiary" onClick={() => refetch()}>
                    Retry
                  </Button>
                }
              />
            ),
            renderEmptyState: () => (
              <TableEmptyState
                header={hasActiveSearch ? 'No Results' : 'No Threads Found'}
                emptyMessage={
                  hasActiveSearch
                    ? 'No threads match your search criteria.'
                    : 'Threads for this workspace will appear here when available.'
                }
                actions={
                  hasActiveSearch ? (
                    <Button kind="tertiary" onClick={dataViewState.resetFilters}>
                      Clear search
                    </Button>
                  ) : undefined
                }
              />
            ),
          },
        }}
      />
    </Stack>
  );
};
