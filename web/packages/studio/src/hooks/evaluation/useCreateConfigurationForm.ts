// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { zodResolver } from '@hookform/resolvers/zod';
import { INFERENCE_HYPERPARAMETER_FIELD_METADATA } from '@nemo/common/src/constants/inferenceParameters';
import {
  DEFAULT_LLM_JUDGE_DEFAULTS,
  EVALUATION_DEFAULT_OUTPUT_TEMPLATE_STRING,
  LLM_JUDGE_SCORE_TYPES,
  METRIC_LABELS,
  METRIC_NAMES_API,
  MetricNameApi,
} from '@nemo/common/src/constants/metrics';
import { InputFileSchemaType } from '@nemo/common/src/types';
import { generateDefaultName } from '@nemo/common/src/utils/generateDefaultName';
import type { InferenceParams } from '@nemo/sdk/generated/platform/schema';
import { EvaluationTargetMode } from '@studio/api/evaluation/types';
import { PLATFORM_BASE_URL } from '@studio/constants/environment';
import { useCallback, useMemo } from 'react';
import { useForm, useFormContext } from 'react-hook-form';
import { z } from 'zod';

/** Metric config shape for evaluation form (type + optional params). */
export type MetricConfig = { type: string; params?: Record<string, unknown> };

const inferenceFieldMeta = INFERENCE_HYPERPARAMETER_FIELD_METADATA;

// Validate metric-specific fields only when their metric is selected
type MetricValidation = {
  apiMetricName: MetricNameApi;
  fieldName: string;
  formConfigKey: 'bleu' | 'rouge' | 'em' | 'f1' | 'stringCheck' | 'llmJudge';
};

export const inferenceParamsSchema = z.object({
  max_tokens: z.coerce
    .number()
    .min(inferenceFieldMeta.max_tokens.min)
    .max(inferenceFieldMeta.max_tokens.max)
    .step(inferenceFieldMeta.max_tokens.step ?? 1),
  temperature: z.coerce
    .number()
    .min(inferenceFieldMeta.temperature.min)
    .max(inferenceFieldMeta.temperature.max)
    .step(inferenceFieldMeta.temperature.step ?? 0.1),
  top_p: z.coerce
    .number()
    .min(inferenceFieldMeta.top_p.min)
    .max(inferenceFieldMeta.top_p.max)
    .step(inferenceFieldMeta.top_p.step ?? 0.01),
});

export type InferenceParamsFormValues = z.infer<typeof inferenceParamsSchema>;

export const DEFAULT_INFERENCE_PARAMS_FORM_VALUES: InferenceParamsFormValues = {
  max_tokens: inferenceFieldMeta.max_tokens.default,
  temperature: inferenceFieldMeta.temperature.default,
  top_p: inferenceFieldMeta.top_p.default,
};

/** Coerce partial API/UI inference fields into the full shape required by evaluation forms. */
export function mergeInferenceParamsFormValues(
  current: Partial<InferenceParamsFormValues> | undefined,
  patch: Partial<InferenceParams>
): InferenceParamsFormValues {
  return inferenceParamsSchema.parse({
    max_tokens:
      patch.max_tokens ?? current?.max_tokens ?? DEFAULT_INFERENCE_PARAMS_FORM_VALUES.max_tokens,
    temperature:
      patch.temperature ?? current?.temperature ?? DEFAULT_INFERENCE_PARAMS_FORM_VALUES.temperature,
    top_p: patch.top_p ?? current?.top_p ?? DEFAULT_INFERENCE_PARAMS_FORM_VALUES.top_p,
  });
}

/** Allows for model names to be alphanumeric, dash, underscore, or at symbol. */
const modelNameRegex = /^[a-z0-9-_.@]*$/i;

const validateConfigName = (modelName: string) => {
  const matches = modelName.match(modelNameRegex);
  return matches ? matches.length > 0 : false;
};

