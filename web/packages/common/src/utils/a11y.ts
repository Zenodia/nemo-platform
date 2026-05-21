// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

/**
 * Get the aria-sort attribute value based on the current sort state.
 *
 * @param sortBy - The current sort field
 * @param targetSortBy - The target sort field
 * @param order - The current sort order
 * @returns The aria-sort attribute value
 */
export const getAriaSort = (
  sortBy: string,
  targetSortBy: string,
  order: 'asc' | 'desc'
): 'ascending' | 'descending' | undefined => {
  if (sortBy === targetSortBy) {
    return order === 'asc' ? 'ascending' : 'descending';
  }
  return undefined;
};
