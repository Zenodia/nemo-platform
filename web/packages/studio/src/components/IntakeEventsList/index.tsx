// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import type { Entry } from '@nemo/sdk/generated/platform/schema';
import { Stack } from '@nvidia/foundations-react-core';
import { EventListItem } from '@studio/components/IntakeEventsList/components/EventListItem';
import { FC } from 'react';

type EntryEventItem = NonNullable<Entry['events']>[number];

interface IntakeEventsListProps {
  /** Array of events to display */
  events: EntryEventItem[];
  /** Entry ID needed for delete operations */
  entryId?: string;
  /** Callback when an event is deleted */
  onDeleteEvent?: (eventId: string) => void;
}

/**
 * Displays a chronological activity feed of events (annotations, actions, feedback) for an intake entry.
 * Uses a timeline-based layout with icons, sentiment badges, and JSON content display.
 *
 * Note: Empty state is handled by the parent route (IntakeEntryEventsRoute).
 */
export const IntakeEventsList: FC<IntakeEventsListProps> = ({ events, onDeleteEvent }) => {
  // Sort events by created_at (newest first)
  const sortedEvents = [...events].sort((a, b) => {
    const dateA = a.created_at ? new Date(a.created_at).getTime() : 0;
    const dateB = b.created_at ? new Date(b.created_at).getTime() : 0;
    return dateB - dateA;
  });

  return (
    <Stack className="w-full">
      {sortedEvents.map((event, index) => (
        <EventListItem
          key={event.id}
          event={event}
          isLast={index === sortedEvents.length - 1}
          onDelete={onDeleteEvent}
        />
      ))}
    </Stack>
  );
};
