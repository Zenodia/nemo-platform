// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

/** The <option> that represents that the user wants to make a new configuration */
export const NEW_CONFIG_SELECT_OPTION = { label: 'New Configuration', value: 'New Configuration' };

/**
 * External documentation links for evaluation features
 */
export const EVALUATION_DOCS_LINKS = {
  CUSTOM_DATA: 'https://docs.nvidia.com/nemo/microservices/latest/evaluate/flows/template.html',
  OUTPUT_FORMAT:
    'https://docs.nvidia.com/nemo/microservices/latest/evaluate/evaluation-custom/output.html',
  CONFIG_TARGETS:
    'https://docs.nvidia.com/nemo/microservices/latest/evaluate/evaluation-jobs/job-target-and-config-matrix.html',
  EVALUATION_TARGETS:
    'https://docs.nvidia.com/nemo/microservices/latest/about/core-concepts/evaluation.html#evaluation-targets',
  EVALUATION_CONFIGS:
    'https://docs.nvidia.com/nemo/microservices/latest/about/core-concepts/evaluation.html#evaluation-configs',
  METRICS: 'https://docs.nvidia.com/nemo/microservices/latest/evaluate/flows/template.html#metrics',
} as const;
