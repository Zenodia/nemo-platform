// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

const DEFAULT_PAGE_SIZE = 50;

export const tablePaginationSort = <T>(debouncedFilterState: {
  page?: number;
  page_size?: number;
  order?: string;
  sort_by?: string;
}) => {
  const order = debouncedFilterState?.order || 'desc';
  const sortBy = debouncedFilterState?.sort_by || 'created_at';
  const prefix = order === 'desc' ? '-' : '';

  return {
    page: debouncedFilterState?.page || 1,
    page_size: debouncedFilterState?.page_size || DEFAULT_PAGE_SIZE,
    sort: `${prefix}${sortBy}` as T,
  };
};
