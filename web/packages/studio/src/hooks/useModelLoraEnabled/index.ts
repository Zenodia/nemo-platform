// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { useAllModels } from '@nemo/common/src/api/models/useModels';
import type { ModelEntity } from '@nemo/sdk/generated/platform/schema';
import { useMemo } from 'react';

interface UseModelLoraEnabledResult {
  /** Whether the model's deployment config has `lora_enabled=true`. */
  isLoraEnabled: boolean;
  isLoading: boolean;
}

export function useModelLoraEnabled(
  model: ModelEntity | null | undefined
): UseModelLoraEnabledResult {
  const workspace = model?.workspace ?? '';
  const name = model?.name ?? '';
  const enabled = Boolean(workspace && name);

  const { data, isFetching, hasNextPage } = useAllModels({
    workspace,
    query: { filter: { lora_enabled: true }, page_size: 1000, sort: 'name' },
    queryOptions: { enabled },
  });

  const loraEnabledNames = useMemo(
    () => new Set(data?.pages.flatMap((p) => p.data ?? []).map((m) => m.name) ?? []),
    [data?.pages]
  );

  return {
    isLoraEnabled: enabled && loraEnabledNames.has(name),
    // `isFetching || hasNextPage` keeps loading true through the entire
    // pagination sweep — without it, callers would briefly see a partial set
    // between page fetches.
    isLoading: enabled && (isFetching || Boolean(hasNextPage)),
  };
}
