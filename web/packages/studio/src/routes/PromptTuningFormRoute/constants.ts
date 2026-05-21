// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

export const SAVE_SUCCESS_MSG = 'Configuration successfully saved.';
export const PROMPT_TUNING_HEADING_TEXT = 'Prompt Tune a Model';
export const SYSTEM_PROMPT_SIZE_ERROR =
  'Your system prompt and learning examples exceed the 10kB limit. Shorten the system prompt or use fewer learning examples.';
/** File limit for system_prompt to avoid overloading models */
export const SYSTEM_PROMPT_BYTES_LIMIT = 10000;
