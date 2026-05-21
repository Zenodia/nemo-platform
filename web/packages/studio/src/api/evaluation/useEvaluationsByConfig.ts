// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { NamedEntity } from '@nemo/common/src/namedEntity';
import { useEvaluationListMetricJobs } from '@nemo/sdk/generated/platform/api';
import { EvaluationListMetricJobsParams } from '@nemo/sdk/generated/platform/schema';

/**
 * Custom hook to fetch evaluation jobs filtered by configuration.
 * Jobs are sorted by most recently created.
 *
 * @example
 * const { data, isLoading } = useEvaluationsByConfig({
 *   page: 1,
 *   page_size: 10
 * });
 *
 * @returns TanStack Query result with evaluation jobs data
 */
export const useEvaluationsByConfig = (
  workspace: string,
  config: NamedEntity & Partial<EvaluationListMetricJobsParams>
) => {
  const params: EvaluationListMetricJobsParams = {
    page: config.page,
    page_size: config.page_size,
    sort: 'created_at',
    // TODO: Support filtering by config namespace and name
    // config: config.namespace && config.name ? `${config.namespace}/${config.name}` : undefined,
  };

  return useEvaluationListMetricJobs(workspace, params);
};
