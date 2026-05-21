// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { z } from 'zod';

export const annotationFormFields = z
  .object({
    modelResponse: z.string().optional(),
    thumb: z.enum(['positive', 'negative']).optional(),
    rating: z.number().min(0).max(1).optional(),
    responseOverride: z.record(z.string(), z.unknown()).optional(),
    hasChanges: z.boolean().optional(), // Need to use a specific field path to store root error
  })
  .refine(
    (data) => {
      return (
        data.thumb !== undefined || data.rating !== undefined || data.responseOverride !== undefined
      );
    },
    {
      path: ['hasChanges'],
      message: 'At least one of thumb, rating, or response override must be provided',
    }
  );
