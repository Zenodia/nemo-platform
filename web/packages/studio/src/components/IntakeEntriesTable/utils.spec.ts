// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import type { Entry } from '@nemo/sdk/generated/platform/schema';
import {
  getEntryResponseContent,
  getEventOrUserRating,
  getEventOrUserThumb,
  getEventOverride,
  isEntryAnnotated,
} from '@studio/components/IntakeEntriesTable/utils';

type EntryEventItem = NonNullable<Entry['events']>[number];

const makeEntry = (overrides: Partial<Entry> = {}): Entry =>
  ({
    id: 'e1',
    events: [],
    data: {},
    ...overrides,
  }) as Entry;

const reviewerEvent = (extra: Record<string, unknown> = {}): EntryEventItem =>
  ({
    event_type: 'reviewer_annotation',
    ...extra,
  }) as unknown as EntryEventItem;

describe('isEntryAnnotated', () => {
  it('returns false when events is empty', () => {
    expect(isEntryAnnotated(makeEntry())).toBe(false);
  });

  it('returns false when events is undefined', () => {
    expect(isEntryAnnotated(makeEntry({ events: undefined }))).toBe(false);
  });

  it('returns true when a reviewer_annotation event exists', () => {
    expect(isEntryAnnotated(makeEntry({ events: [reviewerEvent()] }))).toBe(true);
  });

  it('returns false when events have a different type', () => {
    const entry = makeEntry({
      events: [{ event_type: 'other' } as unknown as EntryEventItem],
    });
    expect(isEntryAnnotated(entry)).toBe(false);
  });
});

describe('getEntryResponseContent', () => {
  it('returns undefined for undefined entry', () => {
    expect(getEntryResponseContent(undefined)).toBeUndefined();
  });

  it('joins choice contents with newline', () => {
    const entry = makeEntry({
      data: {
        response: {
          choices: [{ message: { content: 'hello' } }, { message: { content: 'world' } }],
        },
      },
    } as unknown as Partial<Entry>);
    expect(getEntryResponseContent(entry)).toBe('hello\nworld');
  });

  it('returns undefined when no response data', () => {
    expect(getEntryResponseContent(makeEntry())).toBeUndefined();
  });
});

describe('getEventOrUserThumb', () => {
  it('returns undefined for undefined entry', () => {
    expect(getEventOrUserThumb(undefined)).toBeUndefined();
  });

  it('returns thumb from latest reviewer event', () => {
    const entry = makeEntry({
      events: [reviewerEvent({ thumb: 'up' }), reviewerEvent({ thumb: 'down' })],
    });
    // reversed — last event is checked first
    expect(getEventOrUserThumb(entry)).toBe('down');
  });

  it('falls back to user_rating.thumb when no reviewer event', () => {
    const entry = makeEntry({ user_rating: { thumb: 'up' } } as unknown as Partial<Entry>);
    expect(getEventOrUserThumb(entry)).toBe('up');
  });

  it('returns undefined when no thumb anywhere', () => {
    expect(getEventOrUserThumb(makeEntry())).toBeUndefined();
  });
});

describe('getEventOrUserRating', () => {
  it('returns undefined for undefined entry', () => {
    expect(getEventOrUserRating(undefined)).toBeUndefined();
  });

  it('returns rating from latest reviewer event', () => {
    const entry = makeEntry({
      events: [reviewerEvent({ rating: 3 }), reviewerEvent({ rating: 5 })],
    });
    expect(getEventOrUserRating(entry)).toBe(5);
  });

  it('falls back to user_rating.rating', () => {
    const entry = makeEntry({ user_rating: { rating: 4 } } as unknown as Partial<Entry>);
    expect(getEventOrUserRating(entry)).toBe(4);
  });

  it('returns undefined when no rating anywhere', () => {
    expect(getEventOrUserRating(makeEntry())).toBeUndefined();
  });
});

describe('getEventOverride', () => {
  it('returns undefined for undefined entry', () => {
    expect(getEventOverride(undefined)).toBeUndefined();
  });

  it('returns response_override from latest reviewer event', () => {
    const override = { content: 'fixed' };
    const entry = makeEntry({
      events: [reviewerEvent({ response_override: override })],
    });
    expect(getEventOverride(entry)).toEqual(override);
  });

  it('returns undefined when no response_override', () => {
    const entry = makeEntry({ events: [reviewerEvent()] });
    expect(getEventOverride(entry)).toBeUndefined();
  });
});
