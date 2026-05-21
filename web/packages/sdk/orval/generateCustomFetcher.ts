// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import fs from 'fs';
import type { ServiceConfig } from './constants';
import path from 'path';

/**
 * Utility function to get base URL from environment variables in order of preference
 * @param envVarNames - Array of environment variable names to check in order
 * @param errorMessage - Optional custom error message when no variables are found
 * @returns The first found environment variable value
 * @throws Error if none of the environment variables are defined
 */
const getTemplateBaseUrls = (envVarNames: string[]): string => {
  const checks = envVarNames
    .map((varName) => {
      return `  // Check Vite environment variables first (import.meta.env)
  const VITE_VALUE_${varName} = import.meta.env.${varName};
  if (VITE_VALUE_${varName} && VITE_VALUE_${varName}.trim() !== '') {
    return resolveBrowserBaseUrl(VITE_VALUE_${varName});
  }

  // Fallback to Node.js process.env
  if (typeof process !== 'undefined' && process.env) {
    const NODE_VALUE_${varName.replace(/^VITE_/, '')} = process.env.${varName.replace(/^VITE_/, '')};
    if (NODE_VALUE_${varName.replace(/^VITE_/, '')} && NODE_VALUE_${varName.replace(/^VITE_/, '')}.trim() !== '') {
      return NODE_VALUE_${varName.replace(/^VITE_/, '')};
    }
  }
`;
    })
    .join('\n\n');

  return `${checks}
  // If no variables found, return empty string
  return '';`;
};

/**
 * Reads a template file and replaces placeholders with actual values
 */
const readTemplate = (templateName: string, replacements: Record<string, string> = {}): string => {
  const templatePath = path.join(__dirname, 'templates', templateName);
  let content = fs.readFileSync(templatePath, 'utf8');

  // Replace all placeholders in the template
  Object.entries(replacements).forEach(([key, value]) => {
    // Handle comment-based format
    const commentPlaceholder = new RegExp(
      `  // TEMPLATE_${key}_START[\\s\\S]*?  // TEMPLATE_${key}_END`,
      'g'
    );

    // Then try comment-based format
    if (commentPlaceholder.test(content)) {
      content = content.replace(commentPlaceholder, value);
    }
  });

  return content;
};

/**
 * Generates a custom fetcher for a specific service
 * @param config - The service configuration object
 */
export const generateCustomFetcher = (config: ServiceConfig) => {
  // Use the standard template with service-specific replacements
  const customFetcherContent = readTemplate('customFetcherTemplate.ts', {
    BASE_URL_CHECKS: getTemplateBaseUrls(config.apiEnvKeys || []),
  });
  // Write the custom fetcher to the generated service folder
  const outputPath = path.join(__dirname, '..', 'generated', 'fetchers', `${config.path}.ts`);

  // Ensure the directory exists
  const outputDir = path.dirname(outputPath);
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  fs.writeFileSync(outputPath, customFetcherContent);
  console.log(`✅ Generated custom fetcher for ${config.path} at ${outputPath}`);
};
