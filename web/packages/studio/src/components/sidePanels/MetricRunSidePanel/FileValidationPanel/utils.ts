// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { InputFileSchemaType } from '@nemo/common/src/types';
import { extractUserFriendlyKeysFromRow, getFileRowCount } from '@nemo/common/src/utils/file';
import {
  detectFileStructure,
  type FileFormatDetectionResult,
  validateFileFormat,
} from '@nemo/common/src/utils/fileValidation';
import Papa from 'papaparse';

export type MetricRunValidationFileFormat = 'json' | 'jsonl' | 'csv' | 'parquet';

export interface MetricRunFileValidationResult {
  isValid: boolean;
  format: MetricRunValidationFileFormat | null;
  rowCount?: number;
  detectionResult?: FileFormatDetectionResult;
  availableKeys: Array<{ label: string; value: string }>;
  rootKeys: string[];
  templateFields: string[];
  missingTemplateFields: string[];
  error?: string;
}

export const getMetricRunFileFormatFromPath = (
  path: string
): MetricRunValidationFileFormat | null => {
  const extension = path.toLowerCase().split('.').pop();
  if (
    extension === 'json' ||
    extension === 'jsonl' ||
    extension === 'csv' ||
    extension === 'parquet'
  ) {
    return extension;
  }
  return null;
};

const normalizeTemplateField = (value: string): string | null => {
  const trimmed = value.trim();
  if (!trimmed || trimmed.startsWith('"') || trimmed.startsWith("'")) return null;
  if (trimmed === 'sample' || trimmed.startsWith('sample.')) return null;

  const withoutItemPrefix = trimmed.startsWith('item.') ? trimmed.slice('item.'.length) : trimmed;
  const rootField = withoutItemPrefix.split(/[.[\s]/)[0];
  return /^[A-Za-z_][A-Za-z0-9_-]*$/.test(rootField) ? rootField : null;
};

export const extractPromptTemplateFields = (promptTemplate: string): string[] => {
  const fields = new Set<string>();
  const jinjaExpressionPattern = /{{\s*([^}|]+?)(?:\s*\|[^}]*)?}}/g;
  const formatExpressionPattern = /(^|[^{]){([A-Za-z_][A-Za-z0-9_.-]*)}(?!})/g;

  for (const match of promptTemplate.matchAll(jinjaExpressionPattern)) {
    const field = normalizeTemplateField(match[1] ?? '');
    if (field) fields.add(field);
  }

  for (const match of promptTemplate.matchAll(formatExpressionPattern)) {
    const field = normalizeTemplateField(match[2] ?? '');
    if (field) fields.add(field);
  }

  return Array.from(fields);
};

export const getMetricRunTemplateFieldValidation = (
  promptTemplate: string,
  rootKeys: string[]
): Pick<MetricRunFileValidationResult, 'templateFields' | 'missingTemplateFields'> => {
  const templateFields = extractPromptTemplateFields(promptTemplate);
  return {
    templateFields,
    missingTemplateFields: templateFields.filter((field) => !rootKeys.includes(field)),
  };
};

const detectTabularSchema = (
  firstRow: Record<string, unknown>,
  jobType: 'online' | 'offline'
): FileFormatDetectionResult => {
  const promptKeys = ['prompt', 'input', 'question', 'query'];
  const completionKeys = ['completion', 'ideal_response', 'response', 'output', 'answer'];

  const promptKey = promptKeys.find((key) => firstRow[key] !== undefined);
  const completionKey = completionKeys.find((key) => firstRow[key] !== undefined);

  if (promptKey || completionKey) {
    const hasRequiredFields = !!(promptKey && completionKey);
    return {
      schemaType: InputFileSchemaType.COMPLETION,
      detectedFields: {
        ...(promptKey ? { prompt: promptKey } : {}),
        ...(completionKey ? { completion: completionKey } : {}),
      },
      isComplete: jobType === 'offline' ? false : hasRequiredFields,
      firstRow,
    };
  }

  return {
    schemaType: null,
    firstRow,
  };
};

