// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { ToastProvider } from '@nemo/common/src/providers/toast/ToastProvider';
import type { EntrysPage } from '@nemo/sdk/generated/platform/schema';
import type { Meta, StoryObj } from '@storybook/react';
import { IntakeEntriesTable } from '@studio/components/IntakeEntriesTable';
import { entriesPage1 } from '@studio/mocks/intake/entries';
import { http, HttpResponse } from 'msw';

const ENTRIES_API = '/apis/intake/v2/workspaces/default/entries';

const meta = {
  component: IntakeEntriesTable,
  title: 'DataViews/IntakeEntriesTable',
  decorators: [
    (Story) => (
      <ToastProvider>
        <Story />
      </ToastProvider>
    ),
  ],
  args: {
    workspace: 'default',
    enableSelection: true,
    enableActions: true,
    attributes: { Stack: { className: 'h-[600px]' } },
  },
} satisfies Meta<typeof IntakeEntriesTable>;

export default meta;
type Story = StoryObj<typeof meta>;

const emptyEntriesPage: EntrysPage = {
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
        http.get<never, never, EntrysPage>(ENTRIES_API, () => HttpResponse.json(emptyEntriesPage)),
      ],
    },
  },
};

export const WithData: Story = {
  parameters: {
    msw: {
      handlers: [
        http.get<never, never, EntrysPage>(ENTRIES_API, () =>
          HttpResponse.json(entriesPage1 as unknown as EntrysPage)
        ),
      ],
    },
  },
};
