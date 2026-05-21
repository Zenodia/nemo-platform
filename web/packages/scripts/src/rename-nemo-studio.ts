// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import * as fs from 'fs';
import * as path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const packagesDir = path.resolve(__dirname, '../..');

// Build the search string dynamically so the codemod doesn't rewrite itself
const SEARCH = ['@nemo', '-studio/'].join('');
const REPLACE = '@nemo/';
const EXTENSIONS = new Set(['.ts', '.tsx']);

function walk(dir: string): string[] {
  const results: string[] = [];
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    if (entry.name === 'node_modules' || entry.name === 'dist') continue;
    const fullPath = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      results.push(...walk(fullPath));
    } else if (EXTENSIONS.has(path.extname(entry.name))) {
      results.push(fullPath);
    }
  }
  return results;
}

const files = walk(packagesDir);
let updatedCount = 0;

for (const file of files) {
  const content = fs.readFileSync(file, 'utf8');
  if (!content.includes(SEARCH)) continue;

  const updated = content.replaceAll(SEARCH, REPLACE);
  fs.writeFileSync(file, updated, 'utf8');
  updatedCount++;
  console.log(`  updated: ${path.relative(packagesDir, file)}`);
}

console.log(`\n${updatedCount} file(s) updated.`);
