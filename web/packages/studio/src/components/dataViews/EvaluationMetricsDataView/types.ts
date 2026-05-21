// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import type { DatetimeFilter, MetricsListResponse } from '@nemo/sdk/generated/platform/schema';

/** Filter fields for the metrics list API. */
export interface EvaluationMetricsFilterFields {
  name?: string;
  description?: string;
  type?: string;
  project?: string;
  created_at?: DatetimeFilter;
  updated_at?: DatetimeFilter;
}

export interface EvaluationMetricsDataViewProps {
  workspace: string;
  onRowClick?: (metric: MetricItemWithId) => void;
}

export type MetricItem = MetricsListResponse['data'][number];
export type MetricItemWithId = MetricItem & { id: string };
