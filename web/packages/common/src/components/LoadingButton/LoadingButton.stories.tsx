// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { LoadingButton } from '@nemo/common/src/components/LoadingButton/index';
import type { Meta, StoryObj } from '@storybook/react';

const meta: Meta<typeof LoadingButton> = {
  component: LoadingButton,
  title: 'Studio Common/LoadingButton',
  args: {
    children: 'Submit',
    loading: false,
    height: 40,
  },
};

export default meta;

type Story = StoryObj<typeof LoadingButton>;

export const Default: Story = {};

export const Loading: Story = {
  args: { loading: true },
};

export const Disabled: Story = {
  args: { disabled: true },
};

export const TallButton: Story = {
  args: { height: 56 },
};

export const LoadingTall: Story = {
  args: { loading: true, height: 56 },
};
