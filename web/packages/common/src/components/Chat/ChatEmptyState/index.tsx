// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { Stack, Text, type StackProps } from '@nvidia/foundations-react-core';
import type { FC } from 'react';

import { Nebula } from '../../Nebula';

export interface ChatEmptyStateProps extends StackProps {
  slotHeading?: string;
  slotSubheading?: string;
}

export const ChatEmptyState: FC<ChatEmptyStateProps> = ({
  className,
  slotHeading = 'Ready',
  slotSubheading = 'Prompt your model to get started.',
  ...stackProps
}) => {
  const passedClasses = className?.split(' ') || [];
  return (
    <Stack
      {...stackProps}
      className={['relative'].concat(passedClasses).join(' ')}
      gap="density-md"
      align="center"
      justify="center"
    >
      <Text kind="label/bold/3xl" className="text-center">
        {slotHeading}
      </Text>
      <Text kind="label/regular/lg" className="text-center">
        {slotSubheading}
      </Text>
      <div className="absolute top-0 left-0 w-full h-full">
        <Nebula variant="sphere" />
      </div>
    </Stack>
  );
};
