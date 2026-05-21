// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { useQueryParams } from '@nemo/common/src/hooks/useQueryParams';
import { useEvaluationGetMetric } from '@nemo/sdk/generated/platform/api';
import type { EvaluationConfig } from '@studio/selectors/evaluationConfig';

/**
 * EvaluationConfig with guaranteed non-null name and namespace.
 * When fetched via URL params, these fields are always present.
 */
type HydratedEvaluationConfig = EvaluationConfig & {
  name: string;
  namespace: string;
};

/**
 * Hook for managing selected evaluation config state via URL query parameter.
 *
 * URL param format: `?selectedEvaluationConfig=namespace/configName`
 *
 * @example
 * const { selectedEvaluationConfig, setSelectedEvaluationConfig, resetSelectedEvaluationConfig } = useSelectedEvaluationConfigFromUrl();
 */
export const useSelectedEvaluationConfigFromUrl = () => {
  const { getQueryParam, setQueryParam, removeQueryParam } = useQueryParams();
  const selectedEvaluationConfigParam = getQueryParam('selectedEvaluationConfig');

  // Parse namespace and configName from the full name (format: "namespace/configName")
  const [workspace, configName] = selectedEvaluationConfigParam?.split('/') || ['', ''];

  // Fetch the metric config using platform API (workspace = namespace for URL)
  const {
    data: selectedEvaluationConfig,
    isLoading,
    isError,
    error,
  } = useEvaluationGetMetric(workspace, configName, {
    query: {
      enabled: !!selectedEvaluationConfigParam && !!workspace && !!configName,
    },
  });

  /**
   * Set the selected evaluation config by updating the URL param
   */
  const setSelectedEvaluationConfig = (config: EvaluationConfig) => {
    const name = config.name ?? '';
    const ns = (config as { namespace?: string }).namespace ?? config.workspace ?? '';
    setQueryParam('selectedEvaluationConfig', `${ns}/${name}`);
  };

  /**
   * Clear the selected evaluation config by removing the URL param
   */
  const resetSelectedEvaluationConfig = () => {
    removeQueryParam('selectedEvaluationConfig');
  };

  return {
    selectedEvaluationConfig: selectedEvaluationConfig as HydratedEvaluationConfig | undefined,
    setSelectedEvaluationConfig,
    resetSelectedEvaluationConfig,
    isLoading,
    isError,
    error,
  };
};
