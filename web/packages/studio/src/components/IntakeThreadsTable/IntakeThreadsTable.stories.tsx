// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import type { Entry, EntrysPage } from '@nemo/sdk/generated/platform/schema';
import type { Meta, StoryObj } from '@storybook/react';
import { IntakeThreadsTable } from '@studio/components/IntakeThreadsTable';
import { http, HttpResponse } from 'msw';

const INTAKE_ENTRIES_API = '/apis/intake/v2/workspaces/default/entries';

const meta = {
  component: IntakeThreadsTable,
  title: 'DataViews/IntakeThreadsTable',
  args: {
    workspace: 'default',
    onRowClick: () => {},
  },
} satisfies Meta<typeof IntakeThreadsTable>;

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

const mockEntriesPage = {
  data: [
    {
      id: 'entry-thread-abc123',
      name: 'entry-thread-abc123',
      workspace: 'default',
      created_at: '2025-12-16T22:40:12.241917Z',
      updated_at: '2025-12-16T22:40:12.241918Z',
      data: {
        request: {
          messages: [
            {
              role: 'user',
              content: 'How do I fine-tune a language model for my specific use case?',
            },
          ],
          model: 'meta/llama-3.3-70b-instruct',
        },
        response: {
          choices: [
            {
              index: 0,
              message: {
                role: 'assistant',
                content:
                  'Fine-tuning a language model involves training it on a domain-specific dataset to improve performance on targeted tasks...',
              },
              finish_reason: 'stop',
            },
          ],
          usage: { prompt_tokens: 120, completion_tokens: 250, total_tokens: 370 },
        },
      },
      context: {
        app: 'studio',
        task: 'qa',
        thread_id: 'thread-abc123',
        user_id: 'user-001',
        created_at: '2025-12-16T22:40:12.241855Z',
      },
      events: [],
    },
    {
      id: 'entry-thread-def456',
      name: 'entry-thread-def456',
      workspace: 'default',
      created_at: '2025-12-15T14:20:00.000000Z',
      updated_at: '2025-12-15T14:20:00.000000Z',
      data: {
        request: {
          messages: [
            {
              role: 'user',
              content: 'What are the best practices for prompt engineering?',
            },
          ],
          model: 'nvidia/nemotron-4-340b-instruct',
        },
        response: {
          choices: [
            {
              index: 0,
              message: {
                role: 'assistant',
                content:
                  'Effective prompt engineering involves being specific, providing context, and iterating on your prompts...',
              },
              finish_reason: 'stop',
            },
          ],
          usage: { prompt_tokens: 80, completion_tokens: 180, total_tokens: 260 },
        },
      },
      context: {
        app: 'studio',
        task: 'research',
        thread_id: 'thread-def456',
        user_id: 'user-002',
        created_at: '2025-12-15T14:20:00.000000Z',
      },
      events: [],
    },
    {
      id: 'entry-thread-ghi789',
      name: 'entry-thread-ghi789',
      workspace: 'default',
      created_at: '2025-12-14T09:00:00.000000Z',
      updated_at: '2025-12-14T09:00:00.000000Z',
      data: {
        request: {
          messages: [
            {
              role: 'user',
              content: 'Explain the difference between RAG and fine-tuning.',
            },
          ],
          model: 'meta/llama-3.1-8b-instruct',
        },
        response: {
          choices: [
            {
              index: 0,
              message: {
                role: 'assistant',
                content:
                  'RAG (Retrieval-Augmented Generation) retrieves relevant documents at inference time, while fine-tuning bakes knowledge into model weights...',
              },
              finish_reason: 'stop',
            },
          ],
          usage: { prompt_tokens: 60, completion_tokens: 150, total_tokens: 210 },
        },
      },
      context: {
        app: 'studio',
        task: 'education',
        thread_id: 'thread-ghi789',
        user_id: 'user-003',
        created_at: '2025-12-14T09:00:00.000000Z',
      },
      events: [],
    },
  ] as Entry[],
  pagination: {
    page: 1,
    page_size: 50,
    current_page_size: 3,
    total_pages: 1,
    total_results: 3,
  },
} satisfies EntrysPage;

export const Empty: Story = {
  parameters: {
    msw: {
      handlers: [
        http.get<never, never, EntrysPage>(INTAKE_ENTRIES_API, () =>
          HttpResponse.json(emptyEntriesPage)
        ),
      ],
    },
  },
};

export const WithData: Story = {
  parameters: {
    msw: {
      handlers: [
        http.get<never, never, EntrysPage>(INTAKE_ENTRIES_API, () =>
          HttpResponse.json(mockEntriesPage)
        ),
      ],
    },
  },
};
