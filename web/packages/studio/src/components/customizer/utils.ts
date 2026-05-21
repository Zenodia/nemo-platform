// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { getTrainingOptionsLabel } from '@studio/routes/NewCustomizationRoute/util';

// Platform: Training options are part of hyperparameters, not a separate type
export const trainingOptionsToSelect = (options: Record<string, unknown>, idx: number) => {
  return {
    value: idx.toString(),
    children: getTrainingOptionsLabel(options),
  };
};
