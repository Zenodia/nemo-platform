// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

/** Namespace shape for MSW entity-store mocks. */
export interface Namespace {
  id?: string;
  created_at?: string;
  updated_at?: string;
  description?: string;
}

export interface NamespacesPage {
  object: string;
  data: Namespace[];
  pagination: {
    page: number;
    page_size: number;
    total_results: number;
    total_pages: number;
    current_page_size: number;
  };
}

export const namespace1: Namespace = {
  id: 'john-doe-namespace',
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-01T00:00:00Z',
  description: 'John Doe namespace',
};

export const namespace2: Namespace = {
  id: 'test-namespace',
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-01T00:00:00Z',
  description: 'Test namespace for unit tests',
};

export const namespace3: Namespace = {
  id: 'another-namespace',
  created_at: '2024-01-02T00:00:00Z',
  updated_at: '2024-01-02T00:00:00Z',
  description: 'Another test namespace',
};

export const namespaces = [namespace1, namespace2, namespace3];

export const namespacesPage: NamespacesPage = {
  object: 'list',
  data: namespaces,
  pagination: {
    page: 1,
    page_size: 10,
    current_page_size: namespaces.length,
    total_pages: 1,
    total_results: namespaces.length,
  },
};

export const singleNamespacePage: NamespacesPage = {
  object: 'list',
  data: [namespace1],
  pagination: {
    page: 1,
    page_size: 10,
    current_page_size: 1,
    total_pages: 1,
    total_results: 1,
  },
};

export const emptyNamespacesPage: NamespacesPage = {
  object: 'list',
  data: [],
  pagination: {
    page: 1,
    page_size: 10,
    current_page_size: 0,
    total_pages: 1,
    total_results: 0,
  },
};

/**
 * Creates a namespaces page with filtered namespaces based on search query
 * Filters namespaces by ID substring match (case-insensitive)
 */
export const createFilteredNamespacesPage = (
  searchQuery?: string,
  allNamespaces: Namespace[] = namespaces
): NamespacesPage => {
  const filtered =
    searchQuery && searchQuery.trim()
      ? allNamespaces.filter((ns) => ns.id?.toLowerCase().includes(searchQuery.toLowerCase()))
      : allNamespaces;

  return {
    object: 'list',
    data: filtered,
    pagination: {
      page: 1,
      page_size: 10,
      current_page_size: filtered.length,
      total_pages: 1,
      total_results: filtered.length,
    },
  };
};

/**
 * Creates a namespaces page with specific namespaces
 */
export const createNamespacesPage = (
  namespaceList: Namespace[],
  page: number = 1,
  page_size: number = 10
): NamespacesPage => {
  return {
    object: 'list',
    data: namespaceList,
    pagination: {
      page,
      page_size,
      current_page_size: namespaceList.length,
      total_pages: Math.ceil(namespaceList.length / page_size),
      total_results: namespaceList.length,
    },
  };
};
