// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { ExportJobsPage } from '@nemo/sdk/generated/platform/schema';
import { ExportJobsDataView } from '@studio/components/dataViews/ExportJobsDataView';
import { ROUTES } from '@studio/constants/routes';
import { exportJob1, exportJob2 } from '@studio/mocks/intake/exportJobs';
import { server } from '@studio/mocks/node';
import { renderRoute } from '@studio/tests/util/render';
import { screen, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { http, HttpResponse } from 'msw';

vi.mock('use-debounce', () => ({
  useDebounce: (value: unknown) => [value, { cancel: () => {}, flush: () => {} }],
}));

const EXPORT_JOBS_URL = '*/apis/intake/v2/workspaces/:workspace/export/jobs';

const renderComponent = (initialEntry: string = '/workspaces/default/intake/export-jobs') => {
  return renderRoute(undefined, {
    history: initialEntry,
    routes: [
      {
        path: ROUTES.workspace.intakeExportJobs,
        element: <ExportJobsDataView />,
      },
    ],
  });
};

describe('ExportJobsDataView', () => {
  describe('Data Display', () => {
    it('displays export jobs in the table', async () => {
      renderComponent();

      await waitFor(() => {
        expect(screen.getByText(exportJob1.id)).toBeInTheDocument();
      });

      expect(screen.getByText(exportJob2.id)).toBeInTheDocument();
    });

    it('displays destination URLs', async () => {
      renderComponent();

      await waitFor(() => {
        expect(screen.getByText(exportJob1.output_file_url!)).toBeInTheDocument();
      });
    });

    it('displays results count', async () => {
      renderComponent();

      await waitFor(() => {
        expect(screen.getByText('1-2 of 2 items')).toBeInTheDocument();
      });
    });
  });

  describe('Empty State', () => {
    it('displays empty state when no jobs exist', async () => {
      const emptyPage: ExportJobsPage = {
        data: [],
        pagination: {
          page: 1,
          page_size: 50,
          current_page_size: 0,
          total_pages: 0,
          total_results: 0,
        },
      };

      server.use(
        http.get(EXPORT_JOBS_URL, () => {
          return HttpResponse.json(emptyPage);
        })
      );

      renderComponent();

      await waitFor(() => {
        expect(screen.getByText('No Export Jobs')).toBeInTheDocument();
      });
    });
  });

  describe('Filter Panel', () => {
    it('displays filter options in the panel', async () => {
      const user = userEvent.setup();
      renderComponent();

      const filterButton = await screen.findByTestId('open-filters-button');
      await user.click(filterButton);

      const filterPanel = screen.getByTestId('studio-dataview-filter-panel');
      expect(within(filterPanel).getByText('Status')).toBeInTheDocument();
      expect(within(filterPanel).getByText('Created At')).toBeInTheDocument();
    });
  });

  describe('Job ID Click', () => {
    it('job ID opens side panel', async () => {
      const user = userEvent.setup();
      renderComponent();

      const jobIdLink = await screen.findByText(exportJob1.id);
      await user.click(jobIdLink);

      await waitFor(() => {
        expect(screen.getByText('Export Job Details')).toBeInTheDocument();
      });
    });
  });

  describe('Side Panel', () => {
    it('does not show side panel initially', () => {
      renderComponent();
      const filterPanel = screen.getByTestId('studio-dataview-filter-panel-container');
      expect(filterPanel).toBeInTheDocument();
      expect(filterPanel).toHaveClass('w-0', 'opacity-0');
    });
  });

  describe('filter query params', () => {
    const emptyPage: ExportJobsPage = {
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
        http.get(EXPORT_JOBS_URL, ({ request }) => {
          requestUrls.push(request.url);
          return HttpResponse.json(emptyPage);
        })
      );
      return requestUrls;
    };

    it('sends filter[id] (exact match) when id search is active', async () => {
      const requestUrls = captureRequests();
      renderComponent('/workspaces/default/intake/export-jobs?s=abc123');

      await waitFor(() => {
        expect(requestUrls.some((u) => new URL(u).searchParams.has('filter[id]'))).toBe(true);
      });

      const url = new URL(requestUrls.at(-1)!);
      expect(url.searchParams.get('filter[id]')).toBe('abc123');
      // Exact match — must NOT be wrapped in $like
      expect(url.searchParams.has('filter[id][$like]')).toBe(false);
    });

    it('never emits a top-level search or search[ key', async () => {
      const requestUrls = captureRequests();
      renderComponent('/workspaces/default/intake/export-jobs?s=abc123');

      await waitFor(() => expect(requestUrls.length).toBeGreaterThan(0));

      for (const raw of requestUrls) {
        const params = new URL(raw).searchParams;
        expect(params.has('search')).toBe(false);
        expect(Array.from(params.keys()).some((k) => k.startsWith('search['))).toBe(false);
      }
    });
  });
});
