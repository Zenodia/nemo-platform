// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { UserActionEvent as UserActionEventType } from '@nemo/sdk/generated/platform/schema';
import { Flex, Stack, Text } from '@nvidia/foundations-react-core';
import { EventListItemLayout } from '@studio/components/IntakeEventsList/components/EventListItemLayout';
import { formatEventCreatedBy } from '@studio/util/entries';
import { UserCheck } from 'lucide-react';
import { FC } from 'react';

interface UserActionEventProps {
  /** The user action event to display */
  event: UserActionEventType;
  /** Whether this is the last item in the list */
  isLast: boolean;
  /** Callback when delete action is triggered (event id handled by parent) */
  onDelete?: () => void;
}

/**
 * Renders a user_action event in the timeline.
 * Displays action name and metadata as label-value pairs.
 */
export const UserActionEvent: FC<UserActionEventProps> = ({ event, isLast, onDelete }) => {
  const actor = formatEventCreatedBy(event.created_by);

  return (
    <EventListItemLayout
      icon={<UserCheck size="16" color="white" />}
      slotHeader={
        <Flex gap="density-xs" align="center">
          <Text kind="label/semibold/sm">{actor}</Text>
          <Text kind="label/regular/sm" className="text-secondary">
            made an action
          </Text>
        </Flex>
      }
      timestamp={event.created_at}
      isLast={isLast}
      onDelete={onDelete}
      testIdSuffix="user-action"
    >
      <Stack gap="density-lg">
        <Stack gap="density-sm">
          <Text kind="label/regular/sm" className="text-secondary">
            Action
          </Text>
          <Text kind="label/semibold/md">{event.action}</Text>
        </Stack>
        {event.metadata && Object.keys(event.metadata).length > 0 && (
          <Stack gap="density-md">
            <Text kind="label/regular/sm" className="text-secondary">
              Metadata
            </Text>
            <pre className="text-xs overflow-x-auto w-0 min-w-full">
              {JSON.stringify(event.metadata, null, 2)}
            </pre>
          </Stack>
        )}
      </Stack>
    </EventListItemLayout>
  );
};
