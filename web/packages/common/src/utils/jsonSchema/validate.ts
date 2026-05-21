// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import Ajv2020 from 'ajv/dist/2020';

/**
 * Client-side mirror of the backend's `jsonschema.validator_for(...).check_schema(...)`
 * pre-flight: confirm that a value is a structurally valid JSON Schema document.
 *
 * Uses the Draft 2020-12 meta-schema to match the `$schema` value emitted by
 * `inferJsonSchema`.
 */

const ajv = new Ajv2020({ strict: false, allErrors: true });

export interface ValidationResult {
  valid: boolean;
  errors: string[];
}

export type ParseAndValidateResult =
  | { valid: true; value: Record<string, unknown> }
  | { valid: false; errors: string[] };

export function validateJsonSchemaDocument(schema: unknown): ValidationResult {
  const valid = ajv.validateSchema(schema as object);
  if (valid) return { valid: true, errors: [] };
  const errors = (ajv.errors ?? []).map(formatError);
  return { valid: false, errors: errors.length > 0 ? errors : ['Invalid JSON Schema document'] };
}

/**
 * Parse a JSON string and validate the resulting value as a JSON Schema document.
 * Returns the parsed object on success, or a list of error messages on failure.
 */
export function parseAndValidate(text: string): ParseAndValidateResult {
  let parsed: unknown;
  try {
    parsed = JSON.parse(text);
  } catch (err) {
    return { valid: false, errors: [`Invalid JSON: ${(err as Error).message}`] };
  }
  if (parsed === null || typeof parsed !== 'object' || Array.isArray(parsed)) {
    return { valid: false, errors: ['JSON Schema document must be a JSON object'] };
  }
  const result = validateJsonSchemaDocument(parsed);
  if (!result.valid) return { valid: false, errors: result.errors };
  return { valid: true, value: parsed as Record<string, unknown> };
}

function formatError(err: { instancePath?: string; message?: string }): string {
  const path = err.instancePath || '';
  const msg = err.message ?? 'invalid';
  return path ? `${path} ${msg}` : msg;
}
