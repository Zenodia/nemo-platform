// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

export type CalloutKind = 'note' | 'tip' | 'important' | 'warning' | 'caution';

export interface CalloutConfig {
  label: string;
  borderClassName: string;
  labelClassName: string;
}

export const CALLOUT_MARKER_PATTERN =
  /^\s*\[!(note|tip|important|warning|caution)\][\t ]*(?:\r?\n)?/i;

export const CALLOUT_CONFIG: Record<CalloutKind, CalloutConfig> = {
  note: {
    label: 'Note',
    borderClassName: 'border-l-accent-blue',
    labelClassName: 'text-accent-blue',
  },
  tip: {
    label: 'Tip',
    borderClassName: 'border-l-feedback-success',
    labelClassName: 'text-feedback-success',
  },
  important: {
    label: 'Important',
    borderClassName: 'border-l-accent-purple',
    labelClassName: 'text-accent-purple',
  },
  warning: {
    label: 'Warning',
    borderClassName: 'border-l-feedback-warning',
    labelClassName: 'text-feedback-warning',
  },
  caution: {
    label: 'Caution',
    borderClassName: 'border-l-feedback-danger',
    labelClassName: 'text-feedback-danger',
  },
};
