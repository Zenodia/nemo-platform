// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { ControlledVariableTextArea } from '@nemo/common/src/components/form/ControlledVariableTextArea/index';
import type { VariableDef } from '@nemo/common/src/components/form/VariableTextArea';
import type { Meta, StoryObj } from '@storybook/react';
import { FormProvider, useForm } from 'react-hook-form';

const VARIABLES: VariableDef[] = [
  { name: 'input', description: 'The input from the dataset row.' },
  { name: 'output', description: 'The model output.' },
];

function Harness({ initial }: { initial: string }) {
  const methods = useForm<{ content: string }>({ defaultValues: { content: initial } });
  return (
    <FormProvider {...methods}>
      <div className="max-w-2xl">
        <ControlledVariableTextArea
          variables={VARIABLES}
          useControllerProps={{ control: methods.control, name: 'content' }}
          formFieldProps={{ name: 'content', slotLabel: 'Prompt template' }}
          placeholder="Type your prompt template..."
        />
      </div>
    </FormProvider>
  );
}

const meta: Meta<typeof Harness> = {
  component: Harness,
  title: 'Studio Common/Form/ControlledVariableTextArea',
};

export default meta;
type Story = StoryObj<typeof Harness>;

export const Default: Story = { args: { initial: 'Question: {{input}}\nAnswer:' } };
