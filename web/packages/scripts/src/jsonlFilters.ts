// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { readFileSync } from 'fs';

interface FilterOptions {
  filePath: string;
  column: string;
}

interface JsonRecord {
  [key: string]: string | number | boolean;
}

export const getUniqueColumnValues = (options: FilterOptions): string[] => {
  const { filePath, column } = options;

  // Read the file content
  const fileContent = readFileSync(filePath, 'utf-8');

  // Determine if it's JSONL or JSON
  const isJsonl = fileContent.includes('\n');

  // Parse the content
  let data: JsonRecord[];
  if (isJsonl) {
    data = fileContent
      .split('\n')
      .filter((line) => line.trim())
      .map((line) => JSON.parse(line));
  } else {
    data = JSON.parse(fileContent);
  }

  // Get unique values from the specified column
  const uniqueValues = Array.from(
    new Set(
      data
        .map((item) => item[column])
        .filter((value) => value !== undefined && value !== null)
        .map((value) => String(value))
    )
  ).sort();

  return uniqueValues;
};

// CLI interface
if (require.main === module) {
  const args = process.argv.slice(2);
  if (args.length < 2) {
    console.error('Usage: tsx jsonlFilters.ts <filePath> <column>');
    process.exit(1);
  }

  const [filePath, column] = args;
  const result = getUniqueColumnValues({
    filePath,
    column,
  });

  console.log(JSON.stringify(result, null, 2));
}
