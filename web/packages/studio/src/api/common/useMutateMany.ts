// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { useMutation, UseMutationOptions, UseMutationResult } from '@tanstack/react-query';

/**
 * A wrapper for useMutation that allows a component to create many entities in a typesafe way.
 * Takes a mutation function and returns a mutation hook that can be used to create many entities.
 * @param mutationFn The base mutation function to use for creating a single entity
 * @param options Optional mutation options
 * @returns A mutation hook that can create multiple entities
 */
export const useMutateMany = <TData, TVariables>(
  mutationFn: (variables: TVariables) => Promise<TData>,
  options?: Omit<UseMutationOptions<TData[], Error, TVariables[]>, 'mutationFn'>
): UseMutationResult<TData[], Error, TVariables[]> => {
  return useMutation({
    ...options,
    mutationFn: async (items: TVariables[]) => {
      // Create all items in parallel
      const promises = items.map((item) => mutationFn(item));

      // Wait for all items to complete, whether they succeed or fail
      const results = await Promise.allSettled(promises);

      // Check if any items failed
      const failedItems = results.filter(
        (result): result is PromiseRejectedResult => result.status === 'rejected'
      );

      if (failedItems.length > 0) {
        // If any items failed, throw an error with details about the failures
        throw new Error(
          `Failed to create ${failedItems.length} out of ${items.length} items. Errors: ${failedItems.map((failure) => failure.reason.message).join('; ')}`
        );
      }

      // Return the successful results
      return results
        .filter((result) => result.status === 'fulfilled')
        .map((result) => result.value);
    },
  });
};
