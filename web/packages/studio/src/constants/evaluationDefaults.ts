// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

/**
 * Default template strings and constants for evaluation forms and metrics.
 * Used by LLMJudgeInput, e2e tests, and evaluation configuration.
 */

/** Placeholder for ideal/ground-truth response in LLM judge config template. */
export const defaultIdealMessage = 'Response 1';

/** Placeholder for model output in LLM judge config template. */
export const defaultOutputText = 'Response 2';

/**
 * Template string for ideal/ground-truth column in evaluation metrics.
 * Matches eval fixture columns (e.g. ideal_response).
 */
export const defaultIdealResponse = '{{sample.ideal_response | trim}}';
