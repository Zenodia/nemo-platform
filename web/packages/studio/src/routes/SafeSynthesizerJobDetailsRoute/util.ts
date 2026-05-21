// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { formatElapsedTime } from '@studio/util/date';

export const SAFE_SYNTHESIZER_POLLING_INTERVAL_MS = 5000;

/**
 * Parses an ISO timestamp string as UTC, even if it lacks a timezone indicator.
 * @param dateString - ISO 8601 timestamp (with or without timezone)
 */
const parseUTCTimestamp = (dateString: string): Date => {
  // If already has timezone indicator (Z or +/-offset), use as-is
  if (dateString.endsWith('Z') || /[+-]\d{2}:\d{2}$/.test(dateString)) {
    return new Date(dateString);
  }
  // Otherwise, append 'Z' to treat as UTC
  return new Date(dateString + 'Z');
};

export const getElapsedTime = (created_at?: string, resultSummary_total_time_sec?: number) => {
  if (!created_at) return null;
  const startDate = parseUTCTimestamp(created_at);
  if (resultSummary_total_time_sec == null) return formatElapsedTime(startDate, new Date());
  const endDate = new Date(startDate.getTime() + resultSummary_total_time_sec * 1000);
  return formatElapsedTime(startDate, endDate);
};
