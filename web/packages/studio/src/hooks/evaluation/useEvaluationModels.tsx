// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { BASIC_ALL_MODELS_DROPDOWN_FILTER } from '@nemo/common/src/api/models/useModels';
import { useModelsFromWorkspace } from '@nemo/common/src/api/models/useModelsFromWorkspace';
import { getURNFromNamedEntityRef } from '@nemo/common/src/namedEntity';
import { filterModel } from '@nemo/common/src/utils/models';
import type { Adapter, ModelEntity } from '@nemo/sdk/generated/platform/schema';
import { useWorkspaceFromPath } from '@studio/hooks/useWorkspaceFromPath';
import { useMemo } from 'react';

export interface EvaluationModelItem {
  model: ModelEntity;
  adapter?: Adapter;
  /** "modelName" or "modelName / adapterName" */
  label: string;
  /** URN for models, "URN::adapterName" for adapters */
  value: string;
}

const buildItems = (models: ModelEntity[], search?: string): EvaluationModelItem[] => {
  const lowerSearch = search?.toLowerCase();
  const items: EvaluationModelItem[] = [];

  for (const model of models) {
    const urn = getURNFromNamedEntityRef(model);
    if (!urn) continue;

    const modelMatches = filterModel(model, search);

    if (modelMatches) {
      items.push({ model, label: model.name, value: urn });
    }

    if (model.adapters) {
      for (const adapter of model.adapters) {
        if (adapter.enabled === false) continue;

        const adapterMatches =
          modelMatches || (lowerSearch && adapter.name.toLowerCase().includes(lowerSearch));
        if (!adapterMatches) continue;

        items.push({
          model,
          adapter,
          label: `${model.name} / ${adapter.name}`,
          value: `${urn}::${adapter.name}`,
        });
      }
    }
  }

  return items;
};

export const useEvaluationModels = ({
  enabled,
  search,
}: {
  enabled?: boolean;
  search?: string;
}) => {
  const workspace = useWorkspaceFromPath();

  const { groups, isFetching, error } = useModelsFromWorkspace({
    workspace: workspace ?? null,
    query: BASIC_ALL_MODELS_DROPDOWN_FILTER,
    queryOptions: { enabled },
  });

  const allModels = useMemo(() => groups.flatMap((group) => group.models), [groups]);

  const items = useMemo(() => buildItems(allModels, search), [allModels, search]);

  return {
    /** Flat list of model + adapter items for the dropdown */
    items,
    /** Raw ModelEntity list (needed to look up parent models on submit) */
    models: allModels,
    isLoading: isFetching,
    error,
  };
};
