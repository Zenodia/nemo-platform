// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { EventListItemLayout } from '@studio/components/IntakeEventsList/components/EventListItemLayout';
import { TestProviders } from '@studio/tests/util/TestProviders';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

describe('EventListItemLayout', () => {
  const defaultProps = {
    icon: <span data-testid="test-icon">Icon</span>,
    slotHeader: <span data-testid="header-content">Header Content</span>,
    isLast: false,
    children: <div data-testid="content">Content</div>,
  };

  it('renders the icon', () => {
    render(
      <TestProviders>
        <EventListItemLayout {...defaultProps} />
      </TestProviders>
    );

    expect(screen.getByTestId('test-icon')).toBeInTheDocument();
  });

  it('renders the header content', () => {
    render(
      <TestProviders>
        <EventListItemLayout {...defaultProps} />
      </TestProviders>
    );

    expect(screen.getByTestId('header-content')).toBeInTheDocument();
  });

  it('renders children content', () => {
    render(
      <TestProviders>
        <EventListItemLayout {...defaultProps} />
      </TestProviders>
    );

    expect(screen.getByTestId('content')).toBeInTheDocument();
  });

  it('renders timestamp when provided', () => {
    const timestamp = '2024-01-15T10:30:00Z';

    render(
      <TestProviders>
        <EventListItemLayout {...defaultProps} timestamp={timestamp} />
      </TestProviders>
    );

    // RelativeTime component will render something like "X days ago"
    // We check for the time element it creates
    expect(screen.getByRole('time')).toBeInTheDocument();
  });

  it('does not render timestamp when not provided', () => {
    render(
      <TestProviders>
        <EventListItemLayout {...defaultProps} />
      </TestProviders>
    );

    expect(screen.queryByRole('time')).not.toBeInTheDocument();
  });

  it('renders connecting line when not last item', () => {
    render(
      <TestProviders>
        <EventListItemLayout {...defaultProps} isLast={false} />
      </TestProviders>
    );

    // Check for the connecting line element
    expect(screen.getByTestId('activity-feed-item-event-connecting-line')).toBeInTheDocument();
  });

  it('hides connecting line when last item', () => {
    render(
      <TestProviders>
        <EventListItemLayout {...defaultProps} isLast />
      </TestProviders>
    );

    // The connecting line should not be rendered
    expect(
      screen.queryByTestId('activity-feed-item-event-connecting-line')
    ).not.toBeInTheDocument();
  });

  it('renders delete menu when onDelete is provided', async () => {
    const onDelete = vi.fn();

    render(
      <TestProviders>
        <EventListItemLayout {...defaultProps} onDelete={onDelete} />
      </TestProviders>
    );

    // Find the menu button by aria-label
    const menuButton = screen.getByLabelText('Event actions');
    expect(menuButton).toBeInTheDocument();
  });

  it('does not render delete menu when onDelete is not provided', () => {
    render(
      <TestProviders>
        <EventListItemLayout {...defaultProps} />
      </TestProviders>
    );

    expect(screen.queryByLabelText('Event actions')).not.toBeInTheDocument();
  });

  it('calls onDelete when delete option is clicked', async () => {
    const user = userEvent.setup();
    const onDelete = vi.fn();

    render(
      <TestProviders>
        <EventListItemLayout {...defaultProps} onDelete={onDelete} />
      </TestProviders>
    );

    // Click the menu button
    const menuButton = screen.getByLabelText('Event actions');
    await user.click(menuButton);

    // Click the delete option
    const deleteOption = await screen.findByText('Delete Annotation');
    await user.click(deleteOption);

    expect(onDelete).toHaveBeenCalledTimes(1);
  });

  it('applies custom testIdSuffix', () => {
    render(
      <TestProviders>
        <EventListItemLayout {...defaultProps} testIdSuffix="custom-event" />
      </TestProviders>
    );

    expect(screen.getByTestId('activity-feed-item-custom-event')).toBeInTheDocument();
  });

  it('uses default testIdSuffix when not provided', () => {
    render(
      <TestProviders>
        <EventListItemLayout {...defaultProps} />
      </TestProviders>
    );

    expect(screen.getByTestId('activity-feed-item-event')).toBeInTheDocument();
  });

  it('does not render content wrapper when children is null', () => {
    render(
      <TestProviders>
        <EventListItemLayout {...defaultProps} children={null} />
      </TestProviders>
    );

    // The content wrapper should not be present
    expect(screen.queryByTestId('activity-feed-item-event-content')).not.toBeInTheDocument();
  });
});
