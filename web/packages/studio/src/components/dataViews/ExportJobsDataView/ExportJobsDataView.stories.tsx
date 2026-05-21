// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import type { ExportJobsPage } from '@nemo/sdk/generated/platform/schema';
import type { Meta, StoryObj } from '@storybook/react';
import { ExportJobsDataView } from '@studio/components/dataViews/ExportJobsDataView';
import { mockExportJobsPage } from '@studio/mocks/intake/exportJobs';
import { http, HttpResponse } from 'msw';

const EXPORT_JOBS_API = '/apis/intake/v2/workspaces/default/export/jobs';

const meta = {
  component: ExportJobsDataView,
  title: 'DataViews/ExportJobsDataView',
} satisfies Meta<typeof ExportJobsDataView>;

export default meta;
type Story = StoryObj<typeof meta>;

const emptyExportJobsPage: ExportJobsPage = {
  data: [],
  pagination: {
    page: 1,
    page_size: 50,
    current_page_size: 0,
    total_pages: 0,
    total_results: 0,
  },
};

export const Empty: Story = {
  parameters: {
    msw: {
      handlers: [
        http.get<never, never, ExportJobsPage>(EXPORT_JOBS_API, () =>
          HttpResponse.json(emptyExportJobsPage)
        ),
      ],
    },
  },
};

export const WithData: Story = {
  parameters: {
    msw: {
      handlers: [
        http.get<never, never, ExportJobsPage>(EXPORT_JOBS_API, () =>
          HttpResponse.json(mockExportJobsPage)
        ),
      ],
    },
  },
};
