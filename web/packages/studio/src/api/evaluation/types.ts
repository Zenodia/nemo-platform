// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import type { EvaluationParameters } from '@nemo/sdk/generated/platform/schema';

/** Flattened evaluation params (params + extra merged). */
export type FlattenedEvaluationParams = EvaluationParameters & Record<string, unknown>;

/**
 * Enum for evaluation target modes
 */
export enum EvaluationTargetMode {
  ONLINE = 'online',
  OFFLINE = 'offline',
}
