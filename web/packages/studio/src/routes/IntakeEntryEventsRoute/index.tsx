// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { getGetEntryQueryKey, useDeleteEvent, useGetEntry } from '@nemo/sdk/generated/platform/api';
import { Anchor, Block, Panel, StatusMessage } from '@nvidia/foundations-react-core';
import { IntakeEventsList } from '@studio/components/IntakeEventsList';
import { Loading } from '@studio/components/Layouts/Loading';
import { ROUTE_PARAMS } from '@studio/constants/routes';
import { useWorkspaceFromPath } from '@studio/hooks/useWorkspaceFromPath';
import { getIntakeEntryMessagesRoute } from '@studio/routes/utils';
import { useQueryClient } from '@tanstack/react-query';
import { Star, TriangleAlert } from 'lucide-react';
import { FC, useCallback } from 'react';
import { Link, useParams } from 'react-router-dom';

/**
 * Route component for the intake entry Events & Annotations tab.
 * Displays the events and annotations list for the entry.
 * Used as a child of IntakeEntryLayout which provides the header and navigation.
 */
export const IntakeEntryEventsRoute: FC = () => {
  const { [ROUTE_PARAMS.entryId]: entryId } = useParams() as { [ROUTE_PARAMS.entryId]: string };
  const workspace = useWorkspaceFromPath();
  const { data: entry, isLoading } = useGetEntry(workspace, entryId);
  const queryClient = useQueryClient();
  const { mutate: deleteEvent } = useDeleteEvent();

  const handleDeleteEvent = useCallback(
    (eventId: string) => {
      deleteEvent(
        { workspace, entry: entryId, name: eventId },
        {
          onSuccess: () => {
            queryClient.invalidateQueries({
              queryKey: getGetEntryQueryKey(workspace, entryId),
            });
          },
        }
      );
    },
    [deleteEvent, entryId, queryClient, workspace]
  );

  const panelProps = {
    elevation: 'high' as const,
    slotIcon: <Star />,
    slotHeading: 'Events and Annotations' as const,
  };

  // Loading state
  if (isLoading) {
    return <Loading description="Loading events..." />;
  }

  const events = entry?.events ?? [];

  // Empty state - matches Figma design
  if (events.length === 0) {
    const messagesRoute = getIntakeEntryMessagesRoute(workspace, entryId);
    return (
      <Panel {...panelProps}>
        <StatusMessage
          size="medium"
          slotMedia={<TriangleAlert height={65} width={65} />}
          slotHeading="No Events or Annotations Found"
          slotSubheading={
            <>
              Begin annotating in the{' '}
              <Anchor asChild>
                <Link to={messagesRoute}>Input/Output</Link>
              </Anchor>{' '}
              tab.
            </>
          }
          data-testid="no-events-container"
        />
      </Panel>
    );
  }

  return (
    <Panel {...panelProps}>
      <Block className="pl-4">
        <IntakeEventsList events={events} entryId={entryId} onDeleteEvent={handleDeleteEvent} />
      </Block>
    </Panel>
  );
};
