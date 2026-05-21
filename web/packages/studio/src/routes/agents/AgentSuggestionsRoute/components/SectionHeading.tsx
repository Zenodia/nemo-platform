// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { Text } from '@nvidia/foundations-react-core';
import type { FC } from 'react';

export const SectionHeading: FC<{ children: string }> = ({ children }) => (
  <Text kind="label/bold/sm" color="secondary" className="uppercase tracking-wider">
    {children}
  </Text>
);
