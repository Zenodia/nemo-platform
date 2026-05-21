// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

export interface SampleDatasetFile {
  /** Path to the file relative to public/ directory */
  path: string;
  /** Filename that will be used when uploading to the dataset */
  name: string;
  /** File description for UI */
  description?: string;
}

export interface SampleDataset {
  id: string;
  name: string;
  description: string;
  files: SampleDatasetFile[];
  /** Badge or category for the sample dataset */
  category?: string;
}

export const SAMPLE_DATASETS: SampleDataset[] = [
  {
    id: 'qa-generation-dataset',
    name: 'Q&A Generation Dataset',
    description: 'Boost the model performance by using context-enhanced question-answer pairs.',
    category: 'Question Answering',
    files: [
      {
        path: 'sample-datasets/qa-generation/training.jsonl',
        name: 'training/training.jsonl',
        description: 'Training examples for Q&A generation',
      },
      {
        path: 'sample-datasets/qa-generation/validation.jsonl',
        name: 'validation/validation.jsonl',
        description: 'Validation examples for model evaluation',
      },
      {
        path: 'sample-datasets/qa-generation/test.jsonl',
        name: 'test/test.jsonl',
        description: 'Test examples for final evaluation',
      },
    ],
  },
] as const;

export type SampleDatasetId = (typeof SAMPLE_DATASETS)[number]['id'];
