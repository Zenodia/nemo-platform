/*
 * SPDX-FileCopyrightText: Copyright (c) 2022-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
 * SPDX-License-Identifier: Apache-2.0
 *
 * NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
 * property and proprietary rights in and to this material, related
 * documentation and any modifications thereto. Any use, reproduction,
 * disclosure or distribution of this material and related documentation
 * without an express license agreement from NVIDIA CORPORATION or
 * its affiliates is strictly prohibited.
 */

import { z } from 'zod';

export const chatCompletionMessageRowRoles = [
  'system',
  'user',
  'assistant',
  'tool',
  'developer',
] as const;

export const chatCompletionMessageRowSchema = z.object({
  role: z.enum(chatCompletionMessageRowRoles),
  content: z.string(),
  /** When false, the body is collapsed and not editable. */
  expanded: z.boolean(),
});

export type ChatCompletionMessageRowValues = z.infer<typeof chatCompletionMessageRowSchema>;

export const defaultChatCompletionMessageRow = (): ChatCompletionMessageRowValues => ({
  role: 'user',
  content: '',
  expanded: true,
});
