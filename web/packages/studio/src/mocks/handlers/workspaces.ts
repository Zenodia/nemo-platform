// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { PLATFORM_BASE_URL } from '@studio/constants/environment';
import { http, HttpResponse } from 'msw';

export const workspacesHandlers = [
  http.post(`${PLATFORM_BASE_URL}/apis/entities/v2/workspaces`, async ({ request }) => {
    const { mockWorkspace } = await import('@studio/mocks/workspaces');
    const body = (await request.json()) as { name: string; description?: string };
    return HttpResponse.json({
      id: 'workspace-uuid',
      name: body.name,
      description: body.description,
      created_at: mockWorkspace.created_at,
      updated_at: mockWorkspace.updated_at,
    });
  }),
];
