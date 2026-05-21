// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import seedrandom from 'seedrandom';

/**
 * Validates and calculates split counts from splits array (supports both numbers and percentages)
 * @param splits - Array of numbers or percentage strings
 * @param totalItems - Total number of items to split
 * @returns Array of calculated counts for each split
 */
const calculateSplitCounts = (splits: (number | string)[], totalItems: number): number[] => {
  if (splits.length === 0) {
    throw new Error('splits must be a non-empty array.');
  }

  const countOrPercentage = splits.map((val) => (typeof val === 'string' ? val.trim() : val));

  // Calculate total count if using percentages
  const totalPercentage = countOrPercentage
    .filter((item) => typeof item === 'string' && item.endsWith('%'))
    .reduce((sum: number, perc) => sum + parseFloat((perc as string).slice(0, -1)), 0);

  if (totalPercentage > 100) {
    throw new Error('Percentage values exceed 100%.');
  }

  // Calculate the count for each distribution
  const counts = countOrPercentage.map((item) => {
    if (typeof item === 'string' && item.endsWith('%')) {
      const percentage = parseFloat(item.slice(0, -1));
      return Math.floor((percentage / 100) * totalItems);
    } else if (typeof item === 'number') {
      return Math.min(item, totalItems);
    } else {
      throw new Error('Invalid count or percentage format.');
    }
  });

  const sum = counts.reduce((total, count) => total + count, 0);
  if (sum > totalItems) {
    throw new Error('Sum of splits is greater than total items.');
  }

  return counts;
};

/**
 * Splits an array into chunks based on calculated counts
 * @param array - Array to split
 * @param counts - Array of counts for each split
 * @returns Array of arrays, each containing a chunk of the original array
 */
const splitArrayByCounts = <T>(array: T[], counts: number[]): T[][] => {
  const result: T[][] = [];
  let index = 0;
  for (const count of counts) {
    result.push(array.slice(index, index + count));
    index += count;
  }
  return result;
};

/**
 * Shuffles an array using Fisher-Yates algorithm
 * @param array - Array to shuffle
 * @returns New shuffled array
 */

/**
 * Deterministically shuffles `items` using any serialisable `seed`.
 * Returns a new array — the original is left untouched.
 */
export const shuffleArray = <T>(items: T[], seed?: string): T[] => {
  const rng = seedrandom(seed); // 0 ≤ rng() < 1 (same sequence for same seed)
  const out = [...items]; // shallow-copy so we don’t mutate caller’s array

  // Fisher-Yates
  for (let i = out.length - 1; i > 0; i--) {
    const j = Math.floor(rng() * (i + 1));
    [out[i], out[j]] = [out[j], out[i]];
  }
  return out;
};

export const splitRandomDistribution = <T>(
  array: T[],
  splits: (number | string)[],
  seed?: string
): T[][] => {
  if (array.length === 0) {
    return [];
  }

  const counts = calculateSplitCounts(splits, array.length);
  const shuffledArray = shuffleArray(array, seed);
  return splitArrayByCounts(shuffledArray, counts);
};

/**
 * Finds a sortable key in an object using predefined common keys
 * @param obj - Object to search for sortable keys
 * @param preferredKey - Optional preferred key to use first
 * @returns Found sortable key or null
 */
export const SEQUENTIAL_DISTRIBUTION_KEYS = ['timestamp', 'date', 'created_at', 'id'];
const findSortableKey = <T extends Record<string, unknown>>(
  obj: T,
  preferredKey?: keyof T
): keyof T | null => {
  if (preferredKey && preferredKey in obj) {
    return preferredKey;
  }

  for (const key of SEQUENTIAL_DISTRIBUTION_KEYS) {
    if (key in obj) {
      return key as keyof T;
    }
  }

  return null;
};

/**
 * Sorts an array by a specified key with support for different data types
 * @param array - Array to sort
 * @param key - Key to sort by
 * @param direction - Sort direction ('asc' or 'desc')
 * @returns New sorted array
 */
const sortArrayByKey = <T extends Record<string, unknown>>(
  array: T[],
  key: keyof T,
  direction: 'asc' | 'desc' = 'asc'
): T[] => {
  return [...array].sort((a, b) => {
    const aVal = a[key];
    const bVal = b[key];

    let comparison = 0;

    if (typeof aVal === 'number' && typeof bVal === 'number') {
      comparison = aVal - bVal;
    } else if (typeof aVal === 'string' && typeof bVal === 'string') {
      comparison = aVal.localeCompare(bVal);
    } else if (aVal instanceof Date && bVal instanceof Date) {
      comparison = aVal.getTime() - bVal.getTime();
    } else {
      // Convert to string for comparison if types don't match
      const aStr = String(aVal);
      const bStr = String(bVal);
      comparison = aStr.localeCompare(bStr);
    }

    return direction === 'asc' ? comparison : -comparison;
  });
};

/**
 * Splits the array into a given number of parts using a sequential distribution
 * Sorts the array by a chosen key before splitting.
 * @param array - The array to split.
 * @param splits - The number of parts to split the array into.
 * @param sort - Optional sort configuration with key and direction
 * @returns An array of arrays, each containing a part of the original array.
 */
export const SEQUENTIAL_DISTRIBUTION_ERROR_MESSAGE =
  'No default keys match your file schema; provide a sort key.';
export const splitSequentialDistribution = <T extends Record<string, unknown>>(
  array: T[],
  splits: (number | string)[],
  sort?: {
    key?: keyof T;
    direction?: 'asc' | 'desc';
  }
): T[][] => {
  if (array.length === 0 || splits.length === 0) {
    return [];
  }

  // Find a sortable key
  const keyToSortBy = findSortableKey(array[0], sort?.key);
  if (!keyToSortBy) {
    throw new Error(SEQUENTIAL_DISTRIBUTION_ERROR_MESSAGE);
  }

  // Sort the array by the chosen key
  const sortedArray = sortArrayByKey(array, keyToSortBy, sort?.direction || 'asc');

  // Calculate split counts and split the array
  const counts = calculateSplitCounts(splits, sortedArray.length);
  return splitArrayByCounts(sortedArray, counts);
};

/**
 * Returns a new array with all duplicate values removed.
 * @param array - The array to remove duplicates from.
 * @returns A new array with all duplicate values removed.
 */
export const unique = <T>(array: T[]): T[] => {
  return [...new Set(array)];
};

/**
 * Returns a new array with all values that are present in both arrays.
 * @param array1 - The first array.
 * @param array2 - The second array.
 * @returns A new array with all values that are present in both arrays.
 */
export const intersection = <T>(array1: T[], array2: T[]): T[] => {
  return array1.filter((item) => array2.includes(item));
};
