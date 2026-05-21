// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { useQueryClient, type QueryKey } from '@tanstack/react-query';
import { useEffect } from 'react';

/** Shape of paginated list responses the hook can patch (SDK “*Page” types). */
export type ListQueryPage<TItem> = {
  data: TItem[];
};

function shallowMergeRows<TItem extends object>(existing: TItem, incoming: TItem): TItem {
  return { ...existing, ...incoming };
}

function upsertIntoListPage<TItem>(
  old: ListQueryPage<TItem> | undefined,
  incoming: TItem,
  getRowId: (row: TItem) => string,
  merge: (existing: TItem, incoming: TItem) => TItem,
  addIfMissing: boolean
): ListQueryPage<TItem> | undefined {
  if (old == null || !Array.isArray(old.data)) {
    return old;
  }

  const id = getRowId(incoming);
  const idx = old.data.findIndex((row) => getRowId(row) === id);

  if (idx === -1) {
    if (!addIfMissing) {
      return old;
    }
    return { ...old, data: [...old.data, incoming] };
  }

  const merged = merge(old.data[idx]!, incoming);
  const nextData = [...old.data];
  nextData[idx] = merged;
  return { ...old, data: nextData };
}

export interface UseRehydrateListFromDetailQueryOptions<TItem, TDetail> {
  /** When false, skips cache writes. */
  enabled?: boolean;
  /** Latest entity from a detail query (e.g. `useModelsGetLatestDeployment`). */
  detail: TDetail | null | undefined;
  /**
   * List query key prefix; matches every cached list query whose key starts with this
   * (e.g. `getModelsListDeploymentsQueryKey(workspace)` so paginated keys still match).
   */
  listQueryKey: QueryKey;
  /** Map detail payload to the same shape as list rows (often identity). */
  detailToListItem: (detail: TDetail) => TItem;
  /** Stable row id within the list page (deployment name, dataset id, etc.). */
  getRowId: (row: TItem) => string;
  /**
   * Merge incoming onto the existing list row so fields only present on the list are kept.
   * @default shallow merge `{ ...existing, ...incoming }`
   */
  merge?: (existing: TItem, incoming: TItem) => TItem;
  /**
   * When the row is not on the current page, append it. Default false (only update rows already in cache).
   */
  addIfMissing?: boolean;
}

/**
 * Writes a detail-query result into every matching list-query cache entry so tables stay fresh
 * without refetching (status polling on a side panel, etc.).
 *
 * Pass stable callbacks for `detailToListItem` and `getRowId` (e.g. `useCallback` or module-level
 * functions) when `detail` updates often, to avoid redundant effect runs.
 */
export function useRehydrateListFromDetailQuery<TItem extends object, TDetail>({
  enabled = true,
  detail,
  listQueryKey,
  detailToListItem,
  getRowId,
  merge,
  addIfMissing = false,
}: UseRehydrateListFromDetailQueryOptions<TItem, TDetail>): void {
  const queryClient = useQueryClient();
  const mergeRows = merge ?? shallowMergeRows<TItem>;

  useEffect(() => {
    if (!enabled || detail == null) {
      return;
    }

    const incoming = detailToListItem(detail);

    queryClient.setQueriesData<ListQueryPage<TItem>>({ queryKey: listQueryKey }, (old) =>
      upsertIntoListPage(old, incoming, getRowId, mergeRows, addIfMissing)
    );
  }, [
    addIfMissing,
    detail,
    detailToListItem,
    enabled,
    getRowId,
    listQueryKey,
    mergeRows,
    queryClient,
  ]);
}