// Factory function that creates configData schema
const createConfigDataSchema = (existingConfigs?: Array<{ name?: string }>) => {
  const taken = new Set(
    existingConfigs?.filter((config) => config.name).map((config) => config.name!.toLowerCase()) ||
      []
  );

  return z
    .object({
      id: z.string().optional(),
      workspace: z.string(),
      name: z
        .string()
        .min(1, 'Configuration name is required')
        .refine(validateConfigName, {
          message:
            'Configuration name must only contain alphanumeric characters or the following symbols: @-_.',
        })
        .superRefine((val, ctx) => {
          if (taken.has(val.toLowerCase())) {
            ctx.addIssue({
              code: z.ZodIssueCode.custom,
              message: 'A configuration with this name already exists',
              path: [],
            });
          }
        }),
      project: z.string(),
      description: z.string(),
      evaluationType: z.string().min(1, 'Evaluation type is required'),
      inputFile: z.string().optional(), // Will be conditionally required based on targetMode in superRefine
      metrics: z.array(z.enum(METRIC_NAMES_API)).min(1, 'At least one metric is required'),
      targetMode: z.nativeEnum(EvaluationTargetMode).optional(),
      inferenceRequestTemplate: z
        .object({
          messages: z.array(
            z.object({
              role: z.enum(['user', 'system', 'assistant', 'tool', 'function', 'developer']),
              content: z.string(),
            })
          ),
        })
        .optional(),
      inferenceParams: inferenceParamsSchema,
      // Metric-specific configurations
      metricConfigs: z
        .object({
          stringCheck: z
            .object({
              operator: z.string().optional(),
            })
            .optional(),
          bleu: z
            .object({
              references: z.string().optional(),
              candidate: z.string().optional(),
            })
            .optional(),
          rouge: z
            .object({
              groundTruth: z.string().optional(),
              prediction: z.string().optional(),
            })
            .optional(),
          em: z
            .object({
              groundTruth: z.string().optional(),
              prediction: z.string().optional(),
            })
            .optional(),
          f1: z
            .object({
              groundTruth: z.string().optional(),
              prediction: z.string().optional(),
            })
            .optional(),
          llmJudge: z
            .object({
              model: z.string().optional(),
              systemMessage: z.string().optional(),
              userMessage: z.string().optional(),
              similarityScoreType: z.enum(LLM_JUDGE_SCORE_TYPES).optional(),
              similarityScoreParserPattern: z.string().optional(),
            })
            .optional(),
        })
        .optional(),
      templateSelectorInputPrompt: z.string().optional(),
      templateSelectorInputGroundTruth: z.string().optional(),
      templateSelectorEvaluationOutput: z.string().optional(),
      templateSelectorSystemPrompt: z.string().optional(),
      inputFileKeyPrompt: z.string().optional(),
      inputFileKeyGroundTruth: z.string().optional(),
      inputFileKeyOutput: z.string().optional(),
      templateSelectorOutput: z.string().optional(),
      inputFileCurrentRowIndex: z.number().default(0),
      inputFileTotalRowCount: z.number().nullable().optional(),
      inputFileFormat: z.enum(['json', 'jsonl']).nullable().optional(),
      inputFileDatasetNamespace: z.string().nullable().optional(),
      inputFileDatasetName: z.string().nullable().optional(),
      inputFilePath: z.string().nullable().optional(),
      // Add new fields for file validation
      fileValidationResult: z
        .object({
          isValid: z.boolean(),
          format: z.string().nullable(),
          error: z.string().optional(),
        })
        .optional(),
      fileDetectionResult: z
        .discriminatedUnion('schemaType', [
          z.object({
            schemaType: z.literal('chat-completion'),
            detectedMessages: z.record(z.object({ index: z.number(), selector: z.string() })),
            messagesKey: z.string(),
            isComplete: z.boolean(),
            firstRow: z.record(z.unknown()),
          }),
          z.object({
            schemaType: z.literal('completion'),
            detectedFields: z.object({
              prompt: z.string().optional(),
              completion: z.string().optional(),
            }),
            isComplete: z.boolean(),
            firstRow: z.record(z.unknown()),
          }),
          z.object({
            schemaType: z.null(),
            firstRow: z.record(z.unknown()),
          }),
        ])
        .nullable()
        .optional(),
      detectedSchemaType: z
        .enum([InputFileSchemaType.CHAT_COMPLETION, InputFileSchemaType.COMPLETION])
        .optional(),
      firstRowData: z.record(z.unknown()).nullable().optional(),
    })
    .superRefine((data, ctx) => {
      const targetMode = data.targetMode || EvaluationTargetMode.ONLINE;
      const selectedMetrics = data.metrics || [];

      // In ONLINE mode, inputFile is required
      if (targetMode === EvaluationTargetMode.ONLINE) {
        const inputFile = data.inputFile?.trim();
        if (!inputFile) {
          ctx.addIssue({
            code: z.ZodIssueCode.custom,
            message: 'Input file is required when creating a configuration for LLM Model targets',
            path: ['inputFile'],
          });
        }

        // Check if file is valid
        const isFileValid = data.fileValidationResult?.isValid === true;

        // If file is not valid but metrics are selected, show error
        if (!isFileValid && selectedMetrics.length > 0) {
          ctx.addIssue({
            code: z.ZodIssueCode.custom,
            message: 'Please upload a valid input file before selecting metrics',
            path: ['inputFile'],
          });
        }

        // If schema is not auto-detected or is incomplete, require manual key selection
        const detectedSchemaType = data.detectedSchemaType;
        const fileDetectionResult = data.fileDetectionResult;
        const isSchemaIncomplete =
          !detectedSchemaType ||
          (fileDetectionResult &&
            'isComplete' in fileDetectionResult &&
            !fileDetectionResult.isComplete);

        if (isSchemaIncomplete && inputFile) {
          // Prompt field is required when manual mapping is needed
          if (!data.inputFileKeyPrompt?.trim()) {
            ctx.addIssue({
              code: z.ZodIssueCode.custom,
              message:
                'Please select which field contains the prompt/question from your input data',
              path: ['inputFileKeyPrompt'],
            });
          }

          // Ground Truth field is required when manual mapping is needed
          if (!data.inputFileKeyGroundTruth?.trim()) {
            ctx.addIssue({
              code: z.ZodIssueCode.custom,
              message:
                'Please select which field contains the expected answer/ground truth from your input data',
              path: ['inputFileKeyGroundTruth'],
            });
          }
        }

        // Ground truth is required when metrics are selected and file is valid
        if (isFileValid && selectedMetrics.length > 0 && !data.inputFileKeyGroundTruth?.trim()) {
          ctx.addIssue({
            code: z.ZodIssueCode.custom,
            message:
              'Please select which field contains the expected answer/ground truth from your input data to enable metrics',
            path: ['inputFileKeyGroundTruth'],
          });
        }
      }

      let metricRequiredFields: MetricValidation[] = [
        { apiMetricName: 'bleu', fieldName: 'references', formConfigKey: 'bleu' },
        { apiMetricName: 'string-check', fieldName: 'operator', formConfigKey: 'stringCheck' },
        { apiMetricName: 'rouge', fieldName: 'groundTruth', formConfigKey: 'rouge' },
        { apiMetricName: 'em', fieldName: 'groundTruth', formConfigKey: 'em' },
        { apiMetricName: 'f1', fieldName: 'groundTruth', formConfigKey: 'f1' },
        { apiMetricName: 'llm-judge', fieldName: 'model', formConfigKey: 'llmJudge' },
      ];

      // In OFFLINE mode, the candidate and prediction fields are no longer optional
      if (targetMode === EvaluationTargetMode.OFFLINE) {
        metricRequiredFields = [
          ...metricRequiredFields,
          { apiMetricName: 'bleu', fieldName: 'candidate', formConfigKey: 'bleu' },
          { apiMetricName: 'rouge', fieldName: 'prediction', formConfigKey: 'rouge' },
          { apiMetricName: 'em', fieldName: 'prediction', formConfigKey: 'em' },
          { apiMetricName: 'f1', fieldName: 'prediction', formConfigKey: 'f1' },
        ];
      }

      metricRequiredFields.forEach(({ apiMetricName, fieldName, formConfigKey }) => {
        if (selectedMetrics.includes(apiMetricName)) {
          const metricConfig = data.metricConfigs?.[formConfigKey] as
            | Record<string, string | undefined>
            | undefined;
          const value = metricConfig?.[fieldName]?.trim();
          if (!value) {
            ctx.addIssue({
              code: z.ZodIssueCode.custom,
              message: `${fieldName.charAt(0).toUpperCase() + fieldName.slice(1)} is required for ${METRIC_LABELS[apiMetricName]} metric`,
              path: ['metricConfigs', formConfigKey, fieldName],
            });
          }
        }
      });
    });
};

