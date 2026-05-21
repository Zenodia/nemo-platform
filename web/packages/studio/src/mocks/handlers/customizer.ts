// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { PlatformJobStatusResponse } from '@nemo/sdk/generated/platform/schema';
import { CustomizationJobInput, CustomizationJob } from '@nemo/sdk/vendored/customizer/schema';
import { PLATFORM_BASE_URL } from '@studio/constants/environment';
import { http, HttpResponse } from 'msw';

export const customizerHandlers = [
  // Customizer V2 (Platform) — fixtures loaded on first use
  http.get(`${PLATFORM_BASE_URL}/apis/customization/v2/workspaces/:workspace/targets`, async () => {
    const { getAvailableParentModelsResponse } =
      await import('@studio/mocks/customizer/parent-models');
    return HttpResponse.json(getAvailableParentModelsResponse);
  }),
  http.get(`${PLATFORM_BASE_URL}/apis/customization/v2/workspaces/:workspace/jobs`, async () => {
    const { getCustomizationJobsListResponse } =
      await import('@studio/mocks/customizer/customization-jobs');
    return HttpResponse.json(getCustomizationJobsListResponse);
  }),
  http.post<never, CustomizationJobInput, CustomizationJob>(
    `${PLATFORM_BASE_URL}/apis/customization/v2/workspaces/:workspace/jobs`,
    async () => {
      const { customizationJob1 } = await import('@studio/mocks/customizer/customization-jobs');
      return HttpResponse.json(customizationJob1);
    }
  ),
  http.options(
    `${PLATFORM_BASE_URL}/apis/customization/v2/workspaces/:workspace/jobs/:name`,
    () => new HttpResponse(null, { status: 200 })
  ),
  http.get<never, never, CustomizationJob>(
    `${PLATFORM_BASE_URL}/apis/customization/v2/workspaces/:workspace/jobs/:name`,
    async () => {
      const { customizationJob1 } = await import('@studio/mocks/customizer/customization-jobs');
      return HttpResponse.json(customizationJob1);
    }
  ),
  http.get<never, never, PlatformJobStatusResponse>(
    `${PLATFORM_BASE_URL}/apis/customization/v2/workspaces/:workspace/jobs/:name/status`,
    async () => {
      const { customizationJob1 } = await import('@studio/mocks/customizer/customization-jobs');
      return HttpResponse.json({
        id: customizationJob1.id,
        name: customizationJob1.name,
        status: customizationJob1.status,
        status_details: customizationJob1.status_details,
      } as PlatformJobStatusResponse);
    }
  ),
  http.post<never, never, CustomizationJob>(
    `${PLATFORM_BASE_URL}/apis/customization/v2/workspaces/:workspace/jobs/:name/cancel`,
    async () => {
      const { customizationJob1 } = await import('@studio/mocks/customizer/customization-jobs');
      return HttpResponse.json(customizationJob1);
    }
  ),
  http.get(`${PLATFORM_BASE_URL}/apis/customization/v2/workspaces/:workspace/targets`, async () => {
    const { getAvailableParentModelsResponse } =
      await import('@studio/mocks/customizer/parent-models');
    return HttpResponse.json(getAvailableParentModelsResponse);
  }),
];
