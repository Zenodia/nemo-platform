// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { ChangeEvent } from 'react';

// https://react-hook-form.com/advanced-usage#TransformandParse
export interface Transform<T extends HTMLElement> {
  input?: (value: string) => unknown;
  output?: (e: ChangeEvent<T>) => unknown;
}

export const transformStrOrNum = (value: string): string | number => {
  const numberRegex = /^\d+(\.\d+)?$/;
  if (numberRegex.test(value)) {
    return parseInt(value); // Return as number if it's a valid number string
  }
  return value; // Otherwise, keep it as a string
};

interface FormatWhitespaceHyphensOptions {
  stripTrailing?: boolean;
}

/**
 * Collapses each run of whitespace and/or hyphens into a single hyphen, then strips leading
 * hyphens. By default, a trailing hyphen is preserved so controlled inputs can reflect an
 * in-progress separator after the user presses space.
 * e.g. `foo  bar` -> `foo-bar`, `a--b` -> `a-b`, `  x  ` -> `x-`
 */
export function formatWhitespaceHyphens(
  value: string | ChangeEvent<HTMLInputElement>,
  options: FormatWhitespaceHyphensOptions = {}
): string {
  const raw =
    typeof value === 'string' ? value : (value.currentTarget?.value ?? value.target.value);
  const formatted = raw.replace(/[\s-]+/g, '-').replace(/^-+/, '');
  return options.stripTrailing ? formatted.replace(/-+$/, '') : formatted;
}
