// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { z } from 'zod';

export const mappingSchema = z.object({
  /** Empty key is allowed for the trailing draft row in MappingFields. */
  key: z.string(),
  value: z.string().optional(),
});

export const transformFileSchema = z
  .object({
    filepath: z.string().nonempty('Filepath is required'),
    model: z.string().optional(),
    mappings: z.array(mappingSchema),
  })
  .superRefine((data, ctx) => {
    const keys = new Set<string>();
    for (let i = 0; i < data.mappings.length; i++) {
      const k = data.mappings[i].key.trim();
      if (!k) continue;
      if (keys.has(k)) {
        ctx.addIssue({
          code: z.ZodIssueCode.custom,
          message: 'Mapping keys must be unique.',
          path: ['mappings', i, 'key'],
        });
        break;
      }
      keys.add(k);
    }
  })
  .refine(
    (data) => {
      if (!data.model) {
        return true;
      }
      const hasUserMsg = data.mappings.some(
        (mapping) =>
          mapping.key === 'prompt' || mapping.key === 'instruction' || mapping.key === 'question'
      );
      if (!hasUserMsg) {
        return false;
      }
      return true;
    },
    {
      path: ['model'],
      message:
        'Missing user message for model inference. Please add a mapping with a key of "prompt", "instruction", or "question".',
    }
  );

export type TransformFileFormFields = {
  filepath: string;
  model?: string;
  mappings: z.infer<typeof mappingSchema>[];
};
