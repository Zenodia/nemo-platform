// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0
import { evaluationListMetricJobs } from '@nemo/sdk/generated/platform/api';
import { EvaluationListMetricJobsParams } from '@nemo/sdk/generated/platform/schema';
import { EvaluationJobWithTaskMetrics } from '@studio/api/evaluation/useEvaluationsWithMetrics';

export interface FetchEvaluationsWithMetricsOptions {
  workspace: string;
  query?: EvaluationListMetricJobsParams;
  signal?: AbortSignal;
}

export const fetchEvaluationsWithMetrics = async ({
  workspace,
  query,
  signal,
}: FetchEvaluationsWithMetricsOptions) => {
  const evaluations = await evaluationListMetricJobs(workspace, query, signal);
  if (evaluations.data?.length > 0) {
    const evaluationsWithMetrics = await Promise.all(
      evaluations.data.map(async (evaluation) => {
        try {
          if (!evaluation.workspace) {
            return evaluation;
          }
          if (!evaluation.name) {
            return evaluation;
          }

          const evaluationWithMetrics: EvaluationJobWithTaskMetrics = { ...evaluation, tasks: {} };
          // TODO: Download results
          // const evaluationResult = await getEvaluationResult(
          //   evaluation.workspace,
          //   evaluation.id!,
          //   evaluation.name,
          //   signal
          // );
          // if (evaluationResult.download_url) {
          // }
          return evaluationWithMetrics;
        } catch {
          // if an eval job failed, there will be a 404 returned by fetchEvaluationResults
          // return the original evaluation if there's an error
          return evaluation;
        }
      })
    );
    return { ...evaluations, data: evaluationsWithMetrics };
  }
  return evaluations;
};
