// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

/** How to pick up to `maxRows` items from a sequence. */
export type FileSampleMethod = 'random' | 'head' | 'tail';

export const DEFAULT_MAX_FILE_SAMPLE_ROWS = 10;

/**
 * Picks up to `sampleSize` indices from `[0, populationSize)` using `method`.
 * Returned indices are always sorted ascending so callers preserve original
 * order regardless of method.
 */
export function sampleIndices(
  populationSize: number,
  method: FileSampleMethod,
  sampleSize: number
): number[] {
  if (populationSize <= 0 || sampleSize <= 0) return [];
  const cap = Math.min(sampleSize, populationSize);

  switch (method) {
    case 'head':
      return Array.from({ length: cap }, (_, i) => i);
    case 'tail':
      return Array.from({ length: cap }, (_, i) => populationSize - cap + i);
    case 'random': {
      const indices = Array.from({ length: populationSize }, (_, i) => i);
      for (let i = 0; i < cap; i++) {
        const j = i + Math.floor(Math.random() * (populationSize - i));
        const tmp = indices[i];
        indices[i] = indices[j];
        indices[j] = tmp;
      }
      return indices.slice(0, cap).sort((a, b) => a - b);
    }
    default: {
      const exhaustive: never = method;
      throw new Error(`Unhandled sample method: ${String(exhaustive)}`);
    }
  }
}

/**
 * Returns a newline-joined sample of non-empty lines from `text`.
 * Empty or whitespace-only lines are ignored for counting and sampling.
 */
export function sampleTextLines(
  text: string,
  method: FileSampleMethod,
  maxRows: number = DEFAULT_MAX_FILE_SAMPLE_ROWS
): string {
  const records = text.split(/\r?\n/).filter((line) => line.trim());
  return sampleIndices(records.length, method, maxRows)
    .map((index) => records[index])
    .join('\n');
}
