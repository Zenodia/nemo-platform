// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { useMutation, UseMutationOptions } from '@tanstack/react-query';
import OpenAI from 'openai';
import { ChatCompletion, ChatCompletionChunk } from 'openai/resources/index.mjs';
import { Stream } from 'openai/streaming.mjs';
import pLimit from 'p-limit';

import { ChatMissingModelError } from '../../constants/chat';
import { useChatCompletion } from '../useChatCompletion';

interface CreateChatCompletionsOptions {
  requests: OpenAI.ChatCompletionCreateParams[];
  concurrencyLimit?: number;
  onTaskComplete?: (props: { result: ChatCompletionRequestReturn; completedTasks: number }) => void;
}
type ChatCompletionRequestReturn = Stream<ChatCompletionChunk> | ChatCompletion;
export type UseChatCompletionOptions = Omit<
  UseMutationOptions<ChatCompletionRequestReturn[], Error, CreateChatCompletionsOptions>,
  'mutationFn'
>;
/**
 * Return a useMutation object for creating multiple chat completions using the NIM Proxy microservice.
 * This hook handles the batch operation for sending many chat completion requests throttled by p-limit to
 * prevent overloading the API.
 */
export const useChatCompletions = (options?: UseChatCompletionOptions) => {
  const { mutateAsync } = useChatCompletion();

  const createChatCompletions = ({
    requests,
    concurrencyLimit,
    onTaskComplete,
  }: CreateChatCompletionsOptions) => {
    let completedTasks = 0;
    const limit = pLimit(concurrencyLimit ?? 15);
    const tasks = requests.map((request) =>
      limit(async () => {
        if (!request.model) {
          throw new ChatMissingModelError();
        }
        const result = await mutateAsync(request);
        completedTasks++;
        onTaskComplete?.({ result, completedTasks });
        return result;
      })
    );
    return Promise.all(tasks);
  };

  return useMutation({
    ...options,
    mutationFn: createChatCompletions,
    onSuccess: (...args) => {
      options?.onSuccess?.(...args);
    },
  });
};
