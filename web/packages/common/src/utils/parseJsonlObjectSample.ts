// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

/** Synthetic column when a line is valid JSON but not a plain object (array, scalar, null). */
export const JSONL_SAMPLE_SCALAR_KEY = '__jsonlSampleScalar__';

/** Synthetic column when the line is not valid JSON; cell holds the raw line text. */
export const JSONL_SAMPLE_RAW_LINE_KEY = '__jsonlSampleRawLine__';

export interface JsonlObjectSampleRow {
  id: string;
  /** 1-based index within the sample */
  rowIndex: number;
  /** Top-level key to value for this row (values may be nested structures as JSON in cells). */
  values: Record<string, unknown>;
}

/**
 * Turns a newline-delimited sample (from {@link sampleTextLines}) into rows of objects and a
 * stable column key list (first-seen key order across rows).
 */
export function buildRowsAndKeysFromJsonlSample(text: string): {
  rows: JsonlObjectSampleRow[];
  columnKeys: string[];
} {
  const lines = text.split('\n').filter((line) => line.trim().length > 0);
  const keyOrder: string[] = [];
  const keySeen = new Set<string>();

  const trackKeys = (obj: Record<string, unknown>) => {
    for (const k of Object.keys(obj)) {
      if (!keySeen.has(k)) {
        keySeen.add(k);
        keyOrder.push(k);
      }
    }
  };

  const rows: JsonlObjectSampleRow[] = [];

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    let values: Record<string, unknown>;

    try {
      const parsed: unknown = JSON.parse(line);
      if (parsed !== null && typeof parsed === 'object' && !Array.isArray(parsed)) {
        values = parsed as Record<string, unknown>;
      } else {
        values = { [JSONL_SAMPLE_SCALAR_KEY]: JSON.stringify(parsed) };
      }
    } catch {
      values = { [JSONL_SAMPLE_RAW_LINE_KEY]: line };
    }

    trackKeys(values);
    rows.push({
      id: `jsonl-sample-${i}`,
      rowIndex: i + 1,
      values,
    });
  }

  return { rows, columnKeys: keyOrder };
}

export function formatJsonlSampleCellValue(value: unknown): string {
  if (value === undefined) {
    return '';
  }
  if (value === null) {
    return 'null';
  }
  if (typeof value === 'string') {
    return value;
  }
  if (typeof value === 'number' || typeof value === 'boolean') {
    return String(value);
  }
  try {
    return JSON.stringify(value);
  } catch {
    return String(value);
  }
}

export function labelForJsonlSampleColumnKey(key: string): string {
  if (key === JSONL_SAMPLE_SCALAR_KEY) {
    return '(non-object JSON)';
  }
  if (key === JSONL_SAMPLE_RAW_LINE_KEY) {
    return '(unparsed line)';
  }
  return key;
}
