// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import {
  intersection,
  SEQUENTIAL_DISTRIBUTION_ERROR_MESSAGE,
  SEQUENTIAL_DISTRIBUTION_KEYS,
} from '@studio/util/list';
import { z } from 'zod';

export interface AdvancedFileSplitOptions {
  sortKey?: string;
  seed?: string;
}
export type CreateFileSplitsFormFields = {
  filepath: string;
  splitDescriptor: string;
  training: number;
  testing: number;
  validation: number;
  distributionType: 'random' | 'sequential';
  schemaKeys?: string[];
} & AdvancedFileSplitOptions;

export const createFileSplitsSchema = z
  .object({
    filepath: z.string(),
    splitDescriptor: z.string(),
    training: z.number().min(0).max(100),
    testing: z.number().min(0).max(100),
    validation: z.number().min(0).max(100),
    distributionType: z.enum(['random', 'sequential']),
    seed: z.string().optional(),
    sortKey: z.string().optional(),
    schemaKeys: z.array(z.string()).optional(),
  })
  .refine(
    (data) => {
      const total = data.training + data.testing + data.validation;
      return Math.abs(total - 100) < 0.01; // Allow for small floating point errors
    },
    {
      message: 'Training, testing, and validation percentages must sum to 100%',
      path: ['training'],
    }
  )
  .refine(
    (data) => {
      if (data.distributionType === 'sequential') {
        const schemaKeys = data.schemaKeys ?? [];
        const sortKey = data.sortKey ?? '';
        return (
          intersection(schemaKeys, SEQUENTIAL_DISTRIBUTION_KEYS).length > 0 ||
          schemaKeys.includes(sortKey)
        );
      }
      return true;
    },
    {
      message: SEQUENTIAL_DISTRIBUTION_ERROR_MESSAGE,
      path: ['distributionType'],
    }
  );