// Factory function that creates schema with dynamic validation based on config value
const makeCreateConfigSchema = (existingConfigs?: Array<{ name?: string }>) => {
  return z.object({
    configData: createConfigDataSchema(existingConfigs),
  });
};

// Type for when actually creating a new config (with full validation)
export type CreateConfigFormData = {
  configData: z.infer<ReturnType<typeof createConfigDataSchema>>;
};

// Re-export for backward compatibility
export {
  generateInferenceRequestTemplate,
  generateLLMJudgeUserMessage,
} from '@nemo/common/src/utils/evaluation';

const DEFAULT_CREATE_CONFIG_FORM_VALUES: CreateConfigFormData = {
  configData: {
    id: '',
    name: '',
    workspace: '',
    project: '',
    description: '',
    evaluationType: 'custom',
    inputFile: '',
    metrics: [],
    targetMode: EvaluationTargetMode.ONLINE,
    inferenceRequestTemplate: undefined, // Will be auto-generated from template selectors
    inferenceParams: { ...DEFAULT_INFERENCE_PARAMS_FORM_VALUES },
    metricConfigs: {
      stringCheck: {
        operator: 'equals',
      },
      bleu: {
        references: '', // Will be auto-populated from file
        candidate: EVALUATION_DEFAULT_OUTPUT_TEMPLATE_STRING, // Pre-filled for ONLINE mode by default
      },
      rouge: {
        groundTruth: '', // Will be auto-populated from file
        prediction: EVALUATION_DEFAULT_OUTPUT_TEMPLATE_STRING, // Pre-filled for ONLINE mode by default
      },
      em: {
        groundTruth: '', // Will be auto-populated from file
        prediction: EVALUATION_DEFAULT_OUTPUT_TEMPLATE_STRING, // Pre-filled for ONLINE mode by default
      },
      f1: {
        groundTruth: '', // Will be auto-populated from file
        prediction: EVALUATION_DEFAULT_OUTPUT_TEMPLATE_STRING, // Pre-filled for ONLINE mode by default
      },
      llmJudge: {
        model: '',
        systemMessage: DEFAULT_LLM_JUDGE_DEFAULTS.systemMessage,
        userMessage: '',
        similarityScoreType: 'integer',
        similarityScoreParserPattern: DEFAULT_LLM_JUDGE_DEFAULTS.similarityScoreParserPattern,
      },
    },
    templateSelectorInputPrompt: '', // Will be auto-populated from file
    templateSelectorInputGroundTruth: '', // Will be auto-populated from file
    templateSelectorEvaluationOutput: EVALUATION_DEFAULT_OUTPUT_TEMPLATE_STRING, // Standard template for evaluation output
    templateSelectorSystemPrompt: '', // Will be auto-populated from file
    inputFileKeyPrompt: '', // The original key name selected for prompt field
    inputFileKeyGroundTruth: '', // The original key name selected for ground truth field
    inputFileKeyOutput: '', // The original key name selected for cached output field (offline mode)
    templateSelectorOutput: '', // The interpolated template for cached output (offline mode)
    inputFileCurrentRowIndex: 0, // Current row index for pagination through file
    inputFileTotalRowCount: null, // Total number of rows in the uploaded file
    inputFileFormat: null, // File format ('json' or 'jsonl')
    inputFileDatasetNamespace: null, // Dataset namespace for re-downloading file
    inputFileDatasetName: null, // Dataset name for re-downloading file
    inputFilePath: null, // File path within dataset for re-downloading
    fileValidationResult: undefined,
    fileDetectionResult: undefined,
    detectedSchemaType: undefined,
    firstRowData: null,
  },
};

