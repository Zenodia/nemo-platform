// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import type { ModelEntityFilter } from '@nemo/sdk/generated/platform/schema';
import { useMemo } from 'react';

import { useAllModels } from './useModels';
import { DEFAULT_NAMESPACE } from '../../constants';
import { DEFAULT_PAGE_SIZE } from '../../constants/api';
import { isBaseModel } from '../../utils/models';

export interface UsePromptTunableBaseModelIdsOptions {
  workspace: string;
}

// The prompt-tunable query intentionally sends only `lora_enabled: true` — a
// backend filter-combination bug breaks results when other filter keys are
// included.
const PROMPT_TUNABLE_QUERY = {
  filter: { lora_enabled: true } as ModelEntityFilter,
  page_size: DEFAULT_PAGE_SIZE,
};

/**
 * Fetches the set of base-model ids whose deployments have LoRA enabled
 * (i.e. are prompt-tunable) across the current workspace and the default
 * workspace. Returns a `Set<string>` so consumers can do O(1) id membership
 * checks against another list of models (e.g. to render a "Prompt-Tunable"
 * badge on cards in the displayed base-models list).
 *
 * Auto-fetches every page so the returned Set is complete; without this,
 * matches past the first page would silently be missed.
 */
export interface UsePromptTunableBaseModelIdsResult {
  promptTunableIds: Set<string>;
  isLoading: boolean;
}

export function usePromptTunableBaseModelIds({
  workspace,
}: UsePromptTunableBaseModelIdsOptions): UsePromptTunableBaseModelIdsResult {
  const isDefaultWorkspace = workspace === DEFAULT_NAMESPACE;

  const workspaceQuery = useAllModels({
    workspace,
    query: PROMPT_TUNABLE_QUERY,
  });

  const defaultQuery = useAllModels({
    workspace: DEFAULT_NAMESPACE,
    query: PROMPT_TUNABLE_QUERY,
    queryOptions: { enabled: !isDefaultWorkspace },
  });

  const promptTunableIds = useMemo(() => {
    const workspaceModels = workspaceQuery.data?.pages.flatMap((page) => page.data) ?? [];
    const defaultModels = isDefaultWorkspace
      ? []
      : (defaultQuery.data?.pages.flatMap((page) => page.data) ?? []);

    // Defensive `isBaseModel` filter: the request sends only `lora_enabled: true`
    // (a backend filter-combination bug rules out adding `base_model: false`),
    // so adapter entities can appear in the response.
    return new Set([...workspaceModels, ...defaultModels].filter(isBaseModel).map((m) => m.id));
  }, [workspaceQuery.data, defaultQuery.data, isDefaultWorkspace]);

  const isLoading =
    workspaceQuery.isLoading ||
    workspaceQuery.isFetching ||
    Boolean(workspaceQuery.hasNextPage) ||
    (!isDefaultWorkspace &&
      (defaultQuery.isLoading || defaultQuery.isFetching || Boolean(defaultQuery.hasNextPage)));

  return { promptTunableIds, isLoading };
}
