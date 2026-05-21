// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import {
  Entry,
  FlexibleMessage,
  ReviewerAnnotationEvent,
  ReviewerAnnotationEventCreatedBy,
  ReviewerAnnotationEventResponseOverride,
  UserActionEventCreatedBy,
  UserFeedbackEventCreatedBy,
} from '@nemo/sdk/generated/platform/schema';

type EntryEventItem = NonNullable<Entry['events']>[number];

/**
 * Gets the turn count from an entry's messages.
 * Each user message represents one turn in the conversation.
 */
export const getTurnCount = (entry: Entry): number => {
  const messages = entry.data?.request?.messages;
  if (!messages || !Array.isArray(messages)) return 1;
  return messages.filter((m: FlexibleMessage) => m.role === 'user').length || 1;
};

/**
 * Type guard to check if an event is a ReviewerAnnotationEvent.
 */
export const isReviewerAnnotationEvent = (
  event: EntryEventItem
): event is ReviewerAnnotationEvent => {
  return event.event_type === 'reviewer_annotation';
};

/**
 * Determines if an entry has been annotated by checking for reviewer_annotation events.
 */
export const isEntryAnnotated = (entry: Entry): boolean => {
  if (!entry.events || entry.events.length === 0) return false;
  return entry.events.some(isReviewerAnnotationEvent);
};

/**
 * Gets the most recent reviewer annotation from an entry's events.
 * Returns undefined if no reviewer annotations exist.
 */
export const getAnnotationFromEntry = (entry: Entry): ReviewerAnnotationEvent | undefined => {
  const events = entry.events;
  if (!events || !Array.isArray(events)) return undefined;

  const annotations = events.filter(isReviewerAnnotationEvent);
  if (annotations.length === 0) return undefined;

  // Return the most recent annotation (last one in the array, or sort by created_at)
  return annotations.reduce((latest, current) => {
    if (!latest.created_at) return current;
    if (!current.created_at) return latest;
    return new Date(current.created_at) > new Date(latest.created_at) ? current : latest;
  }, annotations[0]);
};

/**
 * Gets the complete chat history from an entry, combining request messages and response.
 * Returns an array of FlexibleMessage objects in conversation order.
 */
export const getChatHistoryFromEntry = (entry: Entry): FlexibleMessage[] => {
  const messages: FlexibleMessage[] = [];

  // Add request messages (conversation history)
  const requestMessages = entry.data?.request?.messages;
  if (requestMessages && Array.isArray(requestMessages)) {
    messages.push(...requestMessages);
  }

  // Add response message from choices
  const choices = entry.data?.response?.choices;
  if (choices && choices.length > 0) {
    const responseMessage = choices[0]?.message as FlexibleMessage | undefined;
    if (responseMessage && responseMessage.role) {
      messages.push(responseMessage);
    }
  }

  return messages;
};

/**
 * Extracts system context messages from entry's chat history.
 * Returns system messages at the beginning of the conversation.
 */
export const getSystemContextFromEntry = (entry: Entry): FlexibleMessage[] => {
  const messages = entry.data?.request?.messages;
  if (!messages || !Array.isArray(messages)) return [];

  const systemMessages: FlexibleMessage[] = [];
  for (const message of messages) {
    if (message.role === 'system') {
      systemMessages.push(message);
    } else {
      // Stop at first non-system message (system context is typically at the start)
      break;
    }
  }

  return systemMessages;
};

/**
 * Gets non-system messages from an entry (user and assistant messages for display).
 */
export const getNonSystemMessagesFromEntry = (entry: Entry): FlexibleMessage[] => {
  const allMessages = getChatHistoryFromEntry(entry);
  return allMessages.filter((m) => m.role !== 'system');
};

/**
 * Gets the last user message content from an entry's request messages.
 * Returns the content of the last message with role 'user'.
 */
export const getLastUserMessageContent = (entry: Entry): string => {
  const messages = entry.data?.request?.messages;
  if (!messages || !Array.isArray(messages)) return '';
  const userMessages = messages.filter((m: FlexibleMessage) => m.role === 'user');
  if (userMessages.length === 0) return '';
  const content = userMessages.at(-1)?.content;
  return typeof content === 'string' ? content : '';
};

/**
 * Gets the last assistant message content for the Output column.
 * First tries response.choices, then falls back to request messages.
 */
