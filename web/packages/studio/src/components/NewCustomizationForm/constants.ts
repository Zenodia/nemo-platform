// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import {
  distillationSchema,
  dpoSchema,
  hyperparametersSchema,
  loraSchema,
} from '@nemo/common/src/components/TrainingParameterSlider/types';
import type { CustomizationJobInput } from '@nemo/sdk/vendored/customizer/schema';
import { CustomizationCreateJobBody } from '@nemo/sdk/vendored/customizer/zod';
import { z } from 'zod';

export type TrainingType = NonNullable<CustomizationJobInput['training']['type']>;
type TrainingConfig = z.infer<typeof CustomizationCreateJobBody>['spec']['training'];

export interface TrainingMethodOption {
  type: TrainingType;
  label: string;
  description: string;
}

export const TRAINING_METHOD_OPTIONS: TrainingMethodOption[] = [
  {
    type: 'sft',
    label: 'SFT',
    description: 'Supervised Fine-tuning learns from labeled instruction response examples.',
  },
  {
    type: 'dpo',
    label: 'DPO',
    description: 'Direct Preference Optimization uses chosen/rejected pairs to align models.',
  },
];

export const DEFAULT_LORA_VALUES = loraSchema.parse({});

export const TRAINING_DEFAULTS_BY_TYPE: Record<TrainingType, TrainingConfig> = {
  sft: { ...hyperparametersSchema.parse({}), peft: DEFAULT_LORA_VALUES },
  dpo: dpoSchema.parse({}),
  distillation: distillationSchema.parse({ teacher_model: '' }),
};

export const NEW_CUSTOMIZATION_FORM_HYP_DEFAULT_VALUES = TRAINING_DEFAULTS_BY_TYPE.sft;

export const isTrainingType = (value: string): value is TrainingType =>
  TRAINING_METHOD_OPTIONS.some((o) => o.type === value);
