// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import type { Meta, StoryObj } from '@storybook/react';
import { Pre } from '@studio/components/common/Pre';

const meta: Meta<typeof Pre> = {
  component: Pre,
  title: 'Components/Pre',
};

export default meta;

type Story = StoryObj<typeof Pre>;

export const Default: Story = {
  args: {
    children: 'const example = "Hello, Storybook";',
  },
};

export const WithWrapper: Story = {
  args: {
    wrapper: true,
    children: 'Wrapped preformatted text content',
  },
};
