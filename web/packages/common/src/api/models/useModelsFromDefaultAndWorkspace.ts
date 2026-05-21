// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import {
  ModelsListModelsParams,
  ModelEntitysPage,
  ModelEntity,
  ModelEntityFilter,
} from '@nemo/sdk/generated/platform/schema';
import { UseQueryOptions } from '@tanstack/react-query';
import { useEffect, useMemo } from 'react';

import {
  BASIC_ALL_MODELS_DROPDOWN_FILTER,
  buildWorkspaceGroup,
  ModelWorkspaceGroup,
  useModelsInfinite,
} from './useModels';

// The workspace that contributes shared/global base models.
// Change this value if the shared workspace name changes (e.g. "default" → "system").
const SHARED_MODELS_WORKSPACE = 'default';

// Filter for the shared workspace: base models only (finetuning_type=null means NIM/base model,
// not a full-weight finetuned model; prompt=false excludes prompt-tuned models).
// Note: adapters=false is NOT used here because base models have adapters:[] (empty array, not null),
// and the backend filter checks for null, not empty array.
const SHARED_WORKSPACE_FILTER: ModelEntityFilter = {
  finetuning_type: false,
  prompt: false,
};

export interface UseModelsFromDefaultAndWorkspaceOptions {
  queryOptions?: Omit<UseQueryOptions<ModelEntitysPage, Error>, 'queryFn' | 'queryKey'>;
  /** Applied to both workspaces. The shared workspace additionally merges SHARED_WORKSPACE_FILTER into the filter. */
  query?: ModelsListModelsParams;
  workspace: string | null;
}

/**
 * Fetches and combines models from both the shared workspace and the specified workspace.
 *
 * Two-workspace strategy for model dropdowns:
 * - Shared workspace (SHARED_MODELS_WORKSPACE): uses the caller-provided query with
 *   SHARED_WORKSPACE_FILTER merged in (base models only — no prompt, no finetuning_type)
 * - Current workspace: uses the caller-provided query as-is
 * - Filters for available models (model_providers.length > 0 → deployment reached READY)
 * - No deduplication — same model URN may appear under both workspace groups
 * - Returns grouped structure: workspace → namespace → models (for dropdowns)
 *
 * Endpoints:
 * - GET /apis/models/v2/workspaces/{SHARED_MODELS_WORKSPACE}/models
 * - GET /apis/models/v2/workspaces/{workspace}/models
 */
export const useModelsFromDefaultAndWorkspace = (
  options: UseModelsFromDefaultAndWorkspaceOptions
) => {
  const { workspace, query, queryOptions } = options;

  // Shared workspace: apply the caller's full query, but also enforce the base-model filter.
  const sharedWorkspaceResult = useModelsInfinite({
    workspace: SHARED_MODELS_WORKSPACE,
    query: {
      ...BASIC_ALL_MODELS_DROPDOWN_FILTER,
      ...query,
      filter: { ...SHARED_WORKSPACE_FILTER, ...query?.filter },
    },
    queryOptions,
  });

  // Current workspace: caller's query with caller's filter
  const currentWorkspaceResult = useModelsInfinite({
    workspace: workspace ?? undefined,
    query,
    queryOptions: {
      ...queryOptions,
      enabled: queryOptions?.enabled !== false && !!workspace,
    },
  });

  // Auto-fetch next pages for both
  const {
    isFetching: isSharedFetching,
    hasNextPage: sharedHasNext,
    fetchNextPage: fetchSharedNext,
  } = sharedWorkspaceResult;
  useEffect(() => {
    if (!isSharedFetching && sharedHasNext) {
      fetchSharedNext();
    }
  }, [isSharedFetching, sharedHasNext, fetchSharedNext]);

  const {
    isFetching: isCurrentFetching,
    hasNextPage: currentHasNext,
    fetchNextPage: fetchCurrentNext,
  } = currentWorkspaceResult;
  useEffect(() => {
    if (!isCurrentFetching && currentHasNext) {
      fetchCurrentNext();
    }
  }, [isCurrentFetching, currentHasNext, fetchCurrentNext]);

  // Build grouped structure: current workspace first, then shared workspace
  const groups = useMemo((): ModelWorkspaceGroup[] => {
    const flattenPages = (result: typeof sharedWorkspaceResult): ModelEntity[] =>
      result.data?.pages.flatMap((page) => (Array.isArray(page.data) ? page.data : [])) ?? [];

    const isAvailable = (model: ModelEntity) =>
      Array.isArray(model.model_providers) && model.model_providers.length > 0;

    const sharedModels = flattenPages(sharedWorkspaceResult).filter(isAvailable);
    const currentModels = flattenPages(currentWorkspaceResult).filter(isAvailable);

    const result: ModelWorkspaceGroup[] = [];

    if (workspace && currentModels.length > 0) {
      result.push(buildWorkspaceGroup(workspace, currentModels));
    }

    if (sharedModels.length > 0 && workspace !== SHARED_MODELS_WORKSPACE) {
      result.push(buildWorkspaceGroup(SHARED_MODELS_WORKSPACE, sharedModels));
    }

    return result;
    // eslint-disable-next-line react-hooks/exhaustive-deps -- only recompute when page data or workspace changes, not on fetch-status updates
  }, [sharedWorkspaceResult.data, currentWorkspaceResult.data, workspace]);

  return {
    groups,
    isFetching:
      sharedWorkspaceResult.isFetching ||
      currentWorkspaceResult.isFetching ||
      sharedWorkspaceResult.hasNextPage ||
      currentWorkspaceResult.hasNextPage,
    isError: sharedWorkspaceResult.isError || currentWorkspaceResult.isError,
    error: sharedWorkspaceResult.error ?? currentWorkspaceResult.error,
  };
};
