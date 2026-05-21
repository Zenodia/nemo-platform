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

import type { ExcludedChatCompletionRole } from '@nemo/common/src/types/chat';
import type { BadgeProps } from '@nvidia/foundations-react-core';

export type ChatCompletionRoleBadgeColor = NonNullable<BadgeProps['color']>;

/** Solid badge color per message role for quick visual scanning. */
export const CHAT_COMPLETION_ROLE_BADGE_COLOR: Record<
  ExcludedChatCompletionRole,
  ChatCompletionRoleBadgeColor
> = {
  system: 'purple',
  user: 'blue',
  assistant: 'green',
  tool: 'yellow',
  developer: 'teal',
};

export function chatCompletionRoleBadgeColor(role: string): ChatCompletionRoleBadgeColor {
  return CHAT_COMPLETION_ROLE_BADGE_COLOR[role as ExcludedChatCompletionRole] ?? 'gray';
}

export type ChatCompletionRoleSelectItem = {
  value: ExcludedChatCompletionRole;
  children: string;
};

/** Default role labels for {@link ChatCompletionInput}. */
export const DEFAULT_CHAT_COMPLETION_ROLE_ITEMS: ChatCompletionRoleSelectItem[] = [
  { value: 'system', children: 'System' },
  { value: 'user', children: 'User' },
  { value: 'assistant', children: 'Assistant' },
  { value: 'tool', children: 'Tool' },
  { value: 'developer', children: 'Developer' },
];
