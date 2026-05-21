/*
 * SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
 * SPDX-License-Identifier: Apache-2.0
 *
 * NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
 * property and proprietary rights in and to this material, related
 * documentation and any modifications thereto. Any use, reproduction,
 * disclosure or distribution of this material and related documentation
 * without an express license agreement from NVIDIA CORPORATION or
 * its affiliates is strictly prohibited.
 */

import {
  MappingFields,
  type MappingFieldsProps,
} from '@nemo/common/src/components/form/MappingFields/index';
import { Stack, Text } from '@nvidia/foundations-react-core';
import type { Meta, StoryObj } from '@storybook/react';
import { FormProvider, useForm } from 'react-hook-form';

type StoryForm = {
  pairs: Array<{ key: string; value?: string }>;
};

type HarnessProps = Partial<Omit<MappingFieldsProps<StoryForm, 'pairs'>, 'control' | 'name'>> & {
  defaultValues?: StoryForm;
};

function MappingFieldsHarness({ defaultValues = { pairs: [] }, ...fieldProps }: HarnessProps) {
  const methods = useForm<StoryForm>({
    defaultValues,
    mode: 'onChange',
  });
  const pairs = methods.watch('pairs');

  return (
    <FormProvider {...methods}>
      <Stack gap="density-xl" className="max-w-2xl">
        <MappingFields control={methods.control} name="pairs" {...fieldProps} />
        <Stack
          gap="density-sm"
          className="rounded-md border border-[var(--border-subtle-1)] p-density-md"
        >
          <Text kind="body/bold/sm">Live values (Dev only)</Text>
          <pre className="overflow-auto text-xs whitespace-pre-wrap font-mono opacity-90">
            {JSON.stringify(pairs, null, 2)}
          </pre>
        </Stack>
      </Stack>
    </FormProvider>
  );
}

const meta: Meta<typeof MappingFieldsHarness> = {
  component: MappingFieldsHarness,
  title: 'Studio Common/MappingFields',
  decorators: [
    (Story) => (
      <div className="p-density-lg">
        <Story />
      </div>
    ),
  ],
};

export default meta;

type Story = StoryObj<typeof MappingFieldsHarness>;

export const EmptyFreeForm: Story = {
  name: 'Free-form (empty)',
  args: {},
};

export const FreeFormDifferentRatio: Story = {
  name: 'Free-form (different ratio)',
  args: {
    defaultValues: {
      pairs: [
        { key: 'X-Custom-Header', value: 'example' },
        { key: '', value: '' },
      ],
    },
    attributes: {
      keyTextInput: {
        formFieldProps: {
          className: 'flex-4',
        },
      },
    },
  },
};

export const TextInputsNoSuggestions: Story = {
  name: 'Text inputs (no suggestions)',
  args: {
    defaultValues: {
      pairs: [
        { key: 'X-Custom-Header', value: 'example' },
        { key: '', value: '' },
      ],
    },
    keySuggestions: [],
    valueSuggestions: [],
    keyColumnLabel: 'Name',
    valueColumnLabel: 'Value',
    attributes: {
      keyTextInput: {
        placeholder: 'e.g. environment',
        formFieldProps: {
          slotInfo: 'Arbitrary string keys when there is no suggestion list.',
        },
      },
      valueTextInput: {
        placeholder: 'e.g. production',
      },
    },
  },
};

export const FreeFormWithInitialRows: Story = {
  name: 'Free-form (initial rows)',
  args: {
    defaultValues: {
      pairs: [
        { key: 'Content-Type', value: 'application/json' },
        { key: 'X-Request-Id', value: '' },
      ],
    },
    keyColumnLabel: 'Header',
    valueColumnLabel: 'Value',
  },
};

const fileLikeSchema = {
  prompt: 'string',
  response: 'string',
  metadata: 'object',
};

export const FromSchema: Story = {
  name: 'From schema (transform-style)',
  args: {
    defaultValues: { pairs: [] },
    schema: fileLikeSchema,
  },
};

export const CustomSuggestions: Story = {
  name: 'Custom key/value suggestions',
  args: {
    defaultValues: { pairs: [{ key: '', value: '' }] },
    keySuggestions: ['staging', 'production', 'development'],
    valueSuggestions: ['us-west-2', 'us-east-1', 'eu-central-1'],
  },
};

export const CustomSchemaValueTemplate: Story = {
  name: 'Custom schema value template',
  args: {
    defaultValues: { pairs: [] },
    schema: { alpha: 1, beta: 2 },
    schemaValueForKey: (key) => `$env.${key}`,
  },
};

export const Disabled: Story = {
  args: {
    defaultValues: {
      pairs: [{ key: 'only', value: 'row' }],
    },
    disabled: true,
  },
};
