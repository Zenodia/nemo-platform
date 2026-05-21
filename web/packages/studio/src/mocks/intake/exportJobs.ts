// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import type { ExportJob, ExportJobsPage } from '@nemo/sdk/generated/platform/schema';

export const exportJob1 = {
  schema_version: '1.0',
  id: 'int-exp-U6XfM8gYmxV2tiFnwpADv6',
  type_prefix: 'int-exp',
  namespace: 'default',
  project: 'default/sean-test',
  created_at: '2025-12-16T22:25:16.760901',
  updated_at: '2025-12-16T22:25:16.760904',
  custom_fields: {},
  status: 'completed' as const,
  status_details: {
    entries_count: 100,
  },
  config: {
    filters: {
      namespace: 'default',
    },
    limit: 100,
    format_options: {
      row_transformation: true,
    },
  },
  output_file_url: 'hf://datasets/default/dataset-sean-test/export-entitled-herring.jsonl',
} as unknown as ExportJob;

export const exportJob2 = {
  ...exportJob1,
  id: 'int-exp-SecondJob123',
  status: 'pending' as const,
  output_file_url: 'hf://datasets/default/dataset-test/export-second.jsonl',
  created_at: '2025-12-15T10:00:00.000000',
} as unknown as ExportJob;

export const mockExportJobsPage = {
  data: [exportJob1, exportJob2],
  pagination: {
    page: 1,
    page_size: 50,
    current_page_size: 2,
    total_pages: 1,
    total_results: 2,
  },
} as ExportJobsPage;
