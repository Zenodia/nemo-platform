// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { EntryBulkExportModal } from '@studio/components/IntakeEntriesTable/EntryBulkExportModal';
import { PLATFORM_BASE_URL } from '@studio/constants/environment';
import { workspace1 } from '@studio/mocks/entity-store/projects';
import { server } from '@studio/mocks/node';
import { mockUseParams } from '@studio/tests/util/mockUseParams';
import { render } from '@studio/tests/util/render';
import { screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { http, HttpResponse } from 'msw';

// Mock brand assets icons using partial mock pattern
vi.mock('lucide-react', async (importOriginal) => {
  const actual = await importOriginal<typeof import('lucide-react')>();
  return {
    ...actual,
    Database: () => <span data-testid="db-icon" />,
  };
});

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

describe('EntryBulkExportModal', () => {
  const user = userEvent.setup();

  beforeEach(() => {
    mockUseParams({
      workspace: workspace1.workspace,
    });
  });

  it('queries filesets with purpose filter set to dataset', async () => {
    const requestUrls: string[] = [];
    server.use(
      http.get(
        `${PLATFORM_BASE_URL}/apis/files/v2/workspaces/:workspace/filesets`,
        ({ request }) => {
          requestUrls.push(request.url);
          return HttpResponse.json({
            data: [],
            pagination: {
              page: 1,
              page_size: 25,
              current_page_size: 0,
              total_pages: 1,
              total_results: 0,
            },
          });
        }
      )
    );

    render(<EntryBulkExportModal selectedEntries={[mockEntry]} onSuccess={vi.fn()} />);

    const triggerButton = screen.getByTestId('entry-bulk-export-modal-trigger');
    await userEvent.click(triggerButton);

    await waitFor(() => {
      expect(requestUrls.length).toBeGreaterThan(0);
    });

    const url = new URL(requestUrls[0]);
    expect(url.searchParams.get('filter[purpose]')).toBe('dataset');
  });

  it('renders the trigger button', () => {
    render(<EntryBulkExportModal selectedEntries={[mockEntry]} onSuccess={vi.fn()} />);

    expect(screen.getByTestId('entry-bulk-export-modal-trigger')).toBeInTheDocument();
    expect(screen.getByText('Export to Dataset')).toBeInTheDocument();
  });

  it('opens modal when trigger button is clicked', async () => {
    render(<EntryBulkExportModal selectedEntries={[mockEntry]} onSuccess={vi.fn()} />);

    const triggerButton = screen.getByTestId('entry-bulk-export-modal-trigger');
    await user.click(triggerButton);

    // Check modal title is visible
    expect(await screen.findByText('Export Records to Dataset')).toBeInTheDocument();

    // Check form fields
    expect(screen.getByText('Destination Dataset')).toBeInTheDocument();
    expect(screen.getByText('Limit')).toBeInTheDocument();
    expect(screen.getByText('Row Transformation')).toBeInTheDocument();
  });

  it('shows correct entry count in info panel', async () => {
    const entries = [mockEntry, { ...mockEntry, id: 'entry-456' }];
    render(<EntryBulkExportModal selectedEntries={entries} onSuccess={vi.fn()} />);

    const triggerButton = screen.getByTestId('entry-bulk-export-modal-trigger');
    await user.click(triggerButton);

    // Check the info panel shows correct count
    expect(await screen.findByText('2 entries will be exported')).toBeInTheDocument();
  });

  it('disables confirm button until dataset is selected', async () => {
    render(<EntryBulkExportModal selectedEntries={[mockEntry]} onSuccess={vi.fn()} />);

    const triggerButton = screen.getByTestId('entry-bulk-export-modal-trigger');
    await user.click(triggerButton);

    // Find the confirm button - it should be disabled initially
    const confirmButton = await screen.findByRole('button', { name: 'Confirm' });
    expect(confirmButton).toBeDisabled();
  });

  it('renders in controlled mode without trigger button', async () => {
    const onClose = vi.fn();
    render(
      <EntryBulkExportModal
        selectedEntries={[mockEntry]}
        onSuccess={vi.fn()}
        showTrigger={false}
        open
        onClose={onClose}
      />
    );

    // Trigger button should not be present
    expect(screen.queryByTestId('entry-bulk-export-modal-trigger')).not.toBeInTheDocument();

    // Modal should be open
    expect(await screen.findByText('Export Records to Dataset')).toBeInTheDocument();
  });
});
