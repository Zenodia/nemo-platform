// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { ChatCompletionToolsParam, toolSchema } from '@nemo/common/src/zod/tools';
import { AddToolFormFields } from '@studio/components/PromptTuningForm/ToolsSection/components/validation';
import { PromptTuningFormFields } from '@studio/routes/PromptTuningFormRoute/utils';
import { UseFormReturn } from 'react-hook-form';
import { ZodError } from 'zod';

export const useSubmitSingleTool = (
  currentTools: ChatCompletionToolsParam[],
  parentForm: UseFormReturn<PromptTuningFormFields>,
  toolForm: UseFormReturn<AddToolFormFields>
) => {
  return async (formData: AddToolFormFields): Promise<boolean> => {
    try {
      const json = JSON.parse(formData.json);

      // Normalize flat format to OpenAI format if needed (before validation)
      const normalizedTool: ChatCompletionToolsParam = json.function
        ? json // Already in OpenAI format
        : {
            // Convert flat format to OpenAI format
            type: 'function',
            function: {
              name: json.name,
              description: json.description,
              strict: json.strict,
              parameters: json.parameters,
            },
          };

      // Validate against the tool schema (OpenAI format only)
      try {
        toolSchema.parse(normalizedTool);
      } catch (error) {
        if (error instanceof ZodError) {
          const firstError = error.errors[0];
          const fieldPath = firstError?.path.join('.') || 'unknown';
          const errorMessage = `${fieldPath}: ${firstError?.message ?? 'Invalid tool configuration'}`;
          toolForm.setError('json', { message: errorMessage });
          return false;
        }
        throw error;
      }

      // Check for duplicate tool names
      const toolName = normalizedTool.function.name;
      const isDuplicate = currentTools.some((tool) => tool.function.name === toolName);
      if (isDuplicate) {
        toolForm.setError('json', {
          message: `A tool with the name "${toolName}" already exists. Please use a unique name.`,
        });
        return false;
      }

      // Add the new tool to the parent form's tools array
      parentForm.setValue('tools', [...currentTools, normalizedTool], { shouldValidate: true });

      return true;
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : 'Unexpected error while adding tool';
      toolForm.setError('json', { message: errorMessage });
      return false;
    }
  };
};
