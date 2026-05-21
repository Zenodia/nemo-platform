// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { ROUTE_PARAMS } from '@studio/constants/routes';
import { workspace1 } from '@studio/mocks/entity-store/projects';
import {
  mockEvalConfigOnline1,
  mockEvalConfigOffline1,
} from '@studio/mocks/evaluation/v1/evaluations';
import { server } from '@studio/mocks/node';
import { EvaluationMetricsRoute } from '@studio/routes/evaluation/EvaluationMetricsRoute';
import { mockUseNavigate, mockUseParams } from '@studio/tests/util/mockUseParams';
import { TestProviders } from '@studio/tests/util/TestProviders';
import { render, screen } from '@testing-library/react';
import { http, HttpResponse } from 'msw';
import { BrowserRouter } from 'react-router-dom';

vi.mock('@nemo/common/src/components/DataView/StudioDataView', async () => {
  const { studioDataViewMock } = await import('@studio/tests/util');
  return studioDataViewMock();
});

describe('EvaluationMetricsRoute', () => {
  beforeEach(() => {
    mockUseNavigate();
    mockUseParams({
      [ROUTE_PARAMS.workspace]: workspace1.name,
    });
  });

  const renderRoute = () => {
    return render(
      <TestProviders>
        <BrowserRouter>
          <EvaluationMetricsRoute />
        </BrowserRouter>
      </TestProviders>
    );
  };

  describe('Rendering', () => {
    it('should render the metrics table with headers', async () => {
      renderRoute();

      expect(await screen.findByText('Name')).toBeInTheDocument();
      expect(screen.getByText('Type')).toBeInTheDocument();
      expect(screen.getByRole('columnheader', { name: /Created/ })).toBeInTheDocument();
    });

    it('should render metrics data', async () => {
      renderRoute();

      expect(await screen.findByText(mockEvalConfigOnline1.name)).toBeInTheDocument();
      expect(screen.getByText(mockEvalConfigOffline1.name)).toBeInTheDocument();
    });
  });

  describe('Navigation', () => {
    it('should provide launch evaluation button in empty state', async () => {
      server.use(
        http.get('*/apis/evaluation/v2/workspaces/:workspace/metrics', () => {
          return HttpResponse.json({
            data: [],
            pagination: { total_results: 0, total_pages: 0, page: 1, page_size: 10 },
          });
        })
      );

      renderRoute();

      expect(await screen.findByText('New Metric')).toBeInTheDocument();
    });
  });

  describe('Error Handling', () => {
    it('should render error message when API call fails', async () => {
      server.use(
        http.get('*/apis/evaluation/v2/workspaces/:workspace/metrics', () => {
          return HttpResponse.json({ error: 'API Error' }, { status: 500 });
        })
      );

      renderRoute();

      expect(await screen.findByText('Failed to fetch metrics')).toBeInTheDocument();
      expect(screen.getByText('Retry')).toBeInTheDocument();
    });
  });

  describe('Empty States', () => {
    it('should render empty state when no metrics exist', async () => {
      server.use(
        http.get('*/apis/evaluation/v2/workspaces/:workspace/metrics', () => {
          return HttpResponse.json({
            data: [],
            pagination: { total_results: 0, total_pages: 0, page: 1, page_size: 10 },
          });
        })
      );

      renderRoute();
      expect(await screen.findByText('No Metrics')).toBeInTheDocument();
      expect(
        screen.getByText('Create a metric to start evaluating model outputs.')
      ).toBeInTheDocument();
    });
  });

  describe('Sorting', () => {
    it('should render sortable Created column header', async () => {
      renderRoute();

      await screen.findByText(mockEvalConfigOnline1.name);

      const createdHeader = screen.getByRole('columnheader', { name: /Created/ });
      expect(createdHeader).toBeInTheDocument();
    });
  });
});
