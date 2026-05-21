// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { z } from 'zod';

export const iclFewShotExamplesSchema = z.array(
  z.object({
    content: z.string(),
    fileName: z.string(),
  })
);
export type iclFewShotExamplesType = z.infer<typeof iclFewShotExamplesSchema>;

export const parseICLExamples = (
  iclFewShotExamples: iclFewShotExamplesType,
  delimiter: string
): string => {
  return iclFewShotExamples.map((icl) => icl.content).join(delimiter);
};
