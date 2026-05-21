// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { Entry, ReviewerAnnotationEvent } from '@nemo/sdk/generated/platform/schema';
import {
  formatEventCreatedBy,
  getAnnotationFromEntry,
  getChatHistoryFromEntry,
  getLastAssistantMessage,
  getLastInputOutputPair,
  getLastUserMessageContent,
  getNonSystemMessagesFromEntry,
  getRewriteFromAnnotation,
  getSystemContextFromEntry,
  getTurnCount,
  isReviewerAnnotationEvent,
  parseAppRef,
} from '@studio/util/entries';

/**
 * Helper to create partial Entry objects for testing.
 *
 * Uses type assertion to bypass strict type checking for test fixtures.
 * This is acceptable in tests as it allows flexible fixture creation
 * without requiring all Entry properties to be specified.
 *
 * @param partialData - Partial entry data to override defaults
 * @returns A complete Entry object for testing
 */
const createTestEntry = (partialData: Record<string, unknown> = {}): Entry =>
  ({
    data: { request: { messages: [], model: 'test' }, response: { choices: [] } },
    context: { app: 'test', task: 'test' },
    ...partialData,
  }) as unknown as Entry;

describe('entries utilities', () => {
  describe('getTurnCount', () => {
    it('returns 1 for entry with no messages', () => {
      const entry = createTestEntry({ data: { request: { model: 'test' } } });
      expect(getTurnCount(entry)).toBe(1);
    });

    it('returns 1 for entry with empty messages array', () => {
      const entry = createTestEntry({ data: { request: { messages: [], model: 'test' } } });
      expect(getTurnCount(entry)).toBe(1);
    });

    it('counts user messages correctly', () => {
      const entry = createTestEntry({
        data: {
          request: {
            messages: [
              { role: 'system', content: 'You are helpful' },
              { role: 'user', content: 'Hello' },
              { role: 'assistant', content: 'Hi there' },
              { role: 'user', content: 'How are you?' },
              { role: 'assistant', content: 'Good!' },
            ],
            model: 'test',
          },
        },
      });
      expect(getTurnCount(entry)).toBe(2);
    });
  });

  describe('getLastUserMessageContent', () => {
    it('returns empty string for entry with no messages', () => {
      const entry = createTestEntry({ data: { request: { model: 'test' } } });
      expect(getLastUserMessageContent(entry)).toBe('');
    });

    it('returns the last user message content', () => {
      const entry = createTestEntry({
        data: {
          request: {
            messages: [
              { role: 'user', content: 'First question' },
              { role: 'assistant', content: 'First answer' },
              { role: 'user', content: 'Second question' },
            ],
            model: 'test',
          },
        },
      });
      expect(getLastUserMessageContent(entry)).toBe('Second question');
    });
  });

  describe('getLastAssistantMessage', () => {
    it('returns empty string for entry with no response', () => {
      const entry = createTestEntry({ data: { request: { model: 'test' } } });
      expect(getLastAssistantMessage(entry)).toBe('');
    });

    it('returns content from response choices', () => {
      const entry = createTestEntry({
        data: {
          request: { messages: [], model: 'test' },
          response: {
            choices: [{ message: { role: 'assistant', content: 'Response content' } }],
          },
        },
      });
      expect(getLastAssistantMessage(entry)).toBe('Response content');
    });

    it('falls back to request messages if no response', () => {
      const entry = createTestEntry({
        data: {
          request: {
            messages: [
              { role: 'user', content: 'Question' },
              { role: 'assistant', content: 'Answer from request' },
            ],
            model: 'test',
          },
        },
      });
      expect(getLastAssistantMessage(entry)).toBe('Answer from request');
    });
  });

  describe('isReviewerAnnotationEvent', () => {
    it('returns true for reviewer annotation events', () => {
      const event = { event_type: 'reviewer_annotation' } as ReviewerAnnotationEvent;
      expect(isReviewerAnnotationEvent(event)).toBe(true);
    });

    it('returns false for other event types', () => {
      const event = { event_type: 'user_feedback' };
      expect(isReviewerAnnotationEvent(event as never)).toBe(false);
    });
  });

  describe('getAnnotationFromEntry', () => {
    it('returns undefined for entry with no events', () => {
      const entry = createTestEntry();
      expect(getAnnotationFromEntry(entry)).toBeUndefined();
    });

    it('returns undefined for entry with empty events array', () => {
      const entry = createTestEntry({ events: [] });
      expect(getAnnotationFromEntry(entry)).toBeUndefined();
    });

    it('returns undefined when no reviewer annotations exist', () => {
      const entry = createTestEntry({
        events: [{ event_type: 'user_feedback', thumb: 'up' }],
      });
      expect(getAnnotationFromEntry(entry)).toBeUndefined();
    });

    it('returns the annotation when one exists', () => {
      const annotation: ReviewerAnnotationEvent = {
        event_type: 'reviewer_annotation',
        thumb: 'up',
        rewrite: 'Better answer',
      };
      const entry = createTestEntry({ events: [annotation] });
      expect(getAnnotationFromEntry(entry)).toEqual(annotation);
    });

    it('returns the most recent annotation when multiple exist', () => {
      const older: ReviewerAnnotationEvent = {
        event_type: 'reviewer_annotation',
        created_at: '2024-01-01T00:00:00Z',
        thumb: 'down',
      };
      const newer: ReviewerAnnotationEvent = {
        event_type: 'reviewer_annotation',
        created_at: '2024-06-01T00:00:00Z',
        thumb: 'up',
      };
      const entry = createTestEntry({ events: [older, newer] });
      expect(getAnnotationFromEntry(entry)).toEqual(newer);
    });
  });

  describe('getRewriteFromAnnotation', () => {
    it('returns undefined for undefined annotation', () => {
      expect(getRewriteFromAnnotation(undefined)).toBeUndefined();
    });

    it('returns rewrite from annotation.rewrite', () => {
      const annotation: ReviewerAnnotationEvent = {
        event_type: 'reviewer_annotation',
        rewrite: 'Fixed response',
      };
      expect(getRewriteFromAnnotation(annotation)).toBe('Fixed response');
    });

    it('returns content from response_override when rewrite is empty', () => {
      const annotation = {
        event_type: 'reviewer_annotation',
        response_override: {
          choices: [{ message: { content: 'Override content' } }],
        },
      } as ReviewerAnnotationEvent;
      expect(getRewriteFromAnnotation(annotation)).toBe('Override content');
    });

    it('prefers rewrite over response_override', () => {
      const annotation = {
        event_type: 'reviewer_annotation',
        rewrite: 'Direct rewrite',
        response_override: {
          choices: [{ message: { content: 'Override content' } }],
        },
      } as ReviewerAnnotationEvent;
      expect(getRewriteFromAnnotation(annotation)).toBe('Direct rewrite');
    });

    it('returns undefined when rewrite is whitespace only', () => {
      const annotation: ReviewerAnnotationEvent = {
        event_type: 'reviewer_annotation',
        rewrite: '   ',
      };
      expect(getRewriteFromAnnotation(annotation)).toBeUndefined();
    });

    it('returns undefined when annotation has neither rewrite nor response_override', () => {
      const annotation: ReviewerAnnotationEvent = {
        event_type: 'reviewer_annotation',
        thumb: 'up',
      };
      expect(getRewriteFromAnnotation(annotation)).toBeUndefined();
    });

    it('trims whitespace from rewrite content', () => {
      const annotation: ReviewerAnnotationEvent = {
        event_type: 'reviewer_annotation',
        rewrite: '  Trimmed content  ',
      };
      expect(getRewriteFromAnnotation(annotation)).toBe('Trimmed content');
    });

    it('trims whitespace from response_override content', () => {
      const annotation = {
        event_type: 'reviewer_annotation',
        response_override: {
          choices: [{ message: { content: '  Override trimmed  ' } }],
        },
      } as ReviewerAnnotationEvent;
      expect(getRewriteFromAnnotation(annotation)).toBe('Override trimmed');
    });
  });

  describe('getChatHistoryFromEntry', () => {
    it('returns empty array for entry with no data', () => {
      const entry = createTestEntry();
      expect(getChatHistoryFromEntry(entry)).toEqual([]);
    });

    it('returns request messages', () => {
      const entry = createTestEntry({
        data: {
          request: {
            messages: [
              { role: 'system', content: 'System prompt' },
              { role: 'user', content: 'Hello' },
            ],
            model: 'test',
          },
        },
      });
      expect(getChatHistoryFromEntry(entry)).toHaveLength(2);
    });

    it('includes response message from choices', () => {
      const entry = createTestEntry({
        data: {
          request: {
            messages: [{ role: 'user', content: 'Hello' }],
            model: 'test',
          },
          response: {
            choices: [{ message: { role: 'assistant', content: 'Hi!' } }],
          },
        },
      });
      const history = getChatHistoryFromEntry(entry);
      expect(history).toHaveLength(2);
      expect(history[1]).toEqual({ role: 'assistant', content: 'Hi!' });
    });
  });

  describe('getSystemContextFromEntry', () => {
    it('returns empty array for entry with no messages', () => {
      const entry = createTestEntry({ data: { request: { model: 'test' } } });
      expect(getSystemContextFromEntry(entry)).toEqual([]);
    });

    it('returns system messages at the start', () => {
      const entry = createTestEntry({
        data: {
          request: {
            messages: [
              { role: 'system', content: 'First system' },
              { role: 'system', content: 'Second system' },
              { role: 'user', content: 'Hello' },
            ],
            model: 'test',
          },
        },
      });
      const systemMessages = getSystemContextFromEntry(entry);
      expect(systemMessages).toHaveLength(2);
      expect(systemMessages[0].content).toBe('First system');
      expect(systemMessages[1].content).toBe('Second system');
    });

    it('stops at first non-system message', () => {
      const entry = createTestEntry({
        data: {
          request: {
            messages: [
              { role: 'system', content: 'System prompt' },
              { role: 'user', content: 'Hello' },
              { role: 'system', content: 'This should not be included' },
            ],
            model: 'test',
          },
        },
      });
      const systemMessages = getSystemContextFromEntry(entry);
      expect(systemMessages).toHaveLength(1);
      expect(systemMessages[0].content).toBe('System prompt');
    });
  });

  describe('getNonSystemMessagesFromEntry', () => {
    it('filters out system messages', () => {
      const entry = createTestEntry({
        data: {
          request: {
            messages: [
              { role: 'system', content: 'System prompt' },
              { role: 'user', content: 'Hello' },
              { role: 'assistant', content: 'Hi!' },
            ],
            model: 'test',
          },
        },
      });
      const messages = getNonSystemMessagesFromEntry(entry);
      expect(messages).toHaveLength(2);
      expect(messages.every((m) => m.role !== 'system')).toBe(true);
    });
  });

  describe('getLastInputOutputPair', () => {
    it('returns empty array for entry with no messages', () => {
      const entry = createTestEntry({ data: { request: { model: 'test' } } });
      expect(getLastInputOutputPair(entry)).toEqual([]);
    });

    it('returns only last user message and response for single turn', () => {
      const entry = createTestEntry({
        data: {
          request: {
            messages: [{ role: 'user', content: 'Hello' }],
            model: 'test',
          },
          response: {
            choices: [{ message: { role: 'assistant', content: 'Hi there!' } }],
          },
        },
      });
      const pair = getLastInputOutputPair(entry);
      expect(pair).toHaveLength(2);
      expect(pair[0]).toEqual({ role: 'user', content: 'Hello' });
      expect(pair[1]).toEqual({ role: 'assistant', content: 'Hi there!' });
    });

    it('returns only last user message and response for multi-turn conversation', () => {
      const entry = createTestEntry({
        data: {
          request: {
            messages: [
              { role: 'system', content: 'System prompt' },
              { role: 'user', content: 'First question' },
              { role: 'assistant', content: 'First answer' },
              { role: 'user', content: 'Second question' },
              { role: 'assistant', content: 'Second answer' },
              { role: 'user', content: 'Third question' },
            ],
            model: 'test',
          },
          response: {
            choices: [{ message: { role: 'assistant', content: 'Third answer' } }],
          },
        },
      });
      const pair = getLastInputOutputPair(entry);
      expect(pair).toHaveLength(2);
      expect(pair[0]).toEqual({ role: 'user', content: 'Third question' });
      expect(pair[1]).toEqual({ role: 'assistant', content: 'Third answer' });
    });

    it('excludes system messages', () => {
      const entry = createTestEntry({
        data: {
          request: {
            messages: [
              { role: 'system', content: 'System prompt' },
              { role: 'user', content: 'Hello' },
            ],
            model: 'test',
          },
          response: {
            choices: [{ message: { role: 'assistant', content: 'Hi!' } }],
          },
        },
      });
      const pair = getLastInputOutputPair(entry);
      expect(pair).toHaveLength(2);
      expect(pair.every((m) => m.role !== 'system')).toBe(true);
    });

    it('returns only user message if no response', () => {
      const entry = createTestEntry({
        data: {
          request: {
            messages: [{ role: 'user', content: 'Hello' }],
            model: 'test',
          },
        },
      });
      const pair = getLastInputOutputPair(entry);
      expect(pair).toHaveLength(1);
      expect(pair[0]).toEqual({ role: 'user', content: 'Hello' });
    });

    it('returns empty array if no user messages', () => {
      const entry = createTestEntry({
        data: {
          request: {
            messages: [{ role: 'system', content: 'System only' }],
            model: 'test',
          },
          response: {
            choices: [{ message: { role: 'assistant', content: 'Response' } }],
          },
        },
      });
      const pair = getLastInputOutputPair(entry);
      // Only response, no user message
      expect(pair).toHaveLength(1);
      expect(pair[0]).toEqual({ role: 'assistant', content: 'Response' });
    });
  });
});

