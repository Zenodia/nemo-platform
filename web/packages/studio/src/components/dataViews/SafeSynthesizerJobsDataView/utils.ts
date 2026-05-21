// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import type { SafeSynthesizerJob } from '@nemo/sdk/vendored/safe-synthesizer/schema';

export const isCancellableJob = (status: SafeSynthesizerJob['status']) => {
  return status === 'created' || status === 'pending' || status === 'active';
};
