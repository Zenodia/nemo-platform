// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { GradientBackground } from '@nemo/common/src/components/GradientBackground/index';
import { Stack } from '@nvidia/foundations-react-core';
import type { Meta, StoryObj } from '@storybook/react';

const meta: Meta<typeof GradientBackground> = {
  component: GradientBackground,
  title: 'Studio Common/GradientBackground',
  decorators: [
    (Story) => (
      <div className="min-h-[400px] w-full">
        <Story />
      </div>
    ),
  ],
};

export default meta;

type Story = StoryObj<typeof GradientBackground>;

export const Default: Story = {
  render: () => (
    <GradientBackground>
      <Stack gap="density-3xl" padding="density-2xl" className="relative h-[500px]">
        <h2 className="text-lg font-medium text-foreground">Section title</h2>
        <p className="text-foreground">
          Example using Stack as in the component docs. The gradient sits behind the stacked
          content.
        </p>
      </Stack>
    </GradientBackground>
  ),
};

export const WithCustomClassName: Story = {
  render: () => (
    <GradientBackground className="rounded-lg border border-border">
      <div className="relative p-8">
        <p className="text-foreground">
          GradientBackground with custom className (e.g. rounded border) for layout or styling.
        </p>
      </div>
    </GradientBackground>
  ),
};
