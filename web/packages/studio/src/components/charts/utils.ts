// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

interface Options<T> {
  list: T[];
  timestampKey?: string;
  defaultValues: Record<string, unknown>;
}

/**
 * Handles edge case where the graph doesn't render if the metric data only contains one value.
 * Adds an extra dummy data point that represents an empty value at step 0.
 * @param param0
 * @returns
 */
export const prefixDummyPoint = <T extends object>({
  list,
  timestampKey = 'timestamp',
  defaultValues,
}: Options<T>) => {
  if (list.length === 1 && list[0]) {
    const firstEntry = list[0];
    if (timestampKey in firstEntry && typeof firstEntry[timestampKey as keyof T] === 'string') {
      // Convert timestamp to a JavaScript Date object
      const originalDate = new Date(firstEntry[timestampKey as keyof T] as string);
      // Use timetamp one millisecond before the existing data point's timestamp as the first data point for x-axis.
      const rightBefore = new Date(originalDate.getTime() - 1);
      return [
        {
          [timestampKey]: rightBefore.toUTCString(),
          ...defaultValues,
        },
        ...list,
      ] as T[];
    }
  }

  return list;
};
