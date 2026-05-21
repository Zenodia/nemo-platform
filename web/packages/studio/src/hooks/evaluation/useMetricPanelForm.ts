// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { zodResolver } from '@hookform/resolvers/zod';
import {
  chatCompletionMessageRowSchema,
  type ChatCompletionMessageRowValues,
} from '@nemo/common/src/components/ChatCompletionInput';
import {
  evaluationCreateMetricBodyOneIgnoreRequestFailureDefault,
  evaluationCreateMetricBodyOneModelOneFormatDefault,
  evaluationCreateMetricBodyOneScoresItemOneNameRegExp,
  evaluationCreateMetricBodyOneScoresItemOneRubricMin,
  evaluationCreateMetricBodyOneTypeDefault,
} from '@nemo/sdk/generated/platform/zod/evaluator';
import {
  DEFAULT_PROMPT_TEMPLATE,
  DEFAULT_SYSTEM_PROMPT,
} from '@studio/components/evaluation/Jobs/form/defaults';
import {
  DEFAULT_INFERENCE_PARAMS_FORM_VALUES,
  inferenceParamsSchema,
} from '@studio/hooks/evaluation/useCreateConfigurationForm';
import { useForm } from 'react-hook-form';
import { z } from 'zod';

const scoreNameSchema = z
  .string()
  .min(1, 'Score name is required')
  .regex(
    evaluationCreateMetricBodyOneScoresItemOneNameRegExp,
    'Only lowercase letters, numbers, and underscores allowed'
  );

const rangeScoreSchema = z
  .object({
    scoreType: z.literal('range'),
    name: scoreNameSchema,
    description: z.string().optional(),
    minimum: z.number({ required_error: 'Minimum value is required' }),
    maximum: z.number({ required_error: 'Maximum value is required' }),
  })
  .refine((data) => data.minimum < data.maximum, {
    message: 'Minimum must be less than maximum',
    path: ['maximum'],
  });

const rubricItemSchema = z.object({
  label: z.string().min(1, 'Label is required'),
  description: z.string().optional(),
  value: z.number({ required_error: 'Value is required' }),
});

const rubricScoreSchema = z.object({
  scoreType: z.literal('rubric'),
  name: scoreNameSchema,
  description: z.string().optional(),
  rubric: z
    .array(rubricItemSchema)
    .min(
      evaluationCreateMetricBodyOneScoresItemOneRubricMin,
      'At least two rubric items are required'
    ),
});

const scoreSchema = z.union([rangeScoreSchema, rubricScoreSchema]);

export type PanelScoreFormData = z.infer<typeof scoreSchema>;

const metricPanelFormSchema = z.object({
  name: z
    .string()
    .min(1, 'Metric name is required')
    .max(255, 'Metric name must be less than 255 characters')
    .regex(
      /^[\w+.@:]([\w\-+.@:]*[\w+.@:])?$/,
      'Metric name can only contain alphanumeric characters, hyphens, underscores, plus signs, periods, at signs, and colons, and must not start or end with a hyphen'
    ),
  body: z.object({
    type: z
      .literal(evaluationCreateMetricBodyOneTypeDefault)
      .default(evaluationCreateMetricBodyOneTypeDefault),
    description: z.string().optional(),
    model: z.object({
      url: z.string().optional().default(''),
      name: z.string().min(1, 'Judge model is required'),
      format: z
        .enum(['nim', 'openai', 'llama_stack'])
        .default(evaluationCreateMetricBodyOneModelOneFormatDefault),
      api_key_secret: z.string().optional(),
    }),
    scores: z.array(scoreSchema).min(1, 'At least one score is required'),
    messages: z.array(chatCompletionMessageRowSchema).min(1, 'At least one message is required'),
    ignore_request_failure: z
      .boolean()
      .default(evaluationCreateMetricBodyOneIgnoreRequestFailureDefault),
    inference: inferenceParamsSchema,
  }),
});

export type MetricPanelFormData = z.infer<typeof metricPanelFormSchema>;

/** Initial score row for new metrics — lives in this module to avoid a circular import with `defaults.ts`. */
export const DEFAULT_METRIC_PANEL_SCORES: PanelScoreFormData[] = [
  {
    scoreType: 'rubric',
    name: 'quality',
    description: 'Overall quality of the response.',
    rubric: [
      {
        label: 'fails',
        description: 'Fails to address the request, irrelevant, or harmful.',
        value: 0,
      },
      {
        label: 'poor',
        description: 'Partially addresses the request but has significant gaps or errors.',
        value: 1,
      },
      {
        label: 'adequate',
        description: 'Addresses the core request but may lack detail or completeness.',
        value: 2,
      },
      {
        label: 'good',
        description: 'Fully addresses the request with appropriate detail.',
        value: 3,
      },
      {
        label: 'excellent',
        description: 'Comprehensive and well-structured, fully satisfies the needs.',
        value: 4,
      },
    ],
  },
];

const DEFAULT_MESSAGES: ChatCompletionMessageRowValues[] = [
  { role: 'system', content: DEFAULT_SYSTEM_PROMPT, expanded: true },
  { role: 'user', content: DEFAULT_PROMPT_TEMPLATE, expanded: true },
];

export const useMetricPanelForm = ({
  defaultModelName = '',
}: { defaultModelName?: string } = {}) => {
  return useForm<MetricPanelFormData>({
    mode: 'onSubmit',
    resolver: zodResolver(metricPanelFormSchema),
    defaultValues: {
      name: '',
      body: {
        type: evaluationCreateMetricBodyOneTypeDefault,
        model: {
          url: '',
          name: defaultModelName,
          format: evaluationCreateMetricBodyOneModelOneFormatDefault,
        },
        scores: structuredClone(DEFAULT_METRIC_PANEL_SCORES),
        messages: DEFAULT_MESSAGES,
        inference: structuredClone(DEFAULT_INFERENCE_PARAMS_FORM_VALUES),
      },
    },
  });
};
