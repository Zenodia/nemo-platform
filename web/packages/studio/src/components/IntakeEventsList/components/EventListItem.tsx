// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import type { Entry } from '@nemo/sdk/generated/platform/schema';
import { ReviewerAnnotationEvent } from '@studio/components/IntakeEventsList/components/ReviewerAnnotationEvent';
import { UserActionEvent } from '@studio/components/IntakeEventsList/components/UserActionEvent';
import { UserFeedbackEvent } from '@studio/components/IntakeEventsList/components/UserFeedbackEvent';
import { FC } from 'react';

type EntryEventItem = NonNullable<Entry['events']>[number];

interface EventListItemProps {
  /** The event to display */
  event: EntryEventItem;
  /** Whether this is the last item in the list (hides the connecting line) */
  isLast: boolean;
  /** Callback when delete action is triggered */
  onDelete?: (eventId: string) => void;
}

/**
 * Maps an event to the appropriate event type component based on event_type.
 * Acts as a simple routing component that delegates rendering to specialized components.
 */
export const EventListItem: FC<EventListItemProps> = ({ event, isLast, onDelete }) => {
  // Wrap onDelete in closure so child components don't need to know about event id
  const handleDelete = event.id && onDelete ? () => onDelete(event.id!) : undefined;

  switch (event.event_type) {
    case 'user_feedback':
      return <UserFeedbackEvent event={event} isLast={isLast} onDelete={handleDelete} />;
    case 'user_action':
      return <UserActionEvent event={event} isLast={isLast} onDelete={handleDelete} />;
    case 'reviewer_annotation':
      return <ReviewerAnnotationEvent event={event} isLast={isLast} onDelete={handleDelete} />;
    default:
      // Don't render unsupported event types
      return null;
  }
};