export const getLastAssistantMessage = (entry: Entry): string => {
  // Try to get from response.choices first (most recent)
  const choices = entry.data?.response?.choices;
  if (choices && choices.length > 0) {
    const lastChoice = choices[choices.length - 1];
    const content = (lastChoice?.message as FlexibleMessage)?.content;
    if (typeof content === 'string') {
      return content;
    }
  }

  // Fallback to last assistant message in request messages
  const messages = entry.data?.request?.messages;
  if (!messages || !Array.isArray(messages)) return '';
  const assistantMessages = messages.filter((m: FlexibleMessage) => m.role === 'assistant');
  if (assistantMessages.length === 0) return '';
  const content = assistantMessages[assistantMessages.length - 1]?.content;
  return typeof content === 'string' ? content : '';
};

/**
 * Gets only the last user message and the assistant response from an entry.
 * Used for displaying just the input/output pair, not the full conversation history.
 */
export const getLastInputOutputPair = (entry: Entry): FlexibleMessage[] => {
  const messages: FlexibleMessage[] = [];
  const requestMessages = entry.data?.request?.messages;

  // Get last user message
  if (requestMessages && Array.isArray(requestMessages)) {
    const userMessages = requestMessages.filter((m: FlexibleMessage) => m.role === 'user');
    const lastUserMessage = userMessages.at(-1);
    if (lastUserMessage) {
      messages.push(lastUserMessage);
    }
  }

  // Get response from choices
  const choices = entry.data?.response?.choices;
  if (choices && choices.length > 0) {
    const responseMessage = choices[0]?.message as FlexibleMessage | undefined;
    if (responseMessage && responseMessage.role) {
      messages.push(responseMessage);
    }
  }

  return messages;
};

/**
 * Format the created_by field from an event which can be a string or an object.
 * Attempts to extract a human-readable name from various object shapes.
 */
export const formatEventCreatedBy = (
  createdBy:
    | UserFeedbackEventCreatedBy
    | UserActionEventCreatedBy
    | ReviewerAnnotationEventCreatedBy
    | undefined
): string => {
  if (!createdBy) return 'Unknown';
  if (typeof createdBy === 'string') return createdBy;
  if (typeof createdBy === 'object') {
    const obj = createdBy as Record<string, unknown>;
    if (obj.name && typeof obj.name === 'string') return obj.name;
    if (obj.username && typeof obj.username === 'string') return obj.username;
    if (obj.email && typeof obj.email === 'string') return obj.email;
    if (obj.id && typeof obj.id === 'string') return obj.id;
    const firstStringValue = Object.values(obj).find((v) => typeof v === 'string');
    if (firstStringValue) return firstStringValue as string;
  }
  return 'Unknown';
};

/**
 * Parses an app reference string (format: "namespace/name") into its parts.
 * Returns null if the format is invalid.
 */
export const parseAppRef = (
  appRef: string | undefined
): { namespace: string; appName: string } | null => {
  if (!appRef) return null;
  const parts = appRef.split('/');
  if (parts.length !== 2) return null;
  return { namespace: parts[0], appName: parts[1] };
};

/**
 * Extracts text content from a response_override object.
 *
 * The response_override follows the OpenAI chat completion format where the
 * content is nested at `choices[0].message.content`.
 *
 * @param responseOverride - The response override object from an annotation
 * @returns The extracted text content, or undefined if not present
 */
const getResponseOverrideContent = (
  responseOverride?: ReviewerAnnotationEventResponseOverride
): string | undefined => {
  if (!responseOverride) return undefined;
  const choices = responseOverride.choices as Array<{ message?: { content?: string } }> | undefined;
  return choices?.[0]?.message?.content?.trim();
};

/**
 * Gets the rewrite content from an annotation, checking both `rewrite` and `response_override`.
 *
 * @param annotation - The reviewer annotation event
 * @returns The rewrite content string, or undefined if no rewrite exists
 */
export const getRewriteFromAnnotation = (
  annotation?: ReviewerAnnotationEvent
): string | undefined => {
  if (!annotation) return undefined;
  const rewrite = annotation.rewrite?.trim();
  const responseOverrideContent = getResponseOverrideContent(annotation.response_override);
  const content = rewrite || responseOverrideContent;
  return content || undefined;
};
