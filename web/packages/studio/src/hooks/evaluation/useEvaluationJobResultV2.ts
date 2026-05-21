// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { useEvaluationGetMetricJobsResults } from '@nemo/sdk/generated/platform/api';
import { useQuery } from '@tanstack/react-query';

/**
 * Structure of V2 aggregate scores result
 */
export interface AggregateScores {
  scores: Record<string, Record<string, number>>;
}

/**
 * Hook to fetch and parse V2 evaluation job aggregate scores
 */
export const useEvaluationJobResultV2 = (workspace: string, jobName: string) => {
  // Fetch aggregate scores result metadata
  const {
    data: aggregateScoresResult,
    isLoading: isLoadingMetadata,
    error: metadataError,
  } = useEvaluationGetMetricJobsResults(workspace, jobName, 'aggregate-scores', {
    query: {
      enabled: !!workspace && !!jobName,
    },
  });

  // Fetch and parse the actual scores from the download URL
  const {
    data: scores,
    isLoading: isLoadingScores,
    error: scoresError,
  } = useQuery({
    queryKey: [
      'evaluation-job-result-scores',
      workspace,
      jobName,
      aggregateScoresResult?.download_url,
    ],
    queryFn: async () => {
      if (!aggregateScoresResult?.download_url) {
        throw new Error('No download URL available');
      }

      const response = await fetch(aggregateScoresResult.download_url);
      if (!response.ok) {
        throw new Error(`Failed to download results: ${response.statusText}`);
      }

      const data: AggregateScores = await response.json();
      return data;
    },
    enabled: !!aggregateScoresResult?.download_url,
  });

  return {
    result: aggregateScoresResult,
    scores,
    isLoading: isLoadingMetadata || isLoadingScores,
    error: metadataError || scoresError,
  };
};
