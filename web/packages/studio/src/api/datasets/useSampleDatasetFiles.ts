// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { BASE_URL } from '@studio/constants/environment';
import { SampleDataset, SampleDatasetFile } from '@studio/constants/sampleDatasets';
import { queryOptions, useQuery, UseQueryOptions, useSuspenseQuery } from '@tanstack/react-query';

/**
 * Fetches a file from the public directory and converts it to a File object
 */
async function fetchSampleFile(fileConfig: SampleDatasetFile): Promise<File> {
  try {
    const baseUrl = BASE_URL.replace(/\/$/, '');
    const response = await fetch(`${baseUrl}/${fileConfig.path}`);
    if (!response.ok) {
      throw new Error(`Failed to fetch ${fileConfig.path}: ${response.statusText}`);
    }

    const blob = await response.blob();
    return new File([blob], fileConfig.name, {
      type: response.headers.get('content-type') || 'application/octet-stream',
    });
  } catch (error) {
    throw new Error(
      `Error loading sample file ${fileConfig.name}: ${error instanceof Error ? error.message : 'Unknown error'}`
    );
  }
}

/**
 * Loads all files for a sample dataset and returns them as File objects
 * suitable for upload via fileset APIs.
 */
async function loadSampleDatasetFiles(sampleDataset: SampleDataset): Promise<File[]> {
  try {
    const filePromises = sampleDataset.files.map(fetchSampleFile);
    return await Promise.all(filePromises);
  } catch (error) {
    throw new Error(
      `Failed to load sample dataset "${sampleDataset.name}": ${error instanceof Error ? error.message : 'Unknown error'}`
    );
  }
}

interface UseSampleDatasetFilesParams {
  sampleDataset: SampleDataset;
}

export const getSampleDatasetFilesQueryKey = (sampleDatasetId: string) => [
  'sample-dataset-files',
  sampleDatasetId,
];

export type UseSampleDatasetFilesOptions = Omit<
  UseQueryOptions<File[], Error>,
  'queryFn' | 'queryKey'
> &
  UseSampleDatasetFilesParams;

export const useSampleDatasetFilesQueryOptions = ({ sampleDataset }: UseSampleDatasetFilesParams) =>
  queryOptions<File[], Error>({
    queryKey: getSampleDatasetFilesQueryKey(sampleDataset.id),
    queryFn: () => loadSampleDatasetFiles(sampleDataset),
  });

/**
 * A wrapper for useQuery that loads sample dataset files as File objects
 * ready for upload via fileset APIs.
 */
export const useSampleDatasetFiles = ({
  sampleDataset,
  ...options
}: UseSampleDatasetFilesOptions) => {
  return useQuery({
    ...useSampleDatasetFilesQueryOptions({ sampleDataset }),
    ...options,
  });
};

/**
 * A wrapper for useSuspenseQuery that loads sample dataset files as File objects
 * ready for upload via fileset APIs.
 */
export const useSampleDatasetFilesSuspense = ({
  sampleDataset,
  ...options
}: UseSampleDatasetFilesOptions) => {
  return useSuspenseQuery({
    ...useSampleDatasetFilesQueryOptions({ sampleDataset }),
    ...options,
  });
};
