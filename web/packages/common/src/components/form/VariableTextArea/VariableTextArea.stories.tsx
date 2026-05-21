// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

// web/packages/common/src/components/form/VariableTextArea/VariableTextArea.stories.tsx
import {
  VariableTextArea,
  type VariableDef,
} from '@nemo/common/src/components/form/VariableTextArea/index';
import type { Meta, StoryObj } from '@storybook/react';
import { useState } from 'react';

const VARIABLES: VariableDef[] = [
  { name: 'input', description: 'The input from the dataset row.' },
  { name: 'output', description: 'The model output.' },
  { name: 'reference', description: 'The ground-truth reference.' },
];

function Harness({
  initial,
  variables,
  disabled,
}: {
  initial: string;
  variables?: VariableDef[];
  disabled?: boolean;
}) {
  const [value, setValue] = useState(initial);
  return (
    <div className="max-w-2xl">
      <VariableTextArea
        value={value}
        onChange={setValue}
        variables={variables}
        disabled={disabled}
        placeholder="Type your prompt template..."
        attributes={{ TextAreaElement: { 'aria-label': 'prompt' } }}
      />
      <pre className="text-xs mt-2 opacity-70">{JSON.stringify(value)}</pre>
    </div>
  );
}

const meta: Meta<typeof Harness> = {
  component: Harness,
  title: 'Studio Common/Form/VariableTextArea',
};

export default meta;
type Story = StoryObj<typeof Harness>;

export const Empty: Story = {
  args: { initial: '', variables: VARIABLES },
};

export const WithKnownAndUnknown: Story = {
  args: {
    initial: 'Question: {{input}}\nUnknown: {{whoops}}',
    variables: VARIABLES,
  },
};

export const NoVariableList: Story = {
  args: { initial: '{{anything}} is unknown', variables: [] },
};

export const Disabled: Story = {
  args: {
    initial: 'Read-only template with {{input}}',
    variables: VARIABLES,
    disabled: true,
  },
};
