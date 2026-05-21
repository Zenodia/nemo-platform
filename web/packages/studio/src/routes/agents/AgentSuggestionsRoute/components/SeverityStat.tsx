// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { Flex, Text } from '@nvidia/foundations-react-core';
import type { FC } from 'react';

export const SeverityStat: FC<{
  value: number;
  label: 'HIGH' | 'LOW';
  delta?: number;
}> = ({ value, label, delta }) => {
  const colorClass = label === 'HIGH' ? 'text-accent-red' : 'text-accent-green';
  return (
    <Flex align="baseline" gap="density-xs">
      <Text kind="title/2xl">{value}</Text>
      <Text kind="body/bold/sm" className={colorClass}>
        {label}
      </Text>
      {delta !== undefined && delta !== 0 && (
        <Text kind="body/regular/sm" className={colorClass}>
          ({delta > 0 ? '+' : ''}
          {delta})
        </Text>
      )}
    </Flex>
  );
};
