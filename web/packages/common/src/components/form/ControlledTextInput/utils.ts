// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

/**
 * Converts a string value to a number, handling edge cases for negative numbers, decimals, scientific notation, and empty strings.
 *
 * @param value - The string value to convert
 * @param fallback - Optional fallback value if conversion fails
 * @returns The converted number or fallback value
 */
export const stringToNumber = (
  value: string,
  fallback?: number | undefined
): number | undefined => {
  // Handle empty string or whitespace-only strings
  if (!value.length || value.trim() === '') {
    return fallback;
  }

  // Remove leading/trailing whitespace
  const trimmedValue = value.trim();

  // Check if the value is a valid number (including negative numbers, decimals, and scientific notation)
  // This regex allows: optional minus sign, digits, optional decimal point with digits, optional scientific notation
  const numberRegex = /^-?(\d+\.?\d*|\d*\.\d+)([eE][+-]?\d+)?$/;

  if (!numberRegex.test(trimmedValue)) {
    return fallback;
  }

  // Convert to number
  const num = Number(trimmedValue);

  // Check if the result is a valid finite number
  if (isNaN(num) || !isFinite(num)) {
    return fallback;
  }

  return num;
};

/**
 * Converts a string value to an integer, handling edge cases for negative numbers and empty strings.
 * Decimals are truncated (not rounded).
 *
 * @param value - The string value to convert
 * @param fallback - Optional fallback value if conversion fails
 * @returns The converted integer or fallback value
 */
export const stringToInteger = (
  value: string,
  fallback?: number | undefined
): number | undefined => {
  const num = stringToNumber(value, fallback);
  return num !== undefined ? Math.trunc(num) : undefined;
};
