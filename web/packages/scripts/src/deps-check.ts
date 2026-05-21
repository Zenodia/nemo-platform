// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { execFileSync } from 'node:child_process';
import * as path from 'node:path';
import { fileURLToPath } from 'node:url';
import { __dirname } from './getDirname';

interface KnipJsonIssue {
  file: string;
  dependencies?: { name: string }[];
}

interface KnipJsonReport {
  issues: KnipJsonIssue[];
}

const main = () => {
  if (!process.argv[2]) {
    throw new Error('Missing workspace directory as cli argument');
  }
  const webRoot = path.resolve(__dirname, '../../../');
  const workspaceDir = process.argv[2];
  const exclusions = new Set(process.argv[3]?.split(',').filter(Boolean));

  const knipEntry = fileURLToPath(import.meta.resolve('knip'));
  const knipBin = path.join(path.dirname(knipEntry), '..', 'bin', 'knip.js');

  const stdout = execFileSync(
    process.execPath,
    [
      knipBin,
      '--workspace',
      workspaceDir,
      '--include',
      'dependencies',
      '--reporter',
      'json',
      '--no-exit-code',
      '--no-progress',
      '--no-config-hints',
    ],
    { cwd: webRoot, encoding: 'utf8', stdio: ['ignore', 'pipe', 'inherit'] }
  );

  const report: KnipJsonReport = JSON.parse(stdout);
  const unused = new Set<string>();
  for (const issue of report.issues) {
    for (const dep of issue.dependencies ?? []) {
      if (!exclusions.has(dep.name)) unused.add(dep.name);
    }
  }

  if (unused.size > 0) {
    console.log(`\x1b[31mUnused dependencies: ${[...unused].join(', ')}\x1b[0m`);
    process.exit(1);
  }
  console.log('All dependencies are used.');
};

main();
