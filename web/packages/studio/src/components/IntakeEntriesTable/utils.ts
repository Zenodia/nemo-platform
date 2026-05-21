// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { Entry, FlexibleMessage, ThumbDirection } from '@nemo/sdk/generated/platform/schema';

type EntryEventItem = NonNullable<Entry['events']>[number];

/**
 * Determines if an entry has been annotated by checking for reviewer_annotation events.
 */
export const isEntryAnnotated = (entry: Entry): boolean => {
  if (!entry.events || entry.events.length === 0) return false;
  return entry.events.some(
    (event: EntryEventItem) => 'event_type' in event && event.event_type === 'reviewer_annotation'
  );
};

/**
 * Gets the response content from an entry.
 */
export const getEntryResponseContent = (entry: Entry | undefined) => {
  return entry?.data?.response?.choices
    ?.map((choice) => (choice.message as FlexibleMessage)?.content as string)
    .join('\n');
};

/**
 * Gets the thumb direction for an entry from the reviewer annotation event or the user rating in that order.
 * @param entry - The entry to get the thumb for.
 * @returns The thumb direction for the entry.
 */
export const getEventOrUserThumb = (entry?: Entry): ThumbDirection | undefined => {
  if (!entry) return undefined;
  const eventsReverse = [...(entry.events ?? [])]?.reverse();
  const latestReviewerEvent = eventsReverse?.find(
    (event: EntryEventItem) =>
      'event_type' in event &&
      event.event_type === 'reviewer_annotation' &&
      typeof event === 'object'
  );
  const userRatingThumb = entry.user_rating?.thumb;
  if (latestReviewerEvent && 'thumb' in latestReviewerEvent) {
    return latestReviewerEvent.thumb;
  }
  if (userRatingThumb) {
    return userRatingThumb;
  }
};

/**
 * Gets the rating for an entry from the reviewer annotation event or the user rating in that order.
 * @param entry - The entry to get the rating for.
 * @returns The rating for the entry.
 */
export const getEventOrUserRating = (entry?: Entry): number | undefined => {
  if (!entry) return undefined;
  const eventsReverse = [...(entry.events ?? [])]?.reverse();
  const latestReviewerEvent = eventsReverse?.find(
    (event: EntryEventItem) =>
      'event_type' in event &&
      event.event_type === 'reviewer_annotation' &&
      typeof event === 'object'
  );
  const userRatingRating = entry.user_rating?.rating;
  if (
    latestReviewerEvent &&
    'rating' in latestReviewerEvent &&
    latestReviewerEvent.rating !== undefined
  ) {
    return latestReviewerEvent.rating;
  }
  if (userRatingRating !== undefined) {
    return userRatingRating;
  }
};

export const getEventOverride = (entry?: Entry): Record<string, unknown> | undefined => {
  if (!entry) return undefined;
  const eventsReverse = [...(entry.events ?? [])]?.reverse();
  const latestReviewerEvent = eventsReverse?.find(
    (event: EntryEventItem) =>
      'event_type' in event &&
      event.event_type === 'reviewer_annotation' &&
      typeof event === 'object'
  );
  if (latestReviewerEvent && 'response_override' in latestReviewerEvent) {
    return latestReviewerEvent.response_override;
  }
};
