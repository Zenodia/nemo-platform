// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import type { BenchmarksListResponse } from '@nemo/sdk/generated/platform/schema';

export interface EvaluationBenchmarksDataViewProps {
  workspace: string;
  onRowClick?: (benchmark: BenchmarkItemWithId) => void;
}

export type BenchmarkItem = BenchmarksListResponse['data'][number];
export type BenchmarkItemWithId = BenchmarkItem & { id: string };
