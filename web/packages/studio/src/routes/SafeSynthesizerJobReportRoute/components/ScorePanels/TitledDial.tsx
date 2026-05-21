// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { Dial } from '@nemo/common/src/components/Dial';
import { Divider, Flex, Stack, Tag, Text } from '@nvidia/foundations-react-core';
import { FC } from 'react';

interface TitledDialProps {
  title: string;
  value: number;
  displayValue: string;
  color: string;
  description: string;
  grade: string;
}

export const TitledDial: FC<TitledDialProps> = ({
  title,
  value,
  displayValue,
  color,
  description,
  grade,
}) => {
  return (
    <Stack gap="density-sm" data-testid="titled-dial">
      <Flex gap="density-sm">
        <Dial value={value} displayValue={displayValue} color={color} size="m" />
        <Stack align="start" justify="start" gap="density-lg" padding="density-md">
          <Text kind="body/bold/lg">{title}</Text>
          <Tag readOnly>{grade}</Tag>
        </Stack>
      </Flex>
      <Text kind="body/regular/sm">{description}</Text>
      <Divider className="my-density-lg" />
    </Stack>
  );
};
