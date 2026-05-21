// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import Handlebars from 'handlebars';
import { ChatCompletion } from 'openai/resources/index.mjs';

export class InvalidSystemPrompt extends Error {
  constructor(error: unknown) {
    let message;
    if (error instanceof Error) {
      message = error.message;
    } else {
      message = String(error);
    }
    super(`Prompt template has compilation errors. ${message}`);
  }
}

export interface CompileSystemPromptOptions {
  systemPromptTemplate: string;
  iclFewShotExamples?: string | null;
}

export const ICL_TEMPLATE_VAR = 'icl_few_shot_examples';

export const compileSystemPrompt = ({
  systemPromptTemplate,
  iclFewShotExamples,
}: CompileSystemPromptOptions) => {
  const hasTemplateVar = systemPromptTemplate.includes(`{{${ICL_TEMPLATE_VAR}}}`);
  const shouldAddTemplateVar = iclFewShotExamples && !hasTemplateVar;
  const separator = systemPromptTemplate ? '\n\n' : '';
  const newSystemPromptTemplate = `${systemPromptTemplate}${shouldAddTemplateVar ? `${separator}{{${ICL_TEMPLATE_VAR}}}` : ''}`;
  try {
    const template = Handlebars.compile(newSystemPromptTemplate);

    // We use SafeString because Handlebars is designed to produce safe HTML, but we don't
    // need it to produce HTML, just a string we send to NIM.
    const context = {
      [ICL_TEMPLATE_VAR]: new Handlebars.SafeString(iclFewShotExamples ?? ''),
    };

    return { prompt: template(context), promptTemplate: newSystemPromptTemplate };
  } catch (error) {
    throw new InvalidSystemPrompt(error);
  }
};

/**
 * Given a string, this function will return a response object. Useful for returning a response_override for an annotation.
 */
export const buildAssistantResponse = (content: string): Partial<ChatCompletion> => {
  return {
    object: 'chat.completion',
    created: Date.now(),
    choices: [
      {
        index: 0,
        message: {
          role: 'assistant',
          content,
          refusal: null,
        },
        finish_reason: 'stop',
        logprobs: null,
      },
    ],
  };
};
