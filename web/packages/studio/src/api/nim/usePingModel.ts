// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { useChatCompletion } from '@nemo/common/src/hooks/useChatCompletion';
import { useMutation, UseMutationOptions } from '@tanstack/react-query';
import { ChatCompletion } from 'openai/resources/chat/completions.mjs';

export const usePingModel = (
  mutationOptions: UseMutationOptions<boolean, Error, { model: string }>
) => {
  const { mutateAsync: pingModel } = useChatCompletion();

  return useMutation({
    ...mutationOptions,
    mutationFn: async ({ model }: { model: string }) => {
      const response = (await pingModel({
        model,
        stream: false,
        max_tokens: 5,
        messages: [{ role: 'user', content: 'Ping' }],
      })) as ChatCompletion;
      if (response.choices[0].message.content) {
        return true;
      }
      return false;
    },
  });
};