interface UseCreateConfigFormProps {
  disabled?: boolean;
  existingConfigs?: Array<{ name?: string }>;
}

/**
 * A simple wrapper for useForm that sets the default values for the create configuration form
 */
export const useCreateConfigForm = ({ disabled, existingConfigs }: UseCreateConfigFormProps) => {
  const schema = makeCreateConfigSchema(existingConfigs);

  // Generate a unique default name for each form instance
  const defaultValues = useMemo(
    () => ({
      ...DEFAULT_CREATE_CONFIG_FORM_VALUES,
      configData: {
        ...DEFAULT_CREATE_CONFIG_FORM_VALUES.configData,
        name: generateDefaultName(),
      },
    }),
    []
  );

  return useForm<CreateConfigFormData>({
    mode: 'onChange',
    reValidateMode: 'onChange',
    resolver: zodResolver(schema),
    defaultValues,
    disabled,
  });
};

/**
 * Transform metrics array to API object format
 * Extracted for reuse across different evaluation workflows
 */
export const transformMetricsToApiFormat = (configData: CreateConfigFormData['configData']) => {
  return configData.metrics.reduce(
    (acc: Record<string, MetricConfig>, metric: string) => {
      const { metricConfigs } = configData;

      return {
        ...acc,
        [metric]: {
          type: metric,
          params: {
            ...(metric === 'string-check' && {
              check: [
                configData.templateSelectorEvaluationOutput || '',
                metricConfigs?.stringCheck?.operator,
                configData.templateSelectorInputGroundTruth || '',
              ],
            }),
            ...(metric === 'bleu' && {
              references: [metricConfigs?.bleu?.references],
              candidate: metricConfigs?.bleu?.candidate,
            }),
            ...(metric === 'rouge' && {
              ground_truth: metricConfigs?.rouge?.groundTruth,
              prediction: metricConfigs?.rouge?.prediction,
            }),
            ...(metric === 'em' && {
              ground_truth: metricConfigs?.em?.groundTruth,
              prediction: metricConfigs?.em?.prediction,
            }),
            ...(metric === 'f1' && {
              ground_truth: metricConfigs?.f1?.groundTruth,
              prediction: metricConfigs?.f1?.prediction,
            }),
            ...(metric === 'llm-judge' && {
              // Create llm-judge metric using the same URL pattern as target model
              model: {
                api_endpoint: {
                  url: `${PLATFORM_BASE_URL}/v1/chat/completions`,
                  model_id: metricConfigs?.llmJudge?.model ?? '',
                  format: 'nim',
                },
              },
              template: {
                messages: [
                  {
                    role: 'system',
                    content: metricConfigs?.llmJudge?.systemMessage,
                  },
                  {
                    role: 'user',
                    content: metricConfigs?.llmJudge?.userMessage,
                  },
                ],
              },
              scores: {
                similarity: {
                  type: metricConfigs?.llmJudge?.similarityScoreType,
                  parser: {
                    type: 'regex',
                    pattern: metricConfigs?.llmJudge?.similarityScoreParserPattern,
                  },
                },
              },
            }),
          },
        },
      };
    },
    {} as Record<string, MetricConfig>
  );
};