const validateCsvContent = (
  content: string,
  promptTemplate: string,
  jobType: 'online' | 'offline'
): MetricRunFileValidationResult => {
  const parsed = Papa.parse<Record<string, unknown>>(content, {
    header: true,
    skipEmptyLines: true,
  });

  if (parsed.errors.length > 0) {
    return {
      isValid: false,
      format: 'csv',
      availableKeys: [],
      rootKeys: [],
      templateFields: [],
      missingTemplateFields: [],
      error: parsed.errors[0]?.message ?? 'File is not valid CSV',
    };
  }

  const fields = parsed.meta.fields ?? [];
  const rows = parsed.data;

  if (fields.length === 0) {
    return {
      isValid: false,
      format: 'csv',
      availableKeys: [],
      rootKeys: [],
      templateFields: [],
      missingTemplateFields: [],
      error: 'CSV header row is missing',
    };
  }

  if (rows.length === 0) {
    return {
      isValid: false,
      format: 'csv',
      availableKeys: [],
      rootKeys: fields,
      templateFields: [],
      missingTemplateFields: [],
      error: 'File contains no data',
    };
  }

  const firstRow = rows[0] ?? {};
  const rootKeys = fields;
  const templateValidation = getMetricRunTemplateFieldValidation(promptTemplate, rootKeys);
  return {
    isValid: true,
    format: 'csv',
    rowCount: rows.length,
    detectionResult: detectTabularSchema(firstRow, jobType),
    availableKeys: fields.map((field) => ({ label: field, value: field })),
    rootKeys,
    ...templateValidation,
  };
};

const parseNormalizedParquetRows = (content: string): Record<string, unknown>[] => {
  const rows: Record<string, unknown>[] = [];
  const lines = content.split('\n').filter((line) => line.trim());

  for (const line of lines) {
    const parsed = JSON.parse(line) as unknown;
    if (typeof parsed !== 'object' || parsed === null || Array.isArray(parsed)) {
      throw new Error('Parquet row preview must contain objects');
    }
    rows.push(parsed as Record<string, unknown>);
  }

  return rows;
};

const validateNormalizedParquetContent = (
  content: string,
  promptTemplate: string,
  jobType: 'online' | 'offline'
): MetricRunFileValidationResult => {
  const emptyRootTemplateValidation = getMetricRunTemplateFieldValidation(promptTemplate, []);

  let rows: Record<string, unknown>[];
  try {
    rows = parseNormalizedParquetRows(content);
  } catch {
    return {
      isValid: false,
      format: 'parquet',
      availableKeys: [],
      rootKeys: [],
      ...emptyRootTemplateValidation,
      error: 'Parquet file preview could not be parsed',
    };
  }

  if (rows.length === 0) {
    return {
      isValid: false,
      format: 'parquet',
      availableKeys: [],
      rootKeys: [],
      ...emptyRootTemplateValidation,
      error: 'File contains no data',
    };
  }

  const firstRow = rows[0] ?? {};
  const rootKeys = Object.keys(firstRow);
  const templateValidation = getMetricRunTemplateFieldValidation(promptTemplate, rootKeys);

  return {
    isValid: true,
    format: 'parquet',
    rowCount: rows.length,
    detectionResult: detectTabularSchema(firstRow, jobType),
    availableKeys: extractUserFriendlyKeysFromRow(firstRow),
    rootKeys,
    ...templateValidation,
  };
};

export const validateMetricRunFileContent = async ({
  content,
  path,
  promptTemplate,
  jobType,
}: {
  content: string;
  path: string;
  promptTemplate: string;
  jobType: 'online' | 'offline';
}): Promise<MetricRunFileValidationResult> => {
  const format = getMetricRunFileFormatFromPath(path);
  const emptyRootTemplateValidation = getMetricRunTemplateFieldValidation(promptTemplate, []);

  if (!format) {
    return {
      isValid: false,
      format: null,
      availableKeys: [],
      rootKeys: [],
      ...emptyRootTemplateValidation,
      error: 'Unsupported file type',
    };
  }

  if (format === 'csv') {
    return validateCsvContent(content, promptTemplate, jobType);
  }

  if (format === 'parquet') {
    return validateNormalizedParquetContent(content, promptTemplate, jobType);
  }

  const file = new File([content], path, { type: 'application/json' });
  const validationResult = await validateFileFormat(file);

  if (!validationResult.isValid || !validationResult.format) {
    return {
      isValid: false,
      format,
      availableKeys: [],
      rootKeys: [],
      ...emptyRootTemplateValidation,
      error: validationResult.error ?? `File is not valid ${format.toUpperCase()}`,
    };
  }

  const detectionResult = await detectFileStructure(file, format, jobType);
  const firstRow = detectionResult?.firstRow ?? {};
  const rowCount = await getFileRowCount(file, format);
  const availableKeys = extractUserFriendlyKeysFromRow(firstRow);
  const rootKeys = Object.keys(firstRow);
  const templateValidation = getMetricRunTemplateFieldValidation(promptTemplate, rootKeys);

  return {
    isValid: true,
    format,
    rowCount,
    detectionResult,
    availableKeys,
    rootKeys,
    ...templateValidation,
  };
};
