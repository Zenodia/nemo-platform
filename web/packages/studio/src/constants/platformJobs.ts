// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { PlatformJobStatus } from '@nemo/sdk/generated/platform/schema';

export const STATUS_FILTER_OPTIONS = [
  { value: PlatformJobStatus.created, label: 'Created' },
  { value: PlatformJobStatus.pending, label: 'Pending' },
  { value: PlatformJobStatus.active, label: 'Active' },
  { value: PlatformJobStatus.completed, label: 'Completed' },
  { value: PlatformJobStatus.error, label: 'Error' },
  { value: PlatformJobStatus.cancelled, label: 'Cancelled' },
  { value: PlatformJobStatus.cancelling, label: 'Cancelling' },
  { value: PlatformJobStatus.paused, label: 'Paused' },
  { value: PlatformJobStatus.pausing, label: 'Pausing' },
  { value: PlatformJobStatus.resuming, label: 'Resuming' },
];
