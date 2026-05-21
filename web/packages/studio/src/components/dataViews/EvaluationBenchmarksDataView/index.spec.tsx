// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { EvaluationBenchmarksDataView } from '@studio/components/dataViews/EvaluationBenchmarksDataView';
import { PLATFORM_BASE_URL } from '@studio/constants/environment';
import { server } from '@studio/mocks/node';
import { renderRoute } from '@studio/tests/util/render';
import { waitFor } from '@testing-library/react';
import { http, HttpResponse } from 'msw';

vi.mock('use-debounce', () => ({
  useDebounce: (value: unknown) => [value, { cancel: () => {}, flush: () => {} }],
}));

const BENCHMARKS_URL = `${PLATFORM_BASE_URL}/apis/evaluation/v2/workspaces/:workspace/benchmarks`;

const emptyBenchmarksPage = {
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
    http.get(BENCHMARKS_URL, ({ request }) => {
      requestUrls.push(request.url);
      return HttpResponse.json(emptyBenchmarksPage);
    })
  );
  return requestUrls;
};

const renderDataView = (initialEntry: string) =>
  renderRoute(<EvaluationBenchmarksDataView workspace="default" />, {
    history: initialEntry,
    routes: [
      {
        path: '/workspaces/:workspace/evaluation/benchmarks',
        element: <EvaluationBenchmarksDataView workspace="default" />,
      },
    ],
  });

describe('EvaluationBenchmarksDataView', () => {
  afterEach(() => {
    server.resetHandlers();
  });

  it('sends no filter[ or search params on initial render', async () => {
    const requestUrls = captureRequests();
    renderDataView('/workspaces/default/evaluation/benchmarks');

    await waitFor(() => expect(requestUrls.length).toBeGreaterThan(0));

    const url = new URL(requestUrls.at(-1)!);
    const keys = Array.from(url.searchParams.keys());
    expect(keys.some((k) => k.startsWith('filter['))).toBe(false);
    expect(keys.some((k) => k === 'search' || k.startsWith('search['))).toBe(false);
  });

  it('sends filter[name][$like] when name search is active', async () => {
    const requestUrls = captureRequests();
    renderDataView('/workspaces/default/evaluation/benchmarks?s=foo');

    await waitFor(() => {
      expect(requestUrls.some((u) => new URL(u).searchParams.has('filter[name][$like]'))).toBe(
        true
      );
    });

    const url = new URL(requestUrls.at(-1)!);
    expect(url.searchParams.get('filter[name][$like]')).toBe('foo');
  });

  it('sends filter[created_at][$gte]/$lte when column filter is active', async () => {
    const requestUrls = captureRequests();
    const gte = '2026-01-01T00:00:00.000Z';
    const lte = '2026-02-01T00:00:00.000Z';
    const filters = encodeURIComponent(
      JSON.stringify([{ id: 'created_at', value: { $gte: gte, $lte: lte } }])
    );
    renderDataView(`/workspaces/default/evaluation/benchmarks?filters=${filters}`);

    await waitFor(() => {
      expect(requestUrls.some((u) => new URL(u).searchParams.has('filter[created_at][$gte]'))).toBe(
        true
      );
    });

    const url = new URL(requestUrls.at(-1)!);
    expect(url.searchParams.get('filter[created_at][$gte]')).toBe(gte);
    expect(url.searchParams.get('filter[created_at][$lte]')).toBe(lte);
  });

  it('never emits a top-level search or search[ key', async () => {
    const requestUrls = captureRequests();
    const filters = encodeURIComponent(
      JSON.stringify([{ id: 'created_at', value: { $gte: '2026-01-01T00:00:00.000Z' } }])
    );
    renderDataView(`/workspaces/default/evaluation/benchmarks?s=foo&filters=${filters}`);

    await waitFor(() => expect(requestUrls.length).toBeGreaterThan(0));

    for (const raw of requestUrls) {
      const params = new URL(raw).searchParams;
      expect(params.has('search')).toBe(false);
      expect(Array.from(params.keys()).some((k) => k.startsWith('search['))).toBe(false);
    }
  });
});
