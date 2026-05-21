// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { dateTimeFilter } from '@nemo/common/src/components/DataView/dateTimeFilter';
import * as DataView from '@nemo/common/src/components/DataView/internal';
import {
  ROW_ACTIONS_COLUMN_SIZE,
  ROW_SELECTION_COLUMN_SIZE,
  StudioDataView,
} from '@nemo/common/src/components/DataView/StudioDataView';
import { ErrorMessage } from '@nemo/common/src/components/ErrorMessage';
import { RelativeTime } from '@nemo/common/src/components/RelativeTime';
import { TableEmptyState } from '@nemo/common/src/components/TableEmptyState';
import { useDeferredUnmount } from '@nemo/common/src/hooks/useDeferredUnmount';
import { useSetTimeout } from '@nemo/common/src/hooks/useSetTimeout';
import { useStudioDataViewState } from '@nemo/common/src/hooks/useStudioDataViewState';
import { getSortParamWithWhitelist } from '@nemo/common/src/utils/query';
import { useListEntries } from '@nemo/sdk/generated/platform/api';
import { Entry, EntrySortField } from '@nemo/sdk/generated/platform/schema';
import { Anchor, Button, Flex, Stack, Text } from '@nvidia/foundations-react-core';
import { getErrorMessage } from '@studio/api/common/utils';
import { EntryBulkDeleteModal } from '@studio/components/IntakeEntriesTable/EntryBulkDeleteModal';
import { EntryBulkExportModal } from '@studio/components/IntakeEntriesTable/EntryBulkExportModal';
import { EntryRatingCell } from '@studio/components/IntakeEntriesTable/EntryRatingCell';
import { EntryStatusCell } from '@studio/components/IntakeEntriesTable/EntryStatusCell';
import { EntryThumbCell } from '@studio/components/IntakeEntriesTable/EntryThumbCell';
import { getEntryResponseContent } from '@studio/components/IntakeEntriesTable/utils';
import { IntakeThreadPanel } from '@studio/components/IntakeThreadPanel';
import { Loading } from '@studio/components/Layouts/Loading';
import { AnnotationModal } from '@studio/components/modals/AnnotationModal';
import { useWorkspaceFromPathIfExists } from '@studio/hooks/useWorkspaceFromPath';
import { getIntakeEntryRoute } from '@studio/routes/utils';
import { getLastUserMessageContent } from '@studio/util/entries';
import { keepPreviousData } from '@tanstack/react-query';
import { MessagesSquare, X, Upload, Search, Pencil } from 'lucide-react';
import { ComponentProps, FC, ReactNode, useMemo, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';

type EntryWithId = Entry & { id: string };

export interface IntakeEntriesTableProps {
  /** Workspace identifier. Falls back to the `:workspace` route param when not provided. */
  workspace?: string;
  /** Callback when a row is clicked */
  onRowClick?: (entry: Entry) => void;
  /** Enable row actions (default: true) */
  enableActions?: boolean;
  /** Enable checkbox selection (default: true) */
  enableSelection?: boolean;
  /** Empty state actions - shown when no entries exist */
  emptyStateActions?: ReactNode;
  /** No results actions - shown when filters return no results */
  noResultsActions?: ReactNode;
  attributes?: {
    Stack?: ComponentProps<typeof Stack>;
    DataViewRoot?: ComponentProps<typeof DataView.Root<EntryWithId>>;
    DataViewTableContent?: ComponentProps<typeof DataView.TableContent>;
  };
}

/**
 * A table that displays a list of intake entries with filtering, search, and bulk operations.
 */
export const IntakeEntriesTable: FC<IntakeEntriesTableProps> = ({
  workspace: workspaceProp,
  onRowClick,
  enableActions = true,
  enableSelection,
  emptyStateActions,
  noResultsActions,
  attributes,
}) => {
  const navigate = useNavigate();
  const routeWorkspace = useWorkspaceFromPathIfExists();
  const workspace = workspaceProp ?? routeWorkspace ?? '';

  const dataViewState = useStudioDataViewState({
    defaultSort: { id: 'created_at', desc: true },
  });

  const hasActiveFilters =
    !!dataViewState.debouncedSearchBar || dataViewState.debouncedColumnFilters.length > 0;

  const [annotatingEntry, setAnnotatingEntry] = useState<Entry | undefined>(undefined);

  // Thread panel state with deferred unmount for close animation
  const threadPanel = useDeferredUnmount<string>();

  // Export single entry modal state
  const exportSingleEntryModal = useDeferredUnmount<Entry>();

  const [setAnimationTimeout] = useSetTimeout();

  const {
    data: entriesResponse,
    isPending,
    isFetching,
    error,
  } = useListEntries(
    workspace,
    {
      filter: {
        ...dataViewState.apiFilter.filter,
        ...(dataViewState.apiFilter.searchText
          ? { external_id: dataViewState.apiFilter.searchText }
          : {}),
      },
      page: dataViewState.pagination.state.pageIndex + 1,
      page_size: dataViewState.pagination.state.pageSize,
      sort: getSortParamWithWhitelist(
        dataViewState.sorting.state,
        ['created_at', 'updated_at'],
        '-created_at'
      ) as EntrySortField,
    },
    {
      query: {
        placeholderData: keepPreviousData,
      },
    }
  );

  // Ensure each entry has a unique id for DataView row selection
  const entries = useMemo<EntryWithId[]>(
    () =>
      (entriesResponse?.data || []).map((entry: Entry) => ({
        ...entry,
        id: entry.id || `entry-${entry.external_id || Math.random()}`,
      })),
    [entriesResponse?.data]
  );

  // Column definitions
  const makeColumns: ComponentProps<typeof DataView.Root<EntryWithId>>['makeColumns'] = (
    { accessor },
    { rowSelectionColumn, rowActionsColumn }
  ) =>
    [
      enableSelection && rowSelectionColumn({ size: ROW_SELECTION_COLUMN_SIZE }),
      {
        id: 'status',
        header: 'Status',
        enableSorting: false,
        size: 130,
        cell: ({ row }: { row: DataView.TanstackTable.Row<EntryWithId> }) => (
          <EntryStatusCell entry={row.original} />
        ),
      },
      {
        id: 'thumb',
        header: 'Thumb',
        enableSorting: false,
        size: 80,
        cell: ({ row }: { row: DataView.TanstackTable.Row<EntryWithId> }) => (
          <EntryThumbCell entry={row.original} />
        ),
      },
      {
        id: 'rating',
        header: 'Rating',
        enableSorting: false,
        size: 80,
        cell: ({ row }: { row: DataView.TanstackTable.Row<EntryWithId> }) => (
          <EntryRatingCell entry={row.original} />
        ),
      },
      {
        id: 'model_name',
        header: 'Model Name',
        enableSorting: false,
        size: 150,
        cell: ({ row }: { row: DataView.TanstackTable.Row<EntryWithId> }) => {
          const modelName = row.original?.data?.request?.model;
          const routeTo = getIntakeEntryRoute(workspace, row.original.id || '');
          if (routeTo) {
            return (
              <Anchor asChild>
                <Link to={routeTo}>{modelName}</Link>
              </Anchor>
            );
          }
          return (
            <Text className="cursor-pointer" onClick={() => onRowClick?.(row.original)}>
              {modelName}
            </Text>
          );
        },
      },
      {
        id: 'input',
        header: 'Input',
        enableSorting: false,
        cell: ({ row }: { row: DataView.TanstackTable.Row<EntryWithId> }) => {
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
        cell: ({ row }: { row: DataView.TanstackTable.Row<EntryWithId> }) => {
          const content = getEntryResponseContent(row.original);
          return (
            <Text className="truncate" title={content}>
              {content}
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
        meta: {
          filter: dateTimeFilter('Created At'),
        },
        cell({ row }) {
          return row.original?.created_at ? (
            <RelativeTime datetime={row.original.created_at} />
          ) : null;
        },
      }),
      enableActions &&
        rowActionsColumn({
          size: ROW_ACTIONS_COLUMN_SIZE,
          enableResizing: false,
          rowActions: (entry: EntryWithId) => {
            const actions = [
              {
                slotLeft: <Search />,
                children: 'View Details',
                onSelect: () => {
                  navigate(getIntakeEntryRoute(workspace, entry.id || ''));
                },
              },
              {
                slotLeft: <Pencil />,
                children: 'Annotate',
                onSelect: () => {
                  setAnnotatingEntry(entry);
                },
              },
              {
                slotLeft: <Upload />,
                children: 'Upload Entry',
                onSelect: () => {
                  exportSingleEntryModal.open(entry);
                },
              },
            ];
            // Conditionally add View Thread action
            if (entry.context?.thread_id) {
              actions.splice(1, 0, {
                slotLeft: <MessagesSquare />,
                children: 'View Thread',
                onSelect: () => {
                  threadPanel.open(entry.context!.thread_id!);
                },
              });
            }
            return actions;
          },
        }),
    ].filter((col): col is DataView.TanstackTable.ColumnDef<EntryWithId> => Boolean(col));

  // Loading state
  if (isPending) {
    return (
      <Stack className="h-full w-full">
        <Loading description="Loading entries..." />
      </Stack>
    );
  }

  // Error state
  if (error) {
    return <ErrorMessage message={getErrorMessage(error)} />;
  }

  // Default empty state actions
  const defaultEmptyActions = (
    <Text kind="body/regular/md">No entries have been recorded yet.</Text>
  );

  const defaultNoResultsActions = (
    <Button kind="tertiary" onClick={dataViewState.resetFilters}>
      <X /> Clear Filters
    </Button>
  );

  return (
    <>
      <Stack {...attributes?.Stack}>
        <StudioDataView<EntryWithId>
          dataViewState={dataViewState}
          searchField="external_id"
          makeColumns={makeColumns}
          renderBulkActions={({ selectedRows }) => {
            const rows = selectedRows as EntryWithId[];
            if (rows.length === 0) return null;
            return (
              <Flex gap="density-md" align="center">
                <EntryBulkExportModal
                  workspace={workspace}
                  selectedEntries={rows}
                  onSuccess={() =>
                    setAnimationTimeout(() => dataViewState.rowSelection.set({}), 300)
                  }
                />
                <EntryBulkDeleteModal
                  workspace={workspace}
                  selectedEntries={rows}
                  onConfirmSuccess={() =>
                    setAnimationTimeout(() => dataViewState.rowSelection.set({}), 300)
                  }
                />
              </Flex>
            );
          }}
          attributes={{
            DataViewSearchBar: {
              placeholder: 'Search entries by external ID',
            },
            DataViewRoot: {
              data: entries,
              totalCount: entriesResponse?.pagination?.total_results,
              requestStatus: isFetching ? 'loading' : undefined,
            },
            DataViewTableContent: {
              renderEmptyState: () =>
                hasActiveFilters ? (
                  <TableEmptyState
                    header="No Results Found"
                    emptyMessage="No entries match your filters"
                    actions={noResultsActions ?? defaultNoResultsActions}
                  />
                ) : (
                  <TableEmptyState
                    header="No Entries"
                    emptyMessage="Get started by recording entries from your LLM application."
                    actions={emptyStateActions ?? defaultEmptyActions}
                  />
                ),
            },
          }}
        />
      </Stack>
      <AnnotationModal
        open={!!annotatingEntry}
        onClose={() => setAnnotatingEntry(undefined)}
        entry={annotatingEntry}
      />
      {/* Single entry export modal */}
      {exportSingleEntryModal.value && (
        <EntryBulkExportModal
          workspace={workspace}
          selectedEntries={[exportSingleEntryModal.value]}
          onSuccess={exportSingleEntryModal.close}
          showTrigger={false}
          open={!!exportSingleEntryModal.isOpen}
          onClose={exportSingleEntryModal.close}
        />
      )}
      {threadPanel.value && (
        <IntakeThreadPanel
          threadId={threadPanel.value}
          open={threadPanel.isOpen}
          onOpenChange={threadPanel.onOpenChange}
        />
      )}
    </>
  );
};
