// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

/**
 * Removes the UI-only `scoreType` discriminator before sending score definitions to the evaluate-metric API.
 */
export function cleanScoresObj<T extends { scoreType: unknown }>(
  scores: T[]
): Omit<T, 'scoreType'>[] {
  return scores.map((score) => {
    const next = { ...score };
    delete next.scoreType;
    return next as Omit<T, 'scoreType'>;
  });
}

export const parseTestDatasetRows = (raw: string): Record<string, unknown>[] => {
  const trimmed = raw.trim();

  // Try comma-separated array first: [obj, obj, ...] or obj, obj, ...
  try {
    const wrapped = trimmed.startsWith('[') ? trimmed : `[${trimmed}]`;
    return JSON.parse(wrapped) as Record<string, unknown>[];
  } catch {
    // Fall back to JSONL: one JSON object per line
    return trimmed
      .split('\n')
      .map((line) => line.trim())
      .filter((line) => line.length > 0)
      .flatMap((line) => {
        try {
          return [JSON.parse(line) as Record<string, unknown>];
        } catch {
          return [];
        }
      });
  }
};
