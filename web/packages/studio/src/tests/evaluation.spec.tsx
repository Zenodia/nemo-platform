// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { PLATFORM_BASE_URL } from '@studio/constants/environment';
import { ROUTE_PARAMS, ROUTES } from '@studio/constants/routes';
import { datasets } from '@studio/mocks/datasets';
import { workspace1 } from '@studio/mocks/entity-store/projects';
import { server } from '@studio/mocks/node';
import { EvaluationMetricCreateRoute } from '@studio/routes/evaluation/EvaluationMetricCreateRoute';
import { getNewEvaluationMetricRoute } from '@studio/routes/utils';
import { mockUseParams } from '@studio/tests/util/mockUseParams';
import { TestProviders } from '@studio/tests/util/TestProviders';
import { render, screen } from '@testing-library/react';
import { http, HttpResponse } from 'msw';
import { createMemoryRouter, RouterProvider } from 'react-router-dom';

const project = workspace1;

/**
 * Helper function to navigate to the launch evaluation job page
 * @param queryParams - Optional query parameters
 */
async function navigateToLaunchEvaluationForm(queryParams?: Record<string, string>) {
  let history = getNewEvaluationMetricRoute(workspace1.workspace);
  if (queryParams) {
    const searchParams = new URLSearchParams(queryParams);
    history = `${history}?${searchParams.toString()}`;
  }
  const routes = [
    {
      path: ROUTES.workspace.evaluationMetricNew,
      element: <EvaluationMetricCreateRoute />,
    },
  ];

  const router = createMemoryRouter(routes, {
    initialEntries: [history],
  });

  render(
    <TestProviders>
      <RouterProvider router={router} />
    </TestProviders>
  );

  // Wait for the page to load - the Metric component renders "New Evaluation Metric"
  await screen.findByText('New Evaluation Metric');
}

describe('Evaluation:', () => {
  beforeEach(() => {
    vi.clearAllMocks();

    mockUseParams({
      [ROUTE_PARAMS.workspace]: project.name,
    });

    server.use(
      http.get(`${PLATFORM_BASE_URL}/v1/datasets`, () => {
        return HttpResponse.json(datasets);
      })
    );
  });

  describe('Launch New Evaluation Job', () => {
    it('should render the job creation form', async () => {
      await navigateToLaunchEvaluationForm();

      // Verify basic form elements are present
      expect(screen.getByText('Metric Type')).toBeInTheDocument();
      expect(screen.getByText('Score Definitions')).toBeInTheDocument();
    });
  });
});
