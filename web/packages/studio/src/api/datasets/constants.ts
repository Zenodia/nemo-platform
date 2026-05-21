// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

export const ALLOWED_CONTENT_FILE_TYPES = new Set(['csv', 'json', 'jsonl', 'parquet']); // File types that are supported in-memory for manipulation.
export const COMPLETION_PROMPT_KEY_ORDER = ['prompt', 'instruction', 'question']; // Searches for a prompt in the following keys
