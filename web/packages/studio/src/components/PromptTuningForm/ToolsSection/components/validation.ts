// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { z } from 'zod';

/**
 * Validation schema for adding a single tool
 */
export const addToolFormSchema = z.object({
  json: z.string().min(1, { message: 'Tool function json is required' }),
  file: z.instanceof(File).optional(),
});

export type AddToolFormFields = z.infer<typeof addToolFormSchema>;
