// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

export const debounceAsyncRequest = <T extends (...args: Parameters<T>) => Promise<void>>(
  fn: T,
  delay = 2000
) => {
  let timeoutId: NodeJS.Timeout;
  return (...args: Parameters<T>) => {
    if (timeoutId) {
      clearTimeout(timeoutId);
    }
    timeoutId = setTimeout(() => {
      fn(...args);
    }, delay);
  };
};

/**
 * Checks if a number is a power of a given base
 * @param value - The number to check
 * @param base - The base to check against (defaults to 2)
 * @returns true if the number is a power of the base, false otherwise
 */
export const isPowerOf = (value: number, base: number = 2) => {
  if (value <= 0 || base <= 1) {
    return false;
  }

  // For base 2, use the bitwise optimization
  if (base === 2) {
    return (value & (value - 1)) === 0;
  }

  // For other bases, use logarithm approach
  const logResult = Math.log(value) / Math.log(base);
  return Number.isInteger(logResult) && logResult >= 0;
};

export function assertUnreachable(value: never, message?: string): never {
  throw new Error(message ?? `Unknown state: ${JSON.stringify(value)}. This should never happen.`);
}
