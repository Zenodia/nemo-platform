// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { DEFAULT_WORKSPACE } from '@nemo/common/src/models/constants';
import { ButtonLaunchEvaluation } from '@studio/components/evaluation/ButtonLaunchEvaluation';
import { ROUTE_PARAMS, ROUTES } from '@studio/constants/routes';
import { getEvaluationMetricRunRoute, getEvaluationMetricsRunRoute } from '@studio/routes/utils';
import { LOCATION_DISPLAY_TEST_ID } from '@studio/tests/util/constants';
import { LocationDisplay } from '@studio/tests/util/LocationDisplay';
import { mockUseParams } from '@studio/tests/util/mockUseParams';
import { TestProviders } from '@studio/tests/util/TestProviders';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ComponentProps } from 'react';
import { createMemoryRouter, RouterProvider } from 'react-router-dom';

const renderRoute = ({
  buttonProps,
}: { buttonProps?: ComponentProps<typeof ButtonLaunchEvaluation> } = {}) => {
  const router = createMemoryRouter(
    [
      { path: ROUTES.workspace.index, element: <ButtonLaunchEvaluation {...buttonProps} /> },
      {
        path: getEvaluationMetricRunRoute(DEFAULT_WORKSPACE, 'metric-name'),
        element: <LocationDisplay />,
      },
      { path: getEvaluationMetricsRunRoute(DEFAULT_WORKSPACE), element: <LocationDisplay /> },
    ],
    {
      initialEntries: [ROUTES.workspace.index],
    }
  );
  return render(
    <TestProviders>
      <RouterProvider router={router} />
    </TestProviders>
  );
};

describe('ButtonLaunchEvaluation', () => {
  beforeEach(() => {
    mockUseParams({
      [ROUTE_PARAMS.workspace]: DEFAULT_WORKSPACE,
    });
  });
  it('should render the button with correct text', async () => {
    renderRoute();

    expect(await screen.findByText('Launch Evaluation')).toBeInTheDocument();
    expect(screen.getByRole('button')).toBeInTheDocument();
  });

  it('should navigate to correct evaluation launch route when clicked', async () => {
    const user = userEvent.setup();
    const metricRef = 'metric-name';
    renderRoute({ buttonProps: { metricRef } });

    const launchButton = await screen.findByText('Launch Evaluation');
    await user.click(launchButton);

    // Verify we navigated to the correct URL
    const locationElement = await screen.findByTestId(LOCATION_DISPLAY_TEST_ID);
    expect(locationElement).toHaveTextContent(
      getEvaluationMetricRunRoute(DEFAULT_WORKSPACE, metricRef)
    );
  });

  it('should navigate to the generic launch route with model deep linking', async () => {
    const user = userEvent.setup();
    const modelRef = `${DEFAULT_WORKSPACE}/model-name`;
    renderRoute({ buttonProps: { modelRef } });

    const launchButton = await screen.findByText('Launch Evaluation');
    await user.click(launchButton);

    const locationElement = await screen.findByTestId(LOCATION_DISPLAY_TEST_ID);
    expect(locationElement).toHaveTextContent(
      getEvaluationMetricsRunRoute(DEFAULT_WORKSPACE, { model: modelRef })
    );
  });

  it('should navigate to the metric launch route with model deep linking', async () => {
    const user = userEvent.setup();
    const metricRef = 'metric-name';
    const modelRef = `${DEFAULT_WORKSPACE}/model-name`;
    renderRoute({ buttonProps: { metricRef, modelRef } });

    const launchButton = await screen.findByText('Launch Evaluation');
    await user.click(launchButton);

    const locationElement = await screen.findByTestId(LOCATION_DISPLAY_TEST_ID);
    expect(locationElement).toHaveTextContent(
      getEvaluationMetricRunRoute(DEFAULT_WORKSPACE, metricRef, { model: modelRef })
    );
  });

  it('should pass through additional props', async () => {
    renderRoute({ buttonProps: { disabled: true } });

    const button = await screen.findByRole('button');
    expect(button).toBeDisabled();
  });

  it('should navigate to the correct evaluation launch route when metricRef is not provided', async () => {
    const user = userEvent.setup();
    renderRoute();

    const launchButton = await screen.findByText('Launch Evaluation');
    await user.click(launchButton);

    const locationElement = await screen.findByTestId(LOCATION_DISPLAY_TEST_ID);
    expect(locationElement).toHaveTextContent(getEvaluationMetricsRunRoute(DEFAULT_WORKSPACE));
  });
});