/**
 * Custom hook that provides a function to reset the configuration form
 * while preserving key fields (id, name, description, project, targetMode).
 *
 * This is useful when:
 * - Switching between online/offline modes
 * - Removing a file and clearing all file-related data
 * - Any other scenario where you want to reset to defaults but keep user's basic info
 *
 * @example
 * const resetConfigForm = useResetConfigForm();
 * // Later...
 * resetConfigForm();
 */
export const useResetConfigForm = () => {
  const { getValues, reset } = useFormContext<CreateConfigFormData>();

  const resetConfigForm = useCallback(() => {
    // Get ALL current form values to preserve non-configData fields
    // This is important when the form is nested within a parent form (e.g., LaunchEvaluationForm)
    const allCurrentValues = getValues();

    // Get configData fields we want to preserve
    const currentId = getValues('configData.id');
    const currentName = getValues('configData.name');
    const currentDescription = getValues('configData.description');
    const currentProject = getValues('configData.project');
    const currentTargetMode = getValues('configData.targetMode');

    // Reset configData to defaults while preserving:
    // 1. All non-configData fields (e.g., config, mode, targetModel from parent form)
    // 2. Key configData fields (id, name, description, project, targetMode)
    reset({
      ...allCurrentValues,
      configData: {
        ...DEFAULT_CREATE_CONFIG_FORM_VALUES.configData,
        id: currentId,
        name: currentName,
        description: currentDescription,
        project: currentProject,
        targetMode: currentTargetMode,
      },
    });
  }, [getValues, reset]);

  return resetConfigForm;
};
