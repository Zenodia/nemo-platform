// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { useEvaluationGetMetricJob } from '@nemo/sdk/generated/platform/api';
import {
  useAggregatedEvaluationResults,
  useAggregatedEvaluations,
} from '@studio/api/evaluation/details/useAggregatedEvaluations';
import { useParams } from 'react-router-dom';

export const useComparisonResults = () => {
  const { id = '', workspace = '' } = useParams();

  const { data: evaluationData, isLoading, error } = useEvaluationGetMetricJob(workspace, id);

  // Extract metric reference from v2 job spec
  const metricRef =
    typeof evaluationData?.spec?.metric === 'string' ? evaluationData.spec.metric : undefined;
  const [metricWorkspace, metricName] = metricRef?.split('/') || ['', ''];

  const {
    data: aggData,
    error: aggError,
    isLoading: isAggregationLoading,
  } = useAggregatedEvaluations({
    workspace: metricWorkspace,
    name: metricName,
  });
  const {
    data: aggResults,
    error: aggResultsError,
    isLoading: isResultsLoading,
  } = useAggregatedEvaluationResults({
    workspace: metricWorkspace,
    name: metricName,
  });

  if (error || !evaluationData) {
    return {};
  }

  return {
    data: aggData,
    results: aggResults,
    error: aggError || aggResultsError,
    isLoading: isLoading || isAggregationLoading || isResultsLoading,
  };
};
