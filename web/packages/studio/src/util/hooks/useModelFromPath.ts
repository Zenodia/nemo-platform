// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { getEntityReference } from '@nemo/common/src/namedEntity';
import { ROUTE_PARAMS } from '@studio/constants/routes';
import { useRequiredPathParams } from '@studio/util/hooks/useRequiredPathParams';

/**
 * returns the model namespace, name, and full name from the path, e.g.
 * /models/default/my-model -> { workspace: 'default', modelName: 'my-model', model: 'default/my-model' }
 */
export function useModelFromPath() {
  const { workspace, modelName } = useRequiredPathParams([
    ROUTE_PARAMS.workspace,
    ROUTE_PARAMS.modelName,
  ]);

  return {
    workspace,
    modelName,
    model: getEntityReference({ workspace: workspace, name: modelName }),
  };
}
