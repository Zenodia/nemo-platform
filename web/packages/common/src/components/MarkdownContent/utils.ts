// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import {
  CALLOUT_CONFIG,
  type CalloutKind,
} from '@nemo/common/src/components/MarkdownContent/constants';

export const isCalloutKind = (value: unknown): value is CalloutKind =>
  typeof value === 'string' && value in CALLOUT_CONFIG;

export const extractLanguage = (className: string | undefined): string | undefined => {
  const match = className?.match(/\blanguage-([\w-]+)/);
  return match?.[1].toLowerCase();
};
