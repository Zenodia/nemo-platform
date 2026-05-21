#!/usr/bin/env node
// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { execSync } from 'child_process';
import fs from 'fs';
import path from 'path';

const pkgPath = path.resolve(process.cwd(), 'package.json');
const pkg = JSON.parse(fs.readFileSync(pkgPath, 'utf8')) as {
  scripts: {
    lint: string;
    'lint:fix': string;
  };
};

// Run ESLint and capture output
let output: string;
try {
  output = execSync('pnpm exec eslint . --format json', { encoding: 'utf8' });
} catch (e) {
  output = (e as { stdout: string }).stdout;
}

const results: Array<{ warningCount: number }> = JSON.parse(output);
const warningCount: number = results.reduce((sum, file) => sum + file.warningCount, 0);

// Find current max-warnings
const lintScript: string = pkg.scripts.lint;
const lintFixScript: string = pkg.scripts['lint:fix'];
const maxWarningsRegex = /--max-warnings (\d+)/;
const currentMax: number = parseInt(lintScript.match(maxWarningsRegex)?.[1] || '0', 10);

if (warningCount < currentMax) {
  pkg.scripts.lint = lintScript.replace(maxWarningsRegex, `--max-warnings ${warningCount}`);
  pkg.scripts['lint:fix'] = lintFixScript.replace(
    maxWarningsRegex,
    `--max-warnings ${warningCount}`
  );
  fs.writeFileSync(pkgPath, JSON.stringify(pkg, null, 2) + '\n');
  // eslint-disable-next-line no-console
  console.log(`Updated max-warnings to ${warningCount}`);
} else {
  // eslint-disable-next-line no-console
  console.log(`No update needed. Current warnings: ${warningCount}, max-warnings: ${currentMax}`);
}
