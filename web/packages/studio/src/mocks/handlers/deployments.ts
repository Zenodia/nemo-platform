// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { PLATFORM_BASE_URL } from '@studio/constants/environment';
import { http, HttpResponse } from 'msw';

/**
 * Mock handlers for inference deployment endpoints
 */
export const deploymentsHandlers = [
  // List deployments — fixtures loaded on first use
  http.get(`${PLATFORM_BASE_URL}/apis/models/v2/workspaces/:workspace/deployments`, async () => {
    const { getModelDeploymentsListResponse } =
      await import('@studio/mocks/deployment-management/constants');
    return HttpResponse.json(getModelDeploymentsListResponse);
  }),

  // OPTIONS preflight request for CORS
  http.options(`${PLATFORM_BASE_URL}/apis/models/v2/workspaces/:workspace/deployments`, () => {
    return new HttpResponse(null, { status: 204 });
  }),
];
