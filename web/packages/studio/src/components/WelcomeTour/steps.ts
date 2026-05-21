// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { ROUTES } from '@studio/constants/routes';
import type { TourStep } from 'modern-tour';

/**
 * Welcome tour step definitions for modern-tour.
 *
 * Each step targets an element via a `data-tour` attribute selector.
 * To add a new anchor, add `data-tour="<name>"` to the target JSX element
 * and reference it here as `target: '[data-tour="<name>"]'`.
 */

export interface TourRouteSteps {
  route: string;
  steps: TourStep[];
}

export const steps: TourRouteSteps[] = [
  {
    route: ROUTES.workspace.dashboard,
    steps: [
      {
        target: '[data-tour="dashboard-get-started"]',
        title: 'Welcome to NeMo Studio',
        content: 'Accelerate AI development with NVIDIA NeMo.',
        position: 'top',
      },
      {
        target: '[data-tour="nav-workspace"]',
        title: 'Workspaces',
        content:
          'Keep projects, resources, and jobs organized in dedicated workspaces. Select or create a workspace to get started.',
        position: 'bottom-start',
      },
      {
        target: '[data-tour="sidebar"]',
        title: 'Manage Tasks',
        content:
          'Track your AI workflow from agent interactions to model evaluation. Monitor job progress and view logs—all in one place.',
        position: 'right-start',
      },
    ],
  },
];
