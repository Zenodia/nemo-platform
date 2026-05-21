// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

/**
 * Calculates the difference in seconds between two ISO date-time strings.
 * @param date1 ISO date-time string or undefined.
 * @param date2 ISO date-time string or undefined.
 * @returns The difference in seconds between the two dates, or undefined if either date is undefined.
 */
export const getDifferenceInMilliseconds = (date1?: string, date2?: string) => {
  if (!date1 || !date2) return undefined;
  const dateValue1 = new Date(date1);
  const dateValue2 = new Date(date2);
  return dateValue2.getTime() - dateValue1.getTime();
};

/**
 * Converts a UTC ISO string to a local Date object.
 * Handles ISO strings with or without timezone indicators.
 * @param utcIsoString UTC ISO date-time string (e.g., "2025-11-17T21:53:35.903780" or "2025-11-17T21:53:35.903780Z")
 * @returns Date object in the browser's local timezone, or undefined if the input is invalid
 * @example
 * utcToLocalDate("2025-11-17T21:53:35.903780") // Returns Date object in local time
 * utcToLocalDate("2025-11-17T21:53:35.903780Z") // Returns Date object in local time
 */
export const utcToLocalDate = (utcIsoString?: string): Date | undefined => {
  if (!utcIsoString) return undefined;

  // If the string doesn't have a timezone indicator (Z or +/-HH:MM), append 'Z' to treat it as UTC
  const hasTimezone = /Z|[+-]\d{2}:\d{2}$/.test(utcIsoString);
  const isoString = hasTimezone ? utcIsoString : `${utcIsoString}Z`;

  const date = new Date(isoString);

  // Check if the date is valid
  if (isNaN(date.getTime())) {
    return undefined;
  }

  return date;
};

/**
 * Formats the time in seconds into a human-friendly string
 * Only showing the minimum units needed to represent the time
 */
export const formatTimeInSeconds = (seconds?: number) => {
  if (!seconds) return '';
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const remainingSeconds = Math.floor(seconds % 60);
  return [hours, minutes, remainingSeconds]
    .map((val, idx) => `${val}${idx === 0 ? 'h' : idx === 1 ? 'm' : 's'}`)
    .filter((val) => parseInt(val) > 0)
    .join(' ');
};
