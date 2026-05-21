// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { ErrorMessage } from '@nemo/common/src/components/ErrorMessage/index';
import type { Meta, StoryObj } from '@storybook/react';

const meta: Meta<typeof ErrorMessage> = {
  component: ErrorMessage,
  title: 'Studio Common/ErrorMessage',
};

export default meta;

type Story = StoryObj<typeof ErrorMessage>;

export const Default: Story = {
  args: {
    header: 'Error',
    message: 'An unexpected error occurred',
  },
};

export const CustomMessage: Story = {
  args: {
    header: 'Something went wrong',
    message: 'The operation could not be completed. Please try again.',
  },
};
