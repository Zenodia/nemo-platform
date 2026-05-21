// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import {
  getModelEntityChatStatus,
  MODEL_DEPLOYMENT_GRACE_PERIOD_MS,
  type GetModelEntityChatStatusOptions,
  type ModelChatStatus,
} from '@nemo/common/src/utils/models';
import type { ModelEntity } from '@nemo/sdk/generated/platform/schema';
import { useEffect, useState } from 'react';

function optionsSignature(options: GetModelEntityChatStatusOptions | undefined): string {
  if (options === undefined) {
    return '';
  }
  const { adapter, deploymentLoading, deploymentStatus } = options;
  return JSON.stringify({
    adapterName: adapter?.name ?? null,
    deploymentLoading: deploymentLoading ?? false,
    deploymentStatus: deploymentStatus ?? '∅',
  });
}

function resolveChatStatus(
  model: ModelEntity | null | undefined,
  statusOptions?: GetModelEntityChatStatusOptions
): ModelChatStatus {
  if (model) {
    return getModelEntityChatStatus(model, statusOptions);
  }
  // e.g. base model entity still loading for `model.base_model` — do not treat as "no selection"
  if (statusOptions?.deploymentLoading) {
    return 'pending';
  }
  return 'enabled';
}

/**
 * Live {@link ModelChatStatus} for a model selection via {@link getModelEntityChatStatus}.
 * When the status is `pending`, schedules one re-check after {@link MODEL_DEPLOYMENT_GRACE_PERIOD_MS}
 * (e.g. to exit creation grace without remounting).
 */
export function useModelEntityChatStatusWithGrace(
  model: ModelEntity | null | undefined,
  statusOptions?: GetModelEntityChatStatusOptions
): ModelChatStatus {
  const optionsKey = optionsSignature(statusOptions);

  const [status, setStatus] = useState<ModelChatStatus>(() =>
    resolveChatStatus(model, statusOptions)
  );

  useEffect(() => {
    const next = resolveChatStatus(model, statusOptions);
    setStatus(next);
    if (next !== 'pending') {
      return undefined;
    }
    const timeoutId = window.setTimeout(() => {
      setStatus(resolveChatStatus(model, statusOptions));
    }, MODEL_DEPLOYMENT_GRACE_PERIOD_MS);
    return () => window.clearTimeout(timeoutId);
    // eslint-disable-next-line react-hooks/exhaustive-deps -- optionsKey encodes statusOptions; listing statusOptions would reset the grace timeout every render for inline `{}` args.
  }, [model, optionsKey]);

  return status;
}
