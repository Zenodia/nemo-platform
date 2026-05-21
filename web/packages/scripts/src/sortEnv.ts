// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import * as fs from 'fs';
import * as path from 'path';
import yargs from 'yargs';
import { hideBin } from 'yargs/helpers';

const argv = yargs(hideBin(process.argv))
  .option('dir', {
    alias: 'd',
    type: 'string',
    describe: 'Directory containing .env files',
    demandOption: true,
  })
  .help()
  .alias('help', 'h')
  .parseSync();

interface EnvLine {
  type: 'comment' | 'variable' | 'empty';
  content: string;
  key?: string;
  value?: string;
}

const parseEnv = (content: string): EnvLine[] => {
  const lines = content.split(/\r?\n/);
  const result: EnvLine[] = [];

  for (const line of lines) {
    const trimmed = line.trim();

    if (!trimmed) {
      // remove empty lines
      continue;
    }

    if (trimmed.startsWith('#')) {
      // Preserve comments
      result.push({ type: 'comment', content: line });
      continue;
    }

    const [key, ...valueParts] = trimmed.split('=');
    const keyTrimmed = key.trim();
    const value = valueParts.join('=').trim();
    result.push({
      type: 'variable',
      content: line,
      key: keyTrimmed,
      value: value,
    });
  }

  return result;
};

const stringifyEnv = (envLines: EnvLine[]): string => {
  // Sort only the variable lines while preserving comments and their positions
  const sortedLines = [...envLines].sort((a, b) => {
    if (a.type === 'comment' && b.type === 'comment') return 0;
    if (a.type === 'comment') return -1;
    if (b.type === 'comment') return 1;
    return (a.key || '').localeCompare(b.key || '');
  });

  return sortedLines.map((line) => line.content).join('\n');
};

const sortEnvFile = (filePath: string) => {
  const original = fs.readFileSync(filePath, 'utf8');
  const parsed = parseEnv(original);
  const sortedContent = stringifyEnv(parsed);
  fs.writeFileSync(filePath, sortedContent + '\n', 'utf8');
  console.log(`✅ Sorted: ${filePath}`);
};

const sortAllEnvFilesInDir = (envDir: string) => {
  console.log(`Sorting .env files in ${envDir}`);
  if (!fs.existsSync(envDir)) {
    console.error(`❌ Directory does not exist: ${envDir}`);
    process.exit(1);
  }

  const files = fs.readdirSync(envDir);
  const envFiles = files.filter((file) => file.startsWith('.env'));

  if (envFiles.length === 0) {
    console.log(`No .env files found in ${envDir}`);
    return;
  }

  for (const file of envFiles) {
    const fullPath = path.join(envDir, file);
    sortEnvFile(fullPath);
  }
};

try {
  sortAllEnvFilesInDir(argv.dir);
} catch (error) {
  console.error('Error:', error instanceof Error ? error.message : error);
  process.exit(1);
}
