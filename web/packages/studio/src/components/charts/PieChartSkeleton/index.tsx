// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { Flex, Stack, Skeleton } from '@nvidia/foundations-react-core';
import { FC } from 'react';

interface Props {
  width?: string | number;
  height?: string | number;
}
export const PieChartSkeleton: FC<Props> = ({ width, height = 400 }) => {
  return (
    // eslint-disable-next-line no-restricted-syntax
    <Stack style={{ width, height }} gap="density-sm">
      {/* Skeleton for chart title */}
      <Skeleton className="w-1/2 h-[30px]" />

      {/* Skeleton for pie chart area */}
      <Flex align="center" className="self-center justify-center relative w-full h-full">
        <Skeleton kind="circle" className="aspect-square h-3/4" />
      </Flex>
    </Stack>
  );
};
