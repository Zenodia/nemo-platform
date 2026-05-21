// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import type { Entry } from '@nemo/sdk/generated/platform/schema';

export const getUniqueSortedDates = (entries: Entry[]) => {
  // Sort by created_at in ascending order
  const sortedObjects = entries.sort((a, b) => {
    return new Date(a.created_at || '').getTime() - new Date(b.created_at || '').getTime();
  });

  // Map to date-only strings and filter unique dates
  const uniqueDates = new Set(
    sortedObjects.map((obj) => new Date(obj.created_at || '').toISOString().split('T')[0]) // 'YYYY-MM-DD' format
  );
  const today = new Date().toISOString().split('T')[0];
  if (!uniqueDates.has(today) && entries.length > 0) {
    uniqueDates.add(today);
  }

  return Array.from(uniqueDates);
};

export const mapToLabels = (mapping: Record<string, number>, labels: string[]) =>
  labels.map((label) => (mapping[label] ? mapping[label] : 0));

export const countRatingsByDate = (entries: Entry[], ratingValue: boolean) => {
  return entries
    .filter((data) => Boolean(data.user_rating) === ratingValue)
    .reduce(
      (countMap, entry) => {
        const dateKey = new Date(entry.created_at || '').toISOString().split('T')[0];
        if (!countMap[dateKey]) {
          countMap[dateKey] = 1;
        } else {
          countMap[dateKey]++;
        }
        return countMap;
      },
      {} as Record<string, number>
    );
};
