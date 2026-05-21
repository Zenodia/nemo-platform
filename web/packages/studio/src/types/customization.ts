// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import type { CustomizationJobStatusDetails } from '@nemo/sdk/vendored/customizer/schema';

export interface CustomizationMetricValue {
  step: number;
  value: number;
  epoch?: number;
}

/**
 * Training-progress fields that get merged into status_details
 * once training callbacks start reporting.
 */
export interface CustomizationStatusDetailsWithMetrics extends CustomizationJobStatusDetails {
  metrics?: {
    train_loss?: CustomizationMetricValue[];
    val_loss?: CustomizationMetricValue[];
  };
}

export function hasMetrics(
  statusDetails: CustomizationJobStatusDetails | undefined
): statusDetails is CustomizationStatusDetailsWithMetrics {
  return statusDetails !== undefined && 'metrics' in statusDetails;
}
