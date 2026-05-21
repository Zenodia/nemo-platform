// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { EntryBulkDeleteModal } from '@studio/components/IntakeEntriesTable/EntryBulkDeleteModal';
import { render } from '@studio/tests/util/render';
import { screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

// Mock brand assets icons
vi.mock('lucide-react', () => ({
  Trash: () => <span data-testid="trash-icon" />,
}));

const mockEntry = {
  id: 'entry-123',
  name: 'test-entry',
  workspace: 'default',
  data: {
    request: {
      messages: [{ role: 'user' as const, content: 'Hello' }],
      model: 'test-model',
    },
    response: {
      choices: [{ message: { role: 'assistant' as const, content: 'Hi!' } }],
    },
  },
  context: {
    app: 'default/test-app',
    task: 'test-task',
  },
  events: [],
};

describe('EntryBulkDeleteModal', () => {
  const user = userEvent.setup();

  it('renders the trigger button', () => {
    render(
      <EntryBulkDeleteModal
        workspace="default"
        selectedEntries={[mockEntry]}
        onConfirmSuccess={vi.fn()}
      />
    );

    expect(screen.getByTestId('bulk-delete-modal-trigger-button')).toBeInTheDocument();
    expect(screen.getByText('Delete')).toBeInTheDocument();
  });

  it('opens modal when trigger button is clicked', async () => {
    render(
      <EntryBulkDeleteModal
        workspace="default"
        selectedEntries={[mockEntry]}
        onConfirmSuccess={vi.fn()}
      />
    );

    const triggerButton = screen.getByTestId('bulk-delete-modal-trigger-button');
    await user.click(triggerButton);

    // Check modal content is visible
    expect(await screen.findByText(/Delete.*Entry/)).toBeInTheDocument();
    expect(screen.getByText(/Are you sure you want to delete/)).toBeInTheDocument();
  });

  it('shows correct singular form for single entry', async () => {
    render(
      <EntryBulkDeleteModal
        workspace="default"
        selectedEntries={[mockEntry]}
        onConfirmSuccess={vi.fn()}
      />
    );

    const triggerButton = screen.getByTestId('bulk-delete-modal-trigger-button');
    await user.click(triggerButton);

    // Should show "1 entry" in singular form
    expect(await screen.findByText(/1 entry/)).toBeInTheDocument();
  });

  it('shows correct plural form for multiple entries', async () => {
    const entries = [
      mockEntry,
      { ...mockEntry, id: 'entry-456' },
      { ...mockEntry, id: 'entry-789' },
    ];
    render(
      <EntryBulkDeleteModal
        workspace="default"
        selectedEntries={entries}
        onConfirmSuccess={vi.fn()}
      />
    );

    const triggerButton = screen.getByTestId('bulk-delete-modal-trigger-button');
    await user.click(triggerButton);

    // Should show "3 entries" in plural form
    expect(await screen.findByText(/3 entries/)).toBeInTheDocument();
  });

  it('closes modal when cancel button is clicked', async () => {
    render(
      <EntryBulkDeleteModal
        workspace="default"
        selectedEntries={[mockEntry]}
        onConfirmSuccess={vi.fn()}
      />
    );

    const triggerButton = screen.getByTestId('bulk-delete-modal-trigger-button');
    await user.click(triggerButton);

    // Modal should be open
    expect(await screen.findByText(/Delete.*Entry/)).toBeInTheDocument();

    // Click cancel button
    const cancelButton = screen.getByRole('button', { name: 'Cancel' });
    await user.click(cancelButton);

    // Modal should be closed (heading should not be visible)
    // Note: The modal might still be in DOM but hidden
    expect(screen.queryByText(/Are you sure you want to delete/)).not.toBeInTheDocument();
  });
});
