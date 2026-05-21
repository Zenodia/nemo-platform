// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import {
  VariableButton,
  type VariableButtonProps,
} from '@nemo/common/src/components/buttons/VariableButton';
import type { Meta, StoryObj } from '@storybook/react';

const meta: Meta<VariableButtonProps> = {
  component: VariableButton,
  title: 'Studio Common/Buttons/VariableButton',
  args: { onSelect: () => {} },
};

export default meta;
type Story = StoryObj<typeof VariableButton>;

export const WithVariables: Story = {
  args: {
    variables: [
      { name: 'input', description: 'The dataset input.' },
      { name: 'output', description: 'The model output.' },
      { name: 'reference', description: 'The ground-truth reference.' },
    ],
  },
};

export const Empty: Story = {
  args: { variables: [] },
};

export const Disabled: Story = {
  args: {
    variables: [{ name: 'input' }],
    disabled: true,
  },
};
