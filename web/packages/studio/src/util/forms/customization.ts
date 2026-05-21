// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { getURNFromNamedEntityRef } from '@nemo/common/src/namedEntity';
import { FilesetOutput } from '@nemo/sdk/generated/platform/schema';
import { CustomizationJobRequest } from '@nemo/sdk/vendored/customizer/schema';

export interface CustomizerHyperparameters {
  batch_size: number;
  epochs: number;
  learning_rate: number;
  hidden_dropout: number;
  attention_dropout: number;
  ffn_dropout: number;
  weight_decay: number;
  // P-tuning only
  virtual_tokens: number;
  // Lora only
  adapter_dim: number;
  adapter_dropout: number;
}

export interface NewCustomizationFormFields extends CustomizerHyperparameters {
  project: string;
  base_model_id: string;
  description: string;
  training_type: string;
  finetuning_type: string;
  dataset?: FilesetOutput;
  distillation?: Record<string, unknown>;
  trainingFileExists?: boolean;
  validationFileExists?: boolean;
}

/**
 * Maps the new customization form data to a Platform CustomizationJobRequest object.
 * Platform API uses spec.model, spec.training (union), not model_entity/hyperparameters.
 */
export const formToCustomizationCreate = (
  formData: NewCustomizationFormFields
): CustomizationJobRequest => {
  const datasetURI = formData.dataset ? getURNFromNamedEntityRef(formData.dataset) || '' : '';

  const training =
    formData.finetuning_type === 'lora'
      ? {
          type: 'sft' as const,
          batch_size: formData.batch_size,
          epochs: formData.epochs,
          learning_rate: formData.learning_rate,
          weight_decay: formData.weight_decay,
          peft: {
            type: 'lora' as const,
            rank: formData.adapter_dim,
            dropout: formData.adapter_dropout,
          },
        }
      : {
          type: 'sft' as const,
          batch_size: formData.batch_size,
          epochs: formData.epochs,
          learning_rate: formData.learning_rate,
          weight_decay: formData.weight_decay,
        };

  return {
    project: formData.project,
    description: formData.description,
    spec: {
      model: formData.base_model_id,
      dataset: datasetURI,
      training,
    },
  };
};
