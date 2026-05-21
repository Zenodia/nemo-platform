// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { DEFAULT_NAMESPACE } from '@studio/constants/constants';

const MODEL_NAME_LIMIT = 96;
const CUSTOMIZER_SUFFIX_LENGTH = 28;

interface ModelNameFormData {
  model?: string;
  output?: { name?: string };
  training?: { peft?: unknown };
}

export const refineModelName = (formData: ModelNameFormData): boolean => {
  let newModelName = formData.output?.name;
  if (!newModelName) {
    const model = formData.model || '';
    const peftType = formData.training?.peft ? 'lora' : 'all_weights';
    newModelName = `${model}-${peftType}`;
  } else {
    newModelName = `${DEFAULT_NAMESPACE}/${newModelName}`;
  }
  return newModelName.length + CUSTOMIZER_SUFFIX_LENGTH <= MODEL_NAME_LIMIT;
};

export const refineModelNameConfig = {
  message: 'Model name is too long. Please define a shorter name.',
  path: ['output', 'name'],
};
