// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { getColorsFromLength } from '@nemo/common/src/utils/formatters';
import { type AggregateScores } from '@studio/hooks/evaluation/useEvaluationJobResultV2';
import { type EvaluationJobV2 } from '@studio/selectors/evaluationJob';

export type JobAndResultV2 = {
  job: EvaluationJobV2;
  color?: string;
  result?: AggregateScores;
};

interface UseJobsAndResultsV2Props {
  jobs: EvaluationJobV2[];
  results: (AggregateScores | undefined)[];
  filter: {
    metrics: string[];
  };
  prettifyName?: (name: string) => string;
}

interface UseJobsAndResultsV2Return {
  rows: JobAndResultV2[];
  allMetrics: string[];
  activeMetrics: string[];
}

/**
 * V2 version of useJobsAndResults that works with artifact-based aggregate scores
 */
export const useJobsAndResultsV2 = ({
  jobs,
  results,
  filter,
  prettifyName,
}: UseJobsAndResultsV2Props): UseJobsAndResultsV2Return => {
  const combined = jobs.map((job, idx) => ({
    job,
    result: results[idx],
  }));

  const colorList = getColorsFromLength(combined.length);
  const allRowsWithColors = combined.map((row, idx) => ({ ...row, color: colorList[idx] }));

  // Extract all metric names from all results
  const metricOpts = Array.from(
    new Set(
      combined
        .map((row) => {
          if (!row.result?.scores) return [];
          return Object.keys(row.result.scores).map((metricName) => {
            return prettifyName ? prettifyName(metricName) : metricName;
          });
        })
        .flat()
    )
  );

  const metricsToShow = metricOpts.filter((opt) => !filter.metrics.includes(opt));

  // Filter results based on selected metrics
  const allRowsWithFilteredMetrics = allRowsWithColors.map((row) => {
    if (!row.result?.scores) {
      return row;
    }

    const filteredScores: Record<string, Record<string, number>> = {};

    Object.entries(row.result.scores).forEach(([metricName, metricScores]) => {
      const prettifiedMetricName = prettifyName ? prettifyName(metricName) : metricName;
      if (metricsToShow.includes(prettifiedMetricName)) {
        filteredScores[prettifiedMetricName] = metricScores;
      }
    });

    return {
      ...row,
      result: {
        scores: filteredScores,
      },
    };
  });

  return {
    rows: allRowsWithFilteredMetrics,
    allMetrics: metricOpts,
    activeMetrics: metricsToShow,
  };
};
