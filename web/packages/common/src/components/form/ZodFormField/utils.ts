// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { snakeCaseToTitleCase } from '@nemo/common/src/utils/formatters';
import { z } from 'zod';

// Helper function to determine if a field is required
export const isRequired = (zodSchema: z.ZodTypeAny, required: boolean): boolean => {
  if (zodSchema instanceof z.ZodOptional) {
    return false;
  }
  if (zodSchema instanceof z.ZodDefault) {
    return false;
  }
  return required;
};

// Helper function to get the base schema (unwrap optional/default)
export const getBaseSchema = (zodSchema: z.ZodTypeAny): z.ZodTypeAny => {
  let unwrappedSchema = zodSchema;
  while (
    unwrappedSchema instanceof z.ZodOptional ||
    unwrappedSchema instanceof z.ZodDefault ||
    unwrappedSchema instanceof z.ZodEffects
  ) {
    if (unwrappedSchema instanceof z.ZodOptional) {
      unwrappedSchema = unwrappedSchema.unwrap();
    } else if (unwrappedSchema instanceof z.ZodDefault) {
      unwrappedSchema = unwrappedSchema.removeDefault();
    } else if (unwrappedSchema instanceof z.ZodEffects) {
      unwrappedSchema = unwrappedSchema._def.schema;
    }
  }
  return unwrappedSchema;
};

// Helper function to get enum values from ZodEnum
export const getEnumValues = (zodSchema: z.ZodTypeAny): string[] => {
  if (zodSchema instanceof z.ZodEnum) {
    return Object.values(zodSchema.enum);
  }
  if (zodSchema instanceof z.ZodUnion) {
    // For union of literals, extract the literal values
    const options: string[] = [];
    zodSchema.options.forEach((option: z.ZodTypeAny) => {
      if (option instanceof z.ZodLiteral && typeof option.value === 'string') {
        options.push(option.value);
      }
    });
    return options;
  }
  return [];
};

// Helper function to get union options
export const getUnionOptions = (zodSchema: z.ZodTypeAny): string[] => {
  if (zodSchema instanceof z.ZodUnion) {
    return zodSchema.options.map((option: z.ZodTypeAny) => {
      if (option instanceof z.ZodLiteral) {
        const value = option.value;
        return typeof value === 'string' ? value : String(value);
      }
      if (option instanceof z.ZodString) {
        return 'string';
      }
      if (option instanceof z.ZodNumber) {
        return 'number';
      }
      if (option instanceof z.ZodBoolean) {
        return 'boolean';
      }
      return 'unknown';
    });
  }
  return [];
};

export const getFieldName = (controllerName: string): string => {
  const lastPart = controllerName.split('.').pop() ?? controllerName;
  return snakeCaseToTitleCase(lastPart);
};

export const getDefaultValue = (
  zodSchema: z.ZodTypeAny,
  defaultValue?: string | string[] | number | boolean
): string | string[] | number | boolean | undefined => {
  if (defaultValue) {
    return defaultValue;
  }
  if (
    zodSchema instanceof z.ZodOptional &&
    typeof zodSchema.unwrap()._def.defaultValue === 'function'
  ) {
    return zodSchema.unwrap()._def.defaultValue();
  }
  if (
    zodSchema instanceof z.ZodDefault &&
    typeof zodSchema.removeDefault()._def.defaultValue === 'function'
  ) {
    return zodSchema.removeDefault()._def.defaultValue();
  }
  if (typeof zodSchema._def.defaultValue === 'function') {
    return zodSchema._def.defaultValue();
  }
};

export const extractDefaults = <T>(schema: z.ZodType<T>, recursive = false): Partial<T> => {
  // Extract defaults from the schema structure
  if (schema instanceof z.ZodObject) {
    const shape = schema.shape;
    const defaults: Partial<T> = {};

    for (const [key, value] of Object.entries(shape)) {
      let unwrappedValue = value;
      if (value instanceof z.ZodOptional) {
        // Unwrap the optional schema
        unwrappedValue = value.unwrap();
      }
      if (unwrappedValue instanceof z.ZodDefault) {
        defaults[key as keyof T] = unwrappedValue._def.defaultValue();
      } else if (unwrappedValue instanceof z.ZodObject && recursive) {
        defaults[key as keyof T] = extractDefaults(unwrappedValue, recursive) as T[keyof T];
      }
    }
    return defaults;
  }
  return {};
};
