// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { ModelEntity } from '@nemo/sdk/generated/platform/schema';

export type ImportActionsSource = 'library' | 'dataset';

/**
 * Returns true if the user can create a Model from the Prompt Tuning Form using the given model as the base model.
 */
export const isAllowedBaseModel = (model: ModelEntity, project: string) => {
  if (model.prompt) {
    return false;
  }

  const isBaseModel = !model.base_model;
  const isCustomizedModelForProject = !!model.adapters && model.project === project;

  return isBaseModel || isCustomizedModelForProject;
};
