// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { DEFAULT_LLM_JUDGE_DEFAULTS } from '@nemo/common/src/constants/metrics';
import { InputFileSchemaType } from '@nemo/common/src/types';
import {
  FileValidationResult,
  FileFormatDetectionResult,
  validateFileFormat,
} from '@nemo/common/src/utils/fileValidation';
import {
  CreateConfigFormData,
  generateInferenceRequestTemplate,
  generateLLMJudgeUserMessage,
} from '@studio/hooks/evaluation/useCreateConfigurationForm';
import { useCallback, useState } from 'react';
import { UseFormSetValue } from 'react-hook-form';

export interface UseFileValidationOptions {
  setValue: UseFormSetValue<CreateConfigFormData>;
}

export interface UseFileValidationReturn {
  validateFile: (file: File) => Promise<FileValidationResult>;
  updateFormFromFile: (
    validationResult: FileValidationResult,
    detectionResult?: FileFormatDetectionResult
  ) => void;
  isValidationInProgress: boolean;
  lastValidationResult: FileValidationResult | null;
}

/**
 * Hook for handling file validation and form updates
 */
export function useFileValidation({ setValue }: UseFileValidationOptions): UseFileValidationReturn {
  const [isValidationInProgress, setIsValidationInProgress] = useState(false);
  const [lastValidationResult, setLastValidationResult] = useState<FileValidationResult | null>(
    null
  );

  const validateFile = useCallback(async (file: File): Promise<FileValidationResult> => {
    setIsValidationInProgress(true);
    try {
      const result = await validateFileFormat(file);
      setLastValidationResult(result);
      return result;
    } finally {
      setIsValidationInProgress(false);
    }
  }, []);

  const updateFormFromFile = useCallback(
    (validationResult: FileValidationResult, detectionResult?: FileFormatDetectionResult) => {
      // Always set the validation result first
      setValue('configData.fileValidationResult', validationResult);
      setValue('configData.fileDetectionResult', detectionResult);

      if (!validationResult.isValid) {
        // Clear form fields if validation failed
        setValue('configData.metricConfigs', {
          stringCheck: { operator: 'equals' },
          bleu: { references: '', candidate: '' },
          rouge: { groundTruth: '', prediction: '' },
          em: { groundTruth: '', prediction: '' },
          f1: { groundTruth: '', prediction: '' },
          llmJudge: {
            model: '',
            systemMessage: '',
            userMessage: '',
            similarityScoreType: 'integer',
            similarityScoreParserPattern: '',
          },
        });
        setValue('configData.inputFileKeyPrompt', '');
        setValue('configData.inputFileKeyGroundTruth', '');
        setValue('configData.templateSelectorInputPrompt', '');
        setValue('configData.templateSelectorInputGroundTruth', '');
        setValue('configData.templateSelectorSystemPrompt', '');
        setValue('configData.inferenceRequestTemplate', undefined);
        return;
      }

      if (!detectionResult) {
        // Schema detection failed - let form defaults take over
        setValue('configData.detectedSchemaType', undefined);
        return;
      }

      // Generate template strings only for fields we actually detected
      const templateStrings: { prompt?: string; groundTruth?: string; systemPrompt?: string } = {};
      const rawKeys: { prompt?: string; groundTruth?: string } = {};

      if (detectionResult.schemaType === InputFileSchemaType.CHAT_COMPLETION) {
        // Messages format - use the detected selectors
        if (detectionResult.detectedMessages.user) {
          rawKeys.prompt = detectionResult.detectedMessages.user.selector;
          templateStrings.prompt = `{{item.${detectionResult.detectedMessages.user.selector} | trim}}`;
        }
        if (detectionResult.detectedMessages.assistant) {
          rawKeys.groundTruth = detectionResult.detectedMessages.assistant.selector;
          templateStrings.groundTruth = `{{item.${detectionResult.detectedMessages.assistant.selector} | trim}}`;
        }
        if (detectionResult.detectedMessages.system) {
          templateStrings.systemPrompt = `{{item.${detectionResult.detectedMessages.system.selector} | trim}}`;
        }
      } else if (detectionResult.schemaType === InputFileSchemaType.COMPLETION) {
        // Prompt-completion format - only populate if we detected the fields
        if (detectionResult.detectedFields.prompt) {
          rawKeys.prompt = detectionResult.detectedFields.prompt;
          templateStrings.prompt = `{{item.${detectionResult.detectedFields.prompt} | trim}}`;
        }
        if (detectionResult.detectedFields.completion) {
          rawKeys.groundTruth = detectionResult.detectedFields.completion;
          templateStrings.groundTruth = `{{item.${detectionResult.detectedFields.completion} | trim}}`;
        }
      }
      // If schemaType is null (UnknownSchemaDetectionResult), we don't auto-populate anything

      // Set the detected schema type (undefined if schema couldn't be definitively determined)
      setValue(
        'configData.detectedSchemaType',
        detectionResult.schemaType ? (detectionResult.schemaType as InputFileSchemaType) : undefined
      );

      // Update form fields only for detected template strings
      if (templateStrings.prompt) {
        setValue('configData.inputFileKeyPrompt', rawKeys.prompt);
        setValue('configData.templateSelectorInputPrompt', templateStrings.prompt);

        // Generate inference request template only if we have a prompt
        const inferenceRequestTemplate = generateInferenceRequestTemplate(templateStrings.prompt);
        setValue('configData.inferenceRequestTemplate', inferenceRequestTemplate);
      }

      if (templateStrings.groundTruth) {
        setValue('configData.inputFileKeyGroundTruth', rawKeys.groundTruth);
        setValue('configData.templateSelectorInputGroundTruth', templateStrings.groundTruth);

        // Update metric configs with detected ground truth
        setValue('configData.metricConfigs.bleu.references', templateStrings.groundTruth);
        setValue('configData.metricConfigs.rouge.groundTruth', templateStrings.groundTruth);
        setValue('configData.metricConfigs.em.groundTruth', templateStrings.groundTruth);
        setValue('configData.metricConfigs.f1.groundTruth', templateStrings.groundTruth);

        // Set LLM Judge defaults
        setValue(
          'configData.metricConfigs.llmJudge.systemMessage',
          DEFAULT_LLM_JUDGE_DEFAULTS.systemMessage
        );
        setValue(
          'configData.metricConfigs.llmJudge.userMessage',
          generateLLMJudgeUserMessage(templateStrings.groundTruth)
        );
        setValue('configData.metricConfigs.llmJudge.similarityScoreType', 'integer');
        setValue(
          'configData.metricConfigs.llmJudge.similarityScoreParserPattern',
          DEFAULT_LLM_JUDGE_DEFAULTS.similarityScoreParserPattern
        );
      }

      if (templateStrings.systemPrompt) {
        setValue('configData.templateSelectorSystemPrompt', templateStrings.systemPrompt);
      }
    },
    [setValue]
  );

  return {
    validateFile,
    updateFormFromFile,
    isValidationInProgress,
    lastValidationResult,
  };
}
