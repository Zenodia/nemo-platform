// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { useQueries, UseQueryOptions } from '@tanstack/react-query';
import { useMemo } from 'react';

interface UseBatchGetProps<T> {
  /**
   * Array of URNs/IDs to fetch
   */
  urns: string[];
  /**
   * Function to fetch a single item by URN/ID
   */
  fetchFn: (urn: string) => Promise<T>;
  /**
   * Query key prefix for caching
   */
  queryKeyPrefix: string;
  /**
   * Whether the query should be enabled
   */
  enabled?: boolean;
  /**
   * Number of retry attempts
   */
  retry?: number;
  /**
   * Stale time in milliseconds
   */
  staleTime?: number;
}

interface BatchGetResult<T> {
  /**
   * Array of results in the same order as the input URNs
   */
  data: (T | undefined)[];
  /**
   * Whether any of the individual queries are loading
   */
  isLoading: boolean;
  /**
   * Whether any of the individual queries are in error state
   */
  isError: boolean;
  /**
   * Array of errors from individual queries
   */
  errors: (Error | undefined)[];
  /**
   * Whether all queries have completed successfully
   */
  isSuccess: boolean;
  /**
   * Whether all queries are idle (not started)
   */
  isPending: boolean;
  /**
   * Refetch all queries
   */
  refetch: () => void;
}

/**
 * This hook is used for fetching multiple items from the API in a parallel manner
 * with individual URN caching. Each URN is cached separately, so adding new URNs
 * to the list will only fetch the new ones, not refetch existing cached data.
 *
 * @example
 * ```typescript
 * const { data: results, isLoading, error } = useBatchGet({
 *   urns: ['urn1', 'urn2', 'urn3'],
 *   fetchFn: getEvaluationResult,
 *   queryKeyPrefix: 'evaluationResults',
 *   enabled: urns.length > 0,
 *   retry: 3
 * });
 * ```
 */
export const useBatchGet = <T>({
  urns,
  fetchFn,
  queryKeyPrefix,
  ...queryOptions
}: UseBatchGetProps<T> &
  Omit<UseQueryOptions<T, Error>, 'queryKey' | 'queryFn' | 'enabled'>): BatchGetResult<T> => {
  // Deduplicate URNs while preserving order for query creation
  const uniqueUrns = Array.from(new Set(urns));

  // Create individual queries for each unique URN
  const queries = useQueries({
    queries: uniqueUrns.map((urn) => ({
      queryKey: [queryKeyPrefix, 'item', urn],
      queryFn: () => fetchFn(urn),
      ...queryOptions,
    })),
  });

  // Memoize the combined result to avoid unnecessary re-renders
  return useMemo(() => {
    const isLoading = queries.some((query) => query.isLoading);
    const isError = queries.some((query) => query.isError);
    const isSuccess = queries.every((query) => query.isSuccess);
    const isPending = queries.every((query) => query.status === 'pending');

    // Create a map of URN to query result for efficient lookup
    const urnToQueryMap = new Map<string, { data?: T; error?: Error }>();
    uniqueUrns.forEach((urn, index) => {
      const query = queries[index];
      urnToQueryMap.set(urn, {
        data: query.data,
        error: query.error || undefined,
      });
    });

    // Return data in the same order as input URNs, using the mapped results
    const orderedData = urns.map((urn) => urnToQueryMap.get(urn)?.data);

    // Create errors array in the same order as input URNs, filtering out undefined values
    const orderedErrors = urns.map((urn) => urnToQueryMap.get(urn)?.error);

    return {
      data: orderedData,
      isLoading,
      isError,
      errors: orderedErrors,
      isSuccess,
      isPending,
      refetch: () => {
        queries.forEach((query) => query.refetch());
      },
    };
  }, [queries, urns, uniqueUrns]);
};
