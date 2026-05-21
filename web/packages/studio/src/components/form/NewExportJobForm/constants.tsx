// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { ControlledDatePicker } from '@nemo/common/src/components/form/ControlledDatePicker';
import { ControlledSelect } from '@nemo/common/src/components/form/ControlledSelect';
import { ControlledSwitch } from '@nemo/common/src/components/form/ControlledSwitch';
import { ZodFormField } from '@nemo/common/src/components/form/ZodFormField';
import { UseControllerComponentProps } from '@nemo/common/src/types';
import { generateDefaultName } from '@nemo/common/src/utils/generateDefaultName';
import { EntryFilter } from '@nemo/sdk/generated/platform/schema';
import {
  namespaceSchema,
  descriptionSchema,
  URNSchema,
  customFieldsSchema,
  ownershipSchema,
} from '@studio/constants/zod';
import { adjectives, animals } from 'unique-names-generator';
import { z } from 'zod';

export const validateIntakeFileUrl = (url: string) => {
  return (
    url.startsWith('file://') ||
    url.startsWith('hf://') ||
    url.startsWith('nds://') ||
    url.startsWith('fileset://')
  );
};

export const newExportJobFormSchema = z
  .object({
    namespace: namespaceSchema.optional(),
    description: descriptionSchema.optional(),
    config: z
      .object({
        filters: z
          .preprocess((val) => {
            const copy = { ...(val ?? {}) };
            Object.entries(val ?? {}).forEach(([key, value]) => {
              if (value === '') {
                delete (copy as Record<string, unknown>)[key];
              } else if (key === 'created_at' || key === 'updated_at') {
                (copy as Record<string, unknown>)[key] = {
                  gte: value.from as string,
                  lte: value.to as string,
                };
              }
            });
            return copy;
          }, z.record(z.string(), z.any()).optional())
          .describe(
            'Filter criteria for selecting entries (project, context, external_id, has_thumb, has_rating, longest_per_thread, etc.)'
          ),
        search: z
          .record(z.string(), z.any())
          .optional()
          .describe('Search criteria for finding entries'),
        limit: z
          .preprocess(
            (val) => (val === '' || val === undefined ? undefined : Number(val)),
            z.number().optional()
          )
          .describe('Maximum number of entries to export. None means no limit.'),
        format_options: z
          .record(z.string(), z.any())
          .optional()
          .describe('Format options for the export (e.g., row_transformation)'),
      })
      .describe(
        'Configuration for an export job.\n\nDefines what entries to export and how to format them.'
      )
      .describe('The export configuration defining filters, search criteria, and format options.'),
    output_file_url: z
      .string()
      .optional()
      .describe('The URL of the output file to export to (file://, hf://, nds://, etc.)'),
    project: URNSchema.optional(),
    custom_fields: customFieldsSchema,
    ownership: ownershipSchema,
    // Additional fields for UI state
    export_file_name: z
      .string()
      .optional()
      .describe(
        'The name of the export file. Currently only .jsonl files are supported. If not provided, a default name will be generated.'
      ),
    dataset: z.object({
      name: z.string().optional(),
      namespace: z.string().optional(),
      files_url: z.string().optional(),
    }),
  })
  .refine(
    (data) => {
      if (!data.output_file_url) {
        return false;
      }
      return validateIntakeFileUrl(data.output_file_url);
    },
    {
      message: 'Dataset is required',
      path: ['dataset.name'],
    }
  );
export const supportedCriteria: (keyof EntryFilter)[] = [
  'context',
  'created_at',
  'external_id',
  'id',
  'longest_per_thread',
  'project',
  'updated_at',
  'user_rating',
];
export const getExportCriteriaRender = (
  props: { filter: keyof EntryFilter } & UseControllerComponentProps
) => {
  const { filter } = props;
  switch (filter) {
    case 'longest_per_thread':
      return <ControlledSwitch useControllerProps={props.useControllerProps} />;
    case 'project':
      return <ZodFormField {...props} schema={z.string().optional()} />;
    case 'user_rating':
      return (
        <ControlledSelect
          items={['up', 'down']}
          kind="single"
          placeholder="Select a thumb rating"
          useControllerProps={{
            control: props.useControllerProps.control,
            name: 'config.filters.user_rating.thumb',
          }}
        />
      );
    case 'created_at':
    case 'updated_at':
      return (
        <ControlledDatePicker
          kind="range"
          useControllerProps={props.useControllerProps}
          placeholder="yyyy-mm-dd"
          format="yyyy-MM-dd"
          rangeKeys={{ from: 'gte', to: 'lte' }}
        />
      );
    default:
      return <ZodFormField {...props} schema={z.string().optional()} />;
  }
};

export const getDefaultExportFileName = () =>
  `export-${generateDefaultName({ dictionaries: [adjectives, animals], length: 2 })}.jsonl`;
