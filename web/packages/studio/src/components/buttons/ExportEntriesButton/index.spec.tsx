// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { ExportEntriesButton } from '@studio/components/buttons/ExportEntriesButton';
import { ROUTE_PARAMS } from '@studio/constants/routes';
import { workspace1 } from '@studio/mocks/entity-store/projects';
import { server } from '@studio/mocks/node';
import { mockUseParams } from '@studio/tests/util/mockUseParams';
import { render } from '@studio/tests/util/render';
import { screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { http, HttpResponse } from 'msw';

// Mock brand assets icons
vi.mock('lucide-react', () => ({
  Database: () => <span data-testid="db-icon" />,
  Trash: () => <span data-testid="trash-icon" />,
  Filter: () => <span data-testid="filter-icon" />,
}));

const EXPORT_JOBS_URL = '*/apis/intake/v2/workspaces/:workspace/export/jobs';

describe('ExportEntriesButton', () => {
  const user = userEvent.setup();
  beforeEach(() => {
    mockUseParams({
      [ROUTE_PARAMS.workspace]: workspace1.workspace,
    });
  });

  it('renders the export entries button', () => {
    render(<ExportEntriesButton />);

    const button = screen.getByRole('button', { name: /export entries/i });
    expect(button).toBeInTheDocument();
  });

  it('opens the modal when clicking the button', async () => {
    render(<ExportEntriesButton />);

    const button = screen.getByRole('button', { name: /export entries/i });
    await user.click(button);

    expect(await screen.findByText('Export Entries to Dataset')).toBeInTheDocument();
  });

  it('displays the form modal with correct title and submit button', async () => {
    render(<ExportEntriesButton />);

    await user.click(screen.getByRole('button', { name: /export entries/i }));

    expect(await screen.findByText('Export Entries to Dataset')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /confirm/i })).toBeInTheDocument();
  });

  it('closes the modal when clicking the close button', async () => {
    render(<ExportEntriesButton />);

    // Open modal
    await user.click(screen.getByRole('button', { name: /export entries/i }));
    expect(await screen.findByText('Export Entries to Dataset')).toBeInTheDocument();

    // Close modal via X button (typically has name "Close")
    const closeButton = screen.getByRole('button', { name: /close/i });
    await user.click(closeButton);

    await waitFor(() => {
      expect(screen.queryByText('Export Entries to Dataset')).not.toBeInTheDocument();
    });
  });

  it('shows error toast when export job creation fails', async () => {
    // Suppress expected console.error from the component's catch block
    const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

    server.use(
      http.post(EXPORT_JOBS_URL, () => HttpResponse.json({ error: 'Forbidden' }, { status: 403 }))
    );
    render(<ExportEntriesButton />);

    // Open modal
    await user.click(screen.getByRole('button', { name: /export entries/i }));
    expect(await screen.findByText('Export Entries to Dataset')).toBeInTheDocument();

    // Set dataset
    await user.click(screen.getByRole('combobox', { name: 'Dataset Destination' }));
    await user.click(screen.getAllByRole('option')[0]);

    // Submit form
    const confirmButton = screen.getByRole('button', { name: /confirm/i });
    await user.click(confirmButton);

    await waitFor(() => {
      expect(
        screen.getByText('Failed to create export job. Please try again.')
      ).toBeInTheDocument();
    });

    consoleSpy.mockRestore();
  });

  it('closes modal and resets form on successful submission', async () => {
    render(<ExportEntriesButton />);

    // Open modal
    await user.click(screen.getByRole('button', { name: /export entries/i }));
    expect(await screen.findByText('Export Entries to Dataset')).toBeInTheDocument();

    // Set dataset
    await user.click(screen.getByRole('combobox', { name: 'Dataset Destination' }));
    await user.click(screen.getAllByRole('option')[0]);

    // Submit form
    const confirmButton = screen.getByRole('button', { name: /confirm/i });
    await user.click(confirmButton);

    await waitFor(() => {
      expect(screen.getByText('Export job created successfully!')).toBeInTheDocument();
    });

    expect(screen.queryByText('Export Entries to Dataset')).not.toBeInTheDocument();
  });
});
