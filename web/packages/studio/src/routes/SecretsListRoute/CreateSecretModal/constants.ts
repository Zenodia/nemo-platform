// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

// TODO get from sdk once issue #4082 is resolved
export const SECRET_NAME_REGEXP = new RegExp('^[a-z](?!.*--)[a-z0-9\\-@.+_]{1,62}(?<!-)$');

export const SECRET_NAME_HELP =
  'Must start with a letter, use 2–63 lowercase letters, numbers, hyphens, underscores, dots, @, or +. No consecutive or ending hyphens.';
