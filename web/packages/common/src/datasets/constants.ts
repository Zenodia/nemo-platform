// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import type { FilesetOutput } from '@nemo/sdk/generated/platform/schema';

/**
 * Regex pattern for valid fileset names.
 * Fileset names must only contain alphanumeric characters, dots, underscores, and dashes.
 */
export const FILESET_NAME_REGEX = /^[\w\-.]+$/;

/**
 * @deprecated Use FILESET_NAME_REGEX instead
 */
export const DATASET_NAME_REGEX = FILESET_NAME_REGEX;

export class FilesetFileUploadError extends Error {
  constructor(
    public fileset: FilesetOutput,
    public files: File[]
  ) {
    const mappedFileNames = files.map((file) => file.name);
    super(`Error while uploading files: ${mappedFileNames.join(', ')}`);
  }
}

/**
 * Returns the name of the automatically created dataset for a workspace
 * @param workspace - The workspace the dataset belongs to
 * @returns The name of the automatically created dataset for the workspace
 */
export const getWorkspaceDatasetName = (workspace: string): string => {
  return `dataset-${workspace}`;
};
