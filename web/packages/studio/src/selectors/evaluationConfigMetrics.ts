// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { MetricOnlineJobMetricParams } from '@nemo/sdk/generated/platform/schema';

/**
 * Type definitions for LLM-as-a-Judge metric parameters.
 * These represent the expected structure but are not guaranteed by the SDK.
 */
interface LLMJudgeMessage {
  role: string;
  content: string;
}

interface LLMJudgeTemplate {
  messages?: LLMJudgeMessage[];
}

interface LLMJudgeParser {
  pattern?: string;
}

interface LLMJudgeSimilarity {
  type?: string;
  parser?: LLMJudgeParser;
}

interface LLMJudgeScores {
  similarity?: LLMJudgeSimilarity;
}

interface LLMJudgeApiEndpoint {
  model_id?: string;
}

interface LLMJudgeModel {
  api_endpoint?: LLMJudgeApiEndpoint;
}

interface LLMJudgeParams {
  template?: LLMJudgeTemplate;
  scores?: LLMJudgeScores;
  model?: LLMJudgeModel;
  [key: string]: unknown;
}

/**
 * Type guard to check if messages array is valid.
 */
const isMessageArray = (messages: unknown): messages is LLMJudgeMessage[] => {
  return (
    Array.isArray(messages) &&
    messages.every(
      (msg) =>
        typeof msg === 'object' &&
        msg !== null &&
        'role' in msg &&
        'content' in msg &&
        typeof msg.role === 'string' &&
        typeof msg.content === 'string'
    )
  );
};

/**
 * Type guard to check if value is a valid LLMJudgeParams structure.
 */
const isLLMJudgeParams = (params: MetricOnlineJobMetricParams): params is LLMJudgeParams => {
  return typeof params === 'object' && params !== null;
};

/**
 * Extracts the model name from LLM-as-a-Judge metric configuration params.
 * @param params - The metric configuration parameters
 * @returns The model ID or undefined if not found
 */
export const getModelNameFromLLMJudgeParams = (
  params?: MetricOnlineJobMetricParams
): string | undefined => {
  if (!params || !isLLMJudgeParams(params)) {
    return undefined;
  }

  const model = params.model;
  if (
    model &&
    typeof model === 'object' &&
    'api_endpoint' in model &&
    model.api_endpoint &&
    typeof model.api_endpoint === 'object' &&
    'model_id' in model.api_endpoint &&
    typeof model.api_endpoint.model_id === 'string'
  ) {
    return model.api_endpoint.model_id;
  }

  return undefined;
};

/**
 * Extracts the score type from LLM-as-a-Judge metric configuration params.
 * @param params - The metric configuration parameters
 * @returns The score type or undefined if not found
 */
export const getScoreTypeFromLLMJudgeParams = (
  params?: MetricOnlineJobMetricParams
): string | undefined => {
  if (!params || !isLLMJudgeParams(params)) {
    return undefined;
  }

  const scores = params.scores;
  if (
    scores &&
    typeof scores === 'object' &&
    'similarity' in scores &&
    scores.similarity &&
    typeof scores.similarity === 'object' &&
    'type' in scores.similarity &&
    typeof scores.similarity.type === 'string'
  ) {
    return scores.similarity.type;
  }

  return undefined;
};

/**
 * Extracts the parser pattern from LLM-as-a-Judge metric configuration params.
 * @param params - The metric configuration parameters
 * @returns The parser pattern or undefined if not found
 */
export const getParserPatternFromLLMJudgeParams = (
  params?: MetricOnlineJobMetricParams
): string | undefined => {
  if (!params || !isLLMJudgeParams(params)) {
    return undefined;
  }

  const scores = params.scores;
  if (
    scores &&
    typeof scores === 'object' &&
    'similarity' in scores &&
    scores.similarity &&
    typeof scores.similarity === 'object' &&
    'parser' in scores.similarity &&
    scores.similarity.parser &&
    typeof scores.similarity.parser === 'object' &&
    'pattern' in scores.similarity.parser &&
    typeof scores.similarity.parser.pattern === 'string'
  ) {
    return scores.similarity.parser.pattern;
  }

  return undefined;
};

/**
 * Extracts messages from LLM-as-a-Judge metric configuration params.
 * @param params - The metric configuration parameters
 * @returns The messages array or undefined if not found/invalid
 */
export const getMessagesFromLLMJudgeParams = (
  params?: MetricOnlineJobMetricParams
): LLMJudgeMessage[] | undefined => {
  if (!params || !isLLMJudgeParams(params)) {
    return undefined;
  }

  const template = params.template;
  if (
    template &&
    typeof template === 'object' &&
    'messages' in template &&
    isMessageArray(template.messages)
  ) {
    return template.messages;
  }

  return undefined;
};

/**
 * Extracts the system message from LLM-as-a-Judge metric configuration params.
 * @param params - The metric configuration parameters
 * @returns The system message content or undefined if not found
 */
export const getSystemMessageFromLLMJudgeParams = (
  params?: MetricOnlineJobMetricParams
): string | undefined => {
  const messages = getMessagesFromLLMJudgeParams(params);
  return messages?.find((msg) => msg.role === 'system')?.content;
};

/**
 * Extracts the user message from LLM-as-a-Judge metric configuration params.
 * @param params - The metric configuration parameters
 * @returns The user message content or undefined if not found
 */
export const getUserMessageFromLLMJudgeParams = (
  params?: MetricOnlineJobMetricParams
): string | undefined => {
  const messages = getMessagesFromLLMJudgeParams(params);
  return messages?.find((msg) => msg.role === 'user')?.content;
};
