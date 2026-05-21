// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import type {
  Entry,
  ReviewerAnnotationEvent,
  UserActionEvent,
  UserFeedbackEvent,
} from '@nemo/sdk/generated/platform/schema';
import { EventListItem } from '@studio/components/IntakeEventsList/components/EventListItem';
import { TestProviders } from '@studio/tests/util/TestProviders';
import { render, screen } from '@testing-library/react';

type EntryEventItem = NonNullable<Entry['events']>[number];

describe('EventListItem', () => {
  describe('event type routing', () => {
    it('renders UserFeedbackEvent for user_feedback event type', () => {
      const event: UserFeedbackEvent = {
        id: 'event-1',
        event_type: 'user_feedback',
        created_at: '2024-01-15T10:30:00Z',
        created_by: { name: 'User' },
        thumb: 'up',
      };

      render(
        <TestProviders>
          <EventListItem event={event} isLast={false} />
        </TestProviders>
      );

      expect(screen.getByTestId('activity-feed-item-user-feedback')).toBeInTheDocument();
      expect(screen.getByText('provided feedback')).toBeInTheDocument();
    });

    it('renders UserActionEvent for user_action event type', () => {
      const event: UserActionEvent = {
        id: 'event-2',
        event_type: 'user_action',
        created_at: '2024-01-15T10:30:00Z',
        created_by: { name: 'User' },
        action: 'button_clicked',
      };

      render(
        <TestProviders>
          <EventListItem event={event} isLast={false} />
        </TestProviders>
      );

      expect(screen.getByTestId('activity-feed-item-user-action')).toBeInTheDocument();
      expect(screen.getByText('made an action')).toBeInTheDocument();
    });

    it('renders ReviewerAnnotationEvent for reviewer_annotation event type', () => {
      const event: ReviewerAnnotationEvent = {
        id: 'event-3',
        event_type: 'reviewer_annotation',
        created_at: '2024-01-15T10:30:00Z',
        created_by: { name: 'Reviewer' },
        rating: 5,
      };

      render(
        <TestProviders>
          <EventListItem event={event} isLast={false} />
        </TestProviders>
      );

      expect(screen.getByTestId('activity-feed-item-reviewer-annotation')).toBeInTheDocument();
      expect(screen.getByText('annotated')).toBeInTheDocument();
    });

    it('returns null for unsupported event types', () => {
      // Create an event with an unknown type
      const event = {
        id: 'event-4',
        event_type: 'unknown_type',
        created_at: '2024-01-15T10:30:00Z',
      } as unknown as EntryEventItem;

      render(
        <TestProviders>
          <EventListItem event={event} isLast={false} />
        </TestProviders>
      );

      // Should not render any of the event type components
      expect(screen.queryByTestId('activity-feed-item-user-feedback')).not.toBeInTheDocument();
      expect(screen.queryByTestId('activity-feed-item-user-action')).not.toBeInTheDocument();
      expect(
        screen.queryByTestId('activity-feed-item-reviewer-annotation')
      ).not.toBeInTheDocument();
    });
  });

  describe('onDelete handling', () => {
    it('passes onDelete to child component when event has id', () => {
      const onDelete = vi.fn();
      const event: UserFeedbackEvent = {
        id: 'event-1',
        event_type: 'user_feedback',
        created_at: '2024-01-15T10:30:00Z',
        created_by: { name: 'User' },
      };

      render(
        <TestProviders>
          <EventListItem event={event} isLast={false} onDelete={onDelete} />
        </TestProviders>
      );

      // The delete menu should be present
      expect(screen.getByLabelText('Event actions')).toBeInTheDocument();
    });

    it('does not pass onDelete to child component when event has no id', () => {
      const onDelete = vi.fn();
      const event: UserFeedbackEvent = {
        // No id
        event_type: 'user_feedback',
        created_at: '2024-01-15T10:30:00Z',
        created_by: { name: 'User' },
      };

      render(
        <TestProviders>
          <EventListItem event={event} isLast={false} onDelete={onDelete} />
        </TestProviders>
      );

      // The delete menu should not be present
      expect(screen.queryByLabelText('Event actions')).not.toBeInTheDocument();
    });

    it('does not pass onDelete when onDelete prop is undefined', () => {
      const event: UserFeedbackEvent = {
        id: 'event-1',
        event_type: 'user_feedback',
        created_at: '2024-01-15T10:30:00Z',
        created_by: { name: 'User' },
      };

      render(
        <TestProviders>
          <EventListItem event={event} isLast={false} />
        </TestProviders>
      );

      // The delete menu should not be present
      expect(screen.queryByLabelText('Event actions')).not.toBeInTheDocument();
    });

    it('calls onDelete with event id when delete is triggered', async () => {
      const { default: userEvent } = await import('@testing-library/user-event');
      const user = userEvent.setup();
      const onDelete = vi.fn();
      const event: UserFeedbackEvent = {
        id: 'event-123',
        event_type: 'user_feedback',
        created_at: '2024-01-15T10:30:00Z',
        created_by: { name: 'User' },
      };

      render(
        <TestProviders>
          <EventListItem event={event} isLast={false} onDelete={onDelete} />
        </TestProviders>
      );

      const menuButton = screen.getByLabelText('Event actions');
      await user.click(menuButton);

      const deleteOption = await screen.findByText('Delete Annotation');
      await user.click(deleteOption);

      expect(onDelete).toHaveBeenCalledWith('event-123');
    });
  });

  describe('isLast prop', () => {
    it('passes isLast=false to child component', () => {
      const event: UserFeedbackEvent = {
        id: 'event-1',
        event_type: 'user_feedback',
        created_at: '2024-01-15T10:30:00Z',
        created_by: { name: 'User' },
      };

      render(
        <TestProviders>
          <EventListItem event={event} isLast={false} />
        </TestProviders>
      );

      // Connecting line should be visible
      expect(
        screen.getByTestId('activity-feed-item-user-feedback-connecting-line')
      ).toBeInTheDocument();
    });

    it('passes isLast=true to child component', () => {
      const event: UserFeedbackEvent = {
        id: 'event-1',
        event_type: 'user_feedback',
        created_at: '2024-01-15T10:30:00Z',
        created_by: { name: 'User' },
      };

      render(
        <TestProviders>
          <EventListItem event={event} isLast />
        </TestProviders>
      );

      // Connecting line should not be visible
      expect(
        screen.queryByTestId('activity-feed-item-user-feedback-connecting-line')
      ).not.toBeInTheDocument();
    });
  });
});
