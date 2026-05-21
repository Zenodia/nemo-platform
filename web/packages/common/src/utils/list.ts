// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

/**
 * Checks if a value is defined (not null or undefined).
 * @param value - The value to check
 * @returns True if the value is not null or undefined
 * @example
 * const items = [1, null, 3, undefined, 5];
 * const definedItems = items.filter(isDefined); // [1, 3, 5]
 */
export const isDefined = <T>(value: T): value is NonNullable<T> => {
  return value !== null && value !== undefined;
};
