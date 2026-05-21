// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

/**
 * Stainless headers, set by OpenAI's chat completions client, can break CORS.
 * You can reuse this object to remove them from the headers object passed to the OpenAI client.
 */
export const CHAT_CORS_HEADERS = {
  'x-stainless-os': null,
  'x-stainless-arch': null,
  'x-stainless-lang': null,
  'x-stainless-package-version': null,
  'x-stainless-retry-count': null,
  'x-stainless-runtime': null,
  'x-stainless-runtime-version': null,
  'x-stainless-timeout': null,
};

/**
 * Custom error class for when a model name is missing from the chat request
 */
export class ChatMissingModelError extends Error {
  constructor() {
    super('Chat requires model name.');
  }
}
