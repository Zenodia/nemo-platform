#!/usr/bin/env tsx
// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

/**
 * This script generates types for all OpenAPI specs in the NeMo Platform repository.
 * It uses concurrently for parallel execution while maintaining a clean structure.
 */

import { execSync } from 'child_process';
import { serviceConfigs } from './orval/constants';

const services = Object.keys(serviceConfigs) as Array<keyof typeof serviceConfigs>;

interface GenerationConfig {
  service: string;
  zod?: boolean;
}

const generationConfigs: GenerationConfig[] = [
  ...services.map((service) => ({ service, zod: serviceConfigs[service]?.zod })),
];

const generateCommands = (config: GenerationConfig) => {
  const { service, zod } = config;

  const baseCommand = `pnpm run gen:${service}`;
  if (zod) {
    return `${baseCommand} && pnpm run gen:${service}-zod`;
  }
  return baseCommand;
};

const main = async () => {
  console.log('🚀 Starting parallel type generation for all services...\n');

  // Build the concurrently command with all generation commands
  const commands = generationConfigs.map(generateCommands);

  // Create the concurrently command with names and colors
  const serviceNames = generationConfigs.map((config) => config.service);
  const colors = ['red', 'blue', 'green', 'yellow', 'magenta', 'cyan', 'purple', 'white', 'gray'];

  const concurrentlyArgs = [
    '--names',
    serviceNames.join(','),
    '-c',
    colors.slice(0, serviceNames.length).join(','),
    ...commands.map((cmd) => `"${cmd}"`),
  ];

  const concurrentlyCommand = `pnpm exec concurrently ${concurrentlyArgs.join(' ')}`;

  console.log('Executing commands in parallel:');
  commands.forEach((cmd, index) => {
    console.log(`  ${index + 1}. ${cmd}`);
  });
  console.log('');

  try {
    execSync(concurrentlyCommand, { stdio: 'inherit' });
    console.log('\n🎉 All type generation completed successfully!');
  } catch {
    console.error('\n💥 Some type generation failed. Check the output above for details.');
    process.exit(1);
  }
};

main().catch((error) => {
  console.error('💥 Fatal error during type generation:', error);
  process.exit(1);
});
