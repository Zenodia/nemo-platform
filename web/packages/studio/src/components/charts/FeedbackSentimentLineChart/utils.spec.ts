// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import type { Entry } from '@nemo/sdk/generated/platform/schema';
import {
  countRatingsByDate,
  getUniqueSortedDates,
  mapToLabels,
} from '@studio/components/charts/FeedbackSentimentLineChart/utils';

const makeEntry = (created_at: string, user_rating?: unknown): Entry =>
  ({
    id: '1',
    created_at,
    ...(user_rating !== undefined ? { user_rating } : {}),
  }) as Entry;

describe('getUniqueSortedDates', () => {
  it('returns unique sorted dates in YYYY-MM-DD format', () => {
    const entries = [
      makeEntry('2024-03-15T10:00:00Z'),
      makeEntry('2024-03-14T08:00:00Z'),
      makeEntry('2024-03-15T12:00:00Z'),
    ];
    const result = getUniqueSortedDates(entries);
    expect(result[0]).toBe('2024-03-14');
    expect(result[1]).toBe('2024-03-15');
  });

  it('adds today if not already present', () => {
    const entries = [makeEntry('2020-01-01T00:00:00Z')];
    const result = getUniqueSortedDates(entries);
    const today = new Date().toISOString().split('T')[0];
    expect(result).toContain(today);
  });

  it('returns empty array for empty entries', () => {
    expect(getUniqueSortedDates([])).toEqual([]);
  });
});

describe('mapToLabels', () => {
  it('maps counts to labels, defaulting to 0', () => {
    const mapping = { '2024-03-14': 5, '2024-03-15': 3 };
    const labels = ['2024-03-13', '2024-03-14', '2024-03-15'];
    expect(mapToLabels(mapping, labels)).toEqual([0, 5, 3]);
  });

  it('returns all zeros for empty mapping', () => {
    expect(mapToLabels({}, ['a', 'b'])).toEqual([0, 0]);
  });
});

describe('countRatingsByDate', () => {
  it('counts entries with user_rating when ratingValue is true', () => {
    const entries = [
      makeEntry('2024-03-14T10:00:00Z', { thumb: 'up' }),
      makeEntry('2024-03-14T12:00:00Z', { thumb: 'down' }),
      makeEntry('2024-03-15T08:00:00Z'),
    ];
    const result = countRatingsByDate(entries, true);
    expect(result['2024-03-14']).toBe(2);
    expect(result['2024-03-15']).toBeUndefined();
  });

  it('counts entries without user_rating when ratingValue is false', () => {
    const entries = [
      makeEntry('2024-03-14T10:00:00Z', { thumb: 'up' }),
      makeEntry('2024-03-14T12:00:00Z'),
      makeEntry('2024-03-15T08:00:00Z'),
    ];
    const result = countRatingsByDate(entries, false);
    expect(result['2024-03-14']).toBe(1);
    expect(result['2024-03-15']).toBe(1);
  });
});
