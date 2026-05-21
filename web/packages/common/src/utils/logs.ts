// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import type { PlatformJobLog } from '@nemo/sdk/generated/platform/schema';

/**
 * Formats platform job logs into a timestamped text block for display in a code snippet.
 */
export const formatLogs = (logEntries: PlatformJobLog[]): string => {
  return logEntries.map((log) => `[${log.timestamp}]   ${log.message}`).join('\n');
};
