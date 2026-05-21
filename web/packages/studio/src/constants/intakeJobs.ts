// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { JobStatus } from '@nemo/sdk/generated/platform/schema';

export const EXPORT_JOB_STATUS_FILTER_OPTIONS = [
  { value: JobStatus.pending, label: 'Pending' },
  { value: JobStatus.running, label: 'Running' },
  { value: JobStatus.completed, label: 'Completed' },
  { value: JobStatus.failed, label: 'Failed' },
  { value: JobStatus.cancelled, label: 'Cancelled' },
];
