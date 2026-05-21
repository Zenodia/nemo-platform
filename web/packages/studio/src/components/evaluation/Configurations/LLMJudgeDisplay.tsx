// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { Stack, Text } from '@nvidia/foundations-react-core';
import { Pre } from '@studio/components/common/Pre';
import { ReadOnlyField } from '@studio/components/common/ReadOnlyField';
import {
  getModelNameFromLLMJudgeParams,
  getParserPatternFromLLMJudgeParams,
  getScoreTypeFromLLMJudgeParams,
  getSystemMessageFromLLMJudgeParams,
  getUserMessageFromLLMJudgeParams,
} from '@studio/selectors/evaluationConfigMetrics';
import { FC } from 'react';

export interface LLMJudgeDisplayProps {
  metricName: string;
  metricConfig: { type: string; params?: Record<string, unknown> };
}

/**
 * Component to display LLM-as-a-Judge metric details.
 * Shows the model, system/user messages, score type, and parser pattern.
 *
 * @param props.metricName - User-defined name for the metric
 * @param props.metricConfig - Metric configuration containing type and params
 */
export const LLMJudgeDisplay: FC<LLMJudgeDisplayProps> = ({ metricName, metricConfig }) => {
  const params = metricConfig.params;

  const modelName = getModelNameFromLLMJudgeParams(params);
  const systemMessage = getSystemMessageFromLLMJudgeParams(params);
  const userMessage = getUserMessageFromLLMJudgeParams(params);
  const scoreType = getScoreTypeFromLLMJudgeParams(params);
  const parserPattern = getParserPatternFromLLMJudgeParams(params);

  return (
    <Stack gap="density-2xl">
      <Text kind="label/bold/md">{metricName}</Text>
      <ReadOnlyField label="Type" value={metricConfig.type} />

      <Stack gap="density-2xl">
        <ReadOnlyField label="Model" value={modelName} />
        <ReadOnlyField
          label="System Message"
          value={systemMessage ? <Pre>{systemMessage}</Pre> : '-'}
        />
        <ReadOnlyField label="User Message" value={userMessage ? <Pre>{userMessage}</Pre> : '-'} />
      </Stack>

      <Stack gap="density-2xl">
        <ReadOnlyField label="Score Type" value={scoreType || '-'} />
        <ReadOnlyField label="Parser Pattern" value={parserPattern || '-'} />
      </Stack>
    </Stack>
  );
};
