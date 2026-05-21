// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { Stack, Text } from '@nvidia/foundations-react-core';
import type { FC } from 'react';

export const StatColumn: FC<{ label: string; value: number }> = ({ label, value }) => (
  <Stack gap="density-xxs">
    <Text kind="title/xs" color="secondary">
      {label}
    </Text>
    <Text kind="title/2xl">{value}</Text>
  </Stack>
);
