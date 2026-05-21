// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { IntakeEntriesTable } from '@studio/components/IntakeEntriesTable';
import { server } from '@studio/mocks/node';
import { renderRoute } from '@studio/tests/util/render';
import { waitFor } from '@testing-library/react';
import { http, HttpResponse } from 'msw';

vi.mock('use-debounce', () => ({
  useDebounce: (value: unknown) => [value, { cancel: () => {}, flush: () => {} }],
}));

const ENTRIES_URL = '*/apis/intake/v2/workspaces/:workspace/entries';

const emptyEntriesPage = {
  object: 'list',
  data: [],
  pagination: {
    page: 1,
    page_size: 50,
    current_page_size: 0,
    total_pages: 0,
    total_results: 0,
  },
};

const captureRequests = () => {
  const requestUrls: string[] = [];
  server.use(
    http.get(ENTRIES_URL, ({ request }) => {
      requestUrls.push(request.url);
      return HttpResponse.json(emptyEntriesPage);
    })
  );
  return requestUrls;
};

const renderTable = (initialEntry: string) =>
  renderRoute(<IntakeEntriesTable workspace="default" />, {
    history: initialEntry,
    routes: [
      {
        path: '/workspaces/:workspace/intake/entries',
        element: <IntakeEntriesTable workspace="default" />,
      },
    ],
  });

describe('IntakeEntriesTable filter query params', () => {
  afterEach(() => {
    server.resetHandlers();
  });

  it('always scopes requests to the workspace project', async () => {
    const requestUrls = captureRequests();
    renderTable('/workspaces/default/intake/entries');

    await waitFor(() => expect(requestUrls.length).toBeGreaterThan(0));

    const url = new URL(requestUrls.at(-1)!);
    expect(url.pathname).toBe('/apis/intake/v2/workspaces/default/entries');
  });

  it('sends filter[external_id] (exact match) when search is active', async () => {
    const requestUrls = captureRequests();
    renderTable('/workspaces/default/intake/entries?s=entry-123');

    await waitFor(() => {
      expect(requestUrls.some((u) => new URL(u).searchParams.has('filter[external_id]'))).toBe(
        true
      );
    });

    const url = new URL(requestUrls.at(-1)!);
    expect(url.searchParams.get('filter[external_id]')).toBe('entry-123');
    // Exact match — must NOT be wrapped in $like
    expect(url.searchParams.has('filter[external_id][$like]')).toBe(false);
  });

  it('never emits a top-level search or search[ key', async () => {
    const requestUrls = captureRequests();
    renderTable('/workspaces/default/intake/entries?s=foo');

    await waitFor(() => expect(requestUrls.length).toBeGreaterThan(0));

    for (const raw of requestUrls) {
      const params = new URL(raw).searchParams;
      expect(params.has('search')).toBe(false);
      expect(Array.from(params.keys()).some((k) => k.startsWith('search['))).toBe(false);
    }
  });
});
