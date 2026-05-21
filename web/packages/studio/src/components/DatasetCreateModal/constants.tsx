// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { DEFAULT_NAMESPACE } from '@studio/constants/constants';
import { datasetSchema } from '@studio/constants/zod';
import { z } from 'zod';

export const datasetCreateFormSchema = z.object({
  dataset: datasetSchema,
  folderPrefix: z.string().optional(),
  files: z.array(z.instanceof(File)).optional(),
});

export type DatasetCreateFormData = z.infer<typeof datasetCreateFormSchema>;

export const DATASET_CREATE_DEFAULT_VALUES: DatasetCreateFormData = {
  dataset: {
    name: '',
    namespace: DEFAULT_NAMESPACE,
    description: '',
  },
  folderPrefix: '',
  files: [],
};

// https://developer.mozilla.org/en-US/docs/Web/HTTP/MIME_types/Common_types

export enum DatasetCreateModalMode {
  DatasetAndFiles = 'DatasetAndFiles',
  Dataset = 'Dataset',
  Edit = 'Edit',
  Files = 'Files',
}

export const DATASET_CREATE_MODAL_CONTENT: Record<
  DatasetCreateModalMode,
  { title: string; instruction: string; action: string; successToast: string }
> = {
  [DatasetCreateModalMode.DatasetAndFiles]: {
    title: 'Create New Dataset',
    instruction: 'To create a new dataset, simply provide a name, description, and relevant files.',
    action: 'Create Dataset',
    successToast: 'Successfully created dataset!',
  },
  [DatasetCreateModalMode.Dataset]: {
    title: 'Create New Dataset',
    instruction: 'To create a new dataset, simply provide a name and description.',
    action: 'Create Dataset',
    successToast: 'Successfully created dataset!',
  },
  [DatasetCreateModalMode.Edit]: {
    title: 'Edit Dataset',
    instruction: '',
    action: 'Save',
    successToast: 'Successfully updated dataset!',
  },
  [DatasetCreateModalMode.Files]: {
    title: 'Upload New Files',
    instruction: 'Select some files to upload to your dataset.',
    action: 'Upload Files',
    successToast: 'Successfully uploaded files!',
  },
};
