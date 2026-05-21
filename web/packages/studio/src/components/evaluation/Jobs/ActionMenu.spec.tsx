// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { MetricEvaluationJob, PlatformJobStatus } from '@nemo/sdk/generated/platform/schema';
import { ActionMenu } from '@studio/components/evaluation/Jobs/ActionMenu';
import { ROUTE_PARAMS } from '@studio/constants/routes';
import { mockUseParams } from '@studio/tests/util/mockUseParams';
import { customRender as render, screen } from '@studio/tests/util/render';
import userEvent from '@testing-library/user-event';

const TEST_WORKSPACE = 'test-workspace';

// Mock the delete APIs
const mockDeleteMetricJob = vi.fn();
const mockDeleteBenchmarkJob = vi.fn();
vi.mock('@nemo/sdk/generated/platform/api', async (importOriginal) => {
  const original = await importOriginal();
  return {
    // @ts-expect-error expect issue here with spread
    ...original,
    useEvaluationDeleteMetricJob: vi.fn(() => ({
      mutateAsync: mockDeleteMetricJob,
    })),
    useEvaluationDeleteBenchmarkJob: vi.fn(() => ({
      mutateAsync: mockDeleteBenchmarkJob,
    })),
  };
});

describe('ActionMenu', () => {
  const mockJob: MetricEvaluationJob = {
    id: 'test-job-1',
    name: 'test-job-1',
    status: PlatformJobStatus.completed,
    created_at: '2024-01-01T00:00:00Z',
    spec: {
      metric: 'test-namespace/test-metric',
      dataset: 'default/test-dataset',
      params: {
        ignore_request_failure: false,
        parallelism: 8,
      },
    },
  };

  const mockOnNavigateToDetails = vi.fn();

  const mockOnJobDeleted = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    mockDeleteMetricJob.mockResolvedValue(undefined);
    mockUseParams({
      [ROUTE_PARAMS.workspace]: TEST_WORKSPACE,
    });
  });

  describe('Rendering', () => {
    it('should render action menu button', () => {
      render(
        <ActionMenu
          job={mockJob}
          onNavigateToDetails={mockOnNavigateToDetails}
          onJobDeleted={mockOnJobDeleted}
        />
      );

      expect(
        screen.getByRole('button', { name: /Open evaluation job actions menu/ })
      ).toBeInTheDocument();
    });

    it('should show dropdown menu when trigger is clicked', async () => {
      const user = userEvent.setup();
      render(
        <ActionMenu
          job={mockJob}
          onNavigateToDetails={mockOnNavigateToDetails}
          onJobDeleted={mockOnJobDeleted}
        />
      );

      const triggerButton = screen.getByRole('button', {
        name: /Open evaluation job actions menu/,
      });
      await user.click(triggerButton);

      expect(screen.getByText('View Details')).toBeInTheDocument();
      expect(screen.getByText('Delete')).toBeInTheDocument();
    });
  });

  describe('Navigation Actions', () => {
    it('should call onNavigateToDetails when View Details is clicked', async () => {
      const user = userEvent.setup();
      render(
        <ActionMenu
          job={mockJob}
          onNavigateToDetails={mockOnNavigateToDetails}
          onJobDeleted={mockOnJobDeleted}
        />
      );

      const triggerButton = screen.getByRole('button', {
        name: /Open evaluation job actions menu/,
      });
      await user.click(triggerButton);

      const viewDetailsButton = screen.getByText('View Details');
      await user.click(viewDetailsButton);

      expect(mockOnNavigateToDetails).toHaveBeenCalledWith(mockJob);
    });
  });

  describe('Delete Action', () => {
    it('should show delete confirmation modal when Delete is clicked', async () => {
      const user = userEvent.setup();
      render(
        <ActionMenu
          job={mockJob}
          onNavigateToDetails={mockOnNavigateToDetails}
          onJobDeleted={mockOnJobDeleted}
        />
      );

      const triggerButton = screen.getByRole('button', {
        name: /Open evaluation job actions menu/,
      });
      await user.click(triggerButton);

      const deleteButton = screen.getByText('Delete');
      await user.click(deleteButton);

      expect(await screen.findByText('Delete Evaluation Job')).toBeInTheDocument();
      expect(
        screen.getByText((content, element) => {
          return (
            content.includes('Are you sure you want to delete evaluation job') &&
            (element?.textContent?.includes('test-job-1') ?? false)
          );
        })
      ).toBeInTheDocument();
      expect(screen.getByText('This action cannot be undone.')).toBeInTheDocument();
    });

    it('should call delete API and onJobDeleted when confirmed', async () => {
      const user = userEvent.setup();

      render(
        <ActionMenu
          job={mockJob}
          onNavigateToDetails={mockOnNavigateToDetails}
          onJobDeleted={mockOnJobDeleted}
        />
      );

      // Open menu and click delete
      const triggerButton = screen.getByRole('button', {
        name: /Open evaluation job actions menu/,
      });
      await user.click(triggerButton);

      const deleteButton = screen.getByText('Delete');
      await user.click(deleteButton);

      // Confirm deletion
      const confirmButton = await screen.findByRole('button', { name: 'Delete' });
      await user.click(confirmButton);

      expect(mockDeleteMetricJob).toHaveBeenCalledWith({
        workspace: TEST_WORKSPACE,
        name: 'test-job-1',
      });
      expect(mockOnJobDeleted).toHaveBeenCalledWith(mockJob);
    });

    it('should close modal when cancel is clicked', async () => {
      const user = userEvent.setup();
      render(
        <ActionMenu
          job={mockJob}
          onNavigateToDetails={mockOnNavigateToDetails}
          onJobDeleted={mockOnJobDeleted}
        />
      );

      // Open menu and click delete
      const triggerButton = screen.getByRole('button', {
        name: /Open evaluation job actions menu/,
      });
      await user.click(triggerButton);

      const deleteButton = screen.getByText('Delete');
      await user.click(deleteButton);

      // Click cancel
      const cancelButton = await screen.findByRole('button', { name: 'Cancel' });
      await user.click(cancelButton);

      expect(screen.queryByText('Delete Evaluation Job')).not.toBeInTheDocument();
    });

    it('should handle delete API errors gracefully', async () => {
      const user = userEvent.setup();
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
      mockDeleteMetricJob.mockRejectedValue(new Error('Delete failed'));

      render(
        <ActionMenu
          job={mockJob}
          onNavigateToDetails={mockOnNavigateToDetails}
          onJobDeleted={mockOnJobDeleted}
        />
      );

      // Open menu and click delete
      const triggerButton = screen.getByRole('button', {
        name: /Open evaluation job actions menu/,
      });
      await user.click(triggerButton);

      const deleteButton = screen.getByText('Delete');
      await user.click(deleteButton);

      // Confirm deletion
      const confirmButton = await screen.findByRole('button', { name: 'Delete' });
      await user.click(confirmButton);

      expect(consoleSpy).toHaveBeenCalledWith(
        'Failed to delete evaluation job:',
        expect.any(Error)
      );
      expect(mockOnJobDeleted).not.toHaveBeenCalled();

      consoleSpy.mockRestore();
    });

    it('should not show modal when job ID is undefined', async () => {
      const user = userEvent.setup();
      const jobWithoutId = { ...mockJob, name: undefined } as unknown as MetricEvaluationJob;

      render(
        <ActionMenu
          job={jobWithoutId}
          onNavigateToDetails={mockOnNavigateToDetails}
          onJobDeleted={mockOnJobDeleted}
        />
      );

      // Open menu and click delete
      const triggerButton = screen.getByRole('button', {
        name: /Open evaluation job actions menu/,
      });
      await user.click(triggerButton);

      const deleteButton = screen.getByText('Delete');
      await user.click(deleteButton);

      // Modal should not appear when job name is undefined
      expect(screen.queryByText('Delete Evaluation Job')).not.toBeInTheDocument();
    });
  });

  describe('Optional Props', () => {
    it('should work without onJobDeleted callback', async () => {
      const user = userEvent.setup();

      render(<ActionMenu job={mockJob} onNavigateToDetails={mockOnNavigateToDetails} />);

      // Open menu and click delete
      const triggerButton = screen.getByRole('button', {
        name: /Open evaluation job actions menu/,
      });
      await user.click(triggerButton);

      const deleteButton = screen.getByText('Delete');
      await user.click(deleteButton);

      // Confirm deletion - should not throw error
      const confirmButton = await screen.findByRole('button', { name: 'Delete' });
      await user.click(confirmButton);

      // Should complete without errors
      expect(screen.queryByText('Delete Evaluation Job')).not.toBeInTheDocument();
    });
  });
});
