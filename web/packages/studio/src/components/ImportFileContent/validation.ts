// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { ALLOWED_CONTENT_FILE_TYPES } from '@studio/api/datasets/constants';
import { z } from 'zod';

// Validation helper for file extensions
const validateFileExtension = (filename: string) => {
  const extension = filename.split('.').pop() ?? '';
  return ALLOWED_CONTENT_FILE_TYPES.has(extension);
};

// Reusable error message for unsupported file types
const getUnsupportedFileTypeMessage = () => ({
  message: `Unsupported file type. Currently supports: ${[...ALLOWED_CONTENT_FILE_TYPES].join(', ')}`,
});

// Zod schema for import file content form
export const importFileContentSchema = z.object({
  file: z
    .instanceof(File)
    .optional()
    .refine((file) => !file || validateFileExtension(file.name), getUnsupportedFileTypeMessage),
  datasetId: z.string().optional(),
  filepath: z
    .string()
    .optional()
    .refine(
      (filepath) => !filepath || validateFileExtension(filepath),
      getUnsupportedFileTypeMessage
    ),
});

export type ImportFileContentFormFields = z.infer<typeof importFileContentSchema>;
