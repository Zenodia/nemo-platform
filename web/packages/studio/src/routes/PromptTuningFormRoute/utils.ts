// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import {
  MODEL_HYPERPARAMETER_FIELD_METADATA,
  modelInferenceParametersSchema,
} from '@nemo/common/src/constants/inferenceParameters';
import {
  DEFAULT_PROMPT_TEMPLATE,
  DEFAULT_PROMPT_TEMPLATE_COMPILED,
} from '@nemo/common/src/models/constants';
import { compileSystemPrompt } from '@nemo/common/src/models/utils';
import { getPartsFromReference } from '@nemo/common/src/namedEntity';
import { toolsArraySchema } from '@nemo/common/src/zod/tools';
import {
  CreateModelEntityRequest,
  FinetuningType,
  ModelEntity,
} from '@nemo/sdk/generated/platform/schema';
import {
  iclFewShotExamplesSchema,
  parseICLExamples,
} from '@studio/components/PromptTuningForm/InContextLearningSection/utils';
import {
  SYSTEM_PROMPT_BYTES_LIMIT,
  SYSTEM_PROMPT_SIZE_ERROR,
} from '@studio/routes/PromptTuningFormRoute/constants';
import { getHumanReadableFileSize, getTextSizeInBytes } from '@studio/util/files';
import { getModelTools } from '@studio/util/models';
import Handlebars from 'handlebars';
import { z } from 'zod';

export const validateSystemPromptTemplate = (template: string) => {
  try {
    Handlebars.precompile(template);
    return true;
  } catch {
    return false;
  }
};

export const validateModelName = (modelName: string) => {
  const matches = modelName.match(/^[a-z0-9-_.@]*$/i);
  return matches ? matches.length > 0 : false;
};

export const promptTuningFormSchema = modelInferenceParametersSchema.extend({
  name: z.string().min(1, 'Model name is required').refine(validateModelName, {
    message: 'Model name must only contain alphanumeric characters or the following symbols: @-_.',
  }),
  description: z.string().optional(),
  baseModel: z.string().min(1, 'Base model is required'),
  systemPromptTemplate: z
    .string()
    .refine(validateSystemPromptTemplate, { message: 'Invalid system prompt template' }),
  systemPrompt: z.string().refine(
    (systemPrompt) => {
      const { validSystemPromptSize } = validateSystemPromptSize(systemPrompt);
      return validSystemPromptSize;
    },
    {
      message: SYSTEM_PROMPT_SIZE_ERROR,
    }
  ),
  iclFewShotExamples: iclFewShotExamplesSchema.optional(),
  tools: toolsArraySchema.optional(),
  toolsEnabled: z.boolean().optional(),
});

export type PromptTuningFormFields = z.infer<typeof promptTuningFormSchema>;

export const DEFAULT_PROMPT_TUNING_FORM_VALUES: PromptTuningFormFields = {
  name: '',
  baseModel: '',
  description: '',
  systemPromptTemplate: DEFAULT_PROMPT_TEMPLATE,
  systemPrompt: DEFAULT_PROMPT_TEMPLATE_COMPILED,
  iclFewShotExamples: [],
  max_tokens: MODEL_HYPERPARAMETER_FIELD_METADATA.max_tokens.default,
  temperature: MODEL_HYPERPARAMETER_FIELD_METADATA.temperature.default,
  top_p: undefined,
  max_completion_tokens: undefined,
  tools: [],
  toolsEnabled: true,
};

export type PromptTuningFormSectionProps = { isEditable?: boolean };

export const iclDelimiter = '\n\n';

/**
 * Validates if a system prompt size is within the allowed limit
 * @param systemPrompt - The system prompt string to validate
 * @returns Object containing validation result and human-readable size
 * @returns validSystemPromptSize - Whether the system prompt size is within the allowed limit
 * @returns systemPromptSize - Human-readable size of the system prompt (e.g., "5.2 KB")
 */

export const validateSystemPromptSize = (
  systemPrompt: string
): {
  validSystemPromptSize: boolean;
  systemPromptSize: string;
} => {
  const systemPromptBytes = getTextSizeInBytes(systemPrompt);
  return {
    validSystemPromptSize: systemPromptBytes <= SYSTEM_PROMPT_BYTES_LIMIT,
    systemPromptSize: getHumanReadableFileSize(systemPromptBytes, 1000),
  };
};

export const formDataToCreateModelRequest = (
  formData: PromptTuningFormFields,
  workspace: string
): CreateModelEntityRequest => {
  const icl_few_shot_examples = parseICLExamples(formData.iclFewShotExamples ?? [], iclDelimiter);
  const { prompt: system_prompt, promptTemplate: system_prompt_template } = compileSystemPrompt({
    systemPromptTemplate: formData.systemPromptTemplate,
    iclFewShotExamples: icl_few_shot_examples,
  });
  const createModelRequest: CreateModelEntityRequest = {
    name: formData.name,
    description: formData.description || undefined,
    base_model: getPartsFromReference(formData.baseModel).name,
    finetuning_type: FinetuningType.prompt_tuning,
    prompt: {
      system_prompt,
      icl_few_shot_examples,
    },
    custom_fields: {
      tools: formData.toolsEnabled ? JSON.stringify(formData.tools ?? []) : undefined,
      system_prompt_template,
      workspace,
      inference_params: {
        temperature: formData.temperature ?? undefined,
        max_tokens: formData.max_tokens ?? undefined,
        max_completion_tokens: formData.max_completion_tokens ?? undefined,
        top_p: formData.top_p ?? undefined,
      },
    },
  };
  return createModelRequest;
};

export const modelToFormData = (model: ModelEntity): PromptTuningFormFields => {
  const iclFewShotExamples = model.prompt?.icl_few_shot_examples
    ? model.prompt.icl_few_shot_examples.split(iclDelimiter).map((icl, index) => ({
        content: icl,
        fileName: `File ${index + 1}`,
      }))
    : [];
  return {
    name: model.name || '',
    description: model.description || '',
    baseModel: model.base_model || '',
    systemPrompt: model.prompt?.system_prompt || '',
    iclFewShotExamples,
    tools: getModelTools(model),
    toolsEnabled: getModelTools(model).length > 0,
    systemPromptTemplate:
      (model.custom_fields?.system_prompt_template as string) || DEFAULT_PROMPT_TEMPLATE,
    max_tokens:
      (model.custom_fields?.inference_params as { max_tokens?: number })?.max_tokens ||
      MODEL_HYPERPARAMETER_FIELD_METADATA.max_tokens.default,
    temperature:
      (model.custom_fields?.inference_params as { temperature?: number })?.temperature ||
      MODEL_HYPERPARAMETER_FIELD_METADATA.temperature.default,
    max_completion_tokens: (
      model.custom_fields?.inference_params as { max_completion_tokens?: number }
    )?.max_completion_tokens,
    top_p: (model.custom_fields?.inference_params as { top_p?: number })?.top_p,
  };
};
