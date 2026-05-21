// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { ReviewerAnnotationEvent as ReviewerAnnotationEventType } from '@nemo/sdk/generated/platform/schema';
import { CodeSnippet, Flex, Stack, Text } from '@nvidia/foundations-react-core';
import { EventListItemLayout } from '@studio/components/IntakeEventsList/components/EventListItemLayout';
import { ThumbTag } from '@studio/components/IntakeEventsList/components/ThumbTag';
import { formatEventCreatedBy } from '@studio/util/entries';
import { Pencil } from 'lucide-react';
import type { FC, ReactNode } from 'react';

interface ReviewerAnnotationEventProps {
  /** The reviewer annotation event to display */
  event: ReviewerAnnotationEventType;
  /** Whether this is the last item in the list */
  isLast: boolean;
  /** Callback when delete action is triggered (event id handled by parent) */
  onDelete?: () => void;
}

/**
 * Renders a reviewer_annotation event in the timeline.
 * Displays thumb in header, and rating/rewrite/opinion/categories/response_override as label-value pairs.
 */
export const ReviewerAnnotationEvent: FC<ReviewerAnnotationEventProps> = ({
  event,
  isLast,
  onDelete,
}) => {
  const actor = formatEventCreatedBy(event.created_by);

  // Build content items array - only render content section if there are items
  const contentItems: ReactNode[] = [];

  if (typeof event.rating === 'number') {
    contentItems.push(
      <Stack key="rating" gap="density-md">
        <Text kind="label/regular/sm" className="text-secondary">
          Rating
        </Text>
        <Text kind="label/semibold/md">{event.rating}</Text>
      </Stack>
    );
  }

  if (event.rewrite) {
    contentItems.push(
      <Stack key="rewrite" gap="density-md">
        <Text kind="label/regular/sm" className="text-secondary">
          Rewrite
        </Text>
        <Text kind="body/semibold/md">{event.rewrite}</Text>
      </Stack>
    );
  }

  if (event.opinion) {
    contentItems.push(
      <Stack key="opinion" gap="density-md">
        <Text kind="label/regular/sm" className="text-secondary">
          Opinion
        </Text>
        <Text kind="body/semibold/md">{event.opinion}</Text>
      </Stack>
    );
  }

  if (event.categories && Object.keys(event.categories).length > 0) {
    contentItems.push(
      <Stack key="categories" gap="density-md">
        <Text kind="label/regular/sm" className="text-secondary">
          Categories
        </Text>
        <pre className="text-xs overflow-x-auto w-0 min-w-full">
          {JSON.stringify(event.categories, null, 2)}
        </pre>
      </Stack>
    );
  }

  if (event.response_override && Object.keys(event.response_override).length > 0) {
    contentItems.push(
      <Stack key="override" gap="density-md">
        <Text kind="label/regular/sm" className="text-secondary">
          Override
        </Text>
        <div className="w-0 min-w-full overflow-x-auto">
          <CodeSnippet value={JSON.stringify(event.response_override, null, 2)} language="json" />
        </div>
      </Stack>
    );
  }

  return (
    <EventListItemLayout
      icon={<Pencil size="16" color="white" />}
      slotHeader={
        <Flex gap="density-sm" align="center">
          {event.thumb && <ThumbTag thumb={event.thumb} />}
          <Text kind="label/semibold/sm">{actor}</Text>
          <Text kind="label/regular/sm" className="text-secondary">
            annotated
          </Text>
        </Flex>
      }
      timestamp={event.created_at}
      isLast={isLast}
      onDelete={onDelete}
      testIdSuffix="reviewer-annotation"
    >
      {contentItems.length > 0 ? <Stack gap="density-lg">{contentItems}</Stack> : null}
    </EventListItemLayout>
  );
};