describe('parseAppRef', () => {
  it('parses valid app reference with namespace and name', () => {
    const result = parseAppRef('my-namespace/my-app');
    expect(result).toEqual({ namespace: 'my-namespace', appName: 'my-app' });
  });

  it('parses app reference with special characters', () => {
    const result = parseAppRef('ns-123/app_name.v2');
    expect(result).toEqual({ namespace: 'ns-123', appName: 'app_name.v2' });
  });

  it('returns null for undefined input', () => {
    expect(parseAppRef(undefined)).toBeNull();
  });

  it('returns null for empty string', () => {
    expect(parseAppRef('')).toBeNull();
  });

  it('returns null for string without slash', () => {
    expect(parseAppRef('no-slash-here')).toBeNull();
  });

  it('returns null for string with multiple slashes', () => {
    expect(parseAppRef('too/many/slashes')).toBeNull();
  });

  it('handles edge case with empty namespace', () => {
    const result = parseAppRef('/app-name');
    expect(result).toEqual({ namespace: '', appName: 'app-name' });
  });

  it('handles edge case with empty app name', () => {
    const result = parseAppRef('namespace/');
    expect(result).toEqual({ namespace: 'namespace', appName: '' });
  });
});

describe('formatEventCreatedBy', () => {
  it.each([
    // Undefined/null cases
    { input: undefined, expected: 'Unknown', description: 'undefined' },

    // Object with name property (highest priority)
    { input: { name: 'John Doe' }, expected: 'John Doe', description: 'object with name' },
    {
      input: { name: 'Jane Smith', username: 'jsmith', email: 'jane@example.com' },
      expected: 'Jane Smith',
      description: 'object with name, username, and email (name takes priority)',
    },

    // Object with username property (second priority)
    { input: { username: 'jdoe' }, expected: 'jdoe', description: 'object with username only' },
    {
      input: { username: 'jdoe', email: 'john@example.com' },
      expected: 'jdoe',
      description: 'object with username and email (username takes priority)',
    },

    // Object with email property (third priority)
    {
      input: { email: 'john@example.com' },
      expected: 'john@example.com',
      description: 'object with email only',
    },
    {
      input: { email: 'john@example.com', id: 'user-123' },
      expected: 'john@example.com',
      description: 'object with email and id (email takes priority)',
    },

    // Object with id property (fourth priority)
    { input: { id: 'user-123' }, expected: 'user-123', description: 'object with id only' },

    // Object with other string properties (fallback)
    {
      input: { displayName: 'Display Name' },
      expected: 'Display Name',
      description: 'object with arbitrary string property',
    },
    {
      input: { custom_field: 'Custom Value' },
      expected: 'Custom Value',
      description: 'object with snake_case string property',
    },

    // Object with no string values
    { input: {}, expected: 'Unknown', description: 'empty object' },
    { input: { count: 123 }, expected: 'Unknown', description: 'object with only numeric values' },
    {
      input: { active: true, count: 42 },
      expected: 'Unknown',
      description: 'object with only non-string values',
    },

    // Edge cases with empty/invalid name values
    {
      input: { name: '' },
      expected: 'Unknown',
      description: 'object with empty string name (treats as falsy, returns Unknown)',
    },
    {
      input: { name: '   ' },
      expected: '   ',
      description: 'object with whitespace-only name',
    },
    {
      input: { name: 123, username: 'fallback' },
      expected: 'fallback',
      description: 'object with non-string name (falls back to username)',
    },
  ])('returns "$expected" for $description', ({ input, expected }) => {
    expect(formatEventCreatedBy(input as never)).toBe(expected);
  });
});
