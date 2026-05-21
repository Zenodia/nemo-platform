// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { Entry } from '@nemo/sdk/generated/platform/schema';
import { IntakeEntryConversation } from '@studio/components/IntakeEntryConversation/index';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

const createMockEntry = (overrides: Partial<Entry> = {}): Entry =>
  ({
    id: 'test-entry-id',
    data: {
      request: {
        messages: [
          { role: 'system', content: 'You are a helpful assistant.' },
          { role: 'user', content: 'What is the capital of France?' },
        ],
        model: 'test-model',
      },
      response: {
        choices: [
          {
            message: {
              role: 'assistant',
              content: 'The capital of France is Paris.',
            },
            index: 0,
            finish_reason: 'stop',
          },
        ],
      },
    },
    context: {
      app: 'test-app',
      task: 'test-task',
    },
    ...overrides,
  }) as Entry;

describe('IntakeEntryConversation', () => {
  it('renders conversation with user and assistant messages', () => {
    const entry = createMockEntry();
    render(<IntakeEntryConversation entry={entry} />);

    expect(screen.getByText('Conversation')).toBeInTheDocument();
    expect(screen.getByText('What is the capital of France?')).toBeInTheDocument();
    expect(screen.getByText('The capital of France is Paris.')).toBeInTheDocument();
  });

  it('shows warning banner when no messages exist', () => {
    const entry = createMockEntry({
      data: {
        request: { messages: [], model: 'test' },
        response: { choices: [] },
      },
    });
    render(<IntakeEntryConversation entry={entry} />);

    expect(screen.getByText('Chat History Unavailable')).toBeInTheDocument();
  });

  it('toggles to JSON view when clicking JSON button', async () => {
    const user = userEvent.setup();
    const entry = createMockEntry();
    render(<IntakeEntryConversation entry={entry} />);

    const jsonButton = screen.getByRole('radio', { name: /json/i });
    await user.click(jsonButton);

    expect(screen.getByTestId('nv-code-snippet-root')).toBeInTheDocument();
  });
});
