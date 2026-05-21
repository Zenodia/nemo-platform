// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

/**
 * Recursively removes empty objects, arrays, and undefined/null values from an object
 */
export const removeEmptyValues = (obj: unknown): unknown => {
  if (obj === null || obj === undefined) {
    return undefined;
  }

  if (Array.isArray(obj)) {
    const filtered = obj.map(removeEmptyValues).filter((v) => v !== undefined);
    return filtered.length > 0 ? filtered : undefined;
  }

  if (typeof obj === 'object') {
    const filtered = Object.entries(obj)
      .map(([key, value]) => [key, removeEmptyValues(value)])
      .filter(([, value]) => value !== undefined);

    const result = Object.fromEntries(filtered);
    return Object.keys(result).length > 0 ? result : undefined;
  }

  return obj;
};
