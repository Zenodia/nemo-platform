// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import type { ChatCompletionMessageRowValues } from '@nemo/common/src/components/ChatCompletionInput';
import type { ModelSelection } from '@nemo/common/src/components/ModelSelectV2';
import type { InferenceParams } from '@nemo/sdk/generated/platform/schema';
import type { SidePanel } from '@nvidia/foundations-react-core';
import type { MetricItemWithId } from '@studio/components/dataViews/EvaluationMetricsDataView/types';
import type { ComponentProps } from 'react';

export interface MetricRunSidePanelProps {
  metric: MetricItemWithId | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  workspace: string;
  attributes?: {
    SidePanel?: ComponentProps<typeof SidePanel>;
  };
}

export interface MetricRunSidePanelFormData {
  jobType: 'online' | 'offline';
  dataset: string | null;
  model: ModelSelection | null;
  inferenceParams: Partial<InferenceParams>;
  promptMessages: ChatCompletionMessageRowValues[];
  metricName: string | null;
  ignore_request_failure: boolean;
}
